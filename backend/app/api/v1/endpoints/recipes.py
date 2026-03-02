from fastapi import APIRouter, Depends
from ...deps import get_recipe_service
from ....services.recipe_service import RecipeService
from ....schemas.recipe import RecipeSearchRequest, RecipeSearchResponse

router = APIRouter()


@router.post("/recipes/search", response_model=RecipeSearchResponse)
def search_recipes(
    payload: RecipeSearchRequest,
    service: RecipeService = Depends(get_recipe_service),
):
    results = service.search_recipes(query=payload.query, top_k=payload.top_k)
    return RecipeSearchResponse(results=results)