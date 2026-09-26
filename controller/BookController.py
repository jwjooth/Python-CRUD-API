from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from database import get_db
from payload.BookPayload import BookRequest, BookResponse
from service.BookService import BookService

router = APIRouter(prefix="/api/v1/books", tags=["books"])


@router.get("", response_model=list[BookResponse])
def get_books(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = BookService(db)
    return service.get_all(offset, limit)


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    service = BookService(db)
    return service.get_by_id(book_id)


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(request: BookRequest, db: Session = Depends(get_db)):
    service = BookService(db)
    return service.create(request)


@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, request: BookRequest, db: Session = Depends(get_db)):
    service = BookService(db)
    return service.update(book_id, request)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    service = BookService(db)
    service.delete(book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
