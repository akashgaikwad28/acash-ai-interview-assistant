"""Tests for RAG foundation chunking and local retrieval."""

from pathlib import Path

from app.core.config import get_settings
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.rag_service import RAGService
from app.services.vector_store import LocalVectorStore


def test_resume_chunking_adds_metadata() -> None:
    chunker = ChunkingService()
    text = "Skills\nFastAPI Python LangGraph\n\nProjects\nBuilt an AI interview assistant. " * 20

    chunks = chunker.chunk_resume(text, "resume.pdf")

    assert chunks
    assert chunks[0].metadata.source_type == "resume"
    assert chunks[0].metadata.source_name == "resume.pdf"
    assert chunks[0].metadata.chunk_index == 0


def test_local_rag_retrieval_returns_citations(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    settings = get_settings()
    store = LocalVectorStore(settings, EmbeddingService(settings))
    chunks = ChunkingService().chunk_resume(
        "Acash built a FastAPI backend with LangGraph orchestration and ChromaDB retrieval.",
        "resume.pdf",
    )
    store.upsert("resume_collection", chunks)

    result = RAGService(store).retrieve("FastAPI LangGraph ChromaDB")

    assert result.contexts
    assert result.citations[0].source == "resume.pdf"
    assert Path("data/vector_store.json").exists()
