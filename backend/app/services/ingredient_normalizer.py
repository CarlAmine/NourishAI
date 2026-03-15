from __future__ import annotations

import re
from functools import lru_cache
from typing import Iterable, List

ALIAS_MAP = {
    "garbanzo bean": "chickpea",
    "garbanzo beans": "chickpea",
    "chick peas": "chickpea",
    "scallion": "green onion",
    "scallions": "green onion",
    "spring onion": "green onion",
    "spring onions": "green onion",
    "bell peppers": "bell pepper",
    "courgette": "zucchini",
    "capsicum": "bell pepper",
    "cilantro": "coriander",
    "ground beef": "beef",
}


@lru_cache(maxsize=2048)
def normalize_ingredient(text: str) -> str:
    if not text:
        return ""
    cleaned = text.lower().strip()
    cleaned = re.sub(r"\(.*?\)", "", cleaned)
    cleaned = re.sub(r"[^a-z0-9\s-]", "", cleaned)
    cleaned = cleaned.replace("-", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    cleaned = _singularize(cleaned)
    cleaned = ALIAS_MAP.get(cleaned, cleaned)
    return cleaned


def normalize_ingredient_list(items: Iterable[str]) -> List[str]:
    normalized: List[str] = []
    for item in items:
        value = normalize_ingredient(str(item))
        if value:
            normalized.append(value)
    return normalized


def extract_ingredients_from_query(query: str) -> List[str]:
    if not query:
        return []
    if "," in query:
        parts = [p.strip() for p in query.split(",") if p.strip()]
        if len(parts) >= 2:
            return normalize_ingredient_list(parts)
    tokens = [t.strip() for t in re.split(r"\band\b", query, flags=re.IGNORECASE) if t.strip()]
    if len(tokens) >= 2:
        return normalize_ingredient_list(tokens)
    return []


def _singularize(text: str) -> str:
    if text.endswith("ies") and len(text) > 3:
        return text[:-3] + "y"
    if text.endswith("es") and len(text) > 3:
        return text[:-2]
    if text.endswith("s") and len(text) > 3:
        return text[:-1]
    return text
