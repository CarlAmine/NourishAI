from backend.app.schemas.ai import GroundedRecommendationRequest
from backend.app.services.grounded_ai_service import GroundedAIService


class FakeRagService:
    def search_with_diagnostics(self, **kwargs):
        return [], None


class FakeLLMService:
    def generate_structured(self, *args, **kwargs):
        raise AssertionError("LLM should not be called when retrieval is empty")


def test_grounded_recommendation_fallback():
    service = GroundedAIService(rag=FakeRagService(), llm=FakeLLMService())
    req = GroundedRecommendationRequest(ingredients=["chicken"], top_k=3)
    resp = service.grounded_recommendations(req)
    assert resp.recommended_recipes == []
    assert resp.warnings
