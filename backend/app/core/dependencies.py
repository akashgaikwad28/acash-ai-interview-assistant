"""FastAPI dependency helpers.

Purpose:
    Keep API routers thin by centralizing shared dependency checks.
Responsibilities:
    Provide settings injection and reusable admin-token validation.
Dependencies:
    FastAPI Header dependencies and Settings.
Usage:
    Depends(require_admin_token)
"""

from typing import Annotated

from fastapi import Header, HTTPException, status

from app.core.config import Settings, get_settings


def get_app_settings() -> Settings:
    """Return settings for route-level dependency injection."""

    return get_settings()


async def require_admin_token(
    x_admin_token: Annotated[str | None, Header(alias="X-Admin-Token")] = None,
) -> None:
    """Validate the configured admin token for privileged endpoints."""

    settings = get_settings()
    if not x_admin_token or x_admin_token != settings.admin_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin token is missing or invalid.",
        )
