import logging

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas.recipe import ImagePredictResponse, IngredientQuery, SuggestResponse
from app.services import recipe_service

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/predict-image", response_model=ImagePredictResponse,
             summary="Identify a dish from a photo and return its recipe")
async def predict_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            detail=f"Unsupported image type: {file.content_type}. Use JPEG or PNG.")
    image_bytes = await file.read()
    result = recipe_service.predict_from_image(image_bytes)
    if "error" in result and result["error"]:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=result["error"])
    return ImagePredictResponse(predicted_class=result["predicted_class"], recipe=result.get("recipe"))


@router.post("/suggest", response_model=SuggestResponse,
             summary="Get recipe suggestions from a list of ingredients (RAG)")
async def suggest_recipes(query: IngredientQuery):
    results = recipe_service.suggest_by_ingredients(query.ingredients, query.top_k)
    if not results:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="RAG model not available. Place FAISS index in models/ directory.")
    from app.schemas.recipe import RecipeSuggestion
    return SuggestResponse(results=[RecipeSuggestion(**r) for r in results])


@router.get("/lookup/{name}", response_model=ImagePredictResponse,
            summary="Look up a recipe by dish name")
async def lookup_recipe(name: str):
    recipe = recipe_service.get_recipe_by_name(name)
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No recipe found for '{name}'.")
    return ImagePredictResponse(predicted_class=name, recipe=recipe)
