import pytest

from app.db.base import Base
from app.db.session import engine
from app.models import entities  # noqa: F401


@pytest.fixture(autouse=True)
def reset_db() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
