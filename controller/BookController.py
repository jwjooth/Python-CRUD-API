from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from database import get_db
from payload.BookPayload import BookRequest, BookResponse
from service.BookService import BookService

router = APIRouter(prefix="/api/v1/books", tags=["books"])


@router.get("", response_model=list[BookResponse])
def get_all(db: Session = Depends(get_db)) -> list[BookResponse]:
    service = BookService(db)
    return service.get_all()


@router.get("/{id}", response_model=BookResponse)
def get_by_id(id: int, db: Session = Depends(get_db)) -> BookResponse:
    service = BookService(db)
    return service.get_by_id(id)


@router.get("/{title}", response_model=BookResponse)
def get_by_name(
    title: str, exclude_id: int, db: Session = Depends(get_db)
) -> BookResponse:
    service = BookService(db)
    return service.get_by_title(title, exclude_id)


@router.post("", response_model=BookResponse)
def create(request: BookRequest, db: Session = Depends(get_db)) -> BookResponse:
    service = BookService(db)
    return service.create(request)


@router.put("/${id}", response_model=BookResponse)
def update(
    id: int, request: BookRequest, db: Session = Depends(get_db)
) -> BookResponse:
    service = BookService(db)
    return service.update(id, request)


@router.delete("/${id}", response_model=BookResponse)
def delete(id: int, db: Session = Depends(get_db)) -> Response:
    service = BookService(db)
    service.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
