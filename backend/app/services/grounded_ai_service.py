from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..schemas.ai import (
    GroundedRecommendationRequest,
    GroundedRecommendationResponse,
    LLMMealPlanPayload,
    LLMNutritionQAPayload,
    LLMRecommendationPayload,
    MacroSummary,
    MealPlanRequest,
    MealPlanResponse,
    NutritionQARequest,
    NutritionQAResponse,
    RecommendedRecipe,
    SourceRecipeRef,
)
from ..schemas.recipe import RecipeFilters, RetrievalDiagnostics
from ..core.observability import log_event
from .llm_service import LLMService
from .rag_service import RagService

logger = logging.getLogger("nourishai.grounded")

KNOWN_ALLERGENS = {
    "gluten",
    "dairy",
    "soy",
    "egg",
    "fish",
    "shellfish",
    "peanut",
    "peanuts",
    "tree nuts",
    "sesame",
}

DIET_TAG_TO_ALLERGEN = {
    "gluten_free": "gluten",
    "dairy_free": "dairy",
    "soy_free": "soy",
    "egg_free": "egg",
    "nut_free": "tree nuts",
    "peanut_free": "peanut",
    "sesame_free": "sesame",
}


class GroundedAIService:
    def __init__(self, rag: RagService, llm: LLMService) -> None:
        self.rag = rag
        self.llm = llm

    def grounded_recommendations(self, request: GroundedRecommendationRequest) -> GroundedRecommendationResponse:
        query = f"{', '.join(request.ingredients)}. {request.dietary_notes or ''}".strip()
        context_k = request.candidate_k or max(request.top_k * 3, request.top_k + 5)
        results, diagnostics = self.rag.search_with_diagnostics(
            query=query,
            top_k=context_k,
            filters=request.filters,
            rerank=request.rerank,
            candidate_k=context_k,
            ingredients=request.ingredients,
            include_diagnostics=request.include_diagnostics,
        )

        if not results:
            log_event(
                logger,
                "grounded_recommendations_fallback",
                reason="no_results",
                query=query,
                filters=request.filters.model_dump() if request.filters else None,
            )
            return GroundedRecommendationResponse(
                recommended_recipes=[],
                warnings=["No recipes matched the query and filters."],
                source_recipes=[],
                retrieval_diagnostics=diagnostics,
            )

        context = self._build_recipe_context(results)
        system_prompt = (
            "You are NourishAI. Use ONLY the provided recipes as sources. "
            "Do not invent recipes, ingredients, or nutrition facts. "
            "If the context is weak, return fewer items and add a warning."
        )
        user_prompt = (
            "Task: Recommend recipes based on the user's ingredients and dietary notes. "
            "Return JSON that matches the schema. "
            "Include why each recipe was selected, substitutions for missing ingredients, "
            "and warnings for dietary conflicts if present.\n\n"
            f"User ingredients: {request.ingredients}\n"
            f"Dietary notes: {request.dietary_notes or 'none'}\n\n"
            f"Recipes:\n{context}"
        )

        log_event(
            logger,
            "grounded_recommendations_context",
            source_ids=[str(r.get("id", "")) for r in results],
            source_count=len(results),
        )

        llm_start = time.perf_counter()
        try:
            payload = self.llm.generate_structured(system_prompt, user_prompt, LLMRecommendationPayload)
        except Exception as exc:
            log_event(
                logger,
                "grounded_recommendations_llm_failed",
                error=str(exc),
                source_ids=[str(r.get("id", "")) for r in results],
            )
            return GroundedRecommendationResponse(
                recommended_recipes=[],
                warnings=["LLM generation failed; no grounded recommendations were returned."],
                source_recipes=self._source_refs(results),
                retrieval_diagnostics=diagnostics,
            )
        llm_ms = (time.perf_counter() - llm_start) * 1000.0

        allowed_ids = {str(r.get("id", "")) for r in results}
        recipe_map = {str(r.get("id", "")): r for r in results}
        filtered = [r for r in payload.recommended_recipes if r.recipe_id in allowed_ids]
        filtered = filtered[: request.top_k]
        dropped = len(payload.recommended_recipes) - len(filtered)

        warnings = list(payload.warnings)
        if dropped:
            warnings.append("Some recommendations were dropped because they were not in retrieved sources.")

        filtered, conflict_warnings = self._collect_conflicts(filtered, recipe_map, request.filters, request.dietary_notes)
        warnings.extend(conflict_warnings)

        source_refs = self._source_refs(results)

        log_event(
            logger,
            "grounded_recommendations_complete",
            source_count=len(results),
            selected_ids=[r.recipe_id for r in filtered],
            dropped_count=dropped,
            warning_count=len(warnings),
            llm_latency_ms=round(llm_ms, 2),
        )

        return GroundedRecommendationResponse(
            recommended_recipes=filtered,
            warnings=warnings,
            source_recipes=source_refs,
            retrieval_diagnostics=diagnostics,
        )

    def generate_meal_plan(self, request: MealPlanRequest) -> MealPlanResponse:
        query_parts = [request.dietary_profile or "", "meal plan", "balanced"]
        if request.meal_preferences:
            query_parts.append(", ".join(request.meal_preferences))
        query = ". ".join(part for part in query_parts if part).strip()

        candidate_k = request.candidate_k or max(request.days * request.meals_per_day * 3, 10)
        results, diagnostics = self.rag.search_with_diagnostics(
            query=query,
            top_k=candidate_k,
            filters=request.filters,
            rerank=request.rerank,
            candidate_k=candidate_k,
            include_diagnostics=request.include_diagnostics,
        )

        if not results:
            log_event(
                logger,
                "meal_plan_fallback",
                reason="no_results",
                query=query,
                filters=request.filters.model_dump() if request.filters else None,
            )
            return MealPlanResponse(
                days=[],
                dietary_notes=request.dietary_profile,
                warnings=["No recipes matched the meal plan query."],
                source_recipes=[],
                retrieval_diagnostics=diagnostics,
            )

        context = self._build_recipe_context(results)
        system_prompt = (
            "You are NourishAI. Build a meal plan using ONLY the provided recipes. "
            "Do not invent recipes or nutrition values. If data is missing, leave fields null."
        )
        user_prompt = (
            "Task: Create a multi-day meal plan using the provided recipes. "
            "Return JSON that matches the schema.\n\n"
            f"Dietary profile: {request.dietary_profile or 'none'}\n"
            f"Calorie target per day: {request.calorie_target or 'unspecified'}\n"
            f"Days: {request.days}\n"
            f"Meals per day: {request.meals_per_day}\n"
            f"Meal preferences: {request.meal_preferences or []}\n\n"
            f"Recipes:\n{context}"
        )

        log_event(
            logger,
            "meal_plan_context",
            source_ids=[str(r.get("id", "")) for r in results],
            source_count=len(results),
        )

        llm_start = time.perf_counter()
        try:
            payload = self.llm.generate_structured(system_prompt, user_prompt, LLMMealPlanPayload)
        except Exception as exc:
            log_event(
                logger,
                "meal_plan_llm_failed",
                error=str(exc),
                source_ids=[str(r.get("id", "")) for r in results],
            )
            return MealPlanResponse(
                days=[],
                dietary_notes=request.dietary_profile,
                warnings=["LLM generation failed; no meal plan was returned."],
                source_recipes=self._source_refs(results),
                retrieval_diagnostics=diagnostics,
            )
        llm_ms = (time.perf_counter() - llm_start) * 1000.0
        allowed_ids = {str(r.get("id", "")) for r in results}

        filtered_days = []
        removed = 0
        for day in payload.days:
            meals = [meal for meal in day.meals if meal.recipe_id in allowed_ids]
            removed += len(day.meals) - len(meals)
            filtered_days.append(day.model_copy(update={"meals": meals}))

        warnings = list(payload.warnings)
        if removed:
            warnings.append("Some meals were removed because they were not in retrieved sources.")

        source_refs = self._source_refs(results)
        meal_ids = [meal.recipe_id for day in filtered_days for meal in day.meals]
        log_event(
            logger,
            "meal_plan_complete",
            source_count=len(results),
            selected_ids=meal_ids,
            removed_count=removed,
            warning_count=len(warnings),
            llm_latency_ms=round(llm_ms, 2),
        )

        return MealPlanResponse(
            days=filtered_days,
            dietary_notes=payload.dietary_notes or request.dietary_profile,
            warnings=warnings,
            source_recipes=source_refs,
            retrieval_diagnostics=diagnostics,
        )

    def answer_nutrition_question(self, request: NutritionQARequest) -> NutritionQAResponse:
        results, diagnostics = self.rag.search_with_diagnostics(
            query=request.question,
            top_k=request.top_k,
            filters=request.filters,
            rerank=request.rerank,
            candidate_k=request.candidate_k,
            include_diagnostics=request.include_diagnostics,
        )

        if not results:
            log_event(
                logger,
                "nutrition_qa_fallback",
                reason="no_results",
                query=request.question,
                filters=request.filters.model_dump() if request.filters else None,
            )
            return NutritionQAResponse(
                answer="I could not find supporting recipes for that question.",
                supporting_sources=[],
                warnings=["No relevant recipes found."],
                retrieval_diagnostics=diagnostics,
            )

        context = self._build_recipe_context(results)
        system_prompt = (
            "You are NourishAI. Answer ONLY using the provided recipes. "
            "Do not invent nutrition facts. If uncertain, say so."
        )
        user_prompt = (
            "Task: Answer the nutrition question using the recipes below. "
            "Return JSON that matches the schema.\n\n"
            f"Question: {request.question}\n\n"
            f"Recipes:\n{context}"
        )

        log_event(
            logger,
            "nutrition_qa_context",
            source_ids=[str(r.get("id", "")) for r in results],
            source_count=len(results),
        )

        llm_start = time.perf_counter()
        try:
            payload = self.llm.generate_structured(system_prompt, user_prompt, LLMNutritionQAPayload)
        except Exception as exc:
            log_event(
                logger,
                "nutrition_qa_llm_failed",
                error=str(exc),
                source_ids=[str(r.get("id", "")) for r in results],
            )
            return NutritionQAResponse(
                answer="LLM generation failed; unable to answer using retrieved sources.",
                supporting_sources=self._source_refs(results),
                warnings=["LLM generation failed; returning sources only."],
                retrieval_diagnostics=diagnostics,
            )
        llm_ms = (time.perf_counter() - llm_start) * 1000.0
        allowed_ids = {str(r.get("id", "")) for r in results}
        supporting = [rid for rid in payload.supporting_recipe_ids if rid in allowed_ids]
        if not supporting:
            supporting = [str(r.get("id", "")) for r in results[: min(3, len(results))]]
            payload = payload.model_copy(update={"warnings": payload.warnings + ["No supporting source IDs were provided; defaults were used."]})

        source_refs = self._source_refs(results)
        supporting_refs = [ref for ref in source_refs if ref.id in supporting]

        log_event(
            logger,
            "nutrition_qa_complete",
            source_count=len(results),
            supporting_ids=supporting,
            warning_count=len(payload.warnings),
            llm_latency_ms=round(llm_ms, 2),
        )

        return NutritionQAResponse(
            answer=payload.answer,
            supporting_sources=supporting_refs,
            warnings=payload.warnings,
            retrieval_diagnostics=diagnostics,
        )

    def _build_recipe_context(self, recipes: Sequence[Dict[str, Any]]) -> str:
        context_payload = []
        for recipe in recipes:
            context_payload.append(
                {
                    "id": str(recipe.get("id", "")),
                    "title": recipe.get("title", ""),
                    "ingredients": recipe.get("ingredients") or [],
                    "instructions": recipe.get("instructions") or [],
                    "calories": recipe.get("calories"),
                    "protein_g": recipe.get("protein_g"),
                    "carbs_g": recipe.get("carbs_g"),
                    "fat_g": recipe.get("fat_g"),
                    "cuisine": recipe.get("cuisine"),
                    "meal_type": recipe.get("meal_type"),
                    "dietary_tags": recipe.get("dietary_tags"),
                    "allergens": recipe.get("allergens"),
                    "prep_time_minutes": recipe.get("prep_time_minutes"),
                    "cook_time_minutes": recipe.get("cook_time_minutes"),
                    "total_time_minutes": recipe.get("total_time_minutes"),
                }
            )
        return json.dumps(context_payload, ensure_ascii=True)

    @staticmethod
    def _source_refs(recipes: Sequence[Dict[str, Any]]) -> List[SourceRecipeRef]:
        refs = []
        for recipe in recipes:
            refs.append(SourceRecipeRef(id=str(recipe.get("id", "")), title=recipe.get("title", "")))
        return refs

    def _collect_conflicts(
        self,
        recommended: Sequence[RecommendedRecipe],
        recipe_map: Dict[str, Dict[str, Any]],
        filters: Optional[RecipeFilters],
        dietary_notes: Optional[str],
    ) -> Tuple[List[RecommendedRecipe], List[str]]:
        warnings: List[str] = []
        restricted = self._restricted_allergens(filters, dietary_notes)
        if not restricted:
            return list(recommended), warnings

        restricted_set = {r.lower() for r in restricted}
        updated: List[RecommendedRecipe] = []

        for item in recommended:
            recipe = recipe_map.get(item.recipe_id, {})
            allergens = _normalize_list(recipe.get("allergens"))
            conflicts = restricted_set.intersection(allergens)
            if conflicts:
                extra = [f"Contains {allergen}." for allergen in sorted(conflicts)]
                merged = list(dict.fromkeys(item.warnings + extra))
                updated.append(item.model_copy(update={"warnings": merged}))
            else:
                updated.append(item)

        if restricted_set:
            warnings.append(
                "Dietary restrictions were detected; verify allergens in the recommended recipes."
            )
        return updated, warnings

    def _restricted_allergens(self, filters: Optional[RecipeFilters], dietary_notes: Optional[str]) -> List[str]:
        restricted: List[str] = []
        if filters and filters.dietary_tags:
            for tag in filters.dietary_tags:
                key = str(tag).lower()
                if key in DIET_TAG_TO_ALLERGEN:
                    restricted.append(DIET_TAG_TO_ALLERGEN[key])
        if dietary_notes:
            restricted.extend(_extract_allergens_from_notes(dietary_notes))
        return list({r for r in restricted if r})


def _extract_allergens_from_notes(text: str) -> List[str]:
    notes = text.lower()
    allergens: List[str] = []
    for allergen in KNOWN_ALLERGENS:
        if allergen in notes:
            allergens.append(allergen)
    match = re.findall(r"no\s+([a-z\s]+)", notes)
    for item in match:
        value = item.strip()
        if value:
            allergens.append(value)
    return allergens


def _normalize_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).lower() for v in value if str(v).strip()]
    if isinstance(value, str):
        if "," in value:
            return [v.strip().lower() for v in value.split(",") if v.strip()]
        return [value.strip().lower()]
    return [str(value).lower()]
