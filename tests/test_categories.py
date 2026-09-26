from fastapi.testclient import TestClient


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
