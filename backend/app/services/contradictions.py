from __future__ import annotations

from typing import Any

from app.models.risk import RiskProfile


def detect_contradictions(fields: dict[str, Any], profile: RiskProfile) -> list[str]:
    contradictions: list[str] = []

    revenue = fields.get("revenue")
    payroll = fields.get("payroll")
    if isinstance(revenue, (int, float)) and isinstance(payroll, (int, float)) and payroll > revenue:
        contradictions.append("Payroll exceeds revenue; verify reported financials.")

    lines = set(fields.get("lines_of_business", []))
    lob_fields = fields.get("lob_fields") or {}
    if "AUTO" in lines and "driver_schedule" not in str(lob_fields).lower():
        contradictions.append("AUTO coverage indicated but no driver schedule evidence found.")
    if "WC" in lines and payroll in (None, 0):
        contradictions.append("WC indicated without payroll data.")

    if profile.insured_name and len(profile.insured_name) < 3:
        contradictions.append("Insured name appears incomplete.")

    return contradictions
