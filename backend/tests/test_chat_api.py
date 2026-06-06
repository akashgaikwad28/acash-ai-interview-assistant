"""Tests for the RAG-backed chat endpoint."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_chat_endpoint_validates_message() -> None:
    client = TestClient(create_app())

    response = client.post("/api/v1/chat", json={"message": ""})

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_chat_endpoint_returns_contract() -> None:
    client = TestClient(create_app())

    response = client.post("/api/v1/chat", json={"message": "What has Acash built with FastAPI?"})

    assert response.status_code == 200
    payload = response.json()
    assert "response" in payload
    assert "session_id" in payload
    assert isinstance(payload["citations"], list)
