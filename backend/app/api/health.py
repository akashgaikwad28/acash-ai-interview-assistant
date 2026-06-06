"""Health and metrics API endpoints.

Purpose:
    Support deployment probes and lightweight observability for the backend.
Responsibilities:
    Report service configuration status and expose Prometheus-style metrics.
Dependencies:
    Settings injection, health schemas, and in-memory metrics.
Usage:
    Included by app.main under `/api/v1`.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app.core.config import Settings
from app.core.dependencies import get_app_settings
from app.schemas.health import HealthResponse, ServiceStatus
from app.utils.metrics import render_prometheus_metrics


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_app_settings)) -> HealthResponse:
    """Return service liveness and external integration configuration status."""

    services: dict[str, ServiceStatus] = {
        "chromadb": "connected" if settings.chromadb_host else "unknown",
        "google_calendar_api": "active" if settings.google_calendar_refresh_token else "disabled",
    }
    status = "healthy" if services["chromadb"] == "connected" else "degraded"
    return HealthResponse(
        status=status,
        timestamp=datetime.now(timezone.utc),
        services=services,
    )


@router.get("/metrics", response_class=PlainTextResponse)
async def metrics() -> str:
    """Return Prometheus text metrics gathered by request middleware."""

    return render_prometheus_metrics()
