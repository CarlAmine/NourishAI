from __future__ import annotations

import logging
import os
import pickle
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from rank_bm25 import BM25Okapi

from ..ingestion.models import DocumentChunk
from ..services.filters import payload_matches

logger = logging.getLogger("nourishai.lexical")


@dataclass(frozen=True)
class LexicalSearchResult:
    chunk_id: str
    score: float
    payload: Dict[str, Any]
    text: str


class LexicalIndex:
    def __init__(self, index_path: str):
        self.index_path = index_path
        self._bm25: Optional[BM25Okapi] = None
        self._chunk_ids: List[str] = []
        self._payloads: List[Dict[str, Any]] = []
        self._texts: List[str] = []
        self._tokenized: List[List[str]] = []

    @property
    def available(self) -> bool:
        return self._bm25 is not None

    def build(self, chunks: List[DocumentChunk]) -> None:
        self._chunk_ids = [chunk.chunk_id for chunk in chunks]
        self._payloads = [chunk.payload for chunk in chunks]
        self._texts = [chunk.text for chunk in chunks]
        self._tokenized = [self._tokenize(text) for text in self._texts]
        self._bm25 = BM25Okapi(self._tokenized)
        self._save()
        logger.info("Lexical index built with %d chunks", len(self._chunk_ids))

    def load(self) -> None:
        if not os.path.exists(self.index_path):
            logger.warning("Lexical index not found: %s", self.index_path)
            return
        with open(self.index_path, "rb") as handle:
            data = pickle.load(handle)
        self._chunk_ids = data.get("chunk_ids", [])
        self._payloads = data.get("payloads", [])
        self._texts = data.get("texts", [])
        self._tokenized = data.get("tokenized", [])
        if self._tokenized:
            self._bm25 = BM25Okapi(self._tokenized)
        logger.info("Lexical index loaded (%d chunks)", len(self._chunk_ids))

    def search(
        self,
        query: str,
        top_k: int,
        filters,
        doc_types: Optional[List[str]] = None,
    ) -> List[LexicalSearchResult]:
        if self._bm25 is None:
            self.load()
        if self._bm25 is None:
            return []

        tokenized_query = self._tokenize(query)
        scores = self._bm25.get_scores(tokenized_query)

        candidates: List[LexicalSearchResult] = []
        for idx, score in enumerate(scores):
            payload = self._payloads[idx]
            if not payload_matches(payload, filters, doc_types):
                continue
            if score <= 0:
                continue
            candidates.append(
                LexicalSearchResult(
                    chunk_id=self._chunk_ids[idx],
                    score=float(score),
                    payload=payload,
                    text=self._texts[idx],
                )
            )

        candidates.sort(key=lambda item: item.score, reverse=True)
        return candidates[:top_k]

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, "wb") as handle:
            pickle.dump(
                {
                    "chunk_ids": self._chunk_ids,
                    "payloads": self._payloads,
                    "texts": self._texts,
                    "tokenized": self._tokenized,
                },
                handle,
            )

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"[a-z0-9]+", text.lower())
