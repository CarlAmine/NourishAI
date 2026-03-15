from typing import List, Optional, Tuple

from ..schemas.recipe import Recipe, RecipeFilters, RetrievalDiagnostics
from .rag_service import RagService


class RecipeService:
    def __init__(self, rag: RagService):
        self.rag = rag

    def search_recipes(
        self,
        query: str,
        top_k: int,
        filters: Optional[RecipeFilters] = None,
        rerank: bool = True,
        include_diagnostics: bool = False,
        candidate_k: Optional[int] = None,
    ) -> Tuple[List[Recipe], Optional[RetrievalDiagnostics]]:
        if include_diagnostics:
            raw, diagnostics = self.rag.search_with_diagnostics(
                query=query,
                top_k=top_k,
                filters=filters,
                rerank=rerank,
                candidate_k=candidate_k,
                include_diagnostics=True,
            )
        else:
            raw = self.rag.search(
                query=query,
                top_k=top_k,
                filters=filters,
                rerank=rerank,
                candidate_k=candidate_k,
            )
            diagnostics = None

        return [Recipe(**r) for r in raw], diagnostics

    def recommend_recipes(
        self,
        ingredients: List[str],
        dietary_notes: Optional[str],
        top_k: int,
        filters: Optional[RecipeFilters] = None,
        rerank: bool = True,
        include_diagnostics: bool = False,
        candidate_k: Optional[int] = None,
    ) -> Tuple[List[Recipe], Optional[RetrievalDiagnostics]]:
        query = f"{', '.join(ingredients)}. {dietary_notes or ''}".strip()
        if include_diagnostics:
            raw, diagnostics = self.rag.search_with_diagnostics(
                query=query,
                top_k=top_k,
                filters=filters,
                rerank=rerank,
                candidate_k=candidate_k,
                ingredients=ingredients,
                include_diagnostics=True,
            )
        else:
            raw = self.rag.search(
                query=query,
                top_k=top_k,
                filters=filters,
                rerank=rerank,
                candidate_k=candidate_k,
                ingredients=ingredients,
            )
            diagnostics = None

        return [Recipe(**r) for r in raw], diagnostics
