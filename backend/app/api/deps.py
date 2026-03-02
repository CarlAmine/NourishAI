from functools import lru_cache
from ..core.config import settings
from ..services.rag_service import RagService
from ..services.recipe_service import RecipeService


@lru_cache
def get_rag_service() -> RagService:
    return RagService(
        faiss_index_path=settings.FAISS_INDEX_PATH,
        recipes_pkl_path=settings.RECIPES_PKL_PATH,
    )


def get_recipe_service() -> RecipeService:
    return RecipeService(rag=get_rag_service())