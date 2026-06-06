"""Evaluation API endpoint.

Purpose:
    Trigger automated RAG/voice evaluation runs for submission reporting.
Responsibilities:
    Validate admin access and return aggregate evaluation metrics.
Dependencies:
    EvaluationService and admin-token dependency.
Usage:
    POST /api/v1/eval/run with X-Admin-Token.
"""

from fastapi import APIRouter, Depends

from app.core.dependencies import require_admin_token
from app.core.service_factory import get_evaluation_service
from app.schemas.evaluation import EvaluationRunRequest, EvaluationRunResponse
from app.services.evaluation_service import EvaluationService


router = APIRouter(prefix="/eval", dependencies=[Depends(require_admin_token)])


@router.post("/run", response_model=EvaluationRunResponse)
async def run_evaluation(
    payload: EvaluationRunRequest,
    service: EvaluationService = Depends(get_evaluation_service),
) -> EvaluationRunResponse:
    """Run the requested evaluation suite."""

    return await service.run(payload.test_suite)

