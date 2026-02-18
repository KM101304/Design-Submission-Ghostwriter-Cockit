# Deployment

## Baseline
- API: FastAPI container
- Worker: Celery container
- Frontend: Next.js container
- DB: PostgreSQL
- Queue: Redis

## Required env
- `DATABASE_URL`
- `REDIS_URL`
- `AUTH_SECRET_KEY`
- `AUTH_PASSWORD_SALT`
- `OPENAI_API_KEY` (optional but recommended)
- `SENTRY_DSN` (optional)

## Local
```bash
cp .env.example .env
docker compose up --build
```

## Render
Use `infra/render.yaml` as blueprint. Set secrets in Render dashboard.
