# Submission Ghostwriter

AI-native underwriting submission automation cockpit for commercial insurance broker CSRs.

## Stack
- Backend: FastAPI, Pydantic, Celery, Redis, PostgreSQL
- Frontend: Next.js (App Router), Tailwind, Radix primitives ready
- Infra: Docker Compose, local-first deployment

## Monorepo Layout
- `backend/`: API, domain schemas, AI orchestration services, tests
- `frontend/`: single-screen cockpit UI
- `docs/`: architecture and delivery docs
- `infra/`: infrastructure helpers (reserved)

## Quick Start
1. Copy env:
```bash
cp .env.example .env
```
2. Launch stack:
```bash
docker compose up --build
```
3. Verify:
- Backend health: `http://localhost:8000/health`
- Frontend cockpit: `http://localhost:3000`

## MVP Progress
- [x] Phase 1 scaffold + schema + ingestion endpoint
- [ ] Phase 2 extraction + canonical merge
- [ ] Phase 3 missingness + questions
- [ ] Phase 4 cockpit orchestration UX
- [ ] Phase 5 exports + hardening

## First API
`POST /api/v1/ingestion/upload`
- Accepts multipart file uploads (`.pdf`, `.eml`, `.txt`)
- Returns ingestion envelope with deterministic metadata and extraction placeholders:
  - `structured_fields`
  - `field_confidence`
  - `source_citations`

## Testing
From `backend/`:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```
