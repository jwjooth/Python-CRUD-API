"""Book business rules: existence (404), unique-title conflicts (409), and a
validated category reference (400)."""

from sqlalchemy.orm import Session

from entity.BookEntity import Book
from payload.BookPayload import BookCreate, BookResponse, BookUpdate
from repository.BookRepository import BookRepository
from repository.CategoryRepository import CategoryRepository
from utils import (
    DuplicateValueError,
    RelatedRecordMissingError,
    bad_request,
    conflict,
    not_found,
)


class BookService:
    def __init__(self, db: Session) -> None:
        """Bind book and category repositories to the supplied database session."""
        self.repository = BookRepository(db)
        self.categories = CategoryRepository(db)

    def get_all(self, *, offset: int = 0, limit: int = 100) -> list[BookResponse]:
        """Return an ID-ordered page of book response payloads."""
        books = self.repository.get_all(offset=offset, limit=limit)
        return [BookResponse.model_validate(book) for book in books]

    def get_by_id(self, book_id: int) -> BookResponse:
        """Return the book response payload, or raise HTTP 404 if absent."""
        return BookResponse.model_validate(self._require(book_id))

    def create(self, payload: BookCreate) -> BookResponse:
        """Create a book and return its response payload.

        Raise HTTP 400 for a missing category or 409 for a duplicate title."""
        self._require_category(payload.category_id)
        try:
            book = self.repository.create(payload)
        except DuplicateValueError:
            conflict(self._duplicate_message(payload.title))
        except RelatedRecordMissingError:
            bad_request(self._unknown_category_message(payload.category_id))
        return BookResponse.model_validate(book)

    def update(self, book_id: int, payload: BookUpdate) -> BookResponse:
        """Replace book fields and return the updated response payload.

        Raise HTTP 404 for a missing book, 400 for a missing category, or
        409 for a duplicate title."""
        book = self._require(book_id)
        self._require_category(payload.category_id)
        try:
            book = self.repository.update(book, payload)
        except DuplicateValueError:
            conflict(self._duplicate_message(payload.title))
        except RelatedRecordMissingError:
            bad_request(self._unknown_category_message(payload.category_id))
        return BookResponse.model_validate(book)

    def delete(self, book_id: int) -> None:
        """Delete the book, or raise HTTP 404 if it does not exist."""
        self.repository.delete(self._require(book_id))

    def _require(self, book_id: int) -> Book:
        """Return the book entity, or raise HTTP 404 if it does not exist."""
        book = self.repository.get_by_id(book_id)
        if book is None:
            not_found("Book", book_id)
        return book

    def _require_category(self, category_id: int) -> None:
        """Raise HTTP 400 if the referenced category does not exist."""
        # Checked explicitly so the API behaves identically on backends that do
        # not enforce the books.category_id foreign key (e.g. SQLite).
        if self.categories.get_by_id(category_id) is None:
            bad_request(self._unknown_category_message(category_id))

    @staticmethod
    def _duplicate_message(title: str) -> str:
        """Format the conflict detail for a duplicate book title."""
        return f"Book with title {title} already exists."

    @staticmethod
    def _unknown_category_message(category_id: int) -> str:
        """Format the error detail for a missing category reference."""
        return f"category_id {category_id} does not reference an existing category."
