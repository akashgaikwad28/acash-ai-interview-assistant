"""Vapi voice webhook endpoint.

Purpose:
    Handle Vapi tool-call webhooks for availability and interview booking.
Responsibilities:
    Validate webhook secrets, dispatch supported tool calls, and serialize
    tool results in Vapi's expected response shape.
Dependencies:
    CalendarService and voice schemas.
Usage:
    POST /api/v1/voice/webhook with X-Vapi-Secret.
"""

import json
from datetime import date, datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.core.config import Settings
from app.core.dependencies import get_app_settings
from app.core.service_factory import get_calendar_service
from app.schemas.schedule import ScheduleRequest
from app.schemas.voice import VapiToolCall, VapiToolResult, VoiceWebhookRequest, VoiceWebhookResponse
from app.services.calendar_service import CalendarService
from app.services.rag_service import RAGService
from app.core.service_factory import get_rag_service


router = APIRouter(prefix="/voice")


@router.post("/webhook", response_model=VoiceWebhookResponse)
async def voice_webhook(
    payload: VoiceWebhookRequest,
    x_vapi_secret: Annotated[str | None, Header(alias="X-Vapi-Secret")] = None,
    settings: Settings = Depends(get_app_settings),
    calendar: CalendarService = Depends(get_calendar_service),
    rag: RAGService = Depends(get_rag_service),
) -> VoiceWebhookResponse:
    """Process Vapi webhook tool calls."""

    if settings.vapi_secret_token and x_vapi_secret != settings.vapi_secret_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Vapi secret.")

    if payload.message.type != "tool-calls":
        return VoiceWebhookResponse(results=[])

    results = [await _dispatch_tool_call(tool_call, calendar, rag) for tool_call in payload.message.toolCalls]
    return VoiceWebhookResponse(results=results)


async def _dispatch_tool_call(tool_call: VapiToolCall, calendar: CalendarService, rag: RAGService) -> VapiToolResult:
    try:
        if tool_call.function.name == "get_availability":
            target = date.fromisoformat(str(tool_call.function.arguments["target_date"]))
            response = await calendar.get_availability(target, target)
            result = response.model_dump_json()
        elif tool_call.function.name == "book_slot":
            start = datetime.fromisoformat(str(tool_call.function.arguments["start_time"])).astimezone(timezone.utc)
            end = start + timedelta(minutes=30)
            request = ScheduleRequest(
                recruiter_name=str(tool_call.function.arguments["recruiter_name"]),
                recruiter_email=str(tool_call.function.arguments["recruiter_email"]),
                company=tool_call.function.arguments.get("company"),
                start_time=start,
                end_time=end,
            )
            booking_res = await calendar.book_slot(request)
            result = booking_res.model_dump_json()
        elif tool_call.function.name == "query_knowledge_base":
            query = str(tool_call.function.arguments["query"])
            rag_result = rag.retrieve(query)
            context_str = "\n".join([f"Source: {c.source}\nContent: {c.text_snippet}" for c in rag_result.citations])
            result = json.dumps({"status": "success", "context": context_str or "No matching context found."})
        else:
            result = json.dumps({"status": "error", "message": f"Unsupported tool {tool_call.function.name}"})
    except Exception as exc:
        result = json.dumps({"status": "error", "message": str(exc)})
    return VapiToolResult(toolCallId=tool_call.id, result=result)

