from __future__ import annotations

import re
from typing import Any


def extract_risk_facts(raw_text: str, filename: str) -> dict[str, Any]:
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    text = " ".join(lines)

    insured_match = next(
        (re.search(r"^(?:insured|named insured)\s*[:\-]\s*(.+)$", line, re.IGNORECASE) for line in lines if re.search(r"^(?:insured|named insured)\s*[:\-]\s*", line, re.IGNORECASE)),
        None,
    )
    revenue_match = re.search(r"(?:revenue|annual revenue)\s*[:\-]?\s*\$?([0-9,]+(?:\.[0-9]{1,2})?)", text, re.IGNORECASE)
    payroll_match = re.search(r"(?:payroll|annual payroll)\s*[:\-]?\s*\$?([0-9,]+(?:\.[0-9]{1,2})?)", text, re.IGNORECASE)

    lines = []
    for token in ["general liability", "workers comp", "workers compensation", "commercial auto"]:
        if token in text.lower():
            if "liability" in token:
                lines.append("GL")
            elif "workers" in token:
                lines.append("WC")
            elif "auto" in token:
                lines.append("AUTO")

    def money(match_value: str | None) -> float | None:
        if not match_value:
            return None
        return float(match_value.replace(",", ""))

    insured_name = insured_match.group(1).strip() if insured_match and insured_match.group(1) else None
    revenue = money(revenue_match.group(1) if revenue_match else None)
    payroll = money(payroll_match.group(1) if payroll_match else None)

    return {
        "fields": {
            "insured_name": insured_name,
            "revenue": revenue,
            "payroll": payroll,
            "lines_of_business": sorted(set(lines)),
        },
        "confidence": {
            "insured_name": 0.82 if insured_name else 0.0,
            "revenue": 0.78 if revenue is not None else 0.0,
            "payroll": 0.78 if payroll is not None else 0.0,
            "lines_of_business": 0.7 if lines else 0.0,
        },
        "citations": {
            "insured_name": [{"source_document": filename, "page": None, "snippet": insured_name}],
            "revenue": [{"source_document": filename, "page": None, "snippet": revenue_match.group(0) if revenue_match else None}],
            "payroll": [{"source_document": filename, "page": None, "snippet": payroll_match.group(0) if payroll_match else None}],
            "lines_of_business": [{"source_document": filename, "page": None, "snippet": "matched line keywords"}],
        },
    }
