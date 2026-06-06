"""RAG retrieval service.

Purpose:
    Query indexed resume and GitHub chunks and prepare context/citation payloads.
Responsibilities:
    Select collections, apply similarity thresholds, and format source snippets.
Dependencies:
    LocalVectorStore and RAG schemas.
Usage:
    result = rag_service.retrieve("What FastAPI projects has Acash built?")
"""

from app.schemas.rag import Citation, RetrievalResult
from app.services.vector_store import LocalVectorStore


class RAGService:
    """Retrieval facade for candidate resume and repository knowledge."""

    def __init__(self, vector_store: LocalVectorStore) -> None:
        self._vector_store = vector_store

    def retrieve(self, query: str) -> RetrievalResult:
        """Retrieve relevant chunks from resume and GitHub collections."""

        collections = self._select_collections(query)
        contexts = self._vector_store.query(collections, query, top_k=5, min_score=0.40)
        citations = [
            Citation(
                source=self._citation_source(match),
                text_snippet=match.chunk.text[:200],
                score=round(match.score, 4),
            )
            for match in contexts
        ]
        return RetrievalResult(contexts=contexts, citations=citations)

    def _select_collections(self, query: str) -> list[str]:
        lowered = query.lower()
        github_markers = ("repo", "github", "code", "file", ".py", ".ts", ".tsx", "component", "api")
        if any(marker in lowered for marker in github_markers):
            return ["github_collection", "resume_collection"]
        return ["resume_collection", "github_collection"]

    def _citation_source(self, match) -> str:
        metadata = match.chunk.metadata
        if metadata.source_type == "github" and metadata.file_path:
            return f"repo:{metadata.file_path}"
        return metadata.source_name
