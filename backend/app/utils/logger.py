"""Structured JSON logging helpers and request middleware.

Purpose:
    Emit parseable logs with trace IDs, endpoint names, status codes, and latency.
Responsibilities:
    Configure Python logging and attach request-level instrumentation.
Dependencies:
    FastAPI/Starlette request-response middleware and Python logging.
Usage:
    configure_logging(settings.log_level)
    app.middleware("http")(logging_middleware)
"""

import json
import logging
import time
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Request, Response


logger = logging.getLogger("acash_assistant")


def configure_logging(level: str) -> None:
    """Configure root logging for JSON application messages."""

    logging.basicConfig(level=level.upper(), format="%(message)s")
    logger.setLevel(level.upper())


def log_json(level: int, event: str, **fields: object) -> None:
    """Write one structured JSON log event."""

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **fields,
    }
    logger.log(level, json.dumps(payload, default=str, separators=(",", ":")))


async def logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Add trace IDs and request latency logging to every response."""

    trace_id = request.headers.get("X-Trace-Id", str(uuid4()))
    request.state.trace_id = trace_id
    start = time.perf_counter()

    response = await call_next(request)
    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Trace-Id"] = trace_id

    log_json(
        logging.INFO,
        "http_request",
        trace_id=trace_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        latency_ms=latency_ms,
    )
    return response
