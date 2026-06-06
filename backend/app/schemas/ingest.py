"""Ingestion request and response schemas.

Purpose:
    Type the admin ingestion APIs for resume PDFs and GitHub repositories.
Responsibilities:
    Validate request payloads and expose chunk/vector metrics.
Dependencies:
    Pydantic v2 URL validation.
Usage:
    GitHubIngestRequest(repo_url="https://github.com/acash/app")
"""

from pydantic import BaseModel, Field, HttpUrl


class ResumeIngestResponse(BaseModel):
    """Response returned after resume PDF ingestion."""

    status: str = "success"
    filename: str
    chunks_created: int
    vector_ids: list[str]


class GitHubIngestRequest(BaseModel):
    """Request body for public GitHub repository ingestion."""

    repo_url: HttpUrl
    branch: str = Field(default="main", min_length=1, max_length=100)


class GitHubIngestResponse(BaseModel):
    """Response returned after repository ingestion."""

    status: str = "success"
    repo_name: str
    files_processed: int
    chunks_created: int
