import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI

from .logging import configure_logging
from .observability import log_event
from .validation import validate_startup
from .config import settings

logger = logging.getLogger("nourishai")


def _check_artifacts() -> None:
    """Log artifact status. Index is built at Docker build time so this is just a sanity check."""
    faiss_ok = os.path.exists(settings.FAISS_INDEX_PATH) and os.path.getsize(settings.FAISS_INDEX_PATH) > 0
    pkl_ok = os.path.exists(settings.RECIPES_PKL_PATH) and os.path.getsize(settings.RECIPES_PKL_PATH) > 0

    if faiss_ok and pkl_ok:
        logger.info(
            "Artifacts ready — faiss.index (%d bytes), recipe.pkl (%d bytes)",
            os.path.getsize(settings.FAISS_INDEX_PATH),
            os.path.getsize(settings.RECIPES_PKL_PATH),
        )
    else:
        logger.error(
            "Artifacts missing (faiss_ok=%s, pkl_ok=%s). "
            "The index should have been built during Docker build. "
            "Check the build logs for errors in the index-builder stage.",
            faiss_ok, pkl_ok,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    log_event(logger, "startup_begin")
    try:
        # Verify artifacts exist (built at Docker build time)
        _check_artifacts()

        # Initialise services
        from ..api.deps import get_llm_service, get_rag_service
        rag = get_rag_service()
        llm = get_llm_service()
        log_event(logger, "startup_services_initialized")

        # Validate
        report = validate_startup(rag, llm)
        for warning in report["warnings"]:
            log_event(logger, "startup_warning", detail=warning)
        for error in report["errors"]:
            log_event(logger, "startup_error", detail=error)
        if settings.STRICT_STARTUP and report["errors"]:
            raise RuntimeError("Startup validation failed: " + "; ".join(report["errors"]))

    except Exception as exc:
        log_event(logger, "startup_exception", error=str(exc))
        if settings.STRICT_STARTUP:
            raise

    yield
    log_event(logger, "shutdown")
