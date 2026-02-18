from fastapi.testclient import TestClient


def test_login_success(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ghostwriter.dev", "password": "ChangeMe123!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_tenant_mismatch_forbidden(client: TestClient, auth_headers: dict[str, str]) -> None:
    headers = dict(auth_headers)
    headers["x-tenant-id"] = "other-tenant"
    response = client.get("/api/v1/submissions", headers=headers)
    assert response.status_code == 403
