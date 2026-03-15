from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .chunking import chunk_recipe_texts, chunk_text_by_paragraphs
from .loaders import load_ingredient_records, load_nutrition_records, load_recipe_records
from .models import DocumentChunk
from ..core.config import settings
from ..repositories.lexical_index import LexicalIndex
from ..repositories.vector_store import QdrantVectorStore
from ..services.embedding_service import EmbeddingService

logger = logging.getLogger("nourishai.ingestion")


def run_ingestion(
    data_dir: Optional[str] = None,
    recreate: bool = False,
    batch_size: int = 64,
) -> Dict[str, Any]:
    data_root = data_dir or settings.DATA_DIR
    vector_store = QdrantVectorStore(
        url=settings.QDRANT_URL,
        collection_name=settings.QDRANT_COLLECTION,
        vector_size=settings.EMBEDDING_DIM,
    )

    if recreate:
        vector_store.recreate_collection()
    else:
        vector_store.ensure_collection()

    recipes = load_recipe_records(data_root)
    nutrition_refs = load_nutrition_records(data_root)
    ingredients = load_ingredient_records(data_root)

    chunks: List[DocumentChunk] = []
    for record in recipes:
        chunks.extend(_chunks_from_recipe(record))
    for record in nutrition_refs:
        chunks.extend(_chunks_from_nutrition(record))
    for record in ingredients:
        chunks.extend(_chunks_from_ingredient(record))

    logger.info("Prepared %d chunks for ingestion", len(chunks))

    if not chunks:
        return {
            "status": "no_data",
            "chunks": 0,
            "recipes": len(recipes),
            "nutrition": len(nutrition_refs),
            "ingredients": len(ingredients),
        }

    embedder = EmbeddingService(settings.EMBEDDING_MODEL_NAME)

    for batch in _batch_iter(chunks, batch_size):
        texts = [chunk.text for chunk in batch]
        vectors = embedder.embed(texts)
        vector_store.upsert(batch, vectors)

    _write_chunks_store(chunks, settings.CHUNK_STORE_PATH)

    lexical_index = LexicalIndex(settings.LEXICAL_INDEX_PATH)
    lexical_index.build(chunks)

    manifest = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "collection": settings.QDRANT_COLLECTION,
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "counts": {
            "recipes": len(recipes),
            "nutrition": len(nutrition_refs),
            "ingredients": len(ingredients),
            "chunks": len(chunks),
        },
    }
    _write_manifest(manifest, settings.INGESTION_MANIFEST_PATH)
    return {"status": "ok", **manifest}


def _chunks_from_recipe(record: Dict[str, Any]) -> List[DocumentChunk]:
    title = str(record.get("title") or record.get("name") or "").strip()
    doc_id = str(record.get("id") or record.get("recipe_id") or _slugify(title) or uuid.uuid4().hex)
    meal_type = _normalize_tags(record.get("meal_type") or record.get("course"))
    dietary_tags = _normalize_tags(record.get("dietary_tags") or record.get("diet") or record.get("tags"))
    cuisine = _normalize_tags(record.get("cuisine") or record.get("cuisine_type"))
    ingredients = _as_list(record.get("ingredients") or record.get("ingredient_lines"))
    instructions = _as_list(record.get("instructions") or record.get("steps") or record.get("directions"))

    nutrition = record.get("nutrition") or {}
    calories = _coerce_float(record.get("calories") or nutrition.get("calories"))
    protein_g = _coerce_float(nutrition.get("protein_g") or nutrition.get("protein"))
    carbs_g = _coerce_float(nutrition.get("carbs_g") or nutrition.get("carbohydrates"))
    fat_g = _coerce_float(nutrition.get("fat_g") or nutrition.get("fat"))

    base_payload = {
        "doc_id": doc_id,
        "doc_type": "recipe",
        "title": title,
        "meal_type": meal_type,
        "dietary_tags": dietary_tags,
        "cuisine": cuisine,
        "ingredients": ingredients,
        "instructions": instructions,
        "calories": calories,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "source": record.get("source"),
    }

    chunks: List[DocumentChunk] = []
    for chunk in chunk_recipe_texts(record):
        chunk_id = uuid.uuid4().hex
        payload = dict(base_payload)
        payload["chunk_section"] = chunk["section"]
        chunks.append(
            DocumentChunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                doc_type="recipe",
                text=chunk["text"],
                payload=payload,
            )
        )

    return chunks


