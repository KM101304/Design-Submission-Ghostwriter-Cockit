from __future__ import annotations

from pydantic import BaseModel

from app.schemas.pipeline import PipelineResponse


class AsyncPipelineAccepted(BaseModel):
    job_id: str
    submission_id: str
    status: str = "queued"


class AsyncPipelineStatus(BaseModel):
    job_id: str
    status: str
    result: PipelineResponse | None = None
    error: str | None = None
