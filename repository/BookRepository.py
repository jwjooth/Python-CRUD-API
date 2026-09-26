from sqlalchemy import func, select
from sqlalchemy.orm import Session

from entity.BookEntity import Book
from payload.BookPayload import BookRequest


class BookRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        query = select(Book).order_by(Book.id)
        return self.db.execute(query).scalars().all()

    def get_by_id(self, id: int):
        return self.db.get(Book, id)

    def get_by_title(self, title: str, exclude_id: int | None = None):
        query = select(Book).where(func.lower(Book.title) == func.lower(title))
        if exclude_id is not None:
            query = query.where(Book.id != exclude_id)
        return self.db.execute(query).scalars().all()

    def create(self, request: BookRequest):
        book = Book(request)
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def update(self, id: int, request: BookRequest):
        book = self.get_by_id(id)
        if book is None:
            return None
        if request.author is not None:
            book.author = request.author
        if request.title is not None:
            book.title = request.title
        if request.category_id is not None:
            book.category_id = request.category_id
        if request.stock is not None:
            book.stock = request.stock

        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def delete(self, id: int):
        book = self.get_by_id(id)
        if book is None:
            return False
        self.db.delete(book)
        self.db.commit()
        return True
