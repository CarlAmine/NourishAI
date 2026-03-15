from fastapi import APIRouter, Depends

from ...deps import get_retrieval_service
from ....schemas.retrieval import RetrievalRequest, RetrievalResponse
from ....services.retrieval_service import RetrievalService

router = APIRouter()


@router.post("/retrieval/search", response_model=RetrievalResponse)
def retrieval_search(
    payload: RetrievalRequest,
    service: RetrievalService = Depends(get_retrieval_service),
):
    return service.search(payload)
