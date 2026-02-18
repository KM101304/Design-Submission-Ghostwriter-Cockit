from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.orm import Session

from app.api.deps.tenant import tenant_id
from app.db.session import get_db
from app.schemas.submission import SubmissionListItem
from app.services.export import as_json, as_markdown, as_pdf_bytes, pipeline_from_stored_json
from app.services.repository import get_latest_profile_version, list_submissions

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

    if format == "json":
        return Response(content=as_json(result), media_type="application/json")
    if format == "pdf":
        return Response(
            content=as_pdf_bytes(result),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={submission_id}.pdf"},
        )

    return PlainTextResponse(content=as_markdown(result), media_type="text/markdown")
