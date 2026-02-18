from __future__ import annotations

from typing import Any

from app.models.risk import RiskProfile
from app.services.contradictions import detect_contradictions


def build_canonical_profile(submission_id: str, extraction: dict[str, Any]) -> RiskProfile:
    fields = extraction["fields"]
    confidence = extraction["confidence"]
    citations = extraction["citations"]

    revenue = fields.get("revenue")
    payroll = fields.get("payroll")
    profile = RiskProfile(
        submission_id=submission_id,
        insured_name=fields.get("insured_name"),
        revenue=revenue,
        payroll=payroll,
        lines_of_business=fields.get("lines_of_business", []),
        source_citations=citations,
        field_confidence=confidence,
        metadata={"lob_fields": fields.get("lob_fields", {}), "debug": extraction.get("debug", {})},
    )
    profile.contradictions = detect_contradictions(fields, profile)

    return profile
