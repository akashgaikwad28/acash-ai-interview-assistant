"""Chat API schemas.

Purpose:
    Validate recruiter chat requests and responses for the RAG-backed API.
Responsibilities:
    Enforce message length, optional session IDs, and citation payload shape.
Dependencies:
    Pydantic v2 and RAG citation schema.
Usage:
    ChatRequest(message="What has Acash built?")
"""

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.rag import Citation


class ChatRequest(BaseModel):
    """Request body for POST /chat."""

    message: str = Field(..., min_length=1, max_length=1000)
    session_id: UUID | None = None


class ChatResponse(BaseModel):
    """Response body for POST /chat."""

    response: str
    session_id: UUID
    citations: list[Citation]
