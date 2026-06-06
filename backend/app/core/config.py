"""Application settings and environment validation.

Purpose:
    Centralize all environment-driven configuration for the FastAPI backend.
Responsibilities:
    Load `.env` values, normalize CORS origins, and enforce required secrets
    outside local development.
Dependencies:
    pydantic-settings for typed environment parsing.
Usage:
    from app.core.config import get_settings
    settings = get_settings()
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


EnvironmentName = Literal["development", "test", "staging", "production"]


class Settings(BaseSettings):
    """Typed backend configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Acash AI Interview Assistant"
    app_version: str = "1.0.0"
    environment: EnvironmentName = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    frontend_url: str = "http://localhost:3000"
    cors_origins: str | list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    secret_key: str = "dev-secret-key"
    admin_token: str = "dev-admin-token"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "gemini-embedding-2"

    chromadb_host: str = "localhost"
    chromadb_port: int = 8001

    google_calendar_id: str | None = None
    google_calendar_client_id: str | None = None
    google_calendar_client_secret: str | None = None
    google_calendar_refresh_token: str | None = None
    google_calendar_timezone: str = "America/New_York"

    vapi_api_key: str | None = None
    vapi_secret_token: str | None = None

    mongodb_uri: str = "mongodb://localhost:27017"
    log_level: str = "INFO"

    @field_validator("api_v1_prefix")
    @classmethod
    def normalize_prefix(cls, value: str) -> str:
        """Ensure route prefixes use a leading slash and no trailing slash."""

        normalized = value.strip()
        if not normalized.startswith("/"):
            normalized = f"/{normalized}"
        return normalized.rstrip("/")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        """Parse comma-separated CORS origins from environment variables."""

        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        """Require external-service credentials in production-like environments."""

        if self.environment in {"staging", "production"}:
            required = {
                "secret_key": self.secret_key,
                "admin_token": self.admin_token,
                "gemini_api_key": self.gemini_api_key,
                "google_calendar_id": self.google_calendar_id,
                "google_calendar_client_id": self.google_calendar_client_id,
                "google_calendar_client_secret": self.google_calendar_client_secret,
                "google_calendar_refresh_token": self.google_calendar_refresh_token,
            }
            missing = [name for name, value in required.items() if not value or value.startswith("dev-")]
            if missing:
                joined = ", ".join(sorted(missing))
                raise ValueError(f"Missing required production settings: {joined}")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings for dependency injection."""

    return Settings()


settings = get_settings()
