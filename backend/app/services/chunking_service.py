"""Document chunking utilities for resume and GitHub content.

Purpose:
    Split raw document text into retrieval-friendly chunks.
Responsibilities:
    Apply documented chunk sizes, overlaps, and metadata decoration.
Dependencies:
    Standard library only.
Usage:
    chunks = ChunkingService().chunk_resume(text, "resume.pdf")
"""

from app.schemas.rag import DocumentChunk
from app.rag.parser import RAGParser


class ChunkingService:
    """Chunking service that delegates to the RAG module's parser splitters."""

    def __init__(self) -> None:
        self._parser = RAGParser()

    def chunk_resume(self, text: str, source_name: str) -> list[DocumentChunk]:
        """Split resume text into chunks."""
        return self._parser.chunk_resume(text, source_name)

    def chunk_code_file(self, text: str, file_path: str, repo_url: str) -> list[DocumentChunk]:
        """Split repository text files into chunks."""
        return self._parser.chunk_code_file(text, file_path, repo_url)

