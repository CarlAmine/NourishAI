import logging
from typing import List

logger = logging.getLogger("nourishai.rag")


class RagService:
    """
    Replace search() with your real FAISS + embeddings retrieval.
    Keep this free of FastAPI imports: pure business logic.
    """

    def __init__(self, faiss_index_path: str, recipes_pkl_path: str):
        self.faiss_index_path = faiss_index_path
        self.recipes_pkl_path = recipes_pkl_path

    def search(self, query: str, top_k: int) -> List[dict]:
        logger.info("RAG search query=%r top_k=%s", query, top_k)
        return [
            {
                "id": "demo-1",
                "title": "Demo Recipe",
                "ingredients": ["ingredient 1", "ingredient 2"],
                "instructions": ["step 1", "step 2"],
                "calories": 420,
                "score": 0.95,
            }
        ][:top_k]