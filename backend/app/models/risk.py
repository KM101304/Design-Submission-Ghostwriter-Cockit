from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class FieldCitation(BaseModel):
    source_document: str
    page: int | None = None
    snippet: str | None = None


class PriorLoss(BaseModel):
    loss_date: date | None = None
    amount: float | None = None
    description: str | None = None


class RiskLocation(BaseModel):
    address: str
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str = "US"


class CoverageRequest(BaseModel):
    line_of_business: str
    limit: str | None = None
    deductible: str | None = None


class RiskProfile(BaseModel):
    submission_id: str
    insured_name: str | None = None
    entity_type: str | None = None
    revenue: float | None = None
    payroll: float | None = None
    locations: list[RiskLocation] = Field(default_factory=list)
    prior_losses: list[PriorLoss] = Field(default_factory=list)
    lines_of_business: list[str] = Field(default_factory=list)
    coverage_requested: list[CoverageRequest] = Field(default_factory=list)
    underwriting_flags: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    source_citations: dict[str, list[FieldCitation]] = Field(default_factory=dict)
    field_confidence: dict[str, float] = Field(default_factory=dict)
    version: int = 1
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)
