from pydantic import BaseModel, Field
from typing import List, Optional


class Recipe(BaseModel):
    id: str
    title: str
    ingredients: List[str]
    instructions: List[str]
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    cuisine: Optional[List[str]] = None
    meal_type: Optional[List[str]] = None
    dietary_tags: Optional[List[str]] = None
    allergens: Optional[List[str]] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    total_time_minutes: Optional[int] = None
    score: Optional[float] = None


class RecipeFilters(BaseModel):
    cuisine: Optional[List[str]] = None
    meal_type: Optional[List[str]] = None
    dietary_tags: Optional[List[str]] = None

    min_calories: Optional[float] = None
    max_calories: Optional[float] = None
    min_protein_g: Optional[float] = None
    max_protein_g: Optional[float] = None
    min_carbs_g: Optional[float] = None
    max_carbs_g: Optional[float] = None
    min_fat_g: Optional[float] = None
    max_fat_g: Optional[float] = None

    max_prep_time_minutes: Optional[int] = None
    max_total_time_minutes: Optional[int] = None


class RetrievalDiagnostics(BaseModel):
    query: str
    normalized_query: Optional[str] = None
    candidate_k: int
    returned_k: int
    reranked: bool
    filters: Optional[RecipeFilters] = None
    top_ids: List[str] = Field(default_factory=list)
    top_scores: List[float] = Field(default_factory=list)


class RecipeSearchRequest(BaseModel):
    query: str = Field(..., description="Ingredients or free-text query")
    top_k: int = Field(default=5, ge=1, le=50)
    filters: Optional[RecipeFilters] = None
    rerank: bool = Field(default=True)
    include_diagnostics: bool = Field(default=False)
    candidate_k: Optional[int] = Field(default=None, ge=1, le=200)


class RecommendRequest(BaseModel):
    ingredients: List[str] = Field(..., description="Ingredients available")
    dietary_notes: Optional[str] = Field(default=None, description="Optional dietary notes")
    top_k: int = Field(default=5, ge=1, le=50)
    filters: Optional[RecipeFilters] = None
    rerank: bool = Field(default=True)
    include_diagnostics: bool = Field(default=False)
    candidate_k: Optional[int] = Field(default=None, ge=1, le=200)


class RecipeSearchResponse(BaseModel):
    results: List[Recipe]
    diagnostics: Optional[RetrievalDiagnostics] = None
