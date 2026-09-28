"""Book request/response payloads."""

from datetime import datetime

from pydantic import Field

from payload.BasePayload import RequestPayload, ResponsePayload


class BookFields(RequestPayload):
    """Fields shared by book creation and update."""

    category_id: int = Field(..., gt=0, description="Existing category id.")
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique title, compared case-insensitively.",
        examples=["Dune"],
    )
    author: str = Field(..., min_length=1, max_length=255, examples=["Frank Herbert"])
    stock: int = Field(..., ge=0, description="Copies currently in stock.")


class BookCreate(BookFields):
    """Body of `POST /api/v1/books`."""


class BookUpdate(BookFields):
    """Body of `PUT /api/v1/books/{book_id}`."""


class BookResponse(ResponsePayload):
    """Representation of a book."""

    id: int
    category_id: int
    title: str
    author: str
    stock: int
    created_at: datetime
    updated_at: datetime
