from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "NourishAI API"
    ENV: str = Field(default="dev", description="dev|staging|prod")
    LOG_LEVEL: str = Field(default="INFO")

    CORS_ORIGINS: str = Field(default="*", description="Comma-separated origins or *")

    FAISS_INDEX_PATH: str = "models/faiss.index"
    RECIPES_PKL_PATH: str = "models/recipe.pkl"


settings = Settings()