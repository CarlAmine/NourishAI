from __future__ import annotations

import re
from typing import Dict, List


def _as_list(value) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        if "," in value:
            return [v.strip() for v in value.split(",") if v.strip()]
        return [value.strip()]
    return [str(value).strip()]


def chunk_recipe_texts(recipe: Dict[str, object]) -> List[Dict[str, str]]:
    title = str(recipe.get("title") or recipe.get("name") or "").strip()
    ingredients = _as_list(recipe.get("ingredients") or recipe.get("ingredient_lines"))
    steps = _as_list(recipe.get("instructions") or recipe.get("steps") or recipe.get("directions"))

    chunks: List[Dict[str, str]] = []
    if ingredients:
        ing_text = "Ingredients:\n" + "\n".join(f"- {item}" for item in ingredients)
        chunks.append({"section": "ingredients", "text": _prefix_title(title, ing_text)})

    if steps:
        step_groups = _group_steps(steps)
        for idx, group in enumerate(step_groups, start=1):
            step_text = "Instructions (part {idx}):\n".format(idx=idx) + "\n".join(
                f"{i+1}. {step}" for i, step in enumerate(group)
            )
            chunks.append({"section": f"instructions_{idx}", "text": _prefix_title(title, step_text)})

    if not chunks and title:
        chunks.append({"section": "summary", "text": f"Recipe: {title}."})

    return chunks


def chunk_text_by_paragraphs(text: str, max_words: int = 220, min_words: int = 80) -> List[str]:
    cleaned = (text or "").strip()
    if not cleaned:
        return []

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", cleaned) if p.strip()]
    if not paragraphs:
        return []

    chunks: List[str] = []
    current: List[str] = []
    current_words = 0

    for paragraph in paragraphs:
        word_count = _word_count(paragraph)
        if current_words + word_count > max_words and current_words >= min_words:
            chunks.append("\n\n".join(current))
            current = [paragraph]
            current_words = word_count
        else:
            current.append(paragraph)
            current_words += word_count

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def _group_steps(steps: List[str], max_steps: int = 4, max_words: int = 180) -> List[List[str]]:
    groups: List[List[str]] = []
    current: List[str] = []
    current_words = 0

    for step in steps:
        step_words = _word_count(step)
        if current and (len(current) >= max_steps or current_words + step_words > max_words):
            groups.append(current)
            current = [step]
            current_words = step_words
        else:
            current.append(step)
            current_words += step_words

    if current:
        groups.append(current)

    return groups


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _prefix_title(title: str, text: str) -> str:
    if not title:
        return text
    return f"Recipe: {title}\n{text}"
