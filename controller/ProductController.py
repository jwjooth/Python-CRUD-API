from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from database import get_db
from payload.ProductPayload import ProductRequest, ProductResponse
from service.ProductService import ProductService

router = APIRouter(prefix="/api/v1/products", tags=["products"])


@router.get("", response_model=list[ProductResponse])
def get_all(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.get_all(offset, limit)


@router.get("/{id}", response_model=ProductResponse)
def get_by_id(id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_by_id(id)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create(request: ProductRequest, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.create(request)


@router.put("/{id}", response_model=ProductResponse)
def update(id: int, request: ProductRequest, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.update(id, request)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    service.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
