from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI

from app.core.config import settings

LOB_KEYWORDS = {
    "GL": ["general liability", "cgl", "premises liability"],
    "WC": ["workers comp", "workers compensation", "wc policy"],
    "AUTO": ["commercial auto", "fleet", "driver schedule", "auto liability"],
}

LOB_SCHEMAS: dict[str, list[str]] = {
    "GL": ["insured_name", "revenue", "locations", "coverage_requested"],
    "WC": ["insured_name", "payroll", "locations", "class_codes"],
    "AUTO": ["insured_name", "locations", "vehicle_count", "driver_schedule"],
}


def extract_risk_facts(raw_text: str, filename: str) -> dict[str, Any]:
    inferred_lobs = infer_lobs(raw_text)
    if settings.openai_api_key:
        llm_result = _extract_with_llm(raw_text=raw_text, filename=filename, inferred_lobs=inferred_lobs)
        if llm_result:
            return llm_result

    return _extract_with_rules(raw_text=raw_text, filename=filename)


def infer_lobs(raw_text: str) -> list[str]:
    lowered = raw_text.lower()
    found: list[str] = []
    for lob, terms in LOB_KEYWORDS.items():
        if any(term in lowered for term in terms):
            found.append(lob)
    return sorted(set(found))


def _extract_with_rules(raw_text: str, filename: str) -> dict[str, Any]:
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    text = " ".join(lines)

    insured_match = next(
        (
            re.search(r"^(?:insured|named insured)\s*[:\-]\s*(.+)$", line, re.IGNORECASE)
            for line in lines
            if re.search(r"^(?:insured|named insured)\s*[:\-]\s*", line, re.IGNORECASE)
        ),
        None,
    )
    revenue_match = re.search(r"(?:revenue|annual revenue)\s*[:\-]?\s*\$?([0-9,]+(?:\.[0-9]{1,2})?)", text, re.IGNORECASE)
    payroll_match = re.search(r"(?:payroll|annual payroll)\s*[:\-]?\s*\$?([0-9,]+(?:\.[0-9]{1,2})?)", text, re.IGNORECASE)

    lobs = infer_lobs(text)

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
            "lines_of_business": lobs,
        },
        "confidence": {
            "insured_name": 0.82 if insured_name else 0.0,
            "revenue": 0.78 if revenue is not None else 0.0,
            "payroll": 0.78 if payroll is not None else 0.0,
            "lines_of_business": 0.7 if lobs else 0.0,
        },
        "citations": {
            "insured_name": [{"source_document": filename, "page": None, "snippet": insured_name}],
            "revenue": [{"source_document": filename, "page": None, "snippet": revenue_match.group(0) if revenue_match else None}],
            "payroll": [{"source_document": filename, "page": None, "snippet": payroll_match.group(0) if payroll_match else None}],
            "lines_of_business": [{"source_document": filename, "page": None, "snippet": ", ".join(lobs)}],
        },
        "debug": {"mode": "rules", "lobs": lobs},
    }


def _extract_with_llm(raw_text: str, filename: str, inferred_lobs: list[str]) -> dict[str, Any] | None:
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        if not inferred_lobs:
            inferred_lobs = ["GL"]

        lob_fields = {lob: LOB_SCHEMAS.get(lob, []) for lob in inferred_lobs}
        prompt = (
            "You extract underwriting submission fields. Return strict JSON with keys: "
            "insured_name (string|null), revenue (number|null), payroll (number|null), lines_of_business (array of GL/WC/AUTO), "
            "lob_fields (object keyed by lob with any extracted values)."
            f" Focus on these LOBs and fields: {json.dumps(lob_fields)}"
        )
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": raw_text[:16000]},
            ],
        )
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)

        lines = data.get("lines_of_business") or inferred_lobs
        normalized_lines = [line for line in lines if line in {"GL", "WC", "AUTO"}]

        insured_name = data.get("insured_name")
        revenue = data.get("revenue")
        payroll = data.get("payroll")

        return {
            "fields": {
                "insured_name": insured_name,
                "revenue": float(revenue) if revenue is not None else None,
                "payroll": float(payroll) if payroll is not None else None,
                "lines_of_business": sorted(set(normalized_lines or inferred_lobs)),
                "lob_fields": data.get("lob_fields") or {},
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
            "debug": {"mode": "llm", "lobs": inferred_lobs, "lob_fields": data.get("lob_fields") or {}},
        }
    except Exception:
        return None
