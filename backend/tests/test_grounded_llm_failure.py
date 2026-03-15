from backend.app.schemas.ai import GroundedRecommendationRequest
from backend.app.services.grounded_ai_service import GroundedAIService


class FakeRag:
    def search_with_diagnostics(self, **kwargs):
        return [
            {
                "id": "rec-1",
                "title": "Test Recipe",
                "ingredients": ["chicken"],
                "instructions": ["Cook"],
                "calories": 300,
            }
        ], None


class FailingLLM:
    def generate_structured(self, *args, **kwargs):
        raise RuntimeError("LLM failure")


def test_grounded_recommendation_llm_failure_returns_fallback():
    service = GroundedAIService(rag=FakeRag(), llm=FailingLLM())
    request = GroundedRecommendationRequest(ingredients=["chicken"], top_k=1)
    response = service.grounded_recommendations(request)
    assert response.recommended_recipes == []
    assert response.warnings
