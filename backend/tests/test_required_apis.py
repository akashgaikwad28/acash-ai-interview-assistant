"""Contract tests for required API surfaces."""

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import create_app


def test_availability_endpoint_returns_slots() -> None:
    client = TestClient(create_app())

    response = client.get("/api/v1/availability")

    assert response.status_code == 200
    payload = response.json()
    assert "timezone" in payload
    assert isinstance(payload["slots"], list)


def test_schedule_endpoint_creates_booking(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    client = TestClient(create_app())
    start = datetime.now(timezone.utc) + timedelta(days=3)
    start = start.replace(hour=15, minute=0, second=0, microsecond=0)
    end = start + timedelta(minutes=30)

    response = client.post(
        "/api/v1/schedule",
        json={
            "recruiter_name": "Rachel",
            "recruiter_email": "rachel@example.com",
            "company": "Acme",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "scheduled"


def test_voice_webhook_tool_call_returns_results(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    client = TestClient(create_app())
    target_date = (datetime.now(timezone.utc) + timedelta(days=3)).date().isoformat()

    response = client.post(
        "/api/v1/voice/webhook",
        json={
            "message": {
                "type": "tool-calls",
                "toolCalls": [
                    {
                        "id": "call-1",
                        "type": "function",
                        "function": {"name": "get_availability", "arguments": {"target_date": target_date}},
                    }
                ],
            }
        },
    )

    assert response.status_code == 200
    assert response.json()["results"][0]["toolCallId"] == "call-1"


def test_eval_endpoint_requires_admin_token() -> None:
    client = TestClient(create_app())

    response = client.post("/api/v1/eval/run", json={"test_suite": "rag"})

    assert response.status_code == 401


def test_eval_endpoint_succeeds_with_admin_token(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/eval/run",
        json={"test_suite": "rag"},
        headers={"X-Admin-Token": "dev-admin-token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "verdict" in payload
    assert "metrics" in payload

