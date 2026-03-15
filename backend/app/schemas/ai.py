from pydantic import BaseModel, Field
from typing import List, Optional

from .recipe import RecipeFilters, RetrievalDiagnostics


class MacroSummary(BaseModel):
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None


class SourceRecipeRef(BaseModel):
    id: str
    title: str


class GroundedRecommendationRequest(BaseModel):
    ingredients: List[str] = Field(..., description="Ingredients available")
    dietary_notes: Optional[str] = Field(default=None)
    top_k: int = Field(default=5, ge=1, le=50)
    filters: Optional[RecipeFilters] = None
    rerank: bool = Field(default=True)
    include_diagnostics: bool = Field(default=False)
    candidate_k: Optional[int] = Field(default=None, ge=1, le=200)


class RecommendedRecipe(BaseModel):
    recipe_id: str
    title: str
    why_selected: str
    substitutions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    nutrition_summary: Optional[MacroSummary] = None


class LLMRecommendationPayload(BaseModel):
    recommended_recipes: List[RecommendedRecipe]
    warnings: List[str] = Field(default_factory=list)


class GroundedRecommendationResponse(BaseModel):
    recommended_recipes: List[RecommendedRecipe]
    warnings: List[str] = Field(default_factory=list)
    source_recipes: List[SourceRecipeRef] = Field(default_factory=list)
    retrieval_diagnostics: Optional[RetrievalDiagnostics] = None


class MealPlanRequest(BaseModel):
    dietary_profile: Optional[str] = None
    calorie_target: Optional[int] = Field(default=None, ge=0)
    days: int = Field(default=3, ge=1, le=14)
    meals_per_day: int = Field(default=3, ge=1, le=5)
    meal_preferences: Optional[List[str]] = None
    filters: Optional[RecipeFilters] = None
    rerank: bool = Field(default=True)
    include_diagnostics: bool = Field(default=False)
    candidate_k: Optional[int] = Field(default=None, ge=1, le=200)


class MealPlanMeal(BaseModel):
    recipe_id: str
    title: str
    meal_type: Optional[str] = None
    why_selected: str
    estimated_calories: Optional[float] = None
    macros: Optional[MacroSummary] = None
    warnings: List[str] = Field(default_factory=list)


class MealPlanDay(BaseModel):
    day: int
    meals: List[MealPlanMeal]
    estimated_totals: Optional[MacroSummary] = None
    notes: Optional[str] = None


class LLMMealPlanPayload(BaseModel):
    days: List[MealPlanDay]
    dietary_notes: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)


class MealPlanResponse(BaseModel):
    days: List[MealPlanDay]
    dietary_notes: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    source_recipes: List[SourceRecipeRef] = Field(default_factory=list)
    retrieval_diagnostics: Optional[RetrievalDiagnostics] = None


class NutritionQARequest(BaseModel):
    question: str = Field(..., description="Nutrition question grounded in recipes")
    top_k: int = Field(default=5, ge=1, le=50)
    filters: Optional[RecipeFilters] = None
    rerank: bool = Field(default=True)
    include_diagnostics: bool = Field(default=False)
    candidate_k: Optional[int] = Field(default=None, ge=1, le=200)


class LLMNutritionQAPayload(BaseModel):
    answer: str
    supporting_recipe_ids: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class NutritionQAResponse(BaseModel):
    answer: str
    supporting_sources: List[SourceRecipeRef] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    retrieval_diagnostics: Optional[RetrievalDiagnostics] = None
