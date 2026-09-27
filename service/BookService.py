from payload.BookPayload import BookRequest
from repository.BookRepository import BookRepository
from utils import conflict, not_found


class BookService:
    def __init__(self, db):
        self.repository = BookRepository(db)

    def get_all(self, offset: int = 0, limit: int = 100):
        return self.repository.get_all(offset, limit)

    def get_by_id(self, book_id: int):
        book = self.repository.get_by_id(book_id)
        if book is None:
            not_found("Book", book_id)
        return book

    def create(self, request: BookRequest):
        if self.repository.get_by_title(request.title.strip()):
            conflict(f"Book with title {request.title.strip()} already exists.")
        return self.repository.create(request)

    def update(self, book_id: int, request: BookRequest):
        self.get_by_id(book_id)
        if self.repository.get_by_title(request.title.strip(), exclude_id=book_id):
            conflict(f"Book with title {request.title.strip()} already exists.")
        book = self.repository.update(book_id, request)
        if book is None:
            not_found("Book", book_id)
        return book

    def delete(self, book_id: int):
        deleted = self.repository.delete(book_id)
        if not deleted:
            not_found("Book", book_id)
