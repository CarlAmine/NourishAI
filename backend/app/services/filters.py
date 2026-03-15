from __future__ import annotations

from typing import Iterable, List, Optional

from qdrant_client.models import FieldCondition, Filter, MatchAny, Range

from ..schemas.retrieval import RetrievalFilters


def build_qdrant_filter(
    filters: Optional[RetrievalFilters],
    doc_types: Optional[List[str]] = None,
) -> Optional[Filter]:
    if not filters and not doc_types:
        return None

    must: List[FieldCondition] = []
    must_not: List[FieldCondition] = []

    doc_types_norm = _normalize_list(doc_types)
    if doc_types_norm:
        must.append(FieldCondition(key="doc_type", match=MatchAny(any=doc_types_norm)))

    if filters:
        meal_type = _normalize_list(filters.meal_type)
        if meal_type:
            must.append(FieldCondition(key="meal_type", match=MatchAny(any=meal_type)))

        cuisine = _normalize_list(filters.cuisine)
        if cuisine:
            must.append(FieldCondition(key="cuisine", match=MatchAny(any=cuisine)))

        dietary_tags = _normalize_list(filters.dietary_tags)
        if dietary_tags:
            must.append(FieldCondition(key="dietary_tags", match=MatchAny(any=dietary_tags)))

        allergens_exclude = _normalize_list(filters.allergens_exclude)
        if allergens_exclude:
            must_not.append(FieldCondition(key="allergens", match=MatchAny(any=allergens_exclude)))

        _add_range(must, "calories", filters.min_calories, filters.max_calories)
        _add_range(must, "protein_g", filters.min_protein_g, filters.max_protein_g)
        _add_range(must, "carbs_g", filters.min_carbs_g, filters.max_carbs_g)
        _add_range(must, "fat_g", filters.min_fat_g, filters.max_fat_g)

    if not must and not must_not:
        return None

    return Filter(must=must or None, must_not=must_not or None)


def payload_matches(payload: dict, filters: Optional[RetrievalFilters], doc_types: Optional[List[str]] = None) -> bool:
    if doc_types:
        if str(payload.get("doc_type") or "").lower() not in set(_normalize_list(doc_types)):
            return False

    if not filters:
        return True

    if filters.meal_type and not _list_matches(payload.get("meal_type"), filters.meal_type):
        return False
    if filters.cuisine and not _list_matches(payload.get("cuisine"), filters.cuisine):
        return False
    if filters.dietary_tags and not _list_matches(payload.get("dietary_tags"), filters.dietary_tags):
        return False
    if filters.allergens_exclude and _list_matches(payload.get("allergens"), filters.allergens_exclude):
        return False

    if not _range_matches(payload.get("calories"), filters.min_calories, filters.max_calories):
        return False
    if not _range_matches(payload.get("protein_g"), filters.min_protein_g, filters.max_protein_g):
        return False
    if not _range_matches(payload.get("carbs_g"), filters.min_carbs_g, filters.max_carbs_g):
        return False
    if not _range_matches(payload.get("fat_g"), filters.min_fat_g, filters.max_fat_g):
        return False

    return True


def _add_range(conditions: List[FieldCondition], key: str, min_value, max_value) -> None:
    if min_value is None and max_value is None:
        return
    conditions.append(FieldCondition(key=key, range=Range(gte=min_value, lte=max_value)))


def _list_matches(payload_value, filter_values: Iterable[str]) -> bool:
    payload_list = _normalize_list(payload_value)
    if not payload_list:
        return False
    filter_list = set(_normalize_list(filter_values))
    return bool(filter_list.intersection(payload_list))


def _range_matches(payload_value, min_value, max_value) -> bool:
    if payload_value is None:
        return min_value is None and max_value is None
    try:
        value = float(payload_value)
    except (TypeError, ValueError):
        return False
    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False
    return True


def _normalize_list(value) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).lower() for v in value if str(v).strip()]
    if isinstance(value, str):
        if "," in value:
            return [v.strip().lower() for v in value.split(",") if v.strip()]
        return [value.strip().lower()]
    return [str(value).lower()]
