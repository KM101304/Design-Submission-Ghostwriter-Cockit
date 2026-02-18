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
3. Run database migrations and seed default user:
```bash
cd backend
alembic upgrade head
python scripts_seed.py
```
4. Login (default local user):
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \\
  -H 'Content-Type: application/json' \\
  -d '{"email":"admin@ghostwriter.dev","password":"ChangeMe123!"}'
```
5. Verify:
- Backend health: `http://localhost:8000/health`
- Frontend cockpit: `http://localhost:3000`

## MVP Progress
- [x] Phase 1 scaffold + schema + ingestion endpoint
- [~] Phase 2 extraction + canonical merge (initial deterministic engine)
- [~] Phase 3 missingness + questions (initial scoring + drafting)
- [ ] Phase 4 cockpit orchestration UX
- [ ] Phase 5 exports + hardening

## First API
`POST /api/v1/ingestion/upload`
- Accepts multipart file uploads (`.pdf`, `.eml`, `.txt`)
- Returns ingestion envelope with deterministic metadata and extraction placeholders:
  - `structured_fields`
  - `field_confidence`
  - `source_citations`

`POST /api/v1/auth/login`
- Returns JWT bearer token and tenant context

`POST /api/v1/pipeline/run`
- Accepts a submission document and runs the initial pipeline:
  - extraction
  - canonical profile build
  - missingness scoring
  - adaptive question generation
- Persists submission + profile version + audit log (tenant-aware via `x-tenant-id` header)

`POST /api/v1/pipeline/run-async`
- Queues pipeline execution on Celery worker and returns `job_id` + `submission_id`
- Supports idempotent retries with `Idempotency-Key` header

`GET /api/v1/pipeline/jobs/{job_id}`
- Poll job status and retrieve final `PipelineResponse` when completed

`GET /api/v1/submissions`
- Lists recent submissions for the tenant

`GET /api/v1/submissions/{submission_id}/export?format=markdown|json|pdf`
- Exports packet summary as Markdown, JSON, or PDF
- Stores export artifacts through the configured storage backend (`local` or `s3`)

`GET /api/v1/submissions/{submission_id}/audit`
- Returns submission job lifecycle and pipeline audit events

## Storage
- `STORAGE_BACKEND=local` writes artifacts to `STORAGE_LOCAL_PATH`
- `STORAGE_BACKEND=s3` writes artifacts to S3-compatible object storage using:
  - `STORAGE_BUCKET`
  - `STORAGE_S3_REGION`
  - `STORAGE_S3_ENDPOINT` (optional for MinIO/R2/etc.)
  - `STORAGE_S3_ACCESS_KEY`
  - `STORAGE_S3_SECRET_KEY`

## Security
- Tenant isolation enforced from JWT claims + `x-tenant-id` consistency check
- Auth configurable with:
  - `AUTH_SECRET_KEY`
  - `AUTH_PASSWORD_SALT`
  - `AUTH_ACCESS_TOKEN_EXP_MINUTES`
  - `AUTH_SEED_*` bootstrapping credentials
- Local/testing escape hatch: `AUTH_DISABLED=true`

## CI + Deploy
- GitHub Actions workflow: `.github/workflows/ci.yml`
  - migration check on fresh Postgres
  - backend tests
  - frontend build
- Render blueprint: `infra/render.yaml`
- Deployment notes: `docs/deployment.md`

## Testing
From `backend/`:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```
