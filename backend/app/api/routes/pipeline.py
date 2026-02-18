import base64

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps.tenant import tenant_id
from app.db.session import get_db
from app.schemas.async_jobs import AsyncPipelineAccepted, AsyncPipelineStatus
from app.schemas.pipeline import PipelineResponse
from app.services.document_text import DocumentParseError
from app.services.pipeline_engine import run_pipeline_bytes
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
) -> AsyncPipelineAccepted:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name")

    payload = await file.read()
    task = process_submission_task.delay(
        tenant_external_id=tenant,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        payload_b64=base64.b64encode(payload).decode("utf-8"),
    )
    return AsyncPipelineAccepted(job_id=task.id)


@router.get("/jobs/{job_id}", response_model=AsyncPipelineStatus)
def get_job_status(job_id: str) -> AsyncPipelineStatus:
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
    return AsyncPipelineStatus(job_id=job_id, status=status)
