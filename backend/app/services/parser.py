from __future__ import annotations

from hashlib import sha256
from typing import Any


def parse_uploaded_document(filename: str, content: bytes) -> dict[str, Any]:
    # Deterministic stub until AI extraction worker is connected.
    digest = sha256(content).hexdigest()
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else "unknown"

    return {
        "structured_fields": {
            "document_name": filename,
            "document_extension": extension,
            "document_sha256": digest,
        },
        "field_confidence": {
            "document_name": 1.0,
            "document_extension": 1.0,
            "document_sha256": 1.0,
        },
        "source_citations": {
            "document_name": [{"source_document": filename, "page": None, "snippet": None}],
            "document_extension": [{"source_document": filename, "page": None, "snippet": None}],
            "document_sha256": [{"source_document": filename, "page": None, "snippet": None}],
        },
        "warnings": [
            "AI extraction not yet enabled; returning deterministic metadata envelope.",
        ],
    }
