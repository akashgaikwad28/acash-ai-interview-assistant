"""Unit tests for calendar bookings and conflict detection."""

from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import create_app
from app.models.database_models import BookedInterview


def test_calendar_booking_flow_and_conflict_detection() -> None:
    client = TestClient(create_app())
    start = datetime.now(timezone.utc) + timedelta(days=4)
    start = start.replace(hour=10, minute=0, second=0, microsecond=0)
    end = start + timedelta(minutes=30)

    # 1. Book a slot
    response = client.post(
        "/api/v1/schedule",
        json={
            "recruiter_name": "Rachel",
            "recruiter_email": "rachel@example.com",
            "company": "Google",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "scheduled"
    assert "event_id" in payload

    # 2. Try to book the same slot (should return 409 Conflict)
    conflict_response = client.post(
        "/api/v1/schedule",
        json={
            "recruiter_name": "Thomas",
            "recruiter_email": "thomas@example.com",
            "company": "Amazon",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
        },
    )
    assert conflict_response.status_code == 409

    # 3. Verify SQLite DB row entry exists
    import asyncio
    from app.core.database import AsyncSessionLocal
    
    async def verify_db():
        async with AsyncSessionLocal() as session:
            stmt = select(BookedInterview).where(BookedInterview.recruiter_name == "Rachel")
            res = await session.execute(stmt)
            booking = res.scalar_one_or_none()
            assert booking is not None
            assert booking.recruiter_email == "rachel@example.com"
            assert booking.company_name == "Google"

    asyncio.run(verify_db())
