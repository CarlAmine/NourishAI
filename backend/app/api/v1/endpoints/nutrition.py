from fastapi import APIRouter, Depends, HTTPException

from ...deps import get_grounded_ai_service
from ....schemas.ai import NutritionQARequest, NutritionQAResponse
from ....services.grounded_ai_service import GroundedAIService

router = APIRouter()


@router.post("/nutrition/qa", response_model=NutritionQAResponse)
def nutrition_qa(
    payload: NutritionQARequest,
    service: GroundedAIService = Depends(get_grounded_ai_service),
) -> NutritionQAResponse:
    try:
        return service.answer_nutrition_question(payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
