from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class IngredientQuery(BaseModel):
    ingredients: str = Field(
        ...,
        min_length=3,
        example="chicken, garlic, olive oil, fresh basil",
        description="Comma-separated list of ingredients.",
    )
    top_k: int = Field(default=3, ge=1, le=10, description="Number of recipe suggestions to return.")


class NutritionInfo(BaseModel):
    calories: Optional[float] = None
    total_fat: Optional[float] = None
    total_sugar: Optional[float] = None
    sodium: Optional[float] = None
    protein: Optional[float] = None
    saturated_fat: Optional[float] = None


class RecipeDetail(BaseModel):
    name: str
    minutes: Optional[int] = None
    ingredients: List[str] = []
    steps: List[str] = []
    nutrition: NutritionInfo = NutritionInfo()


class RecipeSuggestion(BaseModel):
    match_score: float = Field(..., description="Similarity score as percentage (0-100).")
    recipe_text: str


class SuggestResponse(BaseModel):
    results: List[RecipeSuggestion]


class ImagePredictResponse(BaseModel):
    predicted_class: str
    recipe: Optional[RecipeDetail] = None
    error: Optional[str] = None
