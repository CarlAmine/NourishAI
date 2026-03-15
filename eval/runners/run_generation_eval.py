from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import subprocess
from typing import Any, Dict, List, Optional, Sequence, Type

from backend.app.core.config import settings
from backend.app.schemas.ai import (
    GroundedRecommendationRequest,
    GroundedRecommendationResponse,
    LLMMealPlanPayload,
    LLMNutritionQAPayload,
    LLMRecommendationPayload,
    MacroSummary,
    MealPlanDay,
    MealPlanMeal,
    MealPlanRequest,
    MealPlanResponse,
    NutritionQARequest,
    NutritionQAResponse,
    RecommendedRecipe,
)
from backend.app.schemas.recipe import RecipeFilters
from backend.app.services.grounded_ai_service import GroundedAIService
from backend.app.services.llm_service import LLMService
from backend.app.services.rag_service import RagService
from eval.metrics.generation_metrics import evaluate_generation_case


class OfflineLLMService:
    def generate_structured(self, system_prompt: str, user_prompt: str, schema_model: Type[Any]) -> Any:
        context = _extract_context(user_prompt)
        if schema_model is LLMRecommendationPayload:
            return _offline_recommendations(context, user_prompt)
        if schema_model is LLMMealPlanPayload:
            return _offline_meal_plan(context, user_prompt)
        if schema_model is LLMNutritionQAPayload:
            return _offline_nutrition_qa(context)
        raise RuntimeError(f"Unsupported schema model: {schema_model}")


def _extract_context(user_prompt: str) -> List[Dict[str, Any]]:
    marker = "Recipes:\n"
    if marker not in user_prompt:
        return []
    payload = user_prompt.split(marker, 1)[1].strip()
    if not payload:
        return []
    try:
        data = json.loads(payload)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        return []
    return []


def _extract_int(label: str, text: str, default: int) -> int:
    match = re.search(rf"{re.escape(label)}\s*(\d+)", text)
    if match:
        return int(match.group(1))
    return default


def _extract_dietary_profile(text: str) -> Optional[str]:
    match = re.search(r"Dietary profile:\s*(.+)", text)
    if match:
        value = match.group(1).strip()
        return value if value and value.lower() != "none" else None
    return None


def _macro_summary(recipe: Dict[str, Any]) -> Optional[MacroSummary]:
    calories = recipe.get("calories")
    protein_g = recipe.get("protein_g")
    carbs_g = recipe.get("carbs_g")
    fat_g = recipe.get("fat_g")
    if calories is None and protein_g is None and carbs_g is None and fat_g is None:
        return None
    return MacroSummary(
        calories=calories,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g,
    )


def _offline_recommendations(context: Sequence[Dict[str, Any]], user_prompt: str) -> LLMRecommendationPayload:
    items: List[RecommendedRecipe] = []
    for recipe in context[:3]:
        items.append(
            RecommendedRecipe(
                recipe_id=str(recipe.get("id", "")),
                title=recipe.get("title", ""),
                why_selected="Matches the retrieved ingredients and dietary notes.",
                substitutions=[],
                warnings=[],
                nutrition_summary=_macro_summary(recipe),
            )
        )
    return LLMRecommendationPayload(recommended_recipes=items, warnings=[])


def _offline_meal_plan(context: Sequence[Dict[str, Any]], user_prompt: str) -> LLMMealPlanPayload:
    days = _extract_int("Days:", user_prompt, 1)
    meals_per_day = _extract_int("Meals per day:", user_prompt, 3)
    dietary_notes = _extract_dietary_profile(user_prompt)

    if not context:
        return LLMMealPlanPayload(days=[], dietary_notes=dietary_notes, warnings=["No recipes provided."])

    plan_days: List[MealPlanDay] = []
    for day_index in range(days):
        meals: List[MealPlanMeal] = []
        for meal_index in range(meals_per_day):
            recipe = context[(day_index * meals_per_day + meal_index) % len(context)]
            meal_type = recipe.get("meal_type")
            if isinstance(meal_type, list) and meal_type:
                meal_type_value = str(meal_type[0])
            else:
                meal_type_value = meal_type
            meals.append(
                MealPlanMeal(
                    recipe_id=str(recipe.get("id", "")),
                    title=recipe.get("title", ""),
                    meal_type=meal_type_value,
                    why_selected="Balanced fit for the requested plan.",
                    estimated_calories=recipe.get("calories"),
                    macros=_macro_summary(recipe),
                    warnings=[],
                )
            )
        plan_days.append(MealPlanDay(day=day_index + 1, meals=meals, estimated_totals=None, notes=None))

    return LLMMealPlanPayload(days=plan_days, dietary_notes=dietary_notes, warnings=[])


def _offline_nutrition_qa(context: Sequence[Dict[str, Any]]) -> LLMNutritionQAPayload:
    if not context:
        return LLMNutritionQAPayload(
            answer="No supporting recipes were provided.",
            supporting_recipe_ids=[],
            warnings=["No sources available."],
        )
    top = context[:3]
    titles = ", ".join(recipe.get("title", "") for recipe in top if recipe.get("title"))
    answer = f"Based on the retrieved recipes, relevant options include: {titles}."
    supporting_ids = [str(recipe.get("id", "")) for recipe in top]
    return LLMNutritionQAPayload(answer=answer, supporting_recipe_ids=supporting_ids, warnings=[])


