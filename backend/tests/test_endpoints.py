from fastapi.testclient import TestClient

from backend.app.api import deps
from backend.app.main import app
from backend.app.schemas.ai import (
    GroundedRecommendationResponse,
    MealPlanResponse,
    NutritionQAResponse,
    RecommendedRecipe,
    SourceRecipeRef,
)


class FakeGroundedService:
    def grounded_recommendations(self, payload):
        return GroundedRecommendationResponse(
            recommended_recipes=[
                RecommendedRecipe(recipe_id="rec-1", title="Test", why_selected="fits", substitutions=[], warnings=[])
            ],
            warnings=[],
            source_recipes=[SourceRecipeRef(id="rec-1", title="Test")],
        )

    def generate_meal_plan(self, payload):
        return MealPlanResponse(days=[], warnings=[], source_recipes=[])

    def answer_nutrition_question(self, payload):
        return NutritionQAResponse(answer="Test", supporting_sources=[], warnings=[])


def test_grounded_recommend_endpoint():
    app.dependency_overrides[deps.get_grounded_ai_service] = lambda: FakeGroundedService()
    client = TestClient(app)
    response = client.post(
        "/api/v1/recipes/recommend/grounded",
        json={"ingredients": ["chicken"], "top_k": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert "recommended_recipes" in data
    app.dependency_overrides = {}


def test_meal_plan_endpoint():
    app.dependency_overrides[deps.get_grounded_ai_service] = lambda: FakeGroundedService()
    client = TestClient(app)
    response = client.post(
        "/api/v1/meal-plans/generate",
        json={"days": 2, "meals_per_day": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert "days" in data
    app.dependency_overrides = {}


def test_nutrition_qa_endpoint():
    app.dependency_overrides[deps.get_grounded_ai_service] = lambda: FakeGroundedService()
    client = TestClient(app)
    response = client.post(
        "/api/v1/nutrition/qa",
        json={"question": "How much protein?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    app.dependency_overrides = {}
