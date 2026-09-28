"""API contract: strict payloads, shared pagination, path bounds, health."""

from fastapi.testclient import TestClient

from tests.conftest import _book_payload, _product_payload


def test_health_endpoint(client: TestClient):
    """Verify the health response contains the expected status and welcome message."""
    response = client.get("/")
    assert response.status_code == 200, response.text
    assert response.json() == {"status": "ok", "message": "Welcome to the Products API"}


def test_unknown_body_field_is_rejected(client: TestClient, category_id: int):
    """`extra="forbid"` turns stale clients and typos into 422 instead of silent drops."""
    response = client.post("/api/v1/categories", json={"name": "Sci-Fi", "colour": "red"})
    assert response.status_code == 422, response.text
    assert response.json()["detail"][0]["type"] == "extra_forbidden"

    response = client.post("/api/v1/products", json={**_product_payload(), "colour": "red"})
    assert response.status_code == 422, response.text

    response = client.post("/api/v1/books", json={**_book_payload(category_id), "isbn": "1"})
    assert response.status_code == 422, response.text


def test_names_are_trimmed_at_the_edge(client: TestClient):
    """Verify category requests remove surrounding whitespace from names."""
    response = client.post("/api/v1/categories", json={"name": "  Sci-Fi  "})
    assert response.status_code == 201, response.text
    assert response.json()["name"] == "Sci-Fi"


def test_pagination_bounds(client: TestClient):
    """Verify list endpoints enforce the shared offset and limit bounds."""
    assert client.get("/api/v1/categories", params={"offset": 0, "limit": 100}).status_code == 200
    assert client.get("/api/v1/categories", params={"offset": -1}).status_code == 422
    assert client.get("/api/v1/categories", params={"limit": 0}).status_code == 422
    assert client.get("/api/v1/categories", params={"limit": 101}).status_code == 422
    assert client.get("/api/v1/products", params={"limit": 101}).status_code == 422
    assert client.get("/api/v1/books", params={"limit": 101}).status_code == 422


def test_unknown_query_parameter_is_rejected(client: TestClient):
    """Verify unknown pagination query parameters produce HTTP 422."""
    assert client.get("/api/v1/categories", params={"offset": 0, "page": 1}).status_code == 422


def test_path_ids_must_be_positive_integers(client: TestClient):
    """Verify resource lookups reject zero and non-integer path IDs."""
    for path in ("/api/v1/categories", "/api/v1/products", "/api/v1/books"):
        assert client.get(f"{path}/0").status_code == 422
        assert client.get(f"{path}/abc").status_code == 422


def test_pagination_slices_and_orders_results(client: TestClient):
    """Verify category pagination applies offset and limit in ID order."""
    for index in range(5):
        assert client.post("/api/v1/categories", json={"name": f"Name {index}"}).status_code == 201

    page = client.get("/api/v1/categories", params={"offset": 1, "limit": 2}).json()
    assert [item["name"] for item in page] == ["Name 1", "Name 2"]


def test_large_responses_are_compressed(client: TestClient):
    """Verify large product lists use gzip when the client accepts it."""
    for index in range(20):
        client.post("/api/v1/products", json=_product_payload(name=f"Product {index}"))

    response = client.get("/api/v1/products", headers={"accept-encoding": "gzip"})
    assert response.status_code == 200, response.text
    assert response.headers.get("content-encoding") == "gzip"
