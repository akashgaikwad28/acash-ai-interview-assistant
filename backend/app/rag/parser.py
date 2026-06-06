"""Text and code chunk splitting parser for the RAG engine.

Purpose:
    Implement recursive splitting, syntactical code segmentation, and metadata wrapping.
"""

from hashlib import sha1
from typing import Callable

from app.schemas.rag import ChunkMetadata, DocumentChunk, RetrievedChunk


class RAGParser:
    """Document and codebase chunk parsing splitter engine."""

    resume_chunk_size = 500
    resume_overlap = 50
    code_chunk_size = 1000
    code_overlap = 100

    def chunk_resume(self, text: str, source_name: str) -> list[DocumentChunk]:
        """Split resume text into 500-character chunks with 50-character overlap."""
        return self._chunk_text(
            text=text,
            chunk_size=self.resume_chunk_size,
            overlap=self.resume_overlap,
            metadata_factory=lambda idx, chunk_text: ChunkMetadata(
                source_type="resume",
                source_name=source_name,
                file_path=source_name,
                section=self._infer_resume_section(text),
                chunk_index=idx,
            ),
        )

    def chunk_code_file(self, text: str, file_path: str, repo_url: str) -> list[DocumentChunk]:
        """Split code files into 1000-character chunks with 100-character overlap."""
        normalized = self._prefer_code_boundaries(text)
        source_name = file_path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        return self._chunk_text(
            text=normalized,
            chunk_size=self.code_chunk_size,
            overlap=self.code_overlap,
            metadata_factory=lambda idx, chunk_text: ChunkMetadata(
                source_type="github",
                source_name=source_name,
                file_path=file_path,
                repo_url=repo_url,
                chunk_index=idx,
            ),
        )

    def _chunk_text(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
        metadata_factory: Callable[[int, str], ChunkMetadata],
    ) -> list[DocumentChunk]:
        cleaned = "\n".join(line.rstrip() for line in text.splitlines()).strip()
        if not cleaned:
            return []

        chunks: list[DocumentChunk] = []
        start = 0
        while start < len(cleaned):
            end = min(start + chunk_size, len(cleaned))
            if end < len(cleaned):
                boundary = max(
                    cleaned.rfind("\n\n", start, end),
                    cleaned.rfind("\n", start, end),
                    cleaned.rfind(". ", start, end),
                    cleaned.rfind("? ", start, end),
                )
                if boundary > start + chunk_size // 2:
                    end = boundary + 1
            chunk_text = cleaned[start:end].strip()
            if chunk_text:
                metadata = metadata_factory(len(chunks), chunk_text)
                chunk_id = sha1(
                    f"{metadata.source_type}:{metadata.file_path or metadata.source_name}:{metadata.chunk_index}:{chunk_text}".encode("utf-8")
                ).hexdigest()
                chunks.append(DocumentChunk(id=chunk_id, text=chunk_text, metadata=metadata))
            if end >= len(cleaned):
                break
            start = max(end - overlap, start + 1)
        return chunks

    def _prefer_code_boundaries(self, text: str) -> str:
        """Add paragraph spaces around class, function, and interface signatures."""
        markers = ("class ", "def ", "function ", "export ", "const ", "interface ")
        lines: list[str] = []
        for line in text.splitlines():
            stripped = line.lstrip()
            if stripped.startswith(markers) and lines and lines[-1] != "":
                lines.append("")
            lines.append(line)
        return "\n".join(lines)

    def _infer_resume_section(self, text: str) -> str | None:
        """Infer which section of the resume a page or snippet relates to."""
        lowered = text[:1000].lower()
        for section in ("education", "experience", "projects", "skills", "certifications"):
            if section in lowered:
                return section
        return None

    def format_context_block(self, contexts: list[RetrievedChunk]) -> str:
        """Format retrieved chunks into context payload strings for injection."""
        return "\n\n".join(
            f"Source: {match.chunk.metadata.file_path or match.chunk.metadata.source_name}\nContent: {match.chunk.text}"
            for match in contexts
        )
