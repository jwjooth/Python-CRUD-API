from fastapi.testclient import TestClient


def _product_payload(name: str = "Keyboard", **overrides):
    payload = {
        "name": name,
        "description": "Mechanical keyboard",
        "price": "49.99",
        "stock": 10,
    }
    payload.update(overrides)
    return payload


def test_product_crud_lifecycle(client: TestClient):
    response = client.post("/api/v1/products", json=_product_payload())
    assert response.status_code == 201, response.text
    product_id = response.json()["id"]

    response = client.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 200, response.text

    response = client.put(f"/api/v1/products/{product_id}", json=_product_payload(stock=7))
    assert response.status_code == 200, response.text
    assert response.json()["stock"] == 7

    response = client.delete(f"/api/v1/products/{product_id}")
    assert response.status_code == 204, response.text
    assert client.get(f"/api/v1/products/{product_id}").status_code == 404


def test_product_duplicate_name_conflict(client: TestClient):
    response = client.post("/api/v1/products", json=_product_payload(name="Mouse"))
    assert response.status_code == 201, response.text

    response = client.post("/api/v1/products", json=_product_payload(name="  mOuSe  "))
    assert response.status_code == 409, response.text


def test_product_stock_validation(client: TestClient):
    # Negative stock is rejected before reaching the DB (Pydantic 422).
    response = client.post("/api/v1/products", json=_product_payload(stock=-1))
    assert response.status_code == 422, response.text

    response = client.post("/api/v1/products", json=_product_payload(stock=0))
    assert response.status_code == 201, response.text
    assert response.json()["stock"] == 0
    product_id = response.json()["id"]

    response = client.put(f"/api/v1/products/{product_id}", json=_product_payload(stock=5))
    assert response.status_code == 200, response.text
    response = client.put(f"/api/v1/products/{product_id}", json=_product_payload(stock=0))
    assert response.status_code == 200, response.text
    assert response.json()["stock"] == 0
    response = client.put(f"/api/v1/products/{product_id}", json=_product_payload(stock=-1))
    assert response.status_code == 422, response.text


def test_product_price_validation(client: TestClient):
    response = client.post("/api/v1/products", json=_product_payload(price="-5.00"))
    assert response.status_code == 422, response.text

    response = client.post("/api/v1/products", json=_product_payload(price="0.00"))
    assert response.status_code == 422, response.text


def test_product_not_found(client: TestClient):
    assert client.get("/api/v1/products/9999").status_code == 404
    assert client.delete("/api/v1/products/9999").status_code == 404
