from __future__ import annotations

import json
from io import BytesIO

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

from app.schemas.pipeline import PipelineResponse


def as_markdown(result: PipelineResponse) -> str:
    lines = [
        f"# Submission Summary - {result.profile.submission_id}",
        "",
        "## Risk Profile",
        f"- Insured: {result.profile.insured_name or 'Unknown'}",
        f"- Revenue: {result.profile.revenue}",
        f"- Payroll: {result.profile.payroll}",
        f"- Lines: {', '.join(result.profile.lines_of_business) if result.profile.lines_of_business else 'None'}",
        "",
        "## Completeness",
    ]
    for c in result.completeness:
        lines.append(f"- {c.line_of_business}: {c.completeness_score}% ({c.status})")
        if c.missing_fields:
            lines.append(f"  Missing: {', '.join(c.missing_fields)}")

    lines.extend([
        "",
        "## Follow-up Questions",
    ])
    for question in result.questions.bullet_summary:
        lines.append(f"- {question}")

    lines.extend([
        "",
        "## Email Draft",
        "```",
        result.questions.email_draft,
        "```",
    ])

    return "\n".join(lines)


def as_json(result: PipelineResponse) -> str:
    return result.model_dump_json(indent=2)


def as_pdf_bytes(result: PipelineResponse) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=LETTER)
    width, height = LETTER

    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Submission Summary: {result.profile.submission_id}")
    y -= 24

    c.setFont("Helvetica", 10)
    entries = [
        f"Insured: {result.profile.insured_name or 'Unknown'}",
        f"Revenue: {result.profile.revenue}",
        f"Payroll: {result.profile.payroll}",
        f"Lines: {', '.join(result.profile.lines_of_business) if result.profile.lines_of_business else 'None'}",
        "",
        "Completeness:",
    ]
    for item in result.completeness:
        entries.append(f"- {item.line_of_business}: {item.completeness_score}% ({item.status})")
    entries.append("")
    entries.append("Top Follow-up Questions:")
    for question in result.questions.bullet_summary[:6]:
        entries.append(f"- {question}")

    for line in entries:
        if y < 60:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)
        c.drawString(50, y, line[:110])
        y -= 14

    c.save()
    return buf.getvalue()


def pipeline_from_stored_json(profile_json: str, completeness_json: str, questions_json: str) -> PipelineResponse:
    profile = json.loads(profile_json)
    completeness = json.loads(completeness_json)
    questions = json.loads(questions_json)
    return PipelineResponse.model_validate(
        {
            "profile": profile,
            "completeness": completeness,
            "questions": questions,
        }
    )
