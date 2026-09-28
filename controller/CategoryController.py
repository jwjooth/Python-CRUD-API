"""Category HTTP endpoints. Thin: bind payloads, delegate, declare responses."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from database import get_db
from payload.BasePayload import PaginationPayload
from payload.CategoryPayload import CategoryCreate, CategoryResponse, CategoryUpdate
from service.CategoryService import CategoryService

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])

DbSession = Annotated[Session, Depends(get_db)]
PageParams = Annotated[PaginationPayload, Query()]
CategoryId = Annotated[int, Path(ge=1, description="Category id.")]


@router.get("", response_model=list[CategoryResponse], summary="List categories")
def get_categories(pagination: PageParams, db: DbSession) -> list[CategoryResponse]:
    return CategoryService(db).get_all(offset=pagination.offset, limit=pagination.limit)


@router.get("/{category_id}", response_model=CategoryResponse, summary="Get a category")
def get_category(category_id: CategoryId, db: DbSession) -> CategoryResponse:
    return CategoryService(db).get_by_id(category_id)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a category",
)
def create_category(payload: CategoryCreate, db: DbSession) -> CategoryResponse:
    return CategoryService(db).create(payload)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Replace a category",
)
def update_category(
    category_id: CategoryId, payload: CategoryUpdate, db: DbSession
) -> CategoryResponse:
    return CategoryService(db).update(category_id, payload)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a category",
)
def delete_category(category_id: CategoryId, db: DbSession) -> Response:
    CategoryService(db).delete(category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
