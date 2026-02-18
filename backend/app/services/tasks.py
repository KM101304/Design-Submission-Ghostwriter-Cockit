from __future__ import annotations

import base64

from app.db.session import SessionLocal
from app.services.pipeline_engine import run_pipeline_bytes
from app.services.repository import append_audit_log, get_or_create_tenant, mark_submission_job_status
from app.worker import celery_app


@celery_app.task(
    name="pipeline.process_submission",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=2,
    retry_backoff_max=30,
    retry_jitter=True,
    max_retries=4,
)
def process_submission_task(
    self,
    tenant_external_id: str,
    submission_id: str,
    filename: str,
    content_type: str,
    payload_b64: str,
    source_object_key: str,
) -> dict:
    payload = base64.b64decode(payload_b64.encode("utf-8"))
    with SessionLocal() as db:
        tenant = get_or_create_tenant(db, tenant_external_id)
        mark_submission_job_status(db, submission_id=submission_id, status="running")
        append_audit_log(
            db,
            tenant_id=tenant.id,
            submission_id=submission_id,
            event_type="job_running",
            details={"job_id": self.request.id, "attempt": int(self.request.retries) + 1},
        )
        try:
            result = run_pipeline_bytes(
                db=db,
                tenant_external_id=tenant_external_id,
                filename=filename,
                content_type=content_type,
                payload=payload,
                persist=True,
                submission_id=submission_id,
                source_object_key=source_object_key,
            )
            mark_submission_job_status(db, submission_id=submission_id, status="processed")
            append_audit_log(
                db,
                tenant_id=tenant.id,
                submission_id=submission_id,
                event_type="job_succeeded",
                details={"job_id": self.request.id},
            )
            return result.model_dump(mode="json")
        except Exception as exc:
            mark_submission_job_status(db, submission_id=submission_id, status="failed")
            append_audit_log(
                db,
                tenant_id=tenant.id,
                submission_id=submission_id,
                event_type="job_failed",
                details={"job_id": self.request.id, "error": str(exc)},
            )
            raise
