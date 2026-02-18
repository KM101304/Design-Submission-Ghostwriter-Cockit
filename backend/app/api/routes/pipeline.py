import base64
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps.tenant import tenant_id
from app.db.session import get_db
from app.schemas.async_jobs import AsyncPipelineAccepted, AsyncPipelineStatus
from app.schemas.pipeline import PipelineResponse
from app.services.document_text import DocumentParseError
from app.services.pipeline_engine import compute_payload_sha256, run_pipeline_bytes
from app.services.repository import (
    create_queued_submission,
    generate_idempotency_key,
    get_submission_by_idempotency,
    get_submission_by_job_and_tenant,
)
from app.services.storage import get_storage, safe_filename
from app.services.tasks import process_submission_task
from app.worker import celery_app

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run", response_model=PipelineResponse)
async def run_pipeline(
    file: UploadFile = File(...),
    tenant: str = Depends(tenant_id),
    db: Session = Depends(get_db),
) -> PipelineResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name")

    payload = await file.read()
    try:
        result = run_pipeline_bytes(
            db=db,
            tenant_external_id=tenant,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            payload=payload,
            persist=True,
        )
    except DocumentParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return result


@router.post("/run-async", response_model=AsyncPipelineAccepted)
async def run_pipeline_async(
    file: UploadFile = File(...),
    tenant: str = Depends(tenant_id),
    idempotency_key_header: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
) -> AsyncPipelineAccepted:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name")

    payload = await file.read()
    payload_hash = compute_payload_sha256(payload)
    derived_key = idempotency_key_header or generate_idempotency_key(tenant, file.filename, payload_hash)
    existing = get_submission_by_idempotency(db, derived_key)
    if existing and existing.job_id:
        return AsyncPipelineAccepted(job_id=existing.job_id, submission_id=existing.submission_id, status=existing.job_status)

    submission_id = f"sub_{uuid4().hex[:12]}"
    storage = get_storage()
    source_key = f"submissions/{tenant}/{submission_id}/{safe_filename(file.filename)}"
    storage.put_bytes(source_key, payload, file.content_type or "application/octet-stream")

    job_id = f"job_{uuid4().hex[:20]}"
    create_queued_submission(
        db=db,
        tenant_external_id=tenant,
        submission_id=submission_id,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        source_object_key=source_key,
        idempotency_key=derived_key,
        job_id=job_id,
    )

    task = process_submission_task.apply_async(
        task_id=job_id,
        kwargs={
            "tenant_external_id": tenant,
            "submission_id": submission_id,
            "filename": file.filename,
            "content_type": file.content_type or "application/octet-stream",
            "payload_b64": base64.b64encode(payload).decode("utf-8"),
            "source_object_key": source_key,
        },
    )

    return AsyncPipelineAccepted(job_id=task.id, submission_id=submission_id)


@router.get("/jobs/{job_id}", response_model=AsyncPipelineStatus)
def get_job_status(
    job_id: str,
    tenant: str = Depends(tenant_id),
    db: Session = Depends(get_db),
) -> AsyncPipelineStatus:
    task = celery_app.AsyncResult(job_id)
    status = (task.status or "PENDING").lower()
    if task.successful():
        return AsyncPipelineStatus(
            job_id=job_id,
            status="succeeded",
            result=PipelineResponse.model_validate(task.result),
        )
    if task.failed():
        return AsyncPipelineStatus(
            job_id=job_id,
            status="failed",
            error=str(task.result),
        )

    submission = get_submission_by_job_and_tenant(db, job_id, tenant_external_id=tenant)
    if submission and submission.job_status:
        status = submission.job_status

    return AsyncPipelineStatus(job_id=job_id, status=status)
