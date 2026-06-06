"""Grounded chat agent orchestration.

Purpose:
    Coordinate retrieval, prompt construction, generation, and citations.
Responsibilities:
    Implement the documented Retrieve -> Generate flow for POST /chat.
Dependencies:
    RAGService, GeminiService, and prompt builders.
Usage:
    result = ChatAgent(rag, gemini).run("Tell me about FastAPI")
"""

from dataclasses import dataclass

from app.agents.prompts import build_chat_prompt
from app.schemas.rag import Citation
from app.services.gemini_service import GeminiService
from app.services.rag_service import RAGService


@dataclass(frozen=True)
class ChatAgentResult:
    """Output of a grounded chat agent run."""

    response: str
    citations: list[Citation]


class ChatAgent:
    """RAG chat agent using the documented retrieve-then-generate flow."""

    def __init__(self, rag_service: RAGService, gemini_service: GeminiService) -> None:
        self._rag_service = rag_service
        self._gemini_service = gemini_service

    def run(self, message: str, history: list = None) -> ChatAgentResult:
        """Execute retrieval and grounded generation for one user message."""

        retrieval = self._rag_service.retrieve(message)
        contexts_data = self._format_contexts(retrieval.contexts)
        prompt = build_chat_prompt(contexts_data, message, history)
        response = self._gemini_service.generate_grounded_answer(prompt, retrieval.contexts, message)
        return ChatAgentResult(response=response, citations=retrieval.citations)


    def _format_contexts(self, contexts) -> str:
        return "\n\n".join(
            f"Source: {match.chunk.metadata.file_path or match.chunk.metadata.source_name}\nContent: {match.chunk.text}"
            for match in contexts
        )
