"""Scheduling API schemas.

Purpose:
    Type availability and booking contracts for recruiter interview scheduling.
Responsibilities:
    Validate ISO datetimes, recruiter details, and Google Calendar-like responses.
Dependencies:
    Pydantic v2.
Usage:
    ScheduleRequest(recruiter_name="Rachel", recruiter_email="rachel@example.com", ...)
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, HttpUrl, model_validator


class AvailabilitySlot(BaseModel):
    """One available interview slot."""

    start: datetime
    end: datetime


class AvailabilityResponse(BaseModel):
    """Response for GET /availability."""

    timezone: str
    slots: list[AvailabilitySlot]


class ScheduleRequest(BaseModel):
    """Request for POST /schedule."""

    recruiter_name: str = Field(..., min_length=2, max_length=100)
    recruiter_email: EmailStr
    company: str | None = Field(default=None, max_length=100)
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def validate_time_order(self) -> "ScheduleRequest":
        """Ensure the booking end comes after the start."""

        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class ScheduleResponse(BaseModel):
    """Response for a successful scheduled interview."""

    status: Literal["scheduled"] = "scheduled"
    event_id: str
    html_link: HttpUrl | str
    meet_link: HttpUrl | str
