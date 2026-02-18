from __future__ import annotations

import base64

from app.db.session import SessionLocal
from app.services.pipeline_engine import run_pipeline_bytes
from app.worker import celery_app


@celery_app.task(name="pipeline.process_submission")
def process_submission_task(
    tenant_external_id: str,
    filename: str,
    content_type: str,
    payload_b64: str,
) -> dict:
    payload = base64.b64decode(payload_b64.encode("utf-8"))
    with SessionLocal() as db:
        result = run_pipeline_bytes(
            db=db,
            tenant_external_id=tenant_external_id,
            filename=filename,
            content_type=content_type,
            payload=payload,
            persist=True,
        )
    return result.model_dump(mode="json")
