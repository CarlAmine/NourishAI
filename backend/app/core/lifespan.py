import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI

from .logging import configure_logging
from .observability import log_event
from .validation import validate_startup
from .config import settings

logger = logging.getLogger("nourishai")


def _download_gdrive_folder(folder_id: str, output_dir: str) -> bool:
    """Fallback runtime download if build-time download failed."""
    try:
        import gdown
        os.makedirs(output_dir, exist_ok=True)
        gdown.download_folder(
            id=folder_id,
            output=output_dir,
            quiet=False,
            use_cookies=False,
        )
        return True
    except Exception as exc:
        logger.error("gdown folder download failed: %s", exc)
        return False


def _ensure_artifacts() -> None:
    """
    Verify artifacts exist. If not (build-time download failed),
    attempt a runtime download as fallback.
    """
    faiss_ok = os.path.exists(settings.FAISS_INDEX_PATH) and os.path.getsize(settings.FAISS_INDEX_PATH) > 0
    pkl_ok = os.path.exists(settings.RECIPES_PKL_PATH) and os.path.getsize(settings.RECIPES_PKL_PATH) > 0

    if faiss_ok and pkl_ok:
        logger.info(
            "Artifacts ready — faiss.index (%d bytes), recipe.pkl (%d bytes)",
            os.path.getsize(settings.FAISS_INDEX_PATH),
            os.path.getsize(settings.RECIPES_PKL_PATH),
        )
        return

    logger.warning(
        "Artifacts missing at startup (faiss_ok=%s, pkl_ok=%s) — attempting runtime download",
        faiss_ok, pkl_ok,
    )

    if settings.GDRIVE_FOLDER_ID:
        _download_gdrive_folder(settings.GDRIVE_FOLDER_ID, settings.MODELS_DIR)
    else:
        logger.error("GDRIVE_FOLDER_ID not set — cannot download artifacts.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    log_event(logger, "startup_begin")
    try:
        # Step 1: verify/download artifacts
        _ensure_artifacts()

        # Step 2: initialise services
        from ..api.deps import get_llm_service, get_rag_service
        rag = get_rag_service()
        llm = get_llm_service()
        log_event(logger, "startup_services_initialized")

        # Step 3: validate
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
