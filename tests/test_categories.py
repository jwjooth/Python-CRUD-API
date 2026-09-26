from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pymysql.err import IntegrityError as MySQLIntegrityError
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from entity.CategoryEntity import Category
from repository.CategoryRepository import CategoryRepository


def test_category_crud_lifecycle(client: TestClient):
    response = client.post("/api/v1/categories", json={"name": "Sci-Fi"})
    assert response.status_code == 201, response.text
    category_id = response.json()["id"]

    response = client.get(f"/api/v1/categories/{category_id}")
    assert response.status_code == 200, response.text

    response = client.put(f"/api/v1/categories/{category_id}", json={"name": "Science Fiction"})
    assert response.status_code == 200, response.text
    assert response.json()["name"] == "Science Fiction"

    response = client.delete(f"/api/v1/categories/{category_id}")
    assert response.status_code == 204, response.text
    assert client.get(f"/api/v1/categories/{category_id}").status_code == 404


def test_category_duplicate_name_conflict(client: TestClient):
    response = client.post("/api/v1/categories", json={"name": "Horror"})
    assert response.status_code == 201, response.text

    response = client.post("/api/v1/categories", json={"name": "Horror"})
    assert response.status_code == 409, response.text


def test_category_duplicate_case_insensitive_conflict(client: TestClient):
    response = client.post("/api/v1/categories", json={"name": "Fantasy"})
    assert response.status_code == 201, response.text

    # Service trims + repository compares func.lower -> 409
    response = client.post("/api/v1/categories", json={"name": "  fAnTaSy  "})
    assert response.status_code == 409, response.text


def test_category_update_name_conflict(client: TestClient):
    first = client.post("/api/v1/categories", json={"name": "History"})
    second = client.post("/api/v1/categories", json={"name": "Biography"})
    assert first.status_code == 201 and second.status_code == 201

    response = client.put(f"/api/v1/categories/{second.json()['id']}", json={"name": "history"})
    assert response.status_code == 409, response.text


def test_category_not_found(client: TestClient):
    assert client.get("/api/v1/categories/9999").status_code == 404
    assert client.delete("/api/v1/categories/9999").status_code == 404


@pytest.mark.parametrize("operation", ["create", "update"])
def test_category_conflict_after_precheck(client: TestClient, monkeypatch, operation):
    client.post("/api/v1/categories", json={"name": "Fantasy"})
    second = client.post("/api/v1/categories", json={"name": "History"}).json()["id"]
    # Simulate a concurrent writer winning after the service's duplicate check.
    monkeypatch.setattr(CategoryRepository, "get_by_name", lambda *args, **kwargs: None)
    if operation == "create":
        response = client.post("/api/v1/categories", json={"name": "FANTASY"})
    else:
        response = client.put(f"/api/v1/categories/{second}", json={"name": "FANTASY"})
    assert response.status_code == 409, response.text
    assert response.json()["detail"] == "Category name already exists."


@pytest.mark.parametrize("operation", ["create", "update"])
def test_category_conflict_rolls_back_session(operation):
    engine = create_engine("sqlite://")
    Category.__table__.create(engine)
    with Session(engine) as session:
        repository = CategoryRepository(session)
        repository.create("Fantasy")
        second = repository.create("History")
        with pytest.raises(HTTPException) as conflict:
            if operation == "create":
                repository.create("FANTASY")
            else:
                repository.update(second.id, "FANTASY")
        assert conflict.value.status_code == 409
        assert repository.get_by_id(second.id).name == "History"
        assert repository.create("Biography").name == "Biography"
    engine.dispose()


@pytest.mark.parametrize("operation", ["create", "update"])
@pytest.mark.parametrize(
    "code, message, conflict",
    [
        (1062, "Duplicate entry 'fantasy' for key 'uq_category_name_normalized'", True),
        (1062, "Duplicate entry 'fantasy' for key 'categories.uq_category_name_normalized'", True),
        (1062, "Duplicate entry 'uq_category_name_normalized' for key 'other_index'", False),
        (1048, "Column 'name' cannot be null", False),
    ],
)
def test_category_mysql_integrity_errors(operation, code, message, conflict):
    session = Mock()
    error = IntegrityError("statement", {}, MySQLIntegrityError(code, message))
    session.commit.side_effect = error
    repository = CategoryRepository(session)
    with pytest.raises(HTTPException if conflict else IntegrityError) as caught:
        if operation == "create":
            repository.create("Fantasy")
        else:
            repository.update(1, "Fantasy")
    if conflict:
        assert caught.value.status_code == 409
        assert caught.value.detail == "Category name already exists."
        session.rollback.assert_called_once_with()
    else:
        assert caught.value is error
        session.rollback.assert_not_called()
