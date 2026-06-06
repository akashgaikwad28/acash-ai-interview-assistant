"""Chat API endpoint.

Purpose:
    Serve recruiter questions through the RAG-grounded chat agent.
Responsibilities:
    Validate input, create session IDs, invoke the agent, and return citations.
Dependencies:
    ChatAgent dependency and chat schemas.
Usage:
    POST /api/v1/chat {"message": "..."}
"""

import json
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.agents.chat_agent import ChatAgent
from app.core.rate_limit import limiter
from app.core.service_factory import get_chat_agent
from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.rag import Citation


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(
    request: Request,
    payload: ChatRequest,
    agent: ChatAgent = Depends(get_chat_agent),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> ChatResponse:
    """Answer a recruiter question using retrieved candidate context and save history."""

    session_str = str(payload.session_id) if payload.session_id else str(uuid4())

    # 1. Fetch or create session
    existing_session = await db.conversation_sessions.find_one({"session_id": session_str})
    if not existing_session:
        client_ip = request.client.host if request.client else "127.0.0.1"
        await db.conversation_sessions.insert_one({
            "session_id": session_str,
            "client_ip": client_ip,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        })

    # 2. Save recruiter message
    await db.chat_messages.insert_one({
        "session_id": session_str,
        "sender_role": "user",
        "text_content": payload.message,
        "citations_json": "[]",
        "created_at": datetime.now(timezone.utc),
    })

    # 3. Retrieve conversation history for memory
    cursor = db.chat_messages.find({"session_id": session_str}).sort("created_at", 1)
    history_docs = await cursor.to_list(length=100)

    # Wrap dicts in SimpleNamespace so prompts.py can access .sender_role / .text_content
    history = [SimpleNamespace(**doc) for doc in history_docs]

    # 4. Run agent
    result = agent.run(payload.message, history=history)

    # 5. Save assistant response
    await db.chat_messages.insert_one({
        "session_id": session_str,
        "sender_role": "assistant",
        "text_content": result.response,
        "citations_json": json.dumps([cit.model_dump() for cit in result.citations]),
        "created_at": datetime.now(timezone.utc),
    })

    # Update session timestamp
    await db.conversation_sessions.update_one(
        {"session_id": session_str},
        {"$set": {"updated_at": datetime.now(timezone.utc)}},
    )

    return ChatResponse(response=result.response, session_id=session_str, citations=result.citations)


@router.get("/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Return the full message history for a given session."""
    cursor = db.chat_messages.find(
        {"session_id": session_id},
        {"_id": 0}
    ).sort("created_at", 1)
    messages = await cursor.to_list(length=200)
    return {"session_id": session_id, "messages": messages}
