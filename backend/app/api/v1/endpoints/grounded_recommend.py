from fastapi import APIRouter, Depends, HTTPException

from ...deps import get_grounded_ai_service
from ....schemas.ai import GroundedRecommendationRequest, GroundedRecommendationResponse
from ....services.grounded_ai_service import GroundedAIService

router = APIRouter()


@router.post("/recipes/recommend/grounded", response_model=GroundedRecommendationResponse)
def grounded_recommendations(
    payload: GroundedRecommendationRequest,
    service: GroundedAIService = Depends(get_grounded_ai_service),
) -> GroundedRecommendationResponse:
    try:
        return service.grounded_recommendations(payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
