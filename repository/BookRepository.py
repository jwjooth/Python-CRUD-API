from sqlalchemy import func, select
from sqlalchemy.orm import Session

from entity.BookEntity import Book
from payload.BookPayload import BookRequest


class BookRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, offset: int = 0, limit: int = 100):
        query = select(Book).order_by(Book.id).offset(offset).limit(limit)
        return self.db.execute(query).scalars().all()

    def get_by_id(self, book_id: int):
        return self.db.get(Book, book_id)

    def get_by_title(self, title: str, exclude_id: int | None = None):
        query = select(Book).where(func.lower(Book.title) == title.lower())
        if exclude_id is not None:
            query = query.where(Book.id != exclude_id)
        return self.db.execute(query).scalar_one_or_none()

    def create(self, request: BookRequest):
        data = request.model_dump()
        book = Book(**data)
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def update(self, book_id: int, request: BookRequest):
        book = self.get_by_id(book_id)
        if book is None:
            return None
        data = request.model_dump()
        book.category_id = data["category_id"]
        book.title = data["title"]
        book.author = data["author"]
        book.price = data["price"]
        book.stock = data["stock"]
        self.db.commit()
        self.db.refresh(book)
        return book

    def delete(self, book_id: int):
        book = self.get_by_id(book_id)
        if book is None:
            return False
        self.db.delete(book)
        self.db.commit()
        return True
