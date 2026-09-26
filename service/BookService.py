from fastapi import status
from sqlalchemy.orm import Session

from helper.exception import helperException
from payload.BookPayload import BookRequest, BookResponse
from repository.BookRepository import BookRepository


class BookService:
    def __init__(self, db: Session):
        self.repository = BookRepository(db)

    def get_all(self) -> list[BookResponse]:
        return self.repository.get_all()

    def get_by_id(self, id: int) -> BookResponse:
        book = self.repository.get_by_id(id)
        if book is None:
            helperException(
                status.HTTP_404_NOT_FOUND,
                f"Book with id {id} was not found.",
            )

    def get_by_title(self, title: str, exclude_id: int | None = None) -> BookResponse:
        book = self.repository.get_by_title(title, exclude_id)
        if book is None:
            helperException(
                status.HTTP_404_NOT_FOUND,
                f"Book with title {title} was not found.",
            )

    def create(self, request: BookRequest) -> BookResponse:
        if request.title is None or not request.title.strip():
            helperException(
                status.HTTP_404_NOT_FOUND,
                "Book title is required.",
            )
        if request.author is None or not request.author.strip():
            helperException(
                status.HTTP_404_NOT_FOUND,
                "Book author is required.",
            )
        if request.stock is None or request.stock <= 0:
            helperException(
                status.HTTP_404_NOT_FOUND,
                "Book stock is required and must be greater than zero.",
            )
        if request.price is None or request.price <= 0:
            helperException(
                status.HTTP_404_NOT_FOUND,
                "Book price is required and must be greater than zero",
            )
        if request.category_id is None or request.category_id <= 0:
            helperException(
                status.HTTP_404_NOT_FOUND,
                "Book category_id is required and must be greater than zero",
            )
        return self.repository.create(request)

    def update(self, id: int, request: BookRequest) -> BookResponse:
        self.get_by_id(id)
        if request.title is None or not request.title.strip():
            helperException(
                status.HTTP_404_NOT_FOUND,
                "Book title is required.",
            )
        if request.author is None or not request.author.strip():
            helperException(
                status.HTTP_404_NOT_FOUND,
                "Book author is required.",
            )
        if request.stock is None or request.stock <= 0:
            helperException(
                status.HTTP_404_NOT_FOUND,
                "Book stock is required and must be greater than zero.",
            )
        if request.price is None or request.price <= 0:
            helperException(
                status.HTTP_404_NOT_FOUND,
                "Book price is required and must be greater than zero",
            )
        if request.category_id is None or request.category_id <= 0:
            helperException(
                status.HTTP_404_NOT_FOUND,
                "Book category_id is required and must be greater than zero",
            )

        book = self.repository.update(id, request)
        if book is None:
            helperException(
                status.HTTP_404_NOT_FOUND,
                f"Book with id {id} was not found.",
            )

        return book

    def delete(self, id: int):
        deleted = self.repository.delete(id)
        if not deleted:
            helperException(
                status.HTTP_404_NOT_FOUND,
                f"Book with id {id} was not found.",
            )