def _chunks_from_nutrition(record: Dict[str, Any]) -> List[DocumentChunk]:
    title = str(record.get("title") or record.get("name") or "").strip()
    doc_id = str(record.get("id") or record.get("ref_id") or _slugify(title) or uuid.uuid4().hex)
    text = str(record.get("text") or record.get("description") or "").strip()
    nutrients = _normalize_tags(record.get("nutrients") or record.get("nutrient"))
    source = record.get("source")

    chunks: List[DocumentChunk] = []
    for idx, chunk_text in enumerate(chunk_text_by_paragraphs(text)):
        chunk_id = uuid.uuid4().hex
        payload = {
            "doc_id": doc_id,
            "doc_type": "nutrition",
            "title": title,
            "nutrients": nutrients,
            "source": source,
            "chunk_section": f"paragraph_{idx+1}",
        }
        chunks.append(
            DocumentChunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                doc_type="nutrition",
                text=_prefix_title(title, chunk_text),
                payload=payload,
            )
        )

    return chunks


def _chunks_from_ingredient(record: Dict[str, Any]) -> List[DocumentChunk]:
    name = str(record.get("name") or record.get("ingredient") or "").strip()
    doc_id = str(record.get("id") or record.get("ingredient_id") or _slugify(name) or uuid.uuid4().hex)
    aliases = _normalize_tags(record.get("aliases") or record.get("aka"))
    notes = str(record.get("notes") or record.get("description") or "").strip()
    substitutions = _as_list(record.get("substitutions") or record.get("substitute"))
    allergens = _normalize_tags(record.get("allergens"))
    nutrition = record.get("nutrition") or {}

    calories = _coerce_float(nutrition.get("calories"))
    protein_g = _coerce_float(nutrition.get("protein_g") or nutrition.get("protein"))
    carbs_g = _coerce_float(nutrition.get("carbs_g") or nutrition.get("carbohydrates"))
    fat_g = _coerce_float(nutrition.get("fat_g") or nutrition.get("fat"))

    text = _build_ingredient_text(name, aliases, notes, substitutions, nutrition)
    chunks: List[DocumentChunk] = []
    for idx, chunk_text in enumerate(chunk_text_by_paragraphs(text)):
        chunk_id = uuid.uuid4().hex
        payload = {
            "doc_id": doc_id,
            "doc_type": "ingredient",
            "title": name,
            "aliases": aliases,
            "allergens": allergens,
            "calories": calories,
            "protein_g": protein_g,
            "carbs_g": carbs_g,
            "fat_g": fat_g,
            "source": record.get("source"),
            "chunk_section": f"paragraph_{idx+1}",
        }
        chunks.append(
            DocumentChunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                doc_type="ingredient",
                text=chunk_text,
                payload=payload,
            )
        )

    return chunks


def _write_chunks_store(chunks: Iterable[DocumentChunk], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(
                json.dumps(
                    {
                        "chunk_id": chunk.chunk_id,
                        "doc_id": chunk.doc_id,
                        "doc_type": chunk.doc_type,
                        "text": chunk.text,
                        "payload": chunk.payload,
                    }
                )
                + "\n"
            )


def _write_manifest(manifest: Dict[str, Any], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)


def _batch_iter(items: List[DocumentChunk], batch_size: int) -> Iterable[List[DocumentChunk]]:
    for idx in range(0, len(items), batch_size):
        yield items[idx : idx + batch_size]


def _normalize_tags(value: Any) -> List[str]:
    values = _as_list(value)
    return [v.lower() for v in values]


def _as_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        if "," in value:
            return [v.strip() for v in value.split(",") if v.strip()]
        return [value.strip()]
    return [str(value).strip()]


def _coerce_float(value: Any) -> Optional[float]:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _slugify(text: str) -> str:
    return "-".join(part for part in (text or "").lower().split() if part)


def _prefix_title(title: str, text: str) -> str:
    if not title:
        return text
    return f"{title}\n{text}"


def _build_ingredient_text(
    name: str,
    aliases: List[str],
    notes: str,
    substitutions: List[str],
    nutrition: Dict[str, Any],
) -> str:
    lines = [f"Ingredient: {name}"] if name else []
    if aliases:
        lines.append("Aliases: " + ", ".join(aliases))
    if notes:
        lines.append("Notes: " + notes)
    if substitutions:
        lines.append("Substitutions: " + ", ".join(substitutions))
    if nutrition:
        nutrition_bits = []
        for key in ("calories", "protein_g", "carbs_g", "fat_g"):
            if key in nutrition:
                nutrition_bits.append(f"{key}={nutrition[key]}")
        if nutrition_bits:
            lines.append("Nutrition: " + "; ".join(nutrition_bits))
    return "\n".join(lines)
