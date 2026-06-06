"""Standardized error response schemas for public API contracts.

Purpose:
    Represent API failures in the `{status, code, message, details}` shape.
Responsibilities:
    Keep error payloads consistent across validation, HTTP, and server errors.
Dependencies:
    Pydantic v2 models.
Usage:
    ErrorResponse(code="VALIDATION_ERROR", message="Input validation failed")
"""

from typing import Any, Literal

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """API error payload defined by docs/API_SPEC.md."""

    status: Literal["error"] = "error"
    code: str = Field(..., examples=["VALIDATION_ERROR"])
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
