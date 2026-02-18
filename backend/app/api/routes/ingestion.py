from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.ingestion import IngestionResponse
from app.services.ingestion import ingest_file

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/upload", response_model=IngestionResponse)
async def upload_submission(file: UploadFile = File(...)) -> IngestionResponse:
    try:
        return await ingest_file(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
