from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps.tenant import tenant_id
from app.db.session import get_db
from app.schemas.pipeline import PipelineResponse
from app.services.canonical import build_canonical_profile
from app.services.document_text import DocumentParseError, extract_text
from app.services.extraction import extract_risk_facts
from app.services.missingness import score_missingness
from app.services.questions import generate_question_set
from app.services.repository import store_pipeline_result

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run", response_model=PipelineResponse)
async def run_pipeline(
    file: UploadFile = File(...),
    tenant: str = Depends(tenant_id),
    db: Session = Depends(get_db),
) -> PipelineResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name")

    payload = await file.read()
    try:
        raw_text = extract_text(filename=file.filename, content_type=file.content_type, payload=payload)
    except DocumentParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    extraction = extract_risk_facts(raw_text=raw_text, filename=file.filename)
    submission_id = f"sub_{uuid4().hex[:12]}"
    profile = build_canonical_profile(submission_id=submission_id, extraction=extraction)
    completeness = score_missingness(profile)
    questions = generate_question_set(profile.insured_name, completeness)
    result = PipelineResponse(profile=profile, completeness=completeness, questions=questions)
    store_pipeline_result(
        db,
        tenant_external_id=tenant,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        result=result,
    )

    return result
