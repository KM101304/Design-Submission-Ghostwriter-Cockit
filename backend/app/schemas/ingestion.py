from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IngestionResponse(BaseModel):
    submission_id: str
    filename: str
    content_type: str
    bytes_received: int
    processed_at: datetime
    structured_fields: dict[str, Any] = Field(default_factory=dict)
    field_confidence: dict[str, float] = Field(default_factory=dict)
    source_citations: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
