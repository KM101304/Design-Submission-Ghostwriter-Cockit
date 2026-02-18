from __future__ import annotations

import json

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


def store_pipeline_result(
    db: Session,
    tenant_external_id: str,
    filename: str,
    content_type: str,
    result: PipelineResponse,
) -> None:
    tenant = get_or_create_tenant(db, tenant_external_id)

    submission = Submission(
        submission_id=result.profile.submission_id,
        tenant_id=tenant.id,
        filename=filename,
        content_type=content_type,
        status="processed",
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

    audit = AuditLog(
        tenant_id=tenant.id,
        submission_id=result.profile.submission_id,
        event_type="pipeline_run",
        details=json.dumps({"filename": filename, "content_type": content_type}),
    )
    db.add(audit)

    db.commit()


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
