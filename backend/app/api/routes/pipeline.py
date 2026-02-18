from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.pipeline import PipelineResponse
from app.services.canonical import build_canonical_profile
from app.services.extraction import extract_risk_facts
from app.services.missingness import score_missingness
from app.services.questions import generate_question_set

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run", response_model=PipelineResponse)
async def run_pipeline(file: UploadFile = File(...)) -> PipelineResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name")

    payload = await file.read()
    try:
        raw_text = payload.decode("utf-8", errors="ignore")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Unable to parse file") from exc

    extraction = extract_risk_facts(raw_text=raw_text, filename=file.filename)
    submission_id = f"sub_{uuid4().hex[:12]}"
    profile = build_canonical_profile(submission_id=submission_id, extraction=extraction)
    completeness = score_missingness(profile)
    questions = generate_question_set(profile.insured_name, completeness)

    return PipelineResponse(profile=profile, completeness=completeness, questions=questions)
