"""FastAPI application bootstrap.

Purpose:
    Create the Acash AI Interview Assistant backend application.
Responsibilities:
    Configure settings, CORS, rate limiting, middleware, exception handlers,
    and versioned API routers.
Dependencies:
    FastAPI, pydantic-settings, slowapi, and local API modules.
Usage:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from app.api import chat, evaluation, health, ingest, schedule, voice
from app.core.database import init_db
from app.core.config import Settings, get_settings
from app.core.rate_limit import limiter
from app.utils.errors import register_exception_handlers
from app.utils.logger import configure_logging, log_json, logging_middleware
from app.utils.metrics import metrics_middleware


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Manage app startup and shutdown lifecycle events."""

    settings = get_settings()
    log_json(
        20,
        "app_startup",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )
    await init_db()

    # Auto-ingest resumes from the "resume" folder at the root of the workspace
    from pathlib import Path
    # In Docker: /app/app/main.py → parents[1] = /app (the backend root)
    # Locally: backend/app/main.py → parents[1] = backend/
    backend_root = Path(__file__).resolve().parents[1]
    resume_dir = backend_root / "assets" / "resume"
    if resume_dir.exists() and resume_dir.is_dir():
        from app.services.chunking_service import ChunkingService
        from app.services.embedding_service import EmbeddingService
        from app.services.vector_store import LocalVectorStore
        from app.rag.ingester import PDFExtractor
        from app.rag.resume_intelligence import ResumeIntelligence
        
        parser = ResumeIntelligence()
        embedder = EmbeddingService(settings)
        store = LocalVectorStore(settings, embedder)
        
        for path in resume_dir.glob("*.pdf"):
            try:
                log_json(20, "auto_ingesting_resume", file=path.name)
                text = PDFExtractor.extract(path)
                chunks = parser.parse(text, path.name)
                if chunks:
                    store.upsert("resume_collection", chunks)
                log_json(20, "auto_ingestion_success", file=path.name, chunks=len(chunks))
            except Exception as e:
                log_json(30, "auto_ingestion_failed", file=path.name, error=str(e))

    yield
    log_json(20, "app_shutdown")



def create_app(settings: Settings | None = None) -> FastAPI:
    """Application factory used by Uvicorn and tests."""

    pass

    active_settings = settings or get_settings()
    configure_logging(active_settings.log_level)

    app = FastAPI(
        title=active_settings.app_name,
        version=active_settings.app_version,
        debug=active_settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )


    app.state.settings = active_settings
    app.state.limiter = limiter

    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.middleware("http")(metrics_middleware)
    app.middleware("http")(logging_middleware)

    register_exception_handlers(app)

    app.include_router(health.router, prefix=active_settings.api_v1_prefix, tags=["Health"])
    app.include_router(chat.router, prefix=active_settings.api_v1_prefix, tags=["Chat"])
    app.include_router(schedule.router, prefix=active_settings.api_v1_prefix, tags=["Schedule"])
    app.include_router(ingest.router, prefix=active_settings.api_v1_prefix, tags=["Ingestion"])
    app.include_router(voice.router, prefix=active_settings.api_v1_prefix, tags=["Voice"])
    app.include_router(evaluation.router, prefix=active_settings.api_v1_prefix, tags=["Evaluation"])
    return app


app = create_app()
# Trigger reload 2
# Trigger reload 3
