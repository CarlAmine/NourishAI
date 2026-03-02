import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from .logging import configure_logging

logger = logging.getLogger("nourishai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting NourishAI API")
    # initialize shared resources; failure to load RAG should not prevent boot
    try:
        from ..api.deps import get_rag_service

        # instantiate service to trigger artifact loading only; do not call `search`
        _ = get_rag_service()
        logger.info("RAG service initialized (artifacts may or may not be present)")
    except Exception as exc:  # pragma: no cover - artifacts may be absent
        logger.exception("RAG init failed, continuing without it: %s", exc)

    yield
    logger.info("Shutting down NourishAI API")