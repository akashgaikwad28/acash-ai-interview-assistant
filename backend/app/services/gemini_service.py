"""Gemini text-generation service.

Purpose:
    Call Gemini 2.5 Flash for grounded answer generation.
Responsibilities:
    Use google-genai when configured and provide a deterministic local fallback
    for tests and offline development.
Dependencies:
    Optional google-genai SDK and retrieved RAG contexts.
Usage:
    answer = GeminiService(settings).generate_grounded_answer(prompt, contexts, query)
"""

from app.core.config import Settings
from app.schemas.rag import RetrievedChunk
from app.utils.logger import log_json


class GeminiService:
    """Gemini 2.5 Flash adapter with an offline grounded fallback."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = None

    def generate_grounded_answer(
        self,
        prompt: str,
        contexts: list[RetrievedChunk],
        user_query: str,
    ) -> str:
        """Generate an answer grounded in retrieved contexts."""

        if not contexts:
            return "I don't have that information in my database."

        if self._settings.gemini_api_key:
            try:
                return self._generate_with_gemini(prompt)
            except Exception as exc:  # pragma: no cover - external API safety net
                log_json(30, "gemini_generation_fallback", error=repr(exc))

        return self._generate_local_answer(contexts, user_query)

    def _generate_with_gemini(self, prompt: str) -> str:
        """Call Gemini via google-genai."""

        from google import genai  # type: ignore

        if self._client is None:
            self._client = genai.Client(api_key=self._settings.gemini_api_key)
        response = self._client.models.generate_content(
            model=self._settings.gemini_model,
            contents=prompt,
        )
        return str(response.text or "").strip() or "I don't have that information in my database."

    def _generate_local_answer(self, contexts: list[RetrievedChunk], user_query: str) -> str:
        """Compose a concise extractive answer from retrieved structured chunks."""

        # 1. Filter contexts to prioritize actual resume chunks or READMEs
        target_contexts = []
        for c in contexts:
            source_type = c.chunk.metadata.source_type if hasattr(c.chunk.metadata, "source_type") else ""
            source_name = c.chunk.metadata.source_name if hasattr(c.chunk.metadata, "source_name") else ""
            if type(c.chunk.metadata) is dict:
                source_type = c.chunk.metadata.get("source_type", "")
                source_name = c.chunk.metadata.get("source_name", "")
                
            if source_type == "resume" or (source_name and "readme" in source_name.lower()):
                target_contexts.append(c)
                
        if not target_contexts:
            target_contexts = contexts[:3]

        # 2. Extract and concatenate the top 2 most relevant chunks
        selected_texts = []
        seen = set()
        
        for match in target_contexts[:2]:
            text = match.chunk.text.strip()
            # Clean up the SECTION: markers from the smart parser
            if text.startswith("SECTION:"):
                text = text.split("\n", 1)[-1].strip()
            elif text.startswith("PROJECT:"):
                text = text.replace("PROJECT:", "My project").strip()
            elif text.startswith("WORK EXPERIENCE:"):
                text = text.replace("WORK EXPERIENCE:\n", "").strip()
            elif text.startswith("CANDIDATE PROFILE SUMMARY:"):
                text = text.replace("CANDIDATE PROFILE SUMMARY:\n", "").strip()
                
            # De-duplication
            normalized = text.lower()[:50]
            if normalized in seen:
                continue
            seen.add(normalized)
            
            selected_texts.append(text)
            
        if not selected_texts:
            return "I don't have that information in my database."
            
        combined = "\n\n".join(selected_texts)
        return f"Based on my verified background:\n\n{combined}"

    def _sentences(self, text: str) -> list[str]:
        normalized = text.replace("\n", " ")
        sentences: list[str] = []
        start = 0
        for index, char in enumerate(normalized):
            if char in ".?!":
                sentences.append(normalized[start : index + 1].strip())
                start = index + 1
        tail = normalized[start:].strip()
        if tail:
            sentences.append(tail)
        return sentences

    def _source_label(self, match: RetrievedChunk) -> str:
        metadata = match.chunk.metadata
        return metadata.file_path or metadata.source_name
