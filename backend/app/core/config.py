from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "NourishAI API"
    ENV: str = Field(default="dev", description="dev|staging|prod")
    LOG_LEVEL: str = Field(default="INFO")

    CORS_ORIGINS: str = Field(default="*", description="Comma-separated origins or *")

    # local file paths for retrieval artifacts
    FAISS_INDEX_PATH: str = "models/faiss.index"
    RECIPES_PKL_PATH: str = "models/recipe.pkl"

    # when artifacts are missing the service will try to download everything
    # from this Google Drive folder ID via gdown
    GDRIVE_FOLDER_ID: str = Field(default="10okoRXmRZDGtsF8e5cDxSLEzJWfuF9nl",
                                  description="Drive folder containing faiss.index + recipe.pkl")


settings = Settings()