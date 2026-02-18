from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.orm import Session

from app.api.deps.tenant import tenant_id
from app.db.session import get_db
from app.schemas.submission import AuditLogItem, SubmissionListItem
from app.services.export import as_json, as_markdown, as_pdf_bytes, pipeline_from_stored_json
from app.services.repository import get_latest_profile_version, list_audit_logs, list_submissions, set_export_key
from app.services.storage import get_storage

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.get("", response_model=list[SubmissionListItem])
def get_submissions(
    tenant: str = Depends(tenant_id),
    db: Session = Depends(get_db),
) -> list[SubmissionListItem]:
    rows = list_submissions(db, tenant_external_id=tenant)
    return [
        SubmissionListItem(
            submission_id=row.submission_id,
            filename=row.filename,
            content_type=row.content_type,
            status=row.status,
            job_status=row.job_status,
            job_id=row.job_id,
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.get("/{submission_id}/export")
def export_submission(
    submission_id: str,
    format: str = "markdown",
    tenant: str = Depends(tenant_id),
    db: Session = Depends(get_db),
):
    version = get_latest_profile_version(db, tenant_external_id=tenant, submission_id=submission_id)
    if not version:
        raise HTTPException(status_code=404, detail="Submission not found")

    result = pipeline_from_stored_json(version.profile_json, version.completeness_json, version.questions_json)
    storage = get_storage()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    if format == "json":
        payload = as_json(result).encode("utf-8")
        key = f"exports/{tenant}/{submission_id}/{ts}.json"
        storage.put_bytes(key=key, content=payload, content_type="application/json")
        set_export_key(db, version, "json", key)
        return Response(content=payload, media_type="application/json")
    if format == "pdf":
        payload = as_pdf_bytes(result)
        key = f"exports/{tenant}/{submission_id}/{ts}.pdf"
        storage.put_bytes(key=key, content=payload, content_type="application/pdf")
        set_export_key(db, version, "pdf", key)
        return Response(
            content=payload,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={submission_id}.pdf"},
        )

    payload = as_markdown(result).encode("utf-8")
    key = f"exports/{tenant}/{submission_id}/{ts}.md"
    storage.put_bytes(key=key, content=payload, content_type="text/markdown")
    set_export_key(db, version, "markdown", key)
    return PlainTextResponse(content=payload.decode("utf-8"), media_type="text/markdown")


@router.get("/{submission_id}/audit", response_model=list[AuditLogItem])
def submission_audit(
    submission_id: str,
    tenant: str = Depends(tenant_id),
    db: Session = Depends(get_db),
) -> list[AuditLogItem]:
    logs = list_audit_logs(db, tenant_external_id=tenant, submission_id=submission_id)
    return [AuditLogItem(event_type=log.event_type, details=log.details, created_at=log.created_at) for log in logs]
