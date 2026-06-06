"""Service factory helpers for dependency injection.

Purpose:
    Build service-layer objects from shared settings without coupling routers
    to constructors.
Responsibilities:
    Create chunking, embedding, vector store, ingestion, and retrieval services.
Dependencies:
    Settings and service classes.
Usage:
    Depends(get_ingestion_service)
"""

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import Settings
from app.core.database import get_db
from app.core.dependencies import get_app_settings
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.ingestion_service import IngestionService
from app.services.rag_service import RAGService
from app.services.vector_store import LocalVectorStore
from app.services.gemini_service import GeminiService
from app.agents.chat_agent import ChatAgent
from app.services.calendar_service import CalendarService
from app.services.evaluation_service import EvaluationService


def get_vector_store(settings: Settings = Depends(get_app_settings)) -> LocalVectorStore:
    """Create a vector store with the configured embedding provider."""

    embedder = EmbeddingService(settings)
    return LocalVectorStore(settings, embedder)


def get_ingestion_service(vector_store: LocalVectorStore = Depends(get_vector_store)) -> IngestionService:
    """Create the ingestion service dependency."""

    return IngestionService(ChunkingService(), vector_store)


def get_rag_service(vector_store: LocalVectorStore = Depends(get_vector_store)) -> RAGService:
    """Create the retrieval service dependency."""

    return RAGService(vector_store)


def get_chat_agent(
    settings: Settings = Depends(get_app_settings),
    rag_service: RAGService = Depends(get_rag_service),
) -> ChatAgent:
    """Create the grounded chat agent dependency."""

    return ChatAgent(rag_service, GeminiService(settings))


def get_calendar_service(
    settings: Settings = Depends(get_app_settings),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> CalendarService:
    """Create the calendar service dependency."""

    return CalendarService(settings, db)


def get_evaluation_service(
    rag_service: RAGService = Depends(get_rag_service),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> EvaluationService:
    """Create the evaluation service dependency."""

    return EvaluationService(rag_service, db)
