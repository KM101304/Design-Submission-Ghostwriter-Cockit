from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import UploadFile

from app.schemas.ingestion import IngestionResponse
from app.services.parser import parse_uploaded_document


ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "message/rfc822",
    "text/plain",
}


async def ingest_file(file: UploadFile) -> IngestionResponse:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"Unsupported content type: {file.content_type}")

    payload = await file.read()
    parsed = parse_uploaded_document(filename=file.filename or "unknown", content=payload)

    submission_id = f"sub_{uuid4().hex[:12]}"
    return IngestionResponse(
        submission_id=submission_id,
        filename=file.filename or "unknown",
        content_type=file.content_type or "application/octet-stream",
        bytes_received=len(payload),
        processed_at=datetime.now(timezone.utc),
        structured_fields=parsed["structured_fields"],
        field_confidence=parsed["field_confidence"],
        source_citations=parsed["source_citations"],
        warnings=parsed["warnings"],
    )
