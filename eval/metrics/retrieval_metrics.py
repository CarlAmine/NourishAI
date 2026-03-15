from typing import Any, Dict, List, Optional

from backend.app.schemas.recipe import RecipeFilters
from backend.app.services.rag_service import RagService


def hit_at_k(retrieved_ids: List[str], expected_ids: List[str]) -> int:
    return int(bool(set(retrieved_ids).intersection(expected_ids)))


def recall_at_k(retrieved_ids: List[str], expected_ids: List[str]) -> Optional[float]:
    if not expected_ids:
        return None
    return len(set(retrieved_ids).intersection(expected_ids)) / float(len(set(expected_ids)))


def filter_violations(results: List[Dict[str, Any]], filters: Optional[RecipeFilters], rag: RagService) -> int:
    if not filters:
        return 0
    violations = 0
    for recipe in results:
        if not rag._matches_filters(recipe, filters):
            violations += 1
    return violations


def excluded_violations(retrieved_ids: List[str], excluded_ids: List[str]) -> int:
    return len(set(retrieved_ids).intersection(excluded_ids))


def evaluate_case(
    rag: RagService,
    results: List[Dict[str, Any]],
    expected_ids: List[str],
    excluded_ids: List[str],
    filters: Optional[RecipeFilters],
) -> Dict[str, Any]:
    retrieved_ids = [str(r.get("id", "")) for r in results]
    return {
        "hit_at_k": hit_at_k(retrieved_ids, expected_ids),
        "recall_at_k": recall_at_k(retrieved_ids, expected_ids),
        "filter_violations": filter_violations(results, filters, rag),
        "excluded_violations": excluded_violations(retrieved_ids, excluded_ids),
    }
