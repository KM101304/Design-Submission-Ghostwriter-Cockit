from __future__ import annotations

from typing import Any

from app.models.risk import RiskProfile


def build_canonical_profile(submission_id: str, extraction: dict[str, Any]) -> RiskProfile:
    fields = extraction["fields"]
    confidence = extraction["confidence"]
    citations = extraction["citations"]

    contradictions: list[str] = []
    revenue = fields.get("revenue")
    payroll = fields.get("payroll")
    if isinstance(revenue, float) and isinstance(payroll, float) and payroll > revenue:
        contradictions.append("Payroll exceeds revenue; verify reported financials.")

    return RiskProfile(
        submission_id=submission_id,
        insured_name=fields.get("insured_name"),
        revenue=revenue,
        payroll=payroll,
        lines_of_business=fields.get("lines_of_business", []),
        contradictions=contradictions,
        source_citations=citations,
        field_confidence=confidence,
    )
