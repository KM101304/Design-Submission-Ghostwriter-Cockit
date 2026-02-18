from __future__ import annotations

from uuid import uuid4

from sqlalchemy.orm import Session

from app.schemas.pipeline import PipelineResponse
from app.services.canonical import build_canonical_profile
from app.services.document_text import extract_text
from app.services.extraction import extract_risk_facts
from app.services.missingness import score_missingness
from app.services.questions import generate_question_set
from app.services.repository import store_pipeline_result
from app.services.storage import get_storage, safe_filename


def run_pipeline_bytes(
    db: Session,
    tenant_external_id: str,
    filename: str,
    content_type: str,
    payload: bytes,
    persist: bool = True,
) -> PipelineResponse:
    raw_text = extract_text(filename=filename, content_type=content_type, payload=payload)
    extraction = extract_risk_facts(raw_text=raw_text, filename=filename)
    submission_id = f"sub_{uuid4().hex[:12]}"
    profile = build_canonical_profile(submission_id=submission_id, extraction=extraction)
    completeness = score_missingness(profile)
    questions = generate_question_set(profile.insured_name, completeness)
    result = PipelineResponse(profile=profile, completeness=completeness, questions=questions)

    if persist:
        storage = get_storage()
        key = f"submissions/{tenant_external_id}/{submission_id}/{safe_filename(filename)}"
        storage.put_bytes(key=key, content=payload, content_type=content_type)
        store_pipeline_result(
            db,
            tenant_external_id=tenant_external_id,
            filename=filename,
            content_type=content_type,
            result=result,
            source_object_key=key,
        )

    return result
