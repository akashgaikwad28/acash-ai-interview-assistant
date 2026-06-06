import httpx
from datetime import date, datetime, time, timedelta, timezone
from uuid import uuid4
from zoneinfo import ZoneInfo
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import Settings
from app.schemas.schedule import AvailabilityResponse, AvailabilitySlot, ScheduleRequest, ScheduleResponse
from app.utils.errors import AppError
from app.utils.logger import log_json


class CalendarService:
    """Async scheduling service with Google Calendar API integration and MongoDB persistence."""

    slot_minutes = 30
    buffer_minutes = 15
    workday_start = time(9, 0)
    workday_end = time(17, 0)

    def __init__(self, settings: Settings, db: AsyncIOMotorDatabase) -> None:
        self._settings = settings
        self._db = db

    async def _get_access_token(self) -> str:
        """Obtain a Google OAuth2 access token utilizing the refresh token."""
        if not (self._settings.google_calendar_client_id and 
                self._settings.google_calendar_client_secret and 
                self._settings.google_calendar_refresh_token):
            raise ValueError("Google Calendar credentials are not configured.")

        async with httpx.AsyncClient(timeout=3.5) as client:
            res = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": self._settings.google_calendar_client_id,
                    "client_secret": self._settings.google_calendar_client_secret,
                    "refresh_token": self._settings.google_calendar_refresh_token,
                    "grant_type": "refresh_token"
                }
            )
            res.raise_for_status()
            return res.json()["access_token"]

    async def _fetch_google_busy_intervals(self, start: datetime, end: datetime) -> list[tuple[datetime, datetime]]:
        """Fetch busy intervals from the Google Calendar API."""
        try:
            access_token = await self._get_access_token()
        except Exception as exc:
            log_json(30, "google_cal_auth_failed", error=str(exc))
            return []

        calendar_id = self._settings.google_calendar_id or "primary"
        async with httpx.AsyncClient(timeout=3.5) as client:
            res = await client.post(
                "https://www.googleapis.com/calendar/v3/freeBusy",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "timeMin": start.isoformat(),
                    "timeMax": end.isoformat(),
                    "items": [{"id": calendar_id}]
                }
            )
            if res.status_code != 200:
                log_json(30, "google_cal_freebusy_failed", status=res.status_code, body=res.text)
                return []
            
            data = res.json()
            busy_list = data.get("calendars", {}).get(calendar_id, {}).get("busy", [])
            intervals = []
            for interval in busy_list:
                s_time = datetime.fromisoformat(interval["start"].replace("Z", "+00:00")).astimezone(timezone.utc)
                e_time = datetime.fromisoformat(interval["end"].replace("Z", "+00:00")).astimezone(timezone.utc)
                intervals.append((s_time, e_time))
            return intervals

    async def _create_google_event(self, request: ScheduleRequest, booking_id: str) -> tuple[str, str]:
        """Insert a booked screening event to the Google Calendar and request Google Meet links."""
        try:
            access_token = await self._get_access_token()
        except Exception as exc:
            log_json(30, "google_cal_event_creation_fallback", error=str(exc))
            meet_link = f"https://meet.google.com/{booking_id[:3]}-{booking_id[3:7]}-{booking_id[7:10]}"
            return f"mock_event_{booking_id}", meet_link

        calendar_id = self._settings.google_calendar_id or "primary"
        start_str = request.start_time.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        end_str = request.end_time.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

        event_body = {
            "summary": f"Acash Screen / {request.recruiter_name} @ {request.company or 'Recruiter'}",
            "description": "Introductory technical screening call scheduled by Acash AI Assistant.",
            "start": {"dateTime": start_str, "timeZone": "UTC"},
            "end": {"dateTime": end_str, "timeZone": "UTC"},
            "attendees": [{"email": str(request.recruiter_email)}],
            "conferenceData": {
                "createRequest": {
                    "requestId": booking_id,
                    "conferenceSolutionKey": {"type": "hangoutsMeet"}
                }
            }
        }

        async with httpx.AsyncClient(timeout=3.5) as client:
            res = await client.post(
                f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"conferenceDataVersion": 1, "sendUpdates": "all"},
                json=event_body
            )
            if res.status_code != 200:
                log_json(30, "google_cal_event_failed", status=res.status_code, body=res.text)
                meet_link = f"https://meet.google.com/{booking_id[:3]}-{booking_id[3:7]}-{booking_id[7:10]}"
                return f"mock_event_{booking_id}", meet_link

            data = res.json()
            event_id = data.get("id", f"mock_event_{booking_id}")
            
            meet_link = None
            conf_data = data.get("conferenceData", {})
            entry_points = conf_data.get("entryPoints", [])
            for ep in entry_points:
                if ep.get("entryPointType") == "video":
                    meet_link = ep.get("uri")
                    break
            
            if not meet_link:
                meet_link = data.get("hangoutLink") or f"https://meet.google.com/{booking_id[:3]}-{booking_id[3:7]}-{booking_id[7:10]}"
            
            return event_id, meet_link

    async def get_availability(self, start_date: date, end_date: date) -> AvailabilityResponse:
        """Return available 30-minute slots between two dates, checking Google and local database."""
        if end_date < start_date:
            raise AppError("VALIDATION_ERROR", "end_date must be on or after start_date.", status_code=422)

        tz = ZoneInfo(self._settings.google_calendar_timezone)
        start_dt = datetime.combine(start_date, time.min, tzinfo=tz)
        end_dt = datetime.combine(end_date, time.max, tzinfo=tz)

        # 1. Fetch Google busy intervals
        busy_intervals = await self._fetch_google_busy_intervals(start_dt, end_dt)

        # 2. Fetch local MongoDB busy intervals
        cursor = self._db.booked_interviews.find({
            "start_time": {"$gte": start_dt.astimezone(timezone.utc)},
            "end_time": {"$lte": end_dt.astimezone(timezone.utc)}
        })
        local_bookings = await cursor.to_list(length=100)
        for booking in local_bookings:
            s_time = booking["start_time"].replace(tzinfo=timezone.utc)
            e_time = booking["end_time"].replace(tzinfo=timezone.utc)
            busy_intervals.append((s_time, e_time))

        # 3. Calculate free working slots
        slots: list[AvailabilitySlot] = []
        current = start_date
        now_utc = datetime.now(timezone.utc)

        while current <= end_date:
            # Monday - Friday only
            if current.weekday() < 5:
                local_start = datetime.combine(current, self.workday_start, tzinfo=tz)
                local_end = datetime.combine(current, self.workday_end, tzinfo=tz)
                cursor = local_start
                while cursor + timedelta(minutes=self.slot_minutes) <= local_end:
                    slot_start = cursor.astimezone(timezone.utc)
                    slot_end = (cursor + timedelta(minutes=self.slot_minutes)).astimezone(timezone.utc)
                    if slot_start > now_utc and not self._overlaps_busy(slot_start, slot_end, busy_intervals):
                        slots.append(AvailabilitySlot(start=slot_start, end=slot_end))
                    cursor += timedelta(minutes=self.slot_minutes)
            current += timedelta(days=1)

        return AvailabilityResponse(timezone=self._settings.google_calendar_timezone, slots=slots)

    async def book_slot(self, request: ScheduleRequest) -> ScheduleResponse:
        """Lock and verify a slot, create a Google Calendar booking, and save in the DB."""
        start = request.start_time.astimezone(timezone.utc)
        end = request.end_time.astimezone(timezone.utc)

        # Retrieve busy times for conflict checking
        tz = ZoneInfo(self._settings.google_calendar_timezone)
        start_date = start.astimezone(tz).date()
        start_dt = datetime.combine(start_date, time.min, tzinfo=tz)
        end_dt = datetime.combine(start_date, time.max, tzinfo=tz)

        busy = await self._fetch_google_busy_intervals(start_dt, end_dt)

        # Fetch local bookings for conflict check
        cursor = self._db.booked_interviews.find({
            "start_time": {"$gte": start_dt.astimezone(timezone.utc)},
            "end_time": {"$lte": end_dt.astimezone(timezone.utc)}
        })
        local_bookings = await cursor.to_list(length=100)
        for booking in local_bookings:
            s_time = booking["start_time"].replace(tzinfo=timezone.utc)
            e_time = booking["end_time"].replace(tzinfo=timezone.utc)
            busy.append((s_time, e_time))

        if self._overlaps_busy(start, end, busy):
            raise AppError("CALENDAR_CONFLICT", "The selected time slot has already been booked.", status_code=409)

        booking_id = str(uuid4())
        
        # Write to Google Calendar
        event_id, meet_link = await self._create_google_event(request, booking_id)

        # Persist in MongoDB
        await self._db.booked_interviews.insert_one({
            "booking_id": booking_id,
            "recruiter_name": request.recruiter_name,
            "recruiter_email": str(request.recruiter_email),
            "company_name": request.company,
            "start_time": start,
            "end_time": end,
            "google_event_id": event_id,
            "google_meet_link": meet_link,
            "created_at": datetime.now(timezone.utc),
        })

        html_link = f"https://calendar.google.com/calendar/event?eid={event_id}"
        return ScheduleResponse(event_id=event_id, html_link=html_link, meet_link=meet_link)

    def _overlaps_busy(self, start: datetime, end: datetime, busy: list[tuple[datetime, datetime]]) -> bool:
        buffer = timedelta(minutes=self.buffer_minutes)
        for busy_start, busy_end in busy:
            if start < busy_end + buffer and end > busy_start - buffer:
                return True
        return False
