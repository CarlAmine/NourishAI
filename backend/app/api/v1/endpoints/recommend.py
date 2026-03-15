from fastapi import APIRouter, Depends

from ...deps import get_recipe_service
from ....schemas.recipe import RecommendRequest, RecipeSearchResponse
from ....services.recipe_service import RecipeService

router = APIRouter()


@router.post("/recipes/recommend", response_model=RecipeSearchResponse)
def recommend_recipes(
    payload: RecommendRequest,
    service: RecipeService = Depends(get_recipe_service),
) -> RecipeSearchResponse:
    results, diagnostics = service.recommend_recipes(
        ingredients=payload.ingredients,
        dietary_notes=payload.dietary_notes,
        top_k=payload.top_k,
        filters=payload.filters,
        rerank=payload.rerank,
        include_diagnostics=payload.include_diagnostics,
        candidate_k=payload.candidate_k,
    )
    return RecipeSearchResponse(results=results, diagnostics=diagnostics)
