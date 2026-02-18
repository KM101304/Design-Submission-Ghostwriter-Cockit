from fastapi.testclient import TestClient


def test_ingestion_upload_pdf_success(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("submission.pdf", b"fake-pdf-content", "application/pdf")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "submission.pdf"
    assert body["bytes_received"] == len(b"fake-pdf-content")
    assert "document_sha256" in body["structured_fields"]


def test_ingestion_upload_rejects_unsupported_content_type(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("submission.csv", b"a,b,c", "text/csv")},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "Unsupported content type" in response.json()["detail"]
