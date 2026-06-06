"""MongoDB document models.

Purpose:
    Expose Pydantic document schemas for sessions, bookings, and metrics.
Responsibilities:
    Define document shapes for conversation_sessions, chat_messages,
    booked_interviews, evaluation_runs, and evaluation_metrics collections.
Dependencies:
    Pydantic BaseModel.
Usage:
    from app.models.database_models import ChatMessageDoc
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConversationSessionDoc(BaseModel):
    """Conversation session metadata tracking."""

    session_id: str
    client_ip: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChatMessageDoc(BaseModel):
    """Single message within a recruiter-assistant session."""

    session_id: str
    sender_role: str
    text_content: str
    citations_json: str = "[]"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BookedInterviewDoc(BaseModel):
    """Google Calendar meeting slot reservation entry."""

    booking_id: str
    recruiter_name: str
    recruiter_email: str
    company_name: Optional[str] = None
    start_time: datetime
    end_time: datetime
    google_event_id: Optional[str] = None
    google_meet_link: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EvaluationRunDoc(BaseModel):
    """Grounded QA offline quality run history log."""

    run_id: str
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    test_suite_name: str
    avg_faithfulness: float
    avg_relevance: float
    verdict: str


class EvaluationMetricDoc(BaseModel):
    """Detailed score measurements for queries inside an evaluation run."""

    run_id: str
    test_query: str
    generated_response: str
    faithfulness_score: Optional[float] = None
    relevance_score: Optional[float] = None
