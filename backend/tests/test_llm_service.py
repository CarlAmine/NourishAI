import json

from backend.app.schemas.ai import LLMRecommendationPayload, RecommendedRecipe
from backend.app.services.llm_service import LLMService


class DummyMessage:
    def __init__(self, content: str):
        self.content = content


class DummyChoice:
    def __init__(self, content: str):
        self.message = DummyMessage(content)


class DummyResponse:
    def __init__(self, content: str):
        self.choices = [DummyChoice(content)]


class DummyCompletions:
    def __init__(self, content: str):
        self._content = content

    def create(self, **kwargs):
        return DummyResponse(self._content)


class DummyChat:
    def __init__(self, content: str):
        self.completions = DummyCompletions(content)


class DummyClient:
    def __init__(self, content: str):
        self.chat = DummyChat(content)


def test_llm_service_structured_output():
    payload = LLMRecommendationPayload(
        recommended_recipes=[RecommendedRecipe(recipe_id="rec-1", title="Test", why_selected="fits", substitutions=[], warnings=[])],
        warnings=[],
    )
    content = json.dumps(payload.model_dump())
    client = DummyClient(content)

    service = LLMService(api_key="test", client=client)
    result = service.generate_structured("sys", "user", LLMRecommendationPayload)
    assert result.recommended_recipes[0].recipe_id == "rec-1"
