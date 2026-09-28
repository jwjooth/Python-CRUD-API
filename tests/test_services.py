"""Service layer contract: payload in, response payload out, HTTP error mapping."""

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from payload.BookPayload import BookCreate, BookResponse, BookUpdate
from payload.CategoryPayload import CategoryCreate, CategoryResponse
from payload.ProductPayload import ProductCreate, ProductResponse
from service.BookService import BookService
from service.CategoryService import CategoryService
from service.ProductService import ProductService


def _category(session: Session, name: str = "Fiction") -> int:
    """Create a category through the service and return its ID for book fixtures."""
    return CategoryService(session).create(CategoryCreate(name=name)).id


def test_category_service_returns_response_payloads(db_session: Session):
    """Verify category operations return response payloads with normalized fields."""
    service = CategoryService(db_session)
    created = service.create(CategoryCreate(name="  Fantasy  "))

    assert isinstance(created, CategoryResponse)
    assert created.name == "Fantasy"
    assert created.created_at is not None and created.updated_at is not None
    assert isinstance(service.get_by_id(created.id), CategoryResponse)
    assert all(isinstance(item, CategoryResponse) for item in service.get_all(limit=10))

    updated = service.update(created.id, CategoryCreate(name="FANTASY II"))
    assert isinstance(updated, CategoryResponse)
    assert updated.name == "FANTASY II"


def test_product_service_maps_duplicates_to_409(db_session: Session):
    """Verify duplicate product creates and updates become HTTP 409 conflicts."""
    service = ProductService(db_session)
    payload = ProductCreate(name="Keyboard", price="49.99", stock=3)
    assert isinstance(service.create(payload), ProductResponse)

    with pytest.raises(HTTPException) as duplicate:
        service.create(ProductCreate(name="  kEyBoArD ", price="10.00", stock=1))
    assert duplicate.value.status_code == 409
    assert "kEyBoArD" in duplicate.value.detail

    with pytest.raises(HTTPException) as conflict:
        service.update(
            service.create(ProductCreate(name="Mouse", price="10.00", stock=1)).id,
            ProductCreate(name="KEYBOARD", price="10.00", stock=1),
        )
    assert conflict.value.status_code == 409


def test_product_service_missing_row_is_404(db_session: Session):
    """Verify product reads and deletes raise HTTP 404 for an absent row."""
    service = ProductService(db_session)
    with pytest.raises(HTTPException) as missing:
        service.get_by_id(4242)
    assert missing.value.status_code == 404
    with pytest.raises(HTTPException) as missing:
        service.delete(4242)
    assert missing.value.status_code == 404


def test_book_service_validates_category_reference(db_session: Session):
    """Verify creating a book with a missing category raises HTTP 400."""
    service = BookService(db_session)
    payload = BookCreate(category_id=999, title="Dune", author="Frank Herbert", stock=10)

    with pytest.raises(HTTPException) as invalid:
        service.create(payload)
    assert invalid.value.status_code == 400
    assert "999" in invalid.value.detail


def test_book_service_round_trip(db_session: Session):
    """Verify book payloads, updates, duplicate conflicts, and deletion through the service."""
    service = BookService(db_session)
    category_id = _category(db_session)

    created = service.create(
        BookCreate(category_id=category_id, title="  Dune  ", author="Frank Herbert", stock=10)
    )
    assert isinstance(created, BookResponse)
    assert created.title == "Dune"

    updated = service.update(
        created.id,
        BookUpdate(category_id=category_id, title="Dune Messiah", author="Frank Herbert", stock=2),
    )
    assert isinstance(updated, BookResponse)
    assert updated.title == "Dune Messiah"

    with pytest.raises(HTTPException) as duplicate:
        service.create(
            BookCreate(category_id=category_id, title="  dune mEssiah ", author="Other", stock=1)
        )
    assert duplicate.value.status_code == 409

    service.delete(created.id)
    with pytest.raises(HTTPException) as missing:
        service.get_by_id(created.id)
    assert missing.value.status_code == 404
