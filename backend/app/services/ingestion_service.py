"""Resume and GitHub ingestion service.

Purpose:
    Convert uploaded resumes and public repositories into embedded RAG chunks.
Responsibilities:
    Extract text, filter repository files, chunk content, and persist vectors.
Dependencies:
    Optional pypdf/GitPython, ChunkingService, and LocalVectorStore.
Usage:
    result = await IngestionService(...).ingest_resume(upload)
"""

import shutil
import tempfile
import sys
from pathlib import Path

from fastapi import UploadFile

from app.schemas.ingest import GitHubIngestResponse, ResumeIngestResponse
from app.schemas.rag import DocumentChunk
from app.services.chunking_service import ChunkingService
from app.services.vector_store import LocalVectorStore
from app.utils.errors import AppError

from app.rag.ingester import PDFExtractor, GitHubCrawler


class IngestionService:
    """Service that ingests resume PDFs and GitHub repositories by delegating to the RAG module."""

    def __init__(self, chunker: ChunkingService, vector_store: LocalVectorStore) -> None:
        self._chunker = chunker
        self._vector_store = vector_store

    async def ingest_resume(self, upload: UploadFile) -> ResumeIngestResponse:
        """Parse, chunk, and index an uploaded PDF resume."""

        if upload.content_type not in {"application/pdf", "application/octet-stream"}:
            raise AppError("INGESTION_FAILED", "Resume ingestion accepts PDF files only.", status_code=400)
        if not upload.filename or not upload.filename.lower().endswith(".pdf"):
            raise AppError("INGESTION_FAILED", "Uploaded resume must use a .pdf filename.", status_code=400)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_path = Path(temp_file.name)
            while content := await upload.read(1024 * 1024):
                temp_file.write(content)

        try:
            from app.rag.resume_intelligence import ResumeIntelligence
            text = PDFExtractor.extract(temp_path)
            chunks = ResumeIntelligence().parse(text, upload.filename)
            vector_ids = self._vector_store.upsert("resume_collection", chunks)
        finally:
            temp_path.unlink(missing_ok=True)

        return ResumeIngestResponse(
            filename=upload.filename,
            chunks_created=len(vector_ids),
            vector_ids=vector_ids,
        )

    def ingest_github(self, repo_url: str, branch: str) -> GitHubIngestResponse:
        """Clone, filter, chunk, and index a public GitHub repository."""

        repo_name = GitHubCrawler.repo_name(repo_url)
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / repo_name
            GitHubCrawler.clone_repository(repo_url, branch, repo_path)
            chunks: list[DocumentChunk] = []
            files_processed = 0
            for file_path in GitHubCrawler.get_code_files(repo_path):
                relative_path = file_path.relative_to(repo_path).as_posix()
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                file_chunks = self._chunker.chunk_code_file(content, relative_path, repo_url)
                if file_chunks:
                    files_processed += 1
                    chunks.extend(file_chunks)
            self._vector_store.upsert("github_collection", chunks)

        return GitHubIngestResponse(
            repo_name=repo_name,
            files_processed=files_processed,
            chunks_created=len(chunks),
        )

