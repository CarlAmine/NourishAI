from fastapi import APIRouter

from .endpoints.grounded_recommend import router as grounded_recommend_router
from .endpoints.health import router as health_router
from .endpoints.meal_plans import router as meal_plans_router
from .endpoints.nutrition import router as nutrition_router
from .endpoints.recipes import router as recipes_router
from .endpoints.recommend import router as recommend_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(recipes_router, tags=["recipes"])
api_router.include_router(recommend_router, tags=["recipes"])
api_router.include_router(grounded_recommend_router, tags=["recipes"])
api_router.include_router(meal_plans_router, tags=["meal-plans"])
api_router.include_router(nutrition_router, tags=["nutrition"])
