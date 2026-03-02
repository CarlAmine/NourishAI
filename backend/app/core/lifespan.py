import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from .logging import configure_logging

logger = logging.getLogger("nourishai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting NourishAI API")
    # TODO: init shared resources (FAISS load, embeddings warmup, DB pool)
    yield
    logger.info("Shutting down NourishAI API")