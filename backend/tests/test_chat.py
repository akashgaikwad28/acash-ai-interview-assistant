"""Unit tests for chat session memory and DB persistence."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import create_app
from app.core.database import engine

from app.models.database_models import ChatMessage, ConversationSession


def test_chat_saves_history_in_database() -> None:
    client = TestClient(create_app())
    session_id = "12345678-1234-5678-1234-567812345678"

    # Send first message
    response = client.post(
        "/api/v1/chat",
        json={"message": "Do you know Python?", "session_id": session_id},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == session_id

    # Send second message
    response = client.post(
        "/api/v1/chat",
        json={"message": "Do you know FastAPI?", "session_id": session_id},
    )
    assert response.status_code == 200

    # Verify that the session and all 4 messages (2 user, 2 assistant) exist in the SQLite database
    # Since tests run synchronously, we can query SQLite using a temporary async loop
    import asyncio
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.core.database import AsyncSessionLocal
    
    async def verify_db():
        async with AsyncSessionLocal() as session:
            # Query sessions
            stmt_sessions = select(ConversationSession).where(ConversationSession.session_id == session_id)
            res_sessions = await session.execute(stmt_sessions)
            sess = res_sessions.scalar_one_or_none()
            assert sess is not None

            # Query messages
            stmt_messages = select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc())
            res_messages = await session.execute(stmt_messages)
            messages = res_messages.scalars().all()
            
            assert len(messages) == 4
            assert messages[0].sender_role == "user"
            assert "Python" in messages[0].text_content
            assert messages[1].sender_role == "assistant"
            assert messages[2].sender_role == "user"
            assert "FastAPI" in messages[2].text_content
            assert messages[3].sender_role == "assistant"

    asyncio.run(verify_db())
