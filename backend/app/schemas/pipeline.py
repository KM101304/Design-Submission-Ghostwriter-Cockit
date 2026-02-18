from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.risk import RiskProfile


class CompletenessResult(BaseModel):
    line_of_business: str
    completeness_score: int
    status: str
    missing_fields: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class QuestionSet(BaseModel):
    grouped_questions: dict[str, list[str]]
    email_draft: str
    bullet_summary: list[str]
    plain_english: str


class PipelineResponse(BaseModel):
    profile: RiskProfile
    completeness: list[CompletenessResult]
    questions: QuestionSet
