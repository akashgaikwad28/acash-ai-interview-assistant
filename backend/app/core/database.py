"""Database connection and collection management.

Purpose:
    Provide async MongoDB connections via motor for the FastAPI backend.
Responsibilities:
    Initialize motor client, expose get_db database generator, and
    ensure required indexes exist on startup.
Dependencies:
    motor, pymongo, and config settings.
Usage:
    db = Depends(get_db)
"""

from collections.abc import AsyncIterator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo

from app.core.config import get_settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None

DB_NAME = "acash_interview_assistant"


def _get_client_and_db() -> tuple[AsyncIOMotorClient, AsyncIOMotorDatabase]:
    """Lazily initialize the motor client and database."""
    global _client, _db
    if _client is None or _db is None:
        import certifi
        settings = get_settings()
        _client = AsyncIOMotorClient(settings.mongodb_uri, tlsCAFile=certifi.where())
        _db = _client[DB_NAME]
    return _client, _db


async def get_db() -> AsyncIterator[AsyncIOMotorDatabase]:
    """Yield the MongoDB database instance to API routes."""
    _, db = _get_client_and_db()
    yield db


async def init_db() -> None:
    """Ensure required indexes exist on MongoDB collections."""
    _, db = _get_client_and_db()

    await db.chat_messages.create_index(
        [("session_id", pymongo.ASCENDING)],
        name="idx_chat_messages_session_id",
    )
    await db.chat_messages.create_index(
        [("created_at", pymongo.ASCENDING)],
        name="idx_chat_messages_created_at",
    )
    await db.booked_interviews.create_index(
        [("start_time", pymongo.ASCENDING)],
        name="idx_booked_interviews_start_time",
    )
    await db.booked_interviews.create_index(
        [("end_time", pymongo.ASCENDING)],
        name="idx_booked_interviews_end_time",
    )
    await db.booked_interviews.create_index(
        [("google_event_id", pymongo.ASCENDING)],
        name="idx_booked_interviews_event_id",
        unique=True,
        sparse=True,
    )
    await db.evaluation_metrics.create_index(
        [("run_id", pymongo.ASCENDING)],
        name="idx_evaluation_metrics_run_id",
    )
    await db.conversation_sessions.create_index(
        [("session_id", pymongo.ASCENDING)],
        name="idx_conversation_sessions_session_id",
        unique=True,
    )
