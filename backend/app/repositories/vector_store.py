from __future__ import annotations

import logging
from typing import Iterable, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    PayloadSchemaType,
    PointStruct,
    Range,
    VectorParams,
)

from ..ingestion.models import DocumentChunk

logger = logging.getLogger("nourishai.vector_store")


FILTERABLE_FIELDS = {
    "doc_type": PayloadSchemaType.KEYWORD,
    "meal_type": PayloadSchemaType.KEYWORD,
    "dietary_tags": PayloadSchemaType.KEYWORD,
    "cuisine": PayloadSchemaType.KEYWORD,
    "calories": PayloadSchemaType.FLOAT,
    "protein_g": PayloadSchemaType.FLOAT,
    "carbs_g": PayloadSchemaType.FLOAT,
    "fat_g": PayloadSchemaType.FLOAT,
    "allergens": PayloadSchemaType.KEYWORD,
    "aliases": PayloadSchemaType.KEYWORD,
    "nutrients": PayloadSchemaType.KEYWORD,
}


class QdrantVectorStore:
    def __init__(self, url: str, collection_name: str, vector_size: int):
        self.client = QdrantClient(url=url)
        self.collection_name = collection_name
        self.vector_size = vector_size

    def ensure_collection(self) -> None:
        if not self.client.collection_exists(self.collection_name):
            logger.info("Creating Qdrant collection %s", self.collection_name)
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )
        self._ensure_payload_indexes()

    def recreate_collection(self) -> None:
        logger.info("Recreating Qdrant collection %s", self.collection_name)
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
        )
        self._ensure_payload_indexes()

    def upsert(self, chunks: Iterable[DocumentChunk], vectors: List[List[float]]) -> None:
        points: List[PointStruct] = []
        for chunk, vector in zip(chunks, vectors):
            payload = dict(chunk.payload)
            payload["text"] = chunk.text
            payload["chunk_id"] = chunk.chunk_id
            points.append(PointStruct(id=chunk.chunk_id, vector=vector, payload=payload))

        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(
        self,
        vector: List[float],
        limit: int,
        qdrant_filter: Optional[Filter],
    ):
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit,
            query_filter=qdrant_filter,
            with_payload=True,
        )

    def _ensure_payload_indexes(self) -> None:
        for field_name, schema in FILTERABLE_FIELDS.items():
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field_name,
                    field_schema=schema,
                )
            except Exception:
                pass


def build_range_condition(key: str, min_value: Optional[float], max_value: Optional[float]) -> Optional[FieldCondition]:
    if min_value is None and max_value is None:
        return None
    return FieldCondition(key=key, range=Range(gte=min_value, lte=max_value))


def build_match_any_condition(key: str, values: Optional[List[str]]) -> Optional[FieldCondition]:
    if not values:
        return None
    return FieldCondition(key=key, match=MatchAny(any=values))
