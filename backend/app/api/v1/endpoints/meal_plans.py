from fastapi import APIRouter, Depends, HTTPException

from ...deps import get_grounded_ai_service
from ....schemas.ai import MealPlanRequest, MealPlanResponse
from ....services.grounded_ai_service import GroundedAIService

router = APIRouter()


@router.post("/meal-plans/generate", response_model=MealPlanResponse)
def generate_meal_plan(
    payload: MealPlanRequest,
    service: GroundedAIService = Depends(get_grounded_ai_service),
) -> MealPlanResponse:
    try:
        return service.generate_meal_plan(payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
