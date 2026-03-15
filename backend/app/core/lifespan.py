import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from .logging import configure_logging
from .observability import log_event
from .validation import validate_startup
from .config import settings

logger = logging.getLogger("nourishai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    log_event(logger, "startup_begin")
    try:
        from ..api.deps import get_llm_service, get_rag_service

        rag = get_rag_service()
        llm = get_llm_service()
        log_event(logger, "startup_services_initialized")

        report = validate_startup(rag, llm)
        for warning in report["warnings"]:
            log_event(logger, "startup_warning", detail=warning)
        for error in report["errors"]:
            log_event(logger, "startup_error", detail=error)
        if settings.STRICT_STARTUP and report["errors"]:
            raise RuntimeError("Startup validation failed: " + "; ".join(report["errors"]))
    except Exception as exc:  # pragma: no cover - artifacts may be absent
        log_event(logger, "startup_exception", error=str(exc))
        if settings.STRICT_STARTUP:
            raise

    yield
    log_event(logger, "shutdown")
