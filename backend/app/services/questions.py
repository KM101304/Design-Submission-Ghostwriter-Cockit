from __future__ import annotations

from app.schemas.pipeline import CompletenessResult, QuestionSet


def generate_question_set(insured_name: str | None, completeness: list[CompletenessResult]) -> QuestionSet:
    grouped: dict[str, list[str]] = {}

    for item in completeness:
        prompts = []
        for missing in item.missing_fields:
            if missing == "driver_schedule":
                prompts.append("Please share the current driver schedule and note any drivers added in the last 12 months.")
            elif missing == "locations":
                prompts.append("Please confirm all operating locations, including complete addresses.")
            elif missing == "revenue":
                prompts.append("Please confirm current annual gross revenue.")
            elif missing == "payroll":
                prompts.append("Please confirm current annual payroll by class code.")
            elif missing == "insured_name":
                prompts.append("Please confirm the exact named insured as it should appear on the policy.")
        if prompts:
            grouped[item.line_of_business] = prompts

    all_questions = [q for questions in grouped.values() for q in questions]
    insured = insured_name or "your organization"

    email_draft = (
        f"Subject: Submission follow-up items for {insured}\n\n"
        "Hi team,\n\n"
        "To finalize underwriting review, please provide the following:\n"
        + "\n".join(f"- {q}" for q in all_questions)
        + "\n\nThanks."
    )

    plain_english = (
        "We are close to quote-ready. We just need a few missing details to finish your submission: "
        + "; ".join(all_questions)
        if all_questions
        else "Submission appears complete."
    )

    return QuestionSet(
        grouped_questions=grouped,
        email_draft=email_draft,
        bullet_summary=all_questions,
        plain_english=plain_english,
    )
