"""Application exceptions and global exception handlers.

Purpose:
    Convert framework and domain errors into the standard API error schema.
Responsibilities:
    Register handlers for HTTP, validation, rate limit, and generic exceptions.
Dependencies:
    FastAPI exception hooks and the ErrorResponse schema.
Usage:
    register_exception_handlers(app)
"""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.schemas.errors import ErrorResponse
from app.utils.logger import log_json


class AppError(Exception):
    """Domain exception carrying an API error code and HTTP status."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


def _error_response(status_code: int, code: str, message: str, details: dict[str, Any] | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(code=code, message=message, details=details or {}).model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global exception handlers to a FastAPI application."""

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return _error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else "HTTP request failed"
        code = "HTTP_ERROR" if exc.status_code < 500 else "SERVER_ERROR"
        return _error_response(exc.status_code, code, detail)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = {"errors": exc.errors()}
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "VALIDATION_ERROR",
            "Input validation failed",
            details,
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(_: Request, exc: RateLimitExceeded) -> JSONResponse:
        return _error_response(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "RATE_LIMIT_EXCEEDED",
            "Exceeded request allocation.",
            {"limit": str(exc.detail)},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        trace_id = getattr(request.state, "trace_id", None)
        log_json(logging.ERROR, "unhandled_exception", trace_id=trace_id, error=repr(exc))
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "INTERNAL_SERVER_ERROR",
            "An unexpected server error occurred.",
            {"trace_id": trace_id} if trace_id else {},
        )
