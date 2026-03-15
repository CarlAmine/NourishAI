from functools import lru_cache

from ..core.config import settings
from ..services.grounded_ai_service import GroundedAIService
from ..services.llm_service import LLMService
from ..services.rag_service import RagService
from ..services.recipe_service import RecipeService


@lru_cache
def get_rag_service() -> RagService:
    return RagService(
        faiss_index_path=settings.FAISS_INDEX_PATH,
        recipes_pkl_path=settings.RECIPES_PKL_PATH,
    )


@lru_cache
def get_llm_service() -> LLMService:
    return LLMService(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL,
        temperature=settings.OPENAI_TEMPERATURE,
        max_tokens=settings.OPENAI_MAX_TOKENS,
        timeout_seconds=settings.OPENAI_TIMEOUT_SEC,
    )


def get_grounded_ai_service() -> GroundedAIService:
    return GroundedAIService(rag=get_rag_service(), llm=get_llm_service())


def get_recipe_service() -> RecipeService:
    return RecipeService(rag=get_rag_service())
