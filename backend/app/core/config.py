from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "NourishAI API"
    APP_VERSION: str = "0.2.0"
    ENV: str = Field(default="dev", description="dev|staging|prod")
    LOG_LEVEL: str = Field(default="INFO")
    STRICT_STARTUP: bool = Field(default=False, description="Fail startup if required artifacts are missing")

    CORS_ORIGINS: str = Field(default="*", description="Comma-separated origins or *")

    DATA_DIR: str = "data"
    ARTIFACTS_DIR: str = "artifacts"

    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384
    RETRIEVAL_CANDIDATES: int = 50
    HYBRID_ALPHA: float = 0.65

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "nourishai_chunks"

    LEXICAL_INDEX_PATH: str = "artifacts/lexical_index.pkl"
    CHUNK_STORE_PATH: str = "artifacts/chunks.jsonl"
    INGESTION_MANIFEST_PATH: str = "artifacts/ingestion_manifest.json"

    MODELS_DIR: str = "models"
    CATEGORY_DICT_PATH: str = "models/category_dict.npy"
    RAW_RECIPES_PATH: str = "models/raw_recipes.npy"
    IMAGE_MODEL_PATH: str = "models/490Image.pkl"
    IMAGE_MODEL_URL: str = "https://github.com/CarlAmine/EECE-490/releases/download/v1.0/490Image.pkl"
    IMAGE_MODEL_EXPECTED_SIZE_MB: int = 687
    RECIPES_DATA_PATH: str = "models/recipes_data.pkl"

    FAISS_INDEX_PATH: str = "models/faiss.index"
    RECIPES_PKL_PATH: str = "models/recipe.pkl"

    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.2
    OPENAI_MAX_TOKENS: int = 800
    OPENAI_TIMEOUT_SEC: float = 20.0

    GDRIVE_RAW_RECIPES_ID: str = Field(
        default="1lE6zl-9dJKUnNu6CDuBvHPpGodKrGnoX",
        description="Drive file containing raw_recipes.npy",
    )
    GDRIVE_FOLDER_ID: str = Field(
        default="10okoRXmRZDGtsF8e5cDxSLEzJWfuF9nl",
        description="Drive folder containing faiss.index + recipe.pkl",
    )


settings = Settings()
