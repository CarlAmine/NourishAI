import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.services.model_store import model_store

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load all ML models on startup, release on shutdown."""
    logger.info("🚀 Starting NourishAI backend – loading models...")
    await model_store.load_all()
    logger.info("✅ All models loaded. Server ready.")
    yield
    logger.info("🛑 Shutting down NourishAI backend.")
