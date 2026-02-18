# Submission Ghostwriter Architecture

## North-Star Shape
Submission Ghostwriter is a multi-tenant AI-native submission cockpit for broker CSRs.

Core flow:
1. Ingest (`email`, `pdf`, `supplemental docs`)
2. Parse and extract structured risk facts + source citations
3. Reconcile into canonical `RiskProfile`
4. Compute LOB-specific missingness and blockers
5. Generate adaptive questions and broker/client-ready drafts
6. Export packet (PDF + JSON + Markdown) with provenance

## Service Boundaries
- `backend/app/api`: HTTP contracts and orchestration endpoints
- `backend/app/services`: ingestion, extraction, normalization, scoring, question generation
- `backend/app/models`: canonical risk domain objects
- `frontend`: single-screen cockpit UI (submission list, profile, completeness + actions)
- `backend/alembic`: database migration history and environment

## Data Plane
- PostgreSQL: tenant, users, submissions, profile versions, required-field rules, audit logs
- Redis: async jobs + retries
- Object storage abstraction: source docs, rendered exports, extraction artifacts
- Local dev default uses in-memory SQLite; set `DATABASE_URL` in `.env` for Postgres runtime.

## AI Plane
- OpenAI-backed extraction + reasoning adapters behind service interfaces
- deterministic post-processing for schema validation and contradiction flags
- provenance map for every extracted field (`source_doc`, `page`, `span`, `confidence`)

## Async Execution
- `POST /pipeline/run-async` queues pipeline execution in Celery
- worker task persists pipeline outputs and audit events
- `GET /pipeline/jobs/{job_id}` returns queued/running/succeeded/failed state

## MVP Slice Implemented
- FastAPI app scaffold + health endpoint
- ingestion endpoint (`POST /api/v1/ingestion/upload`)
- canonical `RiskProfile` schema and field provenance models
- deterministic ingestion metadata extraction stub
- pipeline persistence models (`tenants`, `submissions`, `profile_versions`, `audit_logs`)
- export engine for `markdown`, `json`, and `pdf`
- storage abstraction with `local` and `s3` backends for source docs and exports
- initial cockpit shell in Next.js App Router
- tests for schema + ingestion API

## Phase Issues (Target)
- Phase 1: foundation/scaffold/schema
- Phase 2: document extraction + canonical merge engine
- Phase 3: missingness scoring + adaptive questions
- Phase 4: cockpit interactions + pipeline reruns
- Phase 5: export engine + hardening + deployment profile
