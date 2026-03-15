from fastapi import APIRouter, Depends, Response, status
import os

from ...deps import get_llm_service, get_rag_service
from ....core.config import settings
from ....services.llm_service import LLMService
from ....services.rag_service import RagService


router = APIRouter()


def _eval_assets() -> dict:
    return {
        "retrieval_eval": os.path.exists("eval/datasets/retrieval_eval.json"),
        "grounded_generation_eval": os.path.exists("eval/datasets/grounded_generation_eval.json"),
    }


@router.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@router.get("/ready")
def ready(
    response: Response,
    rag: RagService = Depends(get_rag_service),
    llm: LLMService = Depends(get_llm_service),
):
    rag_status = rag.status()
    llm_configured = llm.is_configured()
    eval_assets = _eval_assets()

    ready_flag = rag_status["available"] and not rag_status["artifact_mismatch"]
    if not ready_flag:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "ready": ready_flag,
        "rag": rag_status,
        "openai_configured": llm_configured,
        "openai_model": llm.model,
        "eval_assets": eval_assets,
    }


@router.get("/status")
def status_endpoint(
    response: Response,
    rag: RagService = Depends(get_rag_service),
    llm: LLMService = Depends(get_llm_service),
):
    return ready(response=response, rag=rag, llm=llm)
