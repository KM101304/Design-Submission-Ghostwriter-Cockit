from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SubmissionListItem(BaseModel):
    submission_id: str
    filename: str
    content_type: str
    status: str
    job_status: str
    job_id: str | None = None
    created_at: datetime


class AuditLogItem(BaseModel):
    event_type: str
    details: str
    created_at: datetime
