"""Shared pytest fixtures: SQLite-backed TestClient with get_db override.

The production app requires MySQL (see database.py / config/config.py), which is
not available in unit-test / CI environments. These fixtures spin up an
in-memory SQLite database, create all tables, and override the get_db
dependency so endpoint tests run hermetically via FastAPI's TestClient.
"""

import os

# Dummy MySQL settings must exist before database/main are imported, because
# CommonSettings() requires DB_* at import time. create_engine() itself is lazy
# and never connects, so dummy values are safe here.
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "3306")
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_NAME", "test")

from contextlib import asynccontextmanager  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

# Register entity tables on Base.metadata.
import entity.BookEntity  # noqa: E402, F401
import entity.CategoryEntity  # noqa: E402, F401
import entity.ProductEntity  # noqa: E402, F401
from database import Base, get_db  # noqa: E402
from main import app  # noqa: E402

TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@asynccontextmanager
async def _noop_lifespan(app):
    yield


# Skip main.lifespan in tests: it would try to create tables on the (dummy)
# MySQL engine. Tables are created on the SQLite test_engine per-test instead.
# (starlette>=0.37 TestClient always runs lifespan on __enter__.)
app.router.lifespan_context = _noop_lifespan


@pytest.fixture()
def client():
    """Fresh TestClient with empty tables for every test."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def category_id(client: TestClient) -> int:
    response = client.post("/api/v1/categories", json={"name": "Fiction"})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _book_payload(category_id: int, title: str = "Dune", **overrides):
    payload = {
        "category_id": category_id,
        "title": title,
        "author": "Frank Herbert",
        "price": "19.99",
        "stock": 10,
    }
    payload.update(overrides)
    return payload
