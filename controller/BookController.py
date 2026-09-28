"""Book HTTP endpoints. Thin: bind payloads, delegate, declare responses."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from database import get_db
from payload.BasePayload import PaginationPayload
from payload.BookPayload import BookCreate, BookResponse, BookUpdate
from service.BookService import BookService

router = APIRouter(prefix="/api/v1/books", tags=["books"])

DbSession = Annotated[Session, Depends(get_db)]
PageParams = Annotated[PaginationPayload, Query()]
BookId = Annotated[int, Path(ge=1, description="Book id.")]


@router.get("", response_model=list[BookResponse], summary="List books")
def get_books(pagination: PageParams, db: DbSession) -> list[BookResponse]:
    """Return a page of books ordered by ID."""
    return BookService(db).get_all(offset=pagination.offset, limit=pagination.limit)


@router.get("/{book_id}", response_model=BookResponse, summary="Get a book")
def get_book(book_id: BookId, db: DbSession) -> BookResponse:
    """Return the book with the given ID, or raise HTTP 404."""
    return BookService(db).get_by_id(book_id)


@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a book",
)
def create_book(payload: BookCreate, db: DbSession) -> BookResponse:
    """Create a book from the validated request and return its representation."""
    return BookService(db).create(payload)


@router.put(
    "/{book_id}",
    response_model=BookResponse,
    summary="Replace a book",
)
def update_book(book_id: BookId, payload: BookUpdate, db: DbSession) -> BookResponse:
    """Replace the book fields from the validated request, or raise HTTP 404."""
    return BookService(db).update(book_id, payload)


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a book",
)
def delete_book(book_id: BookId, db: DbSession) -> Response:
    """Delete the book and return an empty HTTP 204 response, or raise HTTP 404."""
    BookService(db).delete(book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
