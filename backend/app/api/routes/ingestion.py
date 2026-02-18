from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.deps.tenant import tenant_id
from app.schemas.ingestion import IngestionResponse
from app.services.ingestion import ingest_file

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/upload", response_model=IngestionResponse)
async def upload_submission(
    file: UploadFile = File(...),
    _: str = Depends(tenant_id),
) -> IngestionResponse:
    try:
        return await ingest_file(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
