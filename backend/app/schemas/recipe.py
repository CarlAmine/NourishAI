from pydantic import BaseModel, Field
from typing import List, Optional


class Recipe(BaseModel):
    id: str
    title: str
    ingredients: List[str]
    instructions: List[str]
    calories: Optional[float] = None
    score: Optional[float] = None


class RecipeSearchRequest(BaseModel):
    query: str = Field(..., description="Ingredients or free-text query")
    top_k: int = Field(default=5, ge=1, le=50)


class RecipeSearchResponse(BaseModel):
    results: List[Recipe]