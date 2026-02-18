from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import AuditLog, ProfileVersion, Submission, Tenant
from app.schemas.pipeline import PipelineResponse


def get_or_create_tenant(db: Session, tenant_external_id: str) -> Tenant:
    tenant = db.scalar(select(Tenant).where(Tenant.external_id == tenant_external_id))
    if tenant:
        return tenant

    tenant = Tenant(external_id=tenant_external_id, name=tenant_external_id)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


def append_audit_log(db: Session, tenant_id: int, submission_id: str, event_type: str, details: dict) -> None:
    log = AuditLog(
        tenant_id=tenant_id,
        submission_id=submission_id,
        event_type=event_type,
        details=json.dumps(details),
    )
    db.add(log)
    db.commit()


def create_queued_submission(
    db: Session,
    tenant_external_id: str,
    submission_id: str,
    filename: str,
    content_type: str,
    source_object_key: str | None,
    idempotency_key: str,
    job_id: str,
) -> Submission:
    tenant = get_or_create_tenant(db, tenant_external_id)
    existing = db.scalar(select(Submission).where(Submission.idempotency_key == idempotency_key))
    if existing:
        return existing

    submission = Submission(
        submission_id=submission_id,
        tenant_id=tenant.id,
        filename=filename,
        content_type=content_type,
        source_object_key=source_object_key,
        status="queued",
        job_status="queued",
        idempotency_key=idempotency_key,
        job_id=job_id,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    append_audit_log(
        db,
        tenant_id=tenant.id,
        submission_id=submission_id,
        event_type="job_queued",
        details={"job_id": job_id, "filename": filename},
    )
    return submission


def get_submission_by_idempotency(db: Session, idempotency_key: str) -> Submission | None:
    return db.scalar(select(Submission).where(Submission.idempotency_key == idempotency_key))


def get_submission_by_job(db: Session, job_id: str) -> Submission | None:
    return db.scalar(select(Submission).where(Submission.job_id == job_id))


def get_submission_by_job_and_tenant(db: Session, job_id: str, tenant_external_id: str) -> Submission | None:
    tenant = get_or_create_tenant(db, tenant_external_id)
    return db.scalar(select(Submission).where(Submission.job_id == job_id, Submission.tenant_id == tenant.id))


def mark_submission_job_status(db: Session, submission_id: str, status: str) -> None:
    sub = db.scalar(select(Submission).where(Submission.submission_id == submission_id))
    if not sub:
        return
    sub.job_status = status
    sub.status = status
    db.add(sub)
    db.commit()


def store_pipeline_result(
    db: Session,
    tenant_external_id: str,
    filename: str,
    content_type: str,
    result: PipelineResponse,
    source_object_key: str | None = None,
    job_status: str = "processed",
) -> None:
    tenant = get_or_create_tenant(db, tenant_external_id)

    submission = db.scalar(select(Submission).where(Submission.submission_id == result.profile.submission_id))
    if submission:
        submission.filename = filename
        submission.content_type = content_type
        submission.source_object_key = source_object_key
        submission.status = "processed"
        submission.job_status = job_status
        db.add(submission)
    else:
        submission = Submission(
            submission_id=result.profile.submission_id,
            tenant_id=tenant.id,
            filename=filename,
            content_type=content_type,
            source_object_key=source_object_key,
            status="processed",
            job_status=job_status,
        )
        db.add(submission)

    version = ProfileVersion(
        submission_id=result.profile.submission_id,
        tenant_id=tenant.id,
        version=result.profile.version,
        profile_json=result.profile.model_dump_json(),
        completeness_json=json.dumps([item.model_dump() for item in result.completeness]),
        questions_json=result.questions.model_dump_json(),
    )
    db.add(version)
    db.commit()

    append_audit_log(
        db,
        tenant_id=tenant.id,
        submission_id=result.profile.submission_id,
        event_type="pipeline_run",
        details={"filename": filename, "content_type": content_type},
    )


def list_submissions(db: Session, tenant_external_id: str) -> list[Submission]:
    tenant = get_or_create_tenant(db, tenant_external_id)
    rows = db.scalars(
        select(Submission)
        .where(Submission.tenant_id == tenant.id)
        .order_by(Submission.created_at.desc())
        .limit(50)
    )
    return list(rows)


def get_latest_profile_version(db: Session, tenant_external_id: str, submission_id: str) -> ProfileVersion | None:
    tenant = get_or_create_tenant(db, tenant_external_id)
    return db.scalar(
        select(ProfileVersion)
        .where(ProfileVersion.tenant_id == tenant.id, ProfileVersion.submission_id == submission_id)
        .order_by(ProfileVersion.version.desc(), ProfileVersion.created_at.desc())
    )


def list_audit_logs(db: Session, tenant_external_id: str, submission_id: str) -> list[AuditLog]:
    tenant = get_or_create_tenant(db, tenant_external_id)
    rows = db.scalars(
        select(AuditLog)
        .where(AuditLog.tenant_id == tenant.id, AuditLog.submission_id == submission_id)
        .order_by(AuditLog.created_at.asc())
    )
    return list(rows)


def set_export_key(
    db: Session,
    version: ProfileVersion,
    export_type: str,
    storage_key: str,
) -> None:
    if export_type == "markdown":
        version.export_markdown_key = storage_key
    elif export_type == "json":
        version.export_json_key = storage_key
    elif export_type == "pdf":
        version.export_pdf_key = storage_key
    db.add(version)
    db.commit()


def generate_idempotency_key(tenant_external_id: str, filename: str, file_sha256: str) -> str:
    return f"{tenant_external_id}:{filename}:{file_sha256[:24]}"


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
