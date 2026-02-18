from __future__ import annotations

from app.models.risk import RiskProfile
from app.schemas.pipeline import CompletenessResult


REQUIRED_FIELDS_BY_LOB: dict[str, list[str]] = {
    "GL": ["insured_name", "revenue", "locations"],
    "WC": ["insured_name", "payroll", "locations"],
    "AUTO": ["insured_name", "locations", "driver_schedule"],
}


def score_missingness(profile: RiskProfile) -> list[CompletenessResult]:
    lobs = profile.lines_of_business or ["GL"]
    results: list[CompletenessResult] = []

    for lob in lobs:
        required = REQUIRED_FIELDS_BY_LOB.get(lob, ["insured_name", "revenue"])
        missing: list[str] = []

        for field in required:
            if field == "insured_name" and not profile.insured_name:
                missing.append(field)
            elif field == "revenue" and profile.revenue is None:
                missing.append(field)
            elif field == "payroll" and profile.payroll is None:
                missing.append(field)
            elif field == "locations" and not profile.locations:
                missing.append(field)
            elif field == "driver_schedule":
                missing.append(field)

        completeness_score = int(round((1 - (len(missing) / max(len(required), 1))) * 100))
        status = "Green" if completeness_score >= 85 else "Yellow" if completeness_score >= 60 else "Red"

        blockers = [f"Missing required field: {f}" for f in missing]
        results.append(
            CompletenessResult(
                line_of_business=lob,
                completeness_score=completeness_score,
                status=status,
                missing_fields=missing,
                blockers=blockers,
            )
        )

    return results
