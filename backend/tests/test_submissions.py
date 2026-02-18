from fastapi.testclient import TestClient


def test_submissions_list_and_exports(client: TestClient, auth_headers: dict[str, str]) -> None:
    content = b"Insured: Harbor Clinical Group\nAnnual Revenue: $4100000\nGeneral Liability"
    run = client.post(
        "/api/v1/pipeline/run",
        files={"file": ("submission.txt", content, "text/plain")},
        headers=auth_headers,
    )
    assert run.status_code == 200
    submission_id = run.json()["profile"]["submission_id"]

    listing = client.get("/api/v1/submissions", headers=auth_headers)
    assert listing.status_code == 200
    rows = listing.json()
    assert any(row["submission_id"] == submission_id for row in rows)

    md_export = client.get(
        f"/api/v1/submissions/{submission_id}/export?format=markdown",
        headers=auth_headers,
    )
    assert md_export.status_code == 200
    assert "Submission Summary" in md_export.text

    json_export = client.get(
        f"/api/v1/submissions/{submission_id}/export?format=json",
        headers=auth_headers,
    )
    assert json_export.status_code == 200
    assert "profile" in json_export.json()

    pdf_export = client.get(
        f"/api/v1/submissions/{submission_id}/export?format=pdf",
        headers=auth_headers,
    )
    assert pdf_export.status_code == 200
    assert pdf_export.headers["content-type"].startswith("application/pdf")

    audit = client.get(f"/api/v1/submissions/{submission_id}/audit", headers=auth_headers)
    assert audit.status_code == 200
    assert len(audit.json()) >= 1
