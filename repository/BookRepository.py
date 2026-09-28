"""Book persistence."""

from typing import ClassVar

from entity.BookEntity import Book
from payload.BookPayload import BookCreate, BookUpdate
from repository.BaseRepository import BaseRepository


class BookRepository(BaseRepository[Book]):
    """Row access for `books`."""

    model: ClassVar[type[Book]] = Book
    unique_index: ClassVar[str] = "uq_book_title_normalized"

    def create(self, payload: BookCreate) -> Book:
        return self.add(**payload.model_dump())

    def update(self, book: Book, payload: BookUpdate) -> Book:
        return self.save(book, **payload.model_dump())
