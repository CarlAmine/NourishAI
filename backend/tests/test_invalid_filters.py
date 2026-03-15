from fastapi.testclient import TestClient

from backend.app.main import app


def test_search_invalid_filters_returns_422():
    client = TestClient(app)
    response = client.post(
        "/api/v1/recipes/search",
        json={
            "query": "chicken",
            "top_k": 3,
            "filters": {"min_calories": "not-a-number"},
        },
    )
    assert response.status_code == 422
