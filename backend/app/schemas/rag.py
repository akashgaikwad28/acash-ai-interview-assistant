"""RAG domain schemas for chunks, citations, and retrieval results.

Purpose:
    Define typed data contracts between ingestion, vector storage, retrieval,
    and agent layers.
Responsibilities:
    Represent document chunks with metadata and retrieval outputs with scores.
Dependencies:
    Pydantic v2.
Usage:
    DocumentChunk(text="...", metadata=ChunkMetadata(...))
"""

from typing import Literal

from pydantic import BaseModel, Field


SourceType = Literal["resume", "github"]


class ChunkMetadata(BaseModel):
    """Metadata attached to every indexed RAG chunk."""

    source_type: SourceType
    source_name: str
    chunk_index: int
    file_path: str | None = None
    repo_url: str | None = None
    section: str | None = None


class DocumentChunk(BaseModel):
    """Text chunk ready for embedding and vector persistence."""

    id: str
    text: str = Field(..., min_length=1)
    metadata: ChunkMetadata


class Citation(BaseModel):
    """Frontend-renderable citation object from retrieved context."""

    source: str
    text_snippet: str
    score: float


class RetrievedChunk(BaseModel):
    """Search result containing a source chunk and relevance score."""

    chunk: DocumentChunk
    score: float


class RetrievalResult(BaseModel):
    """RAG context payload passed to downstream prompt construction."""

    contexts: list[RetrievedChunk]
    citations: list[Citation]
