"""Persistent vector store adapter for local RAG development.

Purpose:
    Store embedded chunks and run cosine retrieval while ChromaDB integration
    is being wired into production infrastructure.
Responsibilities:
    Persist vectors in JSON, upsert chunks, query top-k matches, and keep the
    service boundary compatible with a future Chroma implementation.
Dependencies:
    EmbeddingService and Pydantic RAG schemas.
Usage:
    store.upsert("resume_collection", chunks)
    results = store.query(["resume_collection"], "FastAPI")
"""

from app.core.config import Settings
from app.schemas.rag import DocumentChunk, RetrievedChunk
from app.services.embedding_service import EmbeddingService
from app.rag.database import ChromaRAGDatabase


class LocalVectorStore:
    """Vector store adapter that delegates to the ChromaDB + BM25 RAG engine."""

    def __init__(self, settings: Settings, embedder: EmbeddingService) -> None:
        self._db = ChromaRAGDatabase(settings, embedder)

    def upsert(self, collection_name: str, chunks: list[DocumentChunk]) -> list[str]:
        """Insert or replace chunks in a named collection."""
        return self._db.upsert(collection_name, chunks)

    def query(
        self,
        collection_names: list[str],
        query: str,
        *,
        top_k: int = 5,
        min_score: float = 0.65,
    ) -> list[RetrievedChunk]:
        """Return top matching chunks across selected collections."""
        return self._db.query(collection_names, query, top_k=top_k, min_score=min_score)

