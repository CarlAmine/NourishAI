from backend.app.core.validation import validate_startup


class FakeRag:
    def __init__(self, status):
        self._status = status

    def status(self):
        return self._status


class FakeLLM:
    def __init__(self, configured: bool):
        self._configured = configured

    def is_configured(self):
        return self._configured


def test_validate_startup_reports_missing_artifacts():
    rag = FakeRag(
        {
            "index_loaded": False,
            "recipes_loaded": False,
            "index_count": 0,
            "recipe_count": 0,
            "artifact_mismatch": False,
            "available": False,
        }
    )
    llm = FakeLLM(configured=False)
    report = validate_startup(rag, llm)
    assert report["errors"]
    assert report["warnings"]


def test_validate_startup_warns_on_mismatch():
    rag = FakeRag(
        {
            "index_loaded": True,
            "recipes_loaded": True,
            "index_count": 10,
            "recipe_count": 8,
            "artifact_mismatch": True,
            "available": True,
        }
    )
    llm = FakeLLM(configured=True)
    report = validate_startup(rag, llm)
    assert report["warnings"]
