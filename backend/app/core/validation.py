from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..services.llm_service import LLMService
from ..services.rag_service import RagService
from .config import settings


def validate_startup(rag: Optional[RagService], llm: Optional[LLMService]) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    rag_status = rag.status() if rag else {
        "index_loaded": False,
        "recipes_loaded": False,
        "index_count": 0,
        "recipe_count": 0,
        "artifact_mismatch": False,
        "available": False,
    }

    if not rag_status["index_loaded"]:
        errors.append(f"FAISS index is not loaded at {settings.FAISS_INDEX_PATH}.")
    if not rag_status["recipes_loaded"]:
        errors.append(f"Recipe metadata is not loaded at {settings.RECIPES_PKL_PATH}.")
    if rag_status["artifact_mismatch"]:
        warnings.append("FAISS index count does not match recipe count; rebuild artifacts.")

    llm_configured = llm.is_configured() if llm else False
    if not llm_configured:
        warnings.append("OpenAI API key is not configured; grounded generation endpoints will be limited.")

    return {
        "errors": errors,
        "warnings": warnings,
        "rag_status": rag_status,
        "llm_configured": llm_configured,
    }
