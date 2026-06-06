"""Health and metrics response schemas.

Purpose:
    Type the health probe payload consumed by deployments and frontend checks.
Responsibilities:
    Expose service status and timestamp in a stable API shape.
Dependencies:
    Pydantic v2 models.
Usage:
    HealthResponse(status="healthy", timestamp=..., services={...})
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


ServiceStatus = Literal["connected", "active", "degraded", "disabled", "unknown"]


class HealthResponse(BaseModel):
    """Health endpoint response matching the documented contract."""

    status: Literal["healthy", "degraded"]
    timestamp: datetime
    services: dict[str, ServiceStatus]
