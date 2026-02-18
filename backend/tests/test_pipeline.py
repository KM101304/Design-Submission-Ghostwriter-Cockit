from fastapi.testclient import TestClient


def test_pipeline_run_returns_profile_and_questions(client: TestClient, auth_headers: dict[str, str]) -> None:
    content = b"Insured: Atlas Fabrication LLC\nAnnual Revenue: $5200000\nAnnual Payroll: $1800000\nGeneral Liability\nWorkers Compensation"
    response = client.post(
        "/api/v1/pipeline/run",
        files={"file": ("submission.txt", content, "text/plain")},
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["profile"]["insured_name"] == "Atlas Fabrication LLC"
    assert body["profile"]["revenue"] == 5200000.0
    assert len(body["completeness"]) >= 1
    assert "email_draft" in body["questions"]
