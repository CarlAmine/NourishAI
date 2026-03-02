from typing import List
from ..schemas.recipe import Recipe
from .rag_service import RagService


class RecipeService:
    def __init__(self, rag: RagService):
        self.rag = rag

    def search_recipes(self, query: str, top_k: int) -> List[Recipe]:
        raw = self.rag.search(query=query, top_k=top_k)
        return [Recipe(**r) for r in raw]