from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.ingestion import router as ingestion_router
from app.api.routes.pipeline import router as pipeline_router
from app.api.routes.submissions import router as submissions_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Submission Ghostwriter API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(ingestion_router, prefix=settings.api_prefix)
    app.include_router(pipeline_router, prefix=settings.api_prefix)
    app.include_router(submissions_router, prefix=settings.api_prefix)

    return app


app = create_app()
