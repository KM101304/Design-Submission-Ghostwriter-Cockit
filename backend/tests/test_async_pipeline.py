from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.schemas.pipeline import PipelineResponse


def test_pipeline_run_async_accepts_job(client: TestClient, auth_headers: dict[str, str], monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.routes.pipeline.process_submission_task.apply_async",
        lambda task_id, kwargs: SimpleNamespace(id=task_id),
    )

    response = client.post(
        "/api/v1/pipeline/run-async",
        files={"file": ("submission.txt", b"Insured: Demo", "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["job_id"].startswith("job_")
    assert "submission_id" in response.json()


def test_pipeline_job_status_succeeded(client: TestClient, auth_headers: dict[str, str], monkeypatch) -> None:
    result = PipelineResponse.model_validate(
        {
            "profile": {
                "submission_id": "sub_x",
                "insured_name": "Demo Co",
                "entity_type": None,
                "revenue": None,
                "payroll": None,
                "locations": [],
                "prior_losses": [],
                "lines_of_business": ["GL"],
                "coverage_requested": [],
                "underwriting_flags": [],
                "contradictions": [],
                "source_citations": {},
                "field_confidence": {},
                "version": 1,
                "updated_at": "2026-02-18T00:00:00Z",
                "metadata": {},
            },
            "completeness": [
                {
                    "line_of_business": "GL",
                    "completeness_score": 75,
                    "status": "Yellow",
                    "missing_fields": ["locations"],
                    "blockers": ["Missing required field: locations"],
                }
            ],
            "questions": {
                "grouped_questions": {"GL": ["Please confirm all operating locations, including complete addresses."]},
                "email_draft": "draft",
                "bullet_summary": ["Please confirm all operating locations, including complete addresses."],
                "plain_english": "plain",
            },
        }
    )

    result_payload = result.model_dump(mode="json")

    class FakeResult:
        status = "SUCCESS"
        result = result_payload

        def successful(self) -> bool:
            return True

        def failed(self) -> bool:
            return False

    monkeypatch.setattr("app.api.routes.pipeline.celery_app.AsyncResult", lambda _job_id: FakeResult())

    response = client.get("/api/v1/pipeline/jobs/job-123", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "succeeded"
    assert payload["result"]["profile"]["submission_id"] == "sub_x"
