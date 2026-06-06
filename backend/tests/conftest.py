"""Pytest configuration and shared fixtures."""

import asyncio
import pytest
from sqlalchemy import text
from app.core.database import engine

@pytest.fixture(autouse=True)
def clean_database() -> None:
    """Clean all tables in the database before each test to prevent cross-test contamination."""
    
    async def _clean():
        async with engine.begin() as conn:
            # We wrap table names in quotes and execute standard SQLite drop-row operations
            await conn.execute(text("DELETE FROM booked_interviews;"))
            await conn.execute(text("DELETE FROM chat_messages;"))
            await conn.execute(text("DELETE FROM conversation_sessions;"))
            await conn.execute(text("DELETE FROM evaluation_metrics;"))
            await conn.execute(text("DELETE FROM evaluation_runs;"))
            
    try:
        asyncio.run(_clean())
    except Exception:
        # Fallback for environments where a loop is already running
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_clean())
        else:
            loop.run_until_complete(_clean())
