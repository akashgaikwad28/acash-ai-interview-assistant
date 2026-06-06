"""Scheduling API endpoints.

Purpose:
    Expose recruiter availability lookup and interview booking operations.
Responsibilities:
    Validate date ranges and booking payloads, then delegate to CalendarService.
Dependencies:
    CalendarService and scheduling schemas.
Usage:
    GET /api/v1/availability?start_date=2026-06-08&end_date=2026-06-15
"""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query, Request, status

from app.core.rate_limit import limiter
from app.core.service_factory import get_calendar_service
from app.schemas.schedule import AvailabilityResponse, ScheduleRequest, ScheduleResponse
from app.services.calendar_service import CalendarService


router = APIRouter()


@router.get("/availability", response_model=AvailabilityResponse)
@limiter.limit("40/minute")
async def availability(
    request: Request,
    start_date: date = Query(default_factory=date.today),
    end_date: date | None = None,
    service: CalendarService = Depends(get_calendar_service),
) -> AvailabilityResponse:
    """Return available interview slots for a date range."""

    del request
    return await service.get_availability(start_date, end_date or start_date + timedelta(days=7))


@router.post("/schedule", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def schedule(
    request: Request,
    payload: ScheduleRequest,
    service: CalendarService = Depends(get_calendar_service),
) -> ScheduleResponse:
    """Book an interview slot."""

    del request
    return await service.book_slot(payload)

