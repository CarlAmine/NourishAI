from __future__ import annotations

import argparse
import json
import os
import pickle
import re
from typing import Any, Dict, List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


def load_recipes(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("Recipe JSON must be a list of objects")

    recipes: List[Dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        recipes.append(
            {
                "id": str(item.get("id", "")),
                "title": str(item.get("title", "")),
                "ingredients": _as_list(item.get("ingredients")),
                "instructions": _as_list(item.get("instructions")),
                "calories": item.get("calories"),
                "protein_g": item.get("protein_g"),
                "carbs_g": item.get("carbs_g"),
                "fat_g": item.get("fat_g"),
                "cuisine": _as_list(item.get("cuisine")),
                "meal_type": _as_list(item.get("meal_type")),
                "dietary_tags": _as_list(item.get("dietary_tags")),
                "allergens": _as_list(item.get("allergens")),
                "prep_time_minutes": item.get("prep_time_minutes"),
                "cook_time_minutes": item.get("cook_time_minutes"),
                "total_time_minutes": item.get("total_time_minutes"),
            }
        )
    return recipes


def build_corpus(recipes: List[Dict[str, Any]]) -> List[str]:
    texts: List[str] = []
    for recipe in recipes:
        title = recipe.get("title") or ""
        ingredients = recipe.get("ingredients") or []
        normalized = [normalize_ingredient(str(i)) for i in ingredients if str(i).strip()]
        ingredient_text = ", ".join(normalized) if normalized else ", ".join(str(i) for i in ingredients)
        texts.append(f"{title}. Ingredients: {ingredient_text}")
    return texts


def build_index(texts: List[str], model: SentenceTransformer) -> np.ndarray:
    embeddings = model.encode(texts, show_progress_bar=True)
    vectors = np.asarray(embeddings, dtype="float32")
    faiss.normalize_L2(vectors)
    return vectors


def normalize_ingredient(text: str) -> str:
    cleaned = text.lower().strip()
    cleaned = re.sub(r"\(.*?\)", "", cleaned)
    cleaned = re.sub(r"[^a-z0-9\s-]", "", cleaned)
    cleaned = cleaned.replace("-", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = _singularize(cleaned)
    aliases = {
        "garbanzo beans": "chickpea",
        "garbanzo bean": "chickpea",
        "scallions": "green onion",
        "spring onions": "green onion",
        "courgette": "zucchini",
    }
    return aliases.get(cleaned, cleaned)


def _singularize(text: str) -> str:
    if text.endswith("ies") and len(text) > 3:
        return text[:-3] + "y"
    if text.endswith("es") and len(text) > 3:
        return text[:-2]
    if text.endswith("s") and len(text) > 3:
        return text[:-1]
    return text


def _as_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if str(v).strip()]
    if isinstance(value, str):
        if "," in value:
            return [v.strip() for v in value.split(",") if v.strip()]
        return [value.strip()]
    return [str(value)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build FAISS index for NourishAI recipes")
    parser.add_argument("--recipes", required=True, help="Path to recipes JSON file")
    parser.add_argument("--out-dir", required=True, help="Output directory for faiss.index and recipe.pkl")
    args = parser.parse_args()

    recipes = load_recipes(args.recipes)
    if not recipes:
        raise ValueError("No recipes found in input JSON")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = build_corpus(recipes)
    vectors = build_index(texts, model)

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    os.makedirs(args.out_dir, exist_ok=True)
    index_path = os.path.join(args.out_dir, "faiss.index")
    recipes_path = os.path.join(args.out_dir, "recipe.pkl")

    faiss.write_index(index, index_path)
    with open(recipes_path, "wb") as handle:
        pickle.dump(recipes, handle)

    print(f"Indexed {len(recipes)} recipes")
    print(f"FAISS index: {index_path}")
    print(f"Recipe data: {recipes_path}")


if __name__ == "__main__":
    main()
