from fastapi import APIRouter
from .endpoints.health import router as health_router
from .endpoints.recipes import router as recipes_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(recipes_router, tags=["recipes"])