"""Convert Food.com RAW_recipes.csv to NourishAI recipe JSON format.

Usage:
    python scripts/convert_foodcom.py \
        --input RAW_recipes.csv \
        --output data/recipes.json \
        --limit 50000

The Food.com dataset (Kaggle ID 311962) has 231k recipes.
We default to 50k which gives great search coverage and keeps
the FAISS index small enough to fit in Docker without issues.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from typing import Any

import pandas as pd


NUTRITION_KEYS = [
    "calories",
    "total_fat_pdv",
    "sugar_pdv",
    "sodium_pdv",
    "protein_pdv",
    "saturated_fat_pdv",
    "carbs_pdv",
]

# Tags from the Food.com dataset that map to our dietary_tags field
DIETARY_TAG_MAP = {
    "vegetarian": "vegetarian",
    "vegan": "vegan",
    "gluten-free": "gluten_free",
    "low-carb": "low_carb",
    "high-protein": "high_protein",
    "low-fat": "low_fat",
    "low-sodium": "low_sodium",
    "low-calorie": "low_calorie",
    "dairy-free": "dairy_free",
    "paleo": "paleo",
    "keto": "keto",
}

MEAL_TYPE_MAP = {
    "breakfast": "breakfast",
    "brunch": "breakfast",
    "lunch": "lunch",
    "dinner": "dinner",
    "snacks": "snack",
    "snack": "snack",
    "desserts": "dessert",
    "dessert": "dessert",
    "appetizers": "appetizer",
    "beverages": "beverage",
    "drinks": "beverage",
}

CUISINE_MAP = {
    "italian": "italian",
    "mexican": "mexican",
    "asian": "asian",
    "chinese": "chinese",
    "japanese": "japanese",
    "indian": "indian",
    "french": "french",
    "mediterranean": "mediterranean",
    "american": "american",
    "greek": "greek",
    "thai": "thai",
    "middle-eastern": "middle_eastern",
    "african": "african",
    "spanish": "spanish",
    "korean": "korean",
}


def safe_parse_list(value: Any) -> list[str]:
    """Parse a stringified Python list or return empty list."""
    if not isinstance(value, str):
        return []
    try:
        result = ast.literal_eval(value)
        if isinstance(result, list):
            return [str(v).strip() for v in result if str(v).strip()]
    except (ValueError, SyntaxError):
        pass
    return [v.strip().strip("'\"") for v in value.strip("[]").split(",") if v.strip().strip("'\"")]


def parse_nutrition(value: Any) -> dict[str, float | None]:
    """Parse nutrition list [calories, total_fat, sugar, sodium, protein, sat_fat, carbs]."""
    result: dict[str, float | None] = {k: None for k in NUTRITION_KEYS}
    try:
        nums = ast.literal_eval(value) if isinstance(value, str) else value
        if isinstance(nums, list):
            for i, key in enumerate(NUTRITION_KEYS):
                if i < len(nums):
                    try:
                        result[key] = float(nums[i])
                    except (TypeError, ValueError):
                        pass
    except (ValueError, SyntaxError):
        pass
    return result


def extract_tags(tags: list[str], mapping: dict[str, str]) -> list[str]:
    found = []
    for tag in tags:
        tag_lower = tag.lower().strip()
        if tag_lower in mapping:
            val = mapping[tag_lower]
            if val not in found:
                found.append(val)
    return found


def convert_row(row: pd.Series, idx: int) -> dict[str, Any]:
    tags = safe_parse_list(row.get("tags", ""))
    ingredients = safe_parse_list(row.get("ingredients", ""))
    steps = safe_parse_list(row.get("steps", ""))
    nutrition = parse_nutrition(row.get("nutrition", ""))

    minutes = row.get("minutes")
    try:
        minutes = int(minutes)
        if minutes <= 0 or minutes > 1440:
            minutes = None
    except (TypeError, ValueError):
        minutes = None

    # Heuristic: split total time roughly 30/70 prep/cook
    prep_time = int(minutes * 0.3) if minutes else None
    cook_time = int(minutes * 0.7) if minutes else None

    return {
        "id": str(row.get("id", idx)),
        "title": str(row.get("name", "")).strip().title(),
        "ingredients": ingredients,
        "instructions": steps,
        "calories": nutrition["calories"],
        "protein_g": nutrition["protein_pdv"],   # PDV, not grams — best we have
        "carbs_g": nutrition["carbs_pdv"],
        "fat_g": nutrition["total_fat_pdv"],
        "cuisine": extract_tags(tags, CUISINE_MAP),
        "meal_type": extract_tags(tags, MEAL_TYPE_MAP),
        "dietary_tags": extract_tags(tags, DIETARY_TAG_MAP),
        "allergens": [],
        "prep_time_minutes": prep_time,
        "cook_time_minutes": cook_time,
        "total_time_minutes": minutes,
        "description": str(row.get("description", "")).strip() or None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert Food.com RAW_recipes.csv to NourishAI JSON")
    parser.add_argument("--input", required=True, help="Path to RAW_recipes.csv")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument("--limit", type=int, default=50_000, help="Max recipes to include (default 50000)")
    parser.add_argument("--min-ingredients", type=int, default=3, help="Skip recipes with fewer ingredients")
    parser.add_argument("--min-steps", type=int, default=2, help="Skip recipes with fewer steps")
    args = parser.parse_args()

    print(f"Loading {args.input} ...")
    df = pd.read_csv(args.input)
    print(f"  Raw rows: {len(df):,}")

    # Basic quality filter
    df = df.dropna(subset=["name", "ingredients", "steps"])
    df = df[df["name"].str.strip().str.len() > 2]
    print(f"  After dropna: {len(df):,}")

    recipes = []
    skipped = 0
    for idx, (_, row) in enumerate(df.iterrows()):
        if len(recipes) >= args.limit:
            break
        ingr = safe_parse_list(row.get("ingredients", ""))
        steps = safe_parse_list(row.get("steps", ""))
        if len(ingr) < args.min_ingredients or len(steps) < args.min_steps:
            skipped += 1
            continue
        recipes.append(convert_row(row, idx))

    print(f"  Converted: {len(recipes):,} recipes (skipped {skipped:,})")

    import os
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)

    print(f"  Saved to {args.output}")


if __name__ == "__main__":
    main()
