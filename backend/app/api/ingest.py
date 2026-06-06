"""Admin ingestion API endpoints.

Purpose:
    Expose resume and GitHub ingestion operations to seed the RAG index.
Responsibilities:
    Validate admin access, parse request payloads, and delegate to services.
Dependencies:
    FastAPI UploadFile, ingestion schemas, and IngestionService.
Usage:
    POST /api/v1/ingest/resume with X-Admin-Token and multipart PDF.
"""

from fastapi import APIRouter, Depends, File, UploadFile

from app.core.dependencies import require_admin_token
from app.core.service_factory import get_ingestion_service
from app.schemas.ingest import GitHubIngestRequest, GitHubIngestResponse, ResumeIngestResponse
from app.services.ingestion_service import IngestionService


router = APIRouter(prefix="/ingest", dependencies=[Depends(require_admin_token)])


@router.post("/resume", response_model=ResumeIngestResponse)
async def ingest_resume(
    file: UploadFile = File(...),
    service: IngestionService = Depends(get_ingestion_service),
) -> ResumeIngestResponse:
    """Ingest the candidate resume PDF into the resume collection."""

    return await service.ingest_resume(file)


@router.post("/github", response_model=GitHubIngestResponse)
async def ingest_github(
    payload: GitHubIngestRequest,
    service: IngestionService = Depends(get_ingestion_service),
) -> GitHubIngestResponse:
    """Ingest a public GitHub repository into the GitHub collection."""

    return service.ingest_github(str(payload.repo_url), payload.branch)
