from fastapi.testclient import TestClient

from tests.conftest import _book_payload


def test_book_crud_lifecycle(client: TestClient, category_id: int):
    # Create
    response = client.post("/api/v1/books", json=_book_payload(category_id))
    assert response.status_code == 201, response.text
    book = response.json()
    assert book["title"] == "Dune"
    assert book["category_id"] == category_id
    book_id = book["id"]

    # Read by id
    response = client.get(f"/api/v1/books/{book_id}")
    assert response.status_code == 200, response.text
    assert response.json()["id"] == book_id

    # List
    response = client.get("/api/v1/books", params={"offset": 0, "limit": 100})
    assert response.status_code == 200, response.text
    assert any(item["id"] == book_id for item in response.json())

    # Update
    response = client.put(
        f"/api/v1/books/{book_id}",
        json=_book_payload(category_id, title="Dune Messiah", stock=5),
    )
    assert response.status_code == 200, response.text
    assert response.json()["title"] == "Dune Messiah"
    assert response.json()["stock"] == 5

    # Delete returns 204 with empty body
    response = client.delete(f"/api/v1/books/{book_id}")
    assert response.status_code == 204, response.text

    # Gone afterwards
    response = client.get(f"/api/v1/books/{book_id}")
    assert response.status_code == 404


def test_book_duplicate_title_conflict(client: TestClient, category_id: int):
    response = client.post("/api/v1/books", json=_book_payload(category_id, title="Dune"))
    assert response.status_code == 201, response.text

    # Exact duplicate
    response = client.post("/api/v1/books", json=_book_payload(category_id, title="Dune"))
    assert response.status_code == 409, response.text

    # Case-insensitive + whitespace-insensitive duplicate
    response = client.post("/api/v1/books", json=_book_payload(category_id, title="  dUnE  "))
    assert response.status_code == 409, response.text


def test_book_update_title_conflict(client: TestClient, category_id: int):
    first = client.post("/api/v1/books", json=_book_payload(category_id, title="Dune"))
    second = client.post("/api/v1/books", json=_book_payload(category_id, title="Foundation"))
    assert first.status_code == 201 and second.status_code == 201
    second_id = second.json()["id"]

    response = client.put(
        f"/api/v1/books/{second_id}", json=_book_payload(category_id, title="dune")
    )
    assert response.status_code == 409, response.text


def test_book_not_found(client: TestClient):
    assert client.get("/api/v1/books/9999").status_code == 404
    assert client.delete("/api/v1/books/9999").status_code == 404


def test_book_validation(client: TestClient, category_id: int):
    # Negative price rejected by Pydantic (422)
    response = client.post("/api/v1/books", json=_book_payload(category_id, price="-1.00"))
    assert response.status_code == 422, response.text

    # Negative stock rejected by Pydantic (422)
    response = client.post("/api/v1/books", json=_book_payload(category_id, stock=-1))
    assert response.status_code == 422, response.text

    # Missing required field
    payload = _book_payload(category_id)
    del payload["title"]
    response = client.post("/api/v1/books", json=payload)
    assert response.status_code == 422, response.text
