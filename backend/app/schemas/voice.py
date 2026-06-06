"""Vapi webhook schemas.

Purpose:
    Validate Vapi tool-call webhook payloads and responses.
Responsibilities:
    Represent tool calls and serialized tool results.
Dependencies:
    Pydantic v2.
Usage:
    VoiceWebhookRequest(message={...})
"""

from typing import Any, Literal

from pydantic import BaseModel, Field


class VapiFunctionCall(BaseModel):
    """Function payload inside a Vapi tool call."""

    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class VapiToolCall(BaseModel):
    """One Vapi function tool call."""

    id: str
    type: Literal["function"] = "function"
    function: VapiFunctionCall


class VapiMessage(BaseModel):
    """Vapi webhook message envelope."""

    type: str
    call: dict[str, Any] | None = None
    toolCalls: list[VapiToolCall] = Field(default_factory=list)


class VoiceWebhookRequest(BaseModel):
    """POST /voice/webhook request body."""

    message: VapiMessage


class VapiToolResult(BaseModel):
    """One serialized tool result returned to Vapi."""

    toolCallId: str
    result: str


class VoiceWebhookResponse(BaseModel):
    """POST /voice/webhook response body."""

    results: list[VapiToolResult]
