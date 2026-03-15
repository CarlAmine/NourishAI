from backend.app.schemas.recipe import RecipeFilters
from backend.app.services.rag_service import RagService


def test_metadata_filtering():
    service = RagService("missing.index", "missing.pkl")
    recipe = {
        "id": "rec-1",
        "title": "Test",
        "cuisine": ["italian"],
        "meal_type": ["dinner"],
        "dietary_tags": ["vegetarian"],
        "calories": 450,
        "protein_g": 20,
    }

    filters = RecipeFilters(cuisine=["italian"], min_calories=300, max_calories=500)
    assert service._matches_filters(recipe, filters) is True

    filters = RecipeFilters(cuisine=["mexican"])
    assert service._matches_filters(recipe, filters) is False

    filters = RecipeFilters(max_calories=300)
    assert service._matches_filters(recipe, filters) is False
