"""Tests for Phase 1 backend foundation behavior."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint_returns_expected_shape() -> None:
    client = TestClient(create_app())

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert "timestamp" in payload
    assert payload["services"]["chromadb"] == "connected"
    assert payload["services"]["google_calendar_api"] in {"active", "disabled"}


def test_metrics_endpoint_returns_prometheus_text() -> None:
    client = TestClient(create_app())
    client.get("/api/v1/health")

    response = client.get("/api/v1/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "http_requests_total" in response.text
    assert "request_latency_seconds" in response.text
