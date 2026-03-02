import io
import logging
import re
from typing import Any, Dict, List, Optional

import numpy as np
from PIL import Image

from app.schemas.recipe import NutritionInfo, RecipeDetail
from app.services.model_store import model_store

logger = logging.getLogger(__name__)


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((15, 15))
    arr = np.array(img) / 255.0
    return arr.flatten().reshape(1, -1)


def parse_nutrition(raw: Any) -> NutritionInfo:
    cleaned = re.sub(r"[^\d.,]", "", str(raw))
    parts = [s for s in cleaned.split(",") if s]
    numbers: List[float] = []
    for p in parts:
        try:
            numbers.append(float(p))
        except ValueError:
            pass
    if len(numbers) >= 6:
        idx = [0, 1, 2, 3, 4, 6] if len(numbers) == 7 else list(range(6))
        def _get(i):
            try:
                return numbers[idx[i]]
            except IndexError:
                return None
        return NutritionInfo(
            calories=_get(0), total_fat=_get(1), total_sugar=_get(2),
            sodium=_get(3), protein=_get(4), saturated_fat=_get(5),
        )
    return NutritionInfo()


def parse_ingredients(raw: Any) -> List[str]:
    joined = "".join(raw) if isinstance(raw, (list, tuple)) else str(raw)
    return [s.strip(" '\"") for s in joined.split(",") if s.strip()]


def parse_steps(raw: Any) -> List[str]:
    if isinstance(raw, (list, tuple)):
        return [str(s).strip("'\" ") for s in raw if str(s).strip()]
    return [str(raw)]


def get_recipe_by_name(name: str) -> Optional[RecipeDetail]:
    rd = model_store.recipe_dict
    if not rd:
        return None
    target = name.lower()
    matches = [idx for idx, n in rd["name"].items() if target in n.lower()]
    if not matches:
        return None
    i = matches[0]
    return RecipeDetail(
        name=rd["name"][i],
        minutes=int(rd["minutes"][i]) if rd.get("minutes") else None,
        ingredients=parse_ingredients(rd["ingredients"][i]),
        steps=parse_steps(rd["steps"][i]),
        nutrition=parse_nutrition(rd["nutrition"][i]),
    )


def predict_from_image(image_bytes: bytes) -> Dict[str, Any]:
    if model_store.svc_model is None or not model_store.category_dict:
        return {"error": "Image model not loaded"}
    arr = preprocess_image(image_bytes)
    pred = model_store.svc_model.predict(arr)
    class_name: str = model_store.category_dict.get(pred[0], "unknown")
    readable = class_name.replace("_", " ")
    recipe = get_recipe_by_name(readable)
    return {"predicted_class": readable, "recipe": recipe}


def suggest_by_ingredients(ingredients: str, top_k: int = 3) -> List[Dict[str, Any]]:
    if model_store.faiss_index is None or model_store.sentence_model is None:
        return []
    import faiss as _faiss
    q_embed = model_store.sentence_model.encode([ingredients], convert_to_numpy=True)
    _faiss.normalize_L2(q_embed)
    scores, ids = model_store.faiss_index.search(q_embed, k=top_k)
    return [
        {"match_score": round(float(s) * 100, 2), "recipe_text": model_store.rag_texts[idx]}
        for s, idx in zip(scores[0], ids[0])
    ]
