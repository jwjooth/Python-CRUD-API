"""Product HTTP endpoints. Thin: bind payloads, delegate, declare responses."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from database import get_db
from payload.BasePayload import PaginationPayload
from payload.ProductPayload import ProductCreate, ProductResponse, ProductUpdate
from service.ProductService import ProductService

router = APIRouter(prefix="/api/v1/products", tags=["products"])

DbSession = Annotated[Session, Depends(get_db)]
PageParams = Annotated[PaginationPayload, Query()]
ProductId = Annotated[int, Path(ge=1, description="Product id.")]


@router.get("", response_model=list[ProductResponse], summary="List products")
def get_products(pagination: PageParams, db: DbSession) -> list[ProductResponse]:
    return ProductService(db).get_all(offset=pagination.offset, limit=pagination.limit)


@router.get("/{product_id}", response_model=ProductResponse, summary="Get a product")
def get_product(product_id: ProductId, db: DbSession) -> ProductResponse:
    return ProductService(db).get_by_id(product_id)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a product",
)
def create_product(payload: ProductCreate, db: DbSession) -> ProductResponse:
    return ProductService(db).create(payload)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Replace a product",
)
def update_product(product_id: ProductId, payload: ProductUpdate, db: DbSession) -> ProductResponse:
    return ProductService(db).update(product_id, payload)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a product",
)
def delete_product(product_id: ProductId, db: DbSession) -> Response:
    ProductService(db).delete(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
