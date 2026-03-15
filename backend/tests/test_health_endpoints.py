from fastapi.testclient import TestClient

from backend.app.api import deps
from backend.app.main import app


class FakeRagReady:
    def status(self):
        return {
            "index_loaded": True,
            "recipes_loaded": True,
            "index_count": 10,
            "recipe_count": 10,
            "artifact_mismatch": False,
            "available": True,
        }


class FakeRagNotReady:
    def status(self):
        return {
            "index_loaded": False,
            "recipes_loaded": False,
            "index_count": 0,
            "recipe_count": 0,
            "artifact_mismatch": False,
            "available": False,
        }


class FakeLLM:
    model = "gpt-test"

    def is_configured(self):
        return True


def test_health_endpoint_includes_request_id():
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")
    assert response.json()["status"] == "ok"


def test_ready_endpoint_reports_ready():
    app.dependency_overrides[deps.get_rag_service] = lambda: FakeRagReady()
    app.dependency_overrides[deps.get_llm_service] = lambda: FakeLLM()
    client = TestClient(app)
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ready"] is True
    app.dependency_overrides = {}


def test_ready_endpoint_reports_not_ready():
    app.dependency_overrides[deps.get_rag_service] = lambda: FakeRagNotReady()
    app.dependency_overrides[deps.get_llm_service] = lambda: FakeLLM()
    client = TestClient(app)
    response = client.get("/api/v1/ready")
    assert response.status_code == 503
    payload = response.json()
    assert payload["ready"] is False
    app.dependency_overrides = {}


def test_status_endpoint_alias():
    app.dependency_overrides[deps.get_rag_service] = lambda: FakeRagReady()
    app.dependency_overrides[deps.get_llm_service] = lambda: FakeLLM()
    client = TestClient(app)
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    payload = response.json()
    assert "ready" in payload
    app.dependency_overrides = {}
