from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from backend.app.schemas.ai import (
    GroundedRecommendationResponse,
    MealPlanResponse,
    NutritionQAResponse,
)
from backend.app.schemas.recipe import RecipeFilters
from backend.app.services.rag_service import RagService


def extract_response_ids(response: Any, response_type: str) -> List[str]:
    if response_type == "recommendation" and isinstance(response, GroundedRecommendationResponse):
        return [item.recipe_id for item in response.recommended_recipes]
    if response_type == "meal_plan" and isinstance(response, MealPlanResponse):
        ids: List[str] = []
        for day in response.days:
            ids.extend([meal.recipe_id for meal in day.meals])
        return ids
    if response_type == "nutrition_qa" and isinstance(response, NutritionQAResponse):
        return [source.id for source in response.supporting_sources]
    return []


def extract_warning_messages(response: Any, response_type: str) -> List[str]:
    warnings: List[str] = []
    if hasattr(response, "warnings") and response.warnings:
        warnings.extend(list(response.warnings))

    if response_type == "recommendation" and isinstance(response, GroundedRecommendationResponse):
        for item in response.recommended_recipes:
            warnings.extend(item.warnings)

    if response_type == "meal_plan" and isinstance(response, MealPlanResponse):
        for day in response.days:
            for meal in day.meals:
                warnings.extend(meal.warnings)

    return [msg for msg in warnings if msg]


def is_fallback_response(response: Any, response_type: str) -> bool:
    if response_type == "recommendation" and isinstance(response, GroundedRecommendationResponse):
        return len(response.recommended_recipes) == 0
    if response_type == "meal_plan" and isinstance(response, MealPlanResponse):
        if not response.days:
            return True
        return all(len(day.meals) == 0 for day in response.days)
    if response_type == "nutrition_qa" and isinstance(response, NutritionQAResponse):
        return len(response.supporting_sources) == 0
    return False


def count_source_id_violations(response_ids: Iterable[str], retrieved_ids: Iterable[str]) -> int:
    retrieved_set = set(retrieved_ids)
    return len([rid for rid in response_ids if rid not in retrieved_set])


def count_unknown_refs(response_ids: Iterable[str], recipe_map: Dict[str, Dict[str, Any]]) -> int:
    return len([rid for rid in response_ids if rid not in recipe_map])


def count_filter_violations(
    response_ids: Iterable[str],
    recipe_map: Dict[str, Dict[str, Any]],
    filters: Optional[RecipeFilters],
    rag: RagService,
) -> int:
    if not filters:
        return 0
    violations = 0
    for recipe_id in response_ids:
        recipe = recipe_map.get(recipe_id)
        if recipe and not rag._matches_filters(recipe, filters):
            violations += 1
    return violations


def evaluate_generation_case(
    response_type: str,
    response: Any,
    retrieved_ids: List[str],
    recipe_map: Dict[str, Dict[str, Any]],
    filters: Optional[RecipeFilters],
    rag: RagService,
    expect_fallback: bool,
    expect_warning: bool,
) -> Dict[str, Any]:
    response_ids = extract_response_ids(response, response_type)
    warnings = extract_warning_messages(response, response_type)
    fallback_detected = is_fallback_response(response, response_type)

    return {
        "response_count": len(response_ids),
        "retrieved_count": len(retrieved_ids),
        "source_id_violations": count_source_id_violations(response_ids, retrieved_ids),
        "unknown_recipe_refs": count_unknown_refs(response_ids, recipe_map),
        "filter_violations": count_filter_violations(response_ids, recipe_map, filters, rag),
        "warnings_present": bool(warnings),
        "warning_expected": expect_warning,
        "warning_correct": bool(warnings) == bool(expect_warning),
        "fallback_detected": fallback_detected,
        "fallback_expected": expect_fallback,
        "fallback_correct": fallback_detected == bool(expect_fallback),
    }
