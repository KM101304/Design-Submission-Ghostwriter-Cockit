from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI

from app.core.config import settings


def extract_risk_facts(raw_text: str, filename: str) -> dict[str, Any]:
    if settings.openai_api_key:
        llm_result = _extract_with_llm(raw_text=raw_text, filename=filename)
        if llm_result:
            return llm_result

    return _extract_with_rules(raw_text=raw_text, filename=filename)


def _extract_with_rules(raw_text: str, filename: str) -> dict[str, Any]:
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


def _extract_with_llm(raw_text: str, filename: str) -> dict[str, Any] | None:
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        prompt = (
            "Extract insurance submission fields from text. "
            "Return strict JSON with keys: insured_name (string|null), revenue (number|null), "
            "payroll (number|null), lines_of_business (array of GL/WC/AUTO). "
            "Do not include any other keys."
        )
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": raw_text[:12000]},
            ],
        )
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        lines = data.get("lines_of_business") or []
        normalized_lines = [line for line in lines if line in {"GL", "WC", "AUTO"}]

        insured_name = data.get("insured_name")
        revenue = data.get("revenue")
        payroll = data.get("payroll")

        return {
            "fields": {
                "insured_name": insured_name,
                "revenue": float(revenue) if revenue is not None else None,
                "payroll": float(payroll) if payroll is not None else None,
                "lines_of_business": sorted(set(normalized_lines)),
            },
            "confidence": {
                "insured_name": 0.9 if insured_name else 0.0,
                "revenue": 0.86 if revenue is not None else 0.0,
                "payroll": 0.86 if payroll is not None else 0.0,
                "lines_of_business": 0.84 if normalized_lines else 0.0,
            },
            "citations": {
                "insured_name": [{"source_document": filename, "page": None, "snippet": None}],
                "revenue": [{"source_document": filename, "page": None, "snippet": None}],
                "payroll": [{"source_document": filename, "page": None, "snippet": None}],
                "lines_of_business": [{"source_document": filename, "page": None, "snippet": None}],
            },
        }
    except Exception:
        return None
