from __future__ import annotations

import logging
import os
import pickle
import time
from typing import Any, Dict, List, Optional, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from starlette.exceptions import HTTPException

from .ingredient_normalizer import extract_ingredients_from_query, normalize_ingredient_list
from ..core.observability import log_event
from ..schemas.recipe import RecipeFilters, RetrievalDiagnostics


class RagService:
    logger = logging.getLogger("nourishai.rag")

    def __init__(self, faiss_index_path: str, recipes_pkl_path: str):
        self.faiss_index_path = faiss_index_path
        self.recipes_pkl_path = recipes_pkl_path
        self.index: faiss.Index | None = None
        self.recipes: List[Dict[str, Any]] = []
        self._model: SentenceTransformer | None = None

        self._load_artifacts()

    def search(
        self,
        query: str,
        top_k: int,
        filters: Optional[RecipeFilters] = None,
        rerank: bool = True,
        candidate_k: Optional[int] = None,
        ingredients: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        results, _ = self.search_with_diagnostics(
            query=query,
            top_k=top_k,
            filters=filters,
            rerank=rerank,
            candidate_k=candidate_k,
            ingredients=ingredients,
            include_diagnostics=False,
        )
        return results

    def search_with_diagnostics(
        self,
        query: str,
        top_k: int,
        filters: Optional[RecipeFilters] = None,
        rerank: bool = True,
        candidate_k: Optional[int] = None,
        ingredients: Optional[List[str]] = None,
        include_diagnostics: bool = False,
    ) -> Tuple[List[Dict[str, Any]], Optional[RetrievalDiagnostics]]:
        if self.index is None or not self.recipes:
            log_event(
                self.logger,
                "rag_unavailable",
                index_loaded=self.index is not None,
                recipes_loaded=bool(self.recipes),
            )
            raise HTTPException(status_code=503, detail="RAG index not available. Build it with scripts/build_rag_index.py")

        if not query.strip() or top_k <= 0:
            diagnostics = self._build_diagnostics(
                query=query,
                normalized_query=query.strip(),
                candidate_k=0,
                returned_k=0,
                filters=filters,
                reranked=False,
                top_ids=[],
                top_scores=[],
            ) if include_diagnostics else None
            log_event(
                self.logger,
                "rag_empty_query",
                query=query,
                top_k=top_k,
            )
            return [], diagnostics

        start = time.perf_counter()
        normalized_ingredients = normalize_ingredient_list(ingredients or [])
        if not normalized_ingredients:
            normalized_ingredients = extract_ingredients_from_query(query)

        normalized_query = ", ".join(normalized_ingredients) if normalized_ingredients else query.strip()

        if candidate_k is None:
            if filters or normalized_ingredients or rerank:
                candidate_k = max(top_k * 5, top_k + 10)
            else:
                candidate_k = top_k
        candidate_k = max(candidate_k, top_k)

        if self._model is None:
            self._model = SentenceTransformer("all-MiniLM-L6-v2")

        embed_start = time.perf_counter()
        embedding = self._model.encode([normalized_query], show_progress_bar=False)
        query_vector = np.asarray(embedding, dtype="float32")
        faiss.normalize_L2(query_vector)
        embed_ms = (time.perf_counter() - embed_start) * 1000.0

        search_start = time.perf_counter()
        scores, indices = self.index.search(query_vector, candidate_k)
        search_ms = (time.perf_counter() - search_start) * 1000.0

        filter_start = time.perf_counter()
        candidates: List[Tuple[Dict[str, Any], float]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.recipes):
                continue
            recipe = self.recipes[idx]
            if not self._matches_filters(recipe, filters):
                continue
            candidates.append((recipe, float(score)))
        filter_ms = (time.perf_counter() - filter_start) * 1000.0

        reranked = False
        rerank_start = time.perf_counter()
        if rerank and normalized_ingredients:
            reranked = True
            candidates = self._rerank_candidates(candidates, normalized_ingredients)
        else:
            candidates.sort(key=lambda item: item[1], reverse=True)
        rerank_ms = (time.perf_counter() - rerank_start) * 1000.0

        final = candidates[:top_k]
        results = [self._recipe_to_result(recipe, score) for recipe, score in final]

        diagnostics = None
        if include_diagnostics:
            top_ids = [str(r.get("id", "")) for r, _ in final]
            top_scores = [float(score) for _, score in final]
            diagnostics = self._build_diagnostics(
                query=query,
                normalized_query=normalized_query,
                candidate_k=candidate_k,
                returned_k=len(results),
                filters=filters,
                reranked=reranked,
                top_ids=top_ids,
                top_scores=top_scores,
            )

        total_ms = (time.perf_counter() - start) * 1000.0
        strategy = "reranked" if reranked else ("filtered" if filters else "baseline")
        log_event(
            self.logger,
            "rag_search",
            query=query,
            normalized_query=normalized_query,
            top_k=top_k,
            candidate_k=candidate_k,
            strategy=strategy,
            reranked=reranked,
            filters=filters.model_dump() if filters else None,
            result_ids=[r.get("id") for r in results],
            result_scores=[r.get("score") for r in results],
            timings_ms={
                "total": round(total_ms, 2),
                "embed": round(embed_ms, 2),
                "search": round(search_ms, 2),
                "filter": round(filter_ms, 2),
                "rerank": round(rerank_ms, 2),
            },
        )

        return results, diagnostics

    def _load_artifacts(self) -> None:
        if os.path.exists(self.faiss_index_path):
            try:
                self.index = faiss.read_index(self.faiss_index_path)
                self.logger.info("Loaded FAISS index from %s", self.faiss_index_path)
            except Exception as exc:
                self.logger.warning("Failed to load FAISS index: %s", exc)
                self.index = None
        else:
            self.logger.warning("FAISS index path %s does not exist", self.faiss_index_path)

        if os.path.exists(self.recipes_pkl_path):
            try:
                with open(self.recipes_pkl_path, "rb") as handle:
                    data = pickle.load(handle)
                if isinstance(data, list):
                    self.recipes = data
                else:
                    self.logger.warning("recipes.pkl did not contain a list; got %s", type(data))
                    self.recipes = []
                self.logger.info("Loaded %d recipes from %s", len(self.recipes), self.recipes_pkl_path)
            except Exception as exc:
                self.logger.warning("Failed to load recipes pickle: %s", exc)
                self.recipes = []
        else:
            self.logger.warning("recipes pickle path %s does not exist", self.recipes_pkl_path)

        if self.index is not None and self.recipes:
            index_count = int(self.index.ntotal)
            if index_count != len(self.recipes):
                self.logger.warning(
                    "FAISS index count (%s) does not match recipes count (%s)",
                    index_count,
                    len(self.recipes),
                )

    def status(self) -> Dict[str, Any]:
        index_loaded = self.index is not None
        recipes_loaded = bool(self.recipes)
        index_count = int(self.index.ntotal) if self.index is not None else 0
        recipe_count = len(self.recipes)
        artifact_mismatch = index_loaded and recipes_loaded and index_count != recipe_count
        return {
            "index_loaded": index_loaded,
            "recipes_loaded": recipes_loaded,
            "index_count": index_count,
            "recipe_count": recipe_count,
            "artifact_mismatch": artifact_mismatch,
            "available": index_loaded and recipes_loaded,
        }

    def _matches_filters(self, recipe: Dict[str, Any], filters: Optional[RecipeFilters]) -> bool:
        if not filters:
            return True

        if filters.cuisine and not _list_overlaps(recipe.get("cuisine"), filters.cuisine):
            return False
        if filters.meal_type and not _list_overlaps(recipe.get("meal_type"), filters.meal_type):
            return False
        if filters.dietary_tags and not _list_overlaps(recipe.get("dietary_tags"), filters.dietary_tags):
            return False

        if not _in_range(_get_numeric(recipe, "calories"), filters.min_calories, filters.max_calories):
            return False
        if not _in_range(_get_numeric(recipe, "protein_g"), filters.min_protein_g, filters.max_protein_g):
            return False
        if not _in_range(_get_numeric(recipe, "carbs_g"), filters.min_carbs_g, filters.max_carbs_g):
            return False
        if not _in_range(_get_numeric(recipe, "fat_g"), filters.min_fat_g, filters.max_fat_g):
            return False

        if filters.max_prep_time_minutes is not None:
            prep_time = _get_int(recipe, "prep_time_minutes")
            if prep_time is None or prep_time > filters.max_prep_time_minutes:
                return False

        if filters.max_total_time_minutes is not None:
            total_time = _get_int(recipe, "total_time_minutes")
            if total_time is None or total_time > filters.max_total_time_minutes:
                return False

        return True

    def _rerank_candidates(
        self,
        candidates: List[Tuple[Dict[str, Any], float]],
        query_ingredients: List[str],
    ) -> List[Tuple[Dict[str, Any], float]]:
        reranked: List[Tuple[Dict[str, Any], float]] = []
        query_set = set(query_ingredients)
        for recipe, score in candidates:
            recipe_ingredients = normalize_ingredient_list(recipe.get("ingredients") or [])
            overlap = _overlap_score(query_set, set(recipe_ingredients))
            combined_score = (0.85 * score) + (0.15 * overlap)
            reranked.append((recipe, combined_score))

        reranked.sort(key=lambda item: item[1], reverse=True)
        return reranked

    @staticmethod
    def _recipe_to_result(recipe: Dict[str, Any], score: float) -> Dict[str, Any]:
        return {
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
            "score": float(score),
        }

    @staticmethod
    def _build_diagnostics(
        query: str,
        normalized_query: str,
        candidate_k: int,
        returned_k: int,
        filters: Optional[RecipeFilters],
        reranked: bool,
        top_ids: List[str],
        top_scores: List[float],
    ) -> RetrievalDiagnostics:
        return RetrievalDiagnostics(
            query=query,
            normalized_query=normalized_query,
            candidate_k=candidate_k,
            returned_k=returned_k,
            reranked=reranked,
            filters=filters,
            top_ids=top_ids,
            top_scores=top_scores,
        )


def _list_overlaps(left: Any, right: Any) -> bool:
    left_list = _normalize_list(left)
    right_list = _normalize_list(right)
    return bool(set(left_list).intersection(right_list))


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


def _in_range(value: Optional[float], min_value: Optional[float], max_value: Optional[float]) -> bool:
    if value is None:
        return min_value is None and max_value is None
    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False
    return True


def _get_numeric(recipe: Dict[str, Any], key: str) -> Optional[float]:
    if key in recipe and recipe.get(key) is not None:
        try:
            return float(recipe[key])
        except (TypeError, ValueError):
            return None
    macros = recipe.get("macros") or {}
    if isinstance(macros, dict) and key in macros and macros.get(key) is not None:
        try:
            return float(macros[key])
        except (TypeError, ValueError):
            return None
    return None


def _get_int(recipe: Dict[str, Any], key: str) -> Optional[int]:
    if key in recipe and recipe.get(key) is not None:
        try:
            return int(recipe[key])
        except (TypeError, ValueError):
            return None
    times = recipe.get("times") or {}
    if isinstance(times, dict) and key in times and times.get(key) is not None:
        try:
            return int(times[key])
        except (TypeError, ValueError):
            return None
    return None


def _overlap_score(query_set: set[str], recipe_set: set[str]) -> float:
    if not query_set:
        return 0.0
    return len(query_set.intersection(recipe_set)) / float(len(query_set))
