import logging
import os
import pickle
from typing import Any, Dict, List

import faiss
import gdown
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("nourishai.rag")



# we'll construct the download URL from settings when needed


class RagService:
    """
    FAISS-based retrieval service.  The constructor eagerly ensures that the
    artifacts exist (downloading from Drive if necessary) and then loads them
    into memory.  Search is pure business logic and returns a list of dictionaries
    with a computed `score` field.
    """

    def __init__(self, faiss_index_path: str, recipes_pkl_path: str):
        self.faiss_index_path = faiss_index_path
        self.recipes_pkl_path = recipes_pkl_path
        # transformer model is expensive to download; load lazily in search
        self._model: SentenceTransformer | None = None
        self.index: faiss.Index | None = None
        self.recipes: List[Any] = []

        # ensure the FAISS/recipe artifacts are on disk (download if necessary)
        self._ensure_artifacts()
        self._load_artifacts()

    def _ensure_artifacts(self) -> None:
        os.makedirs(os.path.dirname(self.faiss_index_path), exist_ok=True)

        if not os.path.exists(self.faiss_index_path) or not os.path.exists(self.recipes_pkl_path):
            # fetch the ID from settings if available
            try:
                from ..core.config import settings
                folder_id = settings.GDRIVE_FOLDER_ID
                url = f"https://drive.google.com/drive/folders/{folder_id}"
            except Exception:  # settings might not be initialised yet
                url = None

            if url:
                logger.info("RAG artifacts missing, attempting download from %s", url)
                try:
                    gdown.download_folder(url, output=os.path.dirname(self.faiss_index_path), quiet=False, use_cookies=False)
                except Exception as exc:  # pragma: no cover - network may be unavailable
                    logger.warning("failed to download RAG artifacts: %s", exc)
            else:
                logger.warning("no drive URL available, skipping download attempt")

    def _load_artifacts(self) -> None:
        if os.path.exists(self.faiss_index_path):
            try:
                self.index = faiss.read_index(self.faiss_index_path)
                logger.info("loaded faiss index from %s", self.faiss_index_path)
            except Exception as exc:
                logger.error("error loading faiss index: %s", exc)
                self.index = None
        else:
            logger.warning("faiss index path %s does not exist", self.faiss_index_path)

        if os.path.exists(self.recipes_pkl_path):
            try:
                with open(self.recipes_pkl_path, "rb") as f:
                    self.recipes = pickle.load(f)
                logger.info("loaded %s recipes from %s",
                            len(self.recipes) if hasattr(self.recipes, "__len__") else "?",
                            self.recipes_pkl_path)
            except Exception as exc:
                logger.error("error loading recipes pickle: %s", exc)
                self.recipes = []
        else:
            logger.warning("recipes pickle path %s does not exist", self.recipes_pkl_path)

    def search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        logger.info("RAG search query=%r top_k=%s", query, top_k)
        if self.index is None or not self.recipes:
            logger.warning("search called but artifacts are not loaded, returning empty list")
            return []

        # load the encoder only when we actually need it
        if self._model is None:
            try:
                self._model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            except Exception as exc:  # network or model error
                logger.error("failed to load sentence-transformer model: %s", exc)
                return []

        emb = self._model.encode([query])
        # faiss expects float32
        D, I = self.index.search(np.asarray(emb, dtype="float32"), top_k)
        results: List[Dict[str, Any]] = []
        for dist, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self.recipes):
                continue
            rec = self.recipes[idx]
            if isinstance(rec, dict):
                r = rec.copy()
            else:
                r = rec.__dict__.copy()
            r["score"] = float(dist)
            results.append(r)
        return results
