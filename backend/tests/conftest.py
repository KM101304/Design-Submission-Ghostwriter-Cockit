import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["AUTH_SECRET_KEY"] = "test-secret"
os.environ["AUTH_PASSWORD_SALT"] = "test-salt"
os.environ["AUTH_DISABLED"] = "false"
os.environ["AUTH_SEED_EMAIL"] = "admin@ghostwriter.dev"
os.environ["AUTH_SEED_PASSWORD"] = "ChangeMe123!"
os.environ["AUTH_SEED_TENANT_ID"] = "demo-brokerage"

import pytest
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import engine
from app.main import app
from app.models import entities  # noqa: F401


@pytest.fixture(autouse=True)
def reset_db() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ghostwriter.dev", "password": "ChangeMe123!"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {
        "Authorization": f"Bearer {token}",
        "x-tenant-id": "demo-brokerage",
    }
