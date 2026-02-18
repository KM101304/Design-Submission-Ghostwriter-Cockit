from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ingestion_upload_pdf_success() -> None:
    response = client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("submission.pdf", b"fake-pdf-content", "application/pdf")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "submission.pdf"
    assert body["bytes_received"] == len(b"fake-pdf-content")
    assert "document_sha256" in body["structured_fields"]


def test_ingestion_upload_rejects_unsupported_content_type() -> None:
    response = client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("submission.csv", b"a,b,c", "text/csv")},
    )
    assert response.status_code == 400
    assert "Unsupported content type" in response.json()["detail"]
