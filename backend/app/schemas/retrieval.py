from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RetrievalMode(str, Enum):
    dense = "dense"
    keyword = "keyword"
    hybrid = "hybrid"


class DocumentType(str, Enum):
    recipe = "recipe"
    nutrition = "nutrition"
    ingredient = "ingredient"


class RetrievalFilters(BaseModel):
    meal_type: Optional[List[str]] = None
    dietary_tags: Optional[List[str]] = None
    cuisine: Optional[List[str]] = None
    allergens_exclude: Optional[List[str]] = None

    min_calories: Optional[float] = None
    max_calories: Optional[float] = None
    min_protein_g: Optional[float] = None
    max_protein_g: Optional[float] = None
    min_carbs_g: Optional[float] = None
    max_carbs_g: Optional[float] = None
    min_fat_g: Optional[float] = None
    max_fat_g: Optional[float] = None


class RetrievalRequest(BaseModel):
    query: str = Field(..., description="Ingredient list or free-text query")
    top_k: int = Field(default=5, ge=1, le=50)
    mode: RetrievalMode = Field(default=RetrievalMode.hybrid)
    rerank: bool = Field(default=True, description="Apply hybrid reranking when enabled")
    doc_types: Optional[List[DocumentType]] = Field(default=None)
    filters: Optional[RetrievalFilters] = None
    candidate_k: Optional[int] = Field(default=None, ge=1, le=200)
    include_diagnostics: bool = Field(default=False)


class RetrievedChunk(BaseModel):
    chunk_id: str
    doc_id: str
    doc_type: str
    title: Optional[str] = None
    text: str
    source: Optional[str] = None
    score: float
    dense_score: Optional[float] = None
    keyword_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RetrievalDiagnostics(BaseModel):
    mode: RetrievalMode
    dense_candidates: Optional[int] = None
    keyword_candidates: Optional[int] = None
    candidate_k: Optional[int] = None
    collection: Optional[str] = None
    lexical_index_loaded: Optional[bool] = None
    hybrid_alpha: Optional[float] = None
    filters: Optional[Dict[str, Any]] = None


class RetrievalResponse(BaseModel):
    query: str
    mode: RetrievalMode
    results: List[RetrievedChunk]
    diagnostics: Optional[RetrievalDiagnostics] = None
