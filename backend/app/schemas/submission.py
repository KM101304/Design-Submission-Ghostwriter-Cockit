from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SubmissionListItem(BaseModel):
    submission_id: str
    filename: str
    content_type: str
    status: str
    created_at: datetime
