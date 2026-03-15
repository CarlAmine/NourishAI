import pytest
from starlette.exceptions import HTTPException

from backend.app.services.rag_service import RagService


def test_rag_missing_index_raises():
    service = RagService("missing.index", "missing.pkl")
    with pytest.raises(HTTPException):
        service.search(query="test", top_k=3)
