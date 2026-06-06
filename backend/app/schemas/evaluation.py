"""Evaluation API schemas.

Purpose:
    Type requests and responses for automated evaluation trigger endpoints.
Responsibilities:
    Validate suite names and expose aggregate metric summaries.
Dependencies:
    Pydantic v2.
Usage:
    EvaluationRunRequest(test_suite="rag")
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


TestSuite = Literal["rag", "voice", "all"]


class EvaluationRunRequest(BaseModel):
    """Request body for POST /eval/run."""

    test_suite: TestSuite


class EvaluationRunResponse(BaseModel):
    """Evaluation run summary response."""

    timestamp: datetime
    metrics: dict[str, float]
    verdict: Literal["PASS", "FAIL"]
