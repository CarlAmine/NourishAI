from __future__ import annotations

import contextvars
import logging
import time
import uuid
from typing import Any, Optional

from starlette.requests import Request
from starlette.responses import Response


REQUEST_ID_HEADER = "X-Request-ID"

_request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("request_id", default=None)


def set_request_id(request_id: str) -> None:
    _request_id_ctx.set(request_id)


def get_request_id() -> Optional[str]:
    return _request_id_ctx.get()


def clear_request_id() -> None:
    _request_id_ctx.set(None)


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    logger.info(event, extra={"event": event, **fields})


async def request_context_middleware(request: Request, call_next) -> Response:
    logger = logging.getLogger("nourishai.request")
    request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
    set_request_id(request_id)
    start = time.perf_counter()

    log_event(
        logger,
        "request_received",
        method=request.method,
        path=request.url.path,
        query=request.url.query,
        client=request.client.host if request.client else None,
    )

    try:
        response = await call_next(request)
    except Exception as exc:
        latency_ms = (time.perf_counter() - start) * 1000.0
        logger.exception(
            "request_failed",
            extra={
                "event": "request_failed",
                "method": request.method,
                "path": request.url.path,
                "latency_ms": round(latency_ms, 2),
                "error": str(exc),
            },
        )
        clear_request_id()
        raise

    latency_ms = (time.perf_counter() - start) * 1000.0
    log_event(
        logger,
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        latency_ms=round(latency_ms, 2),
    )

    response.headers[REQUEST_ID_HEADER] = request_id
    clear_request_id()
    return response
