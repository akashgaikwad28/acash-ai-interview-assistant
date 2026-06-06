# Backend

FastAPI backend for the Acash AI Interview Assistant.

## Purpose

This service owns the recruiter-facing API contracts documented in `docs/API_SPEC.md`: health, chat, scheduling, ingestion, voice webhooks, evaluation, and metrics.

## Current Status

Phase 1 foundation is implemented:

- FastAPI application factory
- Typed environment settings
- CORS middleware
- Structured JSON request logging
- Standardized error responses
- SlowAPI rate-limit wiring
- `GET /api/v1/health`
- `GET /api/v1/metrics`
- Admin-protected `POST /api/v1/ingest/resume`
- Admin-protected `POST /api/v1/ingest/github`
- Local persistent vector retrieval foundation for RAG development
- RAG-grounded `POST /api/v1/chat` with citations and offline Gemini fallback
- `GET /api/v1/availability`
- `POST /api/v1/schedule`
- `POST /api/v1/voice/webhook`
- Admin-protected `POST /api/v1/eval/run`

## Setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
.\venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Tests

```bash
cd backend
pytest
```

## Ingestion

Both ingestion endpoints require `X-Admin-Token`.

```bash
curl -X POST http://localhost:8000/api/v1/ingest/resume ^
  -H "X-Admin-Token: dev-admin-token" ^
  -F "file=@resume.pdf"

curl -X POST http://localhost:8000/api/v1/ingest/github ^
  -H "X-Admin-Token: dev-admin-token" ^
  -H "Content-Type: application/json" ^
  -d "{\"repo_url\":\"https://github.com/acash/example\",\"branch\":\"main\"}"
```

## Environment Variables

Use `.env.example` as the canonical local template. Development mode can boot with disabled external services; staging and production require Gemini, Google Calendar, and Vapi secrets.
