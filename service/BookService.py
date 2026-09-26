from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from payload.BookPayload import BookRequest
from repository.BookRepository import BookRepository


class BookService:
    def __init__(self, db: Session):
        self.repository = BookRepository(db)

    def get_all(self, offset: int = 0, limit: int = 100):
        return self.repository.get_all(offset, limit)

    def get_by_id(self, book_id: int):
        book = self.repository.get_by_id(book_id)
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with id {book_id} was not found.",
            )
        return book

    def create(self, request: BookRequest):
        if self.repository.get_by_title(request.title.strip()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Book with title {request.title.strip()} already exists.",
            )
        return self.repository.create(request)

    def update(self, book_id: int, request: BookRequest):
        self.get_by_id(book_id)
        if self.repository.get_by_title(request.title.strip(), exclude_id=book_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Book with title {request.title.strip()} already exists.",
            )
        book = self.repository.update(book_id, request)
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with id {book_id} was not found.",
            )
        return book

    def delete(self, book_id: int):
        deleted = self.repository.delete(book_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with id {book_id} was not found.",
            )
