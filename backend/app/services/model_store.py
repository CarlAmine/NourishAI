import logging
import os
import pickle
from typing import Any, Dict, List

import numpy as np
import requests

from ..core.config import settings

logger = logging.getLogger(__name__)


class ModelStore:
    """Singleton that holds all loaded ML artifacts."""

    def __init__(self):
        self.svc_model: Any = None
        self.category_dict: Dict[int, str] = {}
        self.recipe_dict: Dict[str, Any] = {}
        self.faiss_index: Any = None
        self.rag_texts: List[dict] = []
        self.sentence_model: Any = None

    async def load_all(self):
        os.makedirs(settings.MODELS_DIR, exist_ok=True)
        self._load_category_dict()
        self._load_recipe_dict()
        self._load_image_model()
        self._try_load_rag()

    def _load_category_dict(self):
        path = settings.CATEGORY_DICT_PATH
        if not os.path.exists(path):
            logger.warning("category_dict.npy not found at %s - image prediction disabled.", path)
            return
        self.category_dict = np.load(path, allow_pickle=True).item()
        logger.info("Loaded category_dict with %d classes.", len(self.category_dict))

    def _load_recipe_dict(self):
        path = settings.RAW_RECIPES_PATH
        if not os.path.exists(path):
            logger.warning("raw_recipes.npy not found - downloading from Google Drive...")
            self._download_gdrive(settings.GDRIVE_RAW_RECIPES_ID, path)
        if os.path.exists(path):
            self.recipe_dict = np.load(path, allow_pickle=True).item()
            logger.info("Loaded recipe_dict with %d entries.", len(self.recipe_dict.get("name", {})))
        else:
            logger.error("Could not load recipe_dict.")

    def _load_image_model(self):
        path = settings.IMAGE_MODEL_PATH
        expected = settings.IMAGE_MODEL_EXPECTED_SIZE_MB * 1024 * 1024
        if not os.path.exists(path) or os.path.getsize(path) < expected:
            logger.info("Downloading image model from GitHub Releases...")
            self._download_stream(settings.IMAGE_MODEL_URL, path)
        if os.path.exists(path):
            with open(path, "rb") as f:
                self.svc_model = pickle.load(f)
            logger.info("Image model (SVC) loaded.")
        else:
            logger.error("Image model not available.")

    def _try_load_rag(self):
        faiss_path = settings.FAISS_INDEX_PATH
        data_path = settings.RECIPES_PKL_PATH
        if not (os.path.exists(faiss_path) and os.path.exists(data_path)):
            logger.info("FAISS index not found - RAG endpoint will be unavailable.")
            return
        try:
            import faiss
            from sentence_transformers import SentenceTransformer

            self.faiss_index = faiss.read_index(faiss_path)
            with open(data_path, "rb") as f:
                self.rag_texts = pickle.load(f)
            self.sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("RAG components loaded (%d recipes).", len(self.rag_texts))
        except Exception as exc:
            logger.warning("Could not load RAG components: %s", exc)

    @staticmethod
    def _download_gdrive(file_id: str, destination: str):
        url = f"https://drive.google.com/uc?id={file_id}"
        try:
            import gdown

            gdown.download(url, destination, quiet=False)
        except Exception as exc:
            logger.error("gdown failed: %s", exc)

    @staticmethod
    def _download_stream(url: str, destination: str):
        try:
            with requests.get(url, stream=True, timeout=300) as r:
                r.raise_for_status()
                with open(destination, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            logger.info("Downloaded %s -> %s", url, destination)
        except Exception as exc:
            logger.error("Stream download failed: %s", exc)


model_store = ModelStore()
