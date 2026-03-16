import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI

from .logging import configure_logging
from .observability import log_event
from .validation import validate_startup
from .config import settings

logger = logging.getLogger("nourishai")


def _download_gdrive(file_id: str, destination: str) -> bool:
    """Download a file from Google Drive using gdown. Returns True on success."""
    try:
        import gdown
        os.makedirs(os.path.dirname(destination) or ".", exist_ok=True)
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, destination, quiet=False)
        if os.path.exists(destination) and os.path.getsize(destination) > 0:
            logger.info("Downloaded %s -> %s (%d bytes)", file_id, destination, os.path.getsize(destination))
            return True
        logger.error("gdown finished but file missing or empty: %s", destination)
        return False
    except Exception as exc:
        logger.error("gdown failed for %s: %s", file_id, exc)
        return False


def _ensure_artifacts() -> None:
    """
    Download FAISS index + recipes pickle from Google Drive if they are absent.
    This runs synchronously at startup before RagService tries to load them.
    """
    faiss_ok = os.path.exists(settings.FAISS_INDEX_PATH) and os.path.getsize(settings.FAISS_INDEX_PATH) > 0
    pkl_ok = os.path.exists(settings.RECIPES_PKL_PATH) and os.path.getsize(settings.RECIPES_PKL_PATH) > 0

    if faiss_ok and pkl_ok:
        logger.info("Artifacts already present — skipping download.")
        return

    if not settings.GDRIVE_FOLDER_ID:
        logger.warning("GDRIVE_FOLDER_ID not set — cannot download artifacts.")
        return

    logger.info("Artifacts missing — downloading from Google Drive folder %s", settings.GDRIVE_FOLDER_ID)
    os.makedirs(settings.MODELS_DIR, exist_ok=True)

    try:
        import gdown
        # Download the entire folder (faiss.index + recipe.pkl land in MODELS_DIR)
        gdown.download_folder(
            id=settings.GDRIVE_FOLDER_ID,
            output=settings.MODELS_DIR,
            quiet=False,
            use_cookies=False,
        )
        logger.info("Folder download complete.")
    except Exception as exc:
        logger.error("Folder download failed: %s — trying individual file IDs", exc)
        # Fallback: try individual files if GDRIVE_RAW_RECIPES_ID is set
        if settings.GDRIVE_RAW_RECIPES_ID and not pkl_ok:
            _download_gdrive(settings.GDRIVE_RAW_RECIPES_ID, settings.RECIPES_PKL_PATH)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    log_event(logger, "startup_begin")
    try:
        # ── Step 1: ensure model artifacts are on disk ──────────────────────
        _ensure_artifacts()

        # ── Step 2: initialise services (RagService reads files from disk) ──
        from ..api.deps import get_llm_service, get_rag_service

        rag = get_rag_service()
        llm = get_llm_service()
        log_event(logger, "startup_services_initialized")

        # ── Step 3: validate ─────────────────────────────────────────────────
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
