from __future__ import annotations

import logging
from typing import Dict, Iterable, List, Optional, Tuple

from ..core.config import settings
from ..repositories.lexical_index import LexicalIndex, LexicalSearchResult
from ..repositories.vector_store import QdrantVectorStore
from ..schemas.retrieval import (
    RetrievalDiagnostics,
    RetrievalMode,
    RetrievalRequest,
    RetrievalResponse,
    RetrievedChunk,
)
from .embedding_service import EmbeddingService
from .filters import build_qdrant_filter

logger = logging.getLogger("nourishai.retrieval")


class RetrievalService:
    def __init__(
        self,
        vector_store: QdrantVectorStore,
        lexical_index: LexicalIndex,
        embedder: EmbeddingService,
        hybrid_alpha: float,
    ):
        self.vector_store = vector_store
        self.lexical_index = lexical_index
        self.embedder = embedder
        self.hybrid_alpha = hybrid_alpha

    def search(self, request: RetrievalRequest) -> RetrievalResponse:
        query = request.query.strip()
        if not query:
            return RetrievalResponse(query=request.query, mode=request.mode, results=[])

        doc_types = [dt.value if hasattr(dt, "value") else str(dt) for dt in (request.doc_types or [])]
        candidate_k = request.candidate_k or max(request.top_k, settings.RETRIEVAL_CANDIDATES)

        dense_results = []
        keyword_results: List[LexicalSearchResult] = []

        qdrant_filter = build_qdrant_filter(request.filters, doc_types or None)

        if request.mode in (RetrievalMode.dense, RetrievalMode.hybrid):
            vector = self.embedder.embed([query])[0]
            dense_results = self.vector_store.search(vector, limit=candidate_k, qdrant_filter=qdrant_filter)

        if request.mode in (RetrievalMode.keyword, RetrievalMode.hybrid):
            keyword_results = self.lexical_index.search(
                query=query,
                top_k=candidate_k,
                filters=request.filters,
                doc_types=doc_types or None,
            )

        results = self._merge_results(
            request=request,
            dense_results=dense_results,
            keyword_results=keyword_results,
        )

        diagnostics = None
        if request.include_diagnostics:
            diagnostics = RetrievalDiagnostics(
                mode=request.mode,
                dense_candidates=len(dense_results) if dense_results else 0,
                keyword_candidates=len(keyword_results) if keyword_results else 0,
                candidate_k=candidate_k,
                collection=settings.QDRANT_COLLECTION,
                lexical_index_loaded=self.lexical_index.available,
                hybrid_alpha=self.hybrid_alpha,
                filters=request.filters.model_dump() if request.filters else None,
            )

        return RetrievalResponse(
            query=request.query,
            mode=request.mode,
            results=results[: request.top_k],
            diagnostics=diagnostics,
        )

    def _merge_results(
        self,
        request: RetrievalRequest,
        dense_results: Iterable,
        keyword_results: List[LexicalSearchResult],
    ) -> List[RetrievedChunk]:
        dense_map: Dict[str, Tuple[float, dict]] = {}
        for point in dense_results:
            payload = point.payload or {}
            dense_map[str(point.id)] = (float(point.score), payload)

        keyword_map: Dict[str, Tuple[float, dict, str]] = {}
        for match in keyword_results:
            keyword_map[match.chunk_id] = (match.score, match.payload, match.text)

        if request.mode == RetrievalMode.dense:
            return [
                self._payload_to_chunk(
                    str(point.id),
                    float(point.score),
                    point.payload or {},
                    dense_score=float(point.score),
                )
                for point in dense_results
            ]

        if request.mode == RetrievalMode.keyword:
            return [
                self._payload_to_chunk(
                    match.chunk_id,
                    match.score,
                    match.payload,
                    dense_score=None,
                    keyword_score=match.score,
                    text_override=match.text,
                )
                for match in keyword_results
            ]

        dense_rank = _rank_scores(dense_map)
        keyword_rank = _rank_scores({cid: (score, payload) for cid, (score, payload, _) in keyword_map.items()})

        combined: List[RetrievedChunk] = []
        for chunk_id in set(dense_rank.keys()).union(keyword_rank.keys()):
            dense_score, dense_payload = dense_map.get(chunk_id, (None, {}))
            keyword_entry = keyword_map.get(chunk_id)
            keyword_score = keyword_entry[0] if keyword_entry else None
            keyword_payload = keyword_entry[1] if keyword_entry else {}
            text_override = keyword_entry[2] if keyword_entry else None

            payload = dense_payload or keyword_payload

            if request.rerank:
                combined_score = self.hybrid_alpha * dense_rank.get(chunk_id, 0.0) + (1 - self.hybrid_alpha) * keyword_rank.get(chunk_id, 0.0)
            else:
                combined_score = dense_score if dense_score is not None else (keyword_score or 0.0)

            combined.append(
                self._payload_to_chunk(
                    chunk_id,
                    combined_score,
                    payload,
                    dense_score=dense_score,
                    keyword_score=keyword_score,
                    text_override=text_override,
                )
            )

        combined.sort(key=lambda item: item.score, reverse=True)
        return combined

    @staticmethod
    def _payload_to_chunk(
        chunk_id: str,
        score: float,
        payload: dict,
        dense_score: Optional[float] = None,
        keyword_score: Optional[float] = None,
        text_override: Optional[str] = None,
    ) -> RetrievedChunk:
        text = text_override or payload.get("text") or ""
        metadata = dict(payload)
        metadata.pop("text", None)
        return RetrievedChunk(
            chunk_id=chunk_id,
            doc_id=str(payload.get("doc_id") or ""),
            doc_type=str(payload.get("doc_type") or ""),
            title=payload.get("title"),
            text=text,
            source=payload.get("source"),
            score=float(score),
            dense_score=float(dense_score) if dense_score is not None else None,
            keyword_score=float(keyword_score) if keyword_score is not None else None,
            metadata=metadata,
        )


def _rank_scores(items: Dict[str, Tuple[float, dict]]) -> Dict[str, float]:
    sorted_items = sorted(items.items(), key=lambda item: item[1][0], reverse=True)
    ranks: Dict[str, float] = {}
    for idx, (chunk_id, _) in enumerate(sorted_items):
        ranks[chunk_id] = 1.0 / (idx + 1)
    return ranks
