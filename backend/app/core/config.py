from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "NourishAI"
    APP_VERSION: str = "1.0.0"

    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    MODELS_DIR: str = "models"
    FAISS_INDEX_FILENAME: str = "recipes_index.faiss"
    RECIPES_DATA_FILENAME: str = "recipes_data.pkl"
    RAW_RECIPES_FILENAME: str = "raw_recipes.npy"
    CATEGORY_DICT_FILENAME: str = "category_dict.npy"
    IMAGE_MODEL_FILENAME: str = "490Image.pkl"

    GDRIVE_RAW_RECIPES_ID: str = "1lE6zl-9dJKUnNu6CDuBvHPpGodKrGnoX"
    IMAGE_MODEL_URL: str = "https://github.com/CarlAmine/EECE-490/releases/download/v1.0/490Image.pkl"
    IMAGE_MODEL_EXPECTED_SIZE_MB: int = 687

    @property
    def faiss_index_path(self) -> str:
        return f"{self.MODELS_DIR}/{self.FAISS_INDEX_FILENAME}"

    @property
    def recipes_data_path(self) -> str:
        return f"{self.MODELS_DIR}/{self.RECIPES_DATA_FILENAME}"

    @property
    def raw_recipes_path(self) -> str:
        return f"{self.MODELS_DIR}/{self.RAW_RECIPES_FILENAME}"

    @property
    def category_dict_path(self) -> str:
        return f"{self.MODELS_DIR}/{self.CATEGORY_DICT_FILENAME}"

    @property
    def image_model_path(self) -> str:
        return f"{self.MODELS_DIR}/{self.IMAGE_MODEL_FILENAME}"


settings = Settings()