def _load_dataset(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _git_commit() -> Optional[str]:
    try:
        output = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
        return output.decode("utf-8").strip()
    except Exception:
        return None


def _filters_from_request(request: Any) -> Optional[RecipeFilters]:
    if hasattr(request, "filters"):
        return request.filters
    return None


def _retrieved_ids_from_response(response: Any) -> List[str]:
    if isinstance(response, GroundedRecommendationResponse):
        return [ref.id for ref in response.source_recipes]
    if isinstance(response, MealPlanResponse):
        return [ref.id for ref in response.source_recipes]
    if isinstance(response, NutritionQAResponse):
        if response.retrieval_diagnostics and response.retrieval_diagnostics.top_ids:
            return list(response.retrieval_diagnostics.top_ids)
        return [ref.id for ref in response.supporting_sources]
    return []


def _response_payload(response: Any) -> Dict[str, Any]:
    if hasattr(response, "model_dump"):
        return response.model_dump()
    return {}


def run(args: argparse.Namespace) -> None:
    dataset = _load_dataset(args.dataset)
    cases = dataset.get("cases", [])

    if not os.path.exists(settings.FAISS_INDEX_PATH) or not os.path.exists(settings.RECIPES_PKL_PATH):
        raise RuntimeError(
            "RAG artifacts not found. Build them with: "
            "python scripts/build_rag_index.py --recipes data/sample_recipes.json --out-dir models/"
        )

    rag = RagService(settings.FAISS_INDEX_PATH, settings.RECIPES_PKL_PATH)
    if args.mode == "openai":
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is required for --mode openai")
        llm: Any = LLMService()
    else:
        llm = OfflineLLMService()

    grounded = GroundedAIService(rag=rag, llm=llm)
    recipe_map = {str(recipe.get("id", "")): recipe for recipe in rag.recipes}

    results: List[Dict[str, Any]] = []
    for case in cases:
        case_type = case.get("type")
        request_payload = case.get("request", {})

        if case_type == "recommendation":
            request = GroundedRecommendationRequest.model_validate(request_payload)
            response = grounded.grounded_recommendations(request)
        elif case_type == "meal_plan":
            request = MealPlanRequest.model_validate(request_payload)
            response = grounded.generate_meal_plan(request)
        elif case_type == "nutrition_qa":
            request = NutritionQARequest.model_validate(request_payload)
            response = grounded.answer_nutrition_question(request)
        else:
            raise ValueError(f"Unknown eval case type: {case_type}")

        retrieved_ids = _retrieved_ids_from_response(response)
        metrics = evaluate_generation_case(
            response_type=case_type,
            response=response,
            retrieved_ids=retrieved_ids,
            recipe_map=recipe_map,
            filters=_filters_from_request(request),
            rag=rag,
            expect_fallback=bool(case.get("expect_fallback", False)),
            expect_warning=bool(case.get("expect_warning", False)),
        )

        results.append(
            {
                "case_id": case.get("id"),
                "type": case_type,
                "request": request_payload,
                "response": _response_payload(response),
                "retrieved_ids": retrieved_ids,
                **metrics,
            }
        )

    summary = {
        "cases": len(results),
        "fallback_correct_rate": _ratio([row["fallback_correct"] for row in results]),
        "warning_correct_rate": _ratio([row["warning_correct"] for row in results]),
        "source_id_violations": sum(row["source_id_violations"] for row in results),
        "unknown_recipe_refs": sum(row["unknown_recipe_refs"] for row in results),
        "filter_violations": sum(row["filter_violations"] for row in results),
    }

    os.makedirs(args.out_dir, exist_ok=True)
    run_id = args.run_id or dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
    payload = {
        "run_id": run_id,
        "dataset_path": args.dataset,
        "dataset_version": dataset.get("version"),
        "mode": args.mode,
        "faiss_index_path": settings.FAISS_INDEX_PATH,
        "recipes_pkl_path": settings.RECIPES_PKL_PATH,
        "git_commit": _git_commit(),
        "summary": summary,
        "cases": results,
    }

    json_path = os.path.join(args.out_dir, f"generation_eval_{run_id}.json")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    csv_path = os.path.join(args.out_dir, f"generation_eval_{run_id}.csv")
    csv_fields = [
        "case_id",
        "type",
        "fallback_correct",
        "warning_correct",
        "source_id_violations",
        "unknown_recipe_refs",
        "filter_violations",
        "response_count",
        "retrieved_count",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=csv_fields)
        writer.writeheader()
        for row in results:
            writer.writerow({field: row.get(field) for field in csv_fields})

    print("Generation evaluation complete.")
    print(f"Run ID: {run_id}")
    print(f"JSON: {json_path}")
    print(f"CSV:  {csv_path}")
    print(
        "Summary: fallback_correct_rate={:.2f}, warning_correct_rate={:.2f}, "
        "source_id_violations={}, filter_violations={}".format(
            summary["fallback_correct_rate"],
            summary["warning_correct_rate"],
            summary["source_id_violations"],
            summary["filter_violations"],
        )
    )


def _ratio(flags: List[bool]) -> float:
    if not flags:
        return 0.0
    return sum(1 for flag in flags if flag) / float(len(flags))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run grounded generation evaluation for NourishAI.")
    parser.add_argument(
        "--dataset",
        default="eval/datasets/grounded_generation_eval.json",
        help="Path to grounded generation evaluation dataset JSON.",
    )
    parser.add_argument(
        "--out-dir",
        default="eval/outputs",
        help="Directory to write evaluation artifacts.",
    )
    parser.add_argument(
        "--mode",
        choices=["offline", "openai"],
        default="offline",
        help="offline uses deterministic stub LLM; openai calls the real API.",
    )
    parser.add_argument("--run-id", default=None, help="Optional run identifier.")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
