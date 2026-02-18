from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_submissions_list_and_exports() -> None:
    content = b"Insured: Harbor Clinical Group\nAnnual Revenue: $4100000\nGeneral Liability"
    run = client.post(
        "/api/v1/pipeline/run",
        files={"file": ("submission.txt", content, "text/plain")},
        headers={"x-tenant-id": "demo-brokerage"},
    )
    assert run.status_code == 200
    submission_id = run.json()["profile"]["submission_id"]

    listing = client.get("/api/v1/submissions", headers={"x-tenant-id": "demo-brokerage"})
    assert listing.status_code == 200
    rows = listing.json()
    assert any(row["submission_id"] == submission_id for row in rows)

    md_export = client.get(
        f"/api/v1/submissions/{submission_id}/export?format=markdown",
        headers={"x-tenant-id": "demo-brokerage"},
    )
    assert md_export.status_code == 200
    assert "Submission Summary" in md_export.text

    json_export = client.get(
        f"/api/v1/submissions/{submission_id}/export?format=json",
        headers={"x-tenant-id": "demo-brokerage"},
    )
    assert json_export.status_code == 200
    assert "profile" in json_export.json()

    pdf_export = client.get(
        f"/api/v1/submissions/{submission_id}/export?format=pdf",
        headers={"x-tenant-id": "demo-brokerage"},
    )
    assert pdf_export.status_code == 200
    assert pdf_export.headers["content-type"].startswith("application/pdf")
