import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DB = Path(__file__).parent / "test.db"
os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{TEST_DB.as_posix()}"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000"
os.environ["TESTING"] = "1"

from app.main import app
from app.database.base import Base
from app.database.session import engine


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    if TEST_DB.exists():
        TEST_DB.unlink()
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
