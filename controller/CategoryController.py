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
    """Return a page of categories ordered by ID."""
    return CategoryService(db).get_all(offset=pagination.offset, limit=pagination.limit)


@router.get("/{category_id}", response_model=CategoryResponse, summary="Get a category")
def get_category(category_id: CategoryId, db: DbSession) -> CategoryResponse:
    """Return the category with the given ID, or raise HTTP 404."""
    return CategoryService(db).get_by_id(category_id)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a category",
)
def create_category(payload: CategoryCreate, db: DbSession) -> CategoryResponse:
    """Create a category from the validated request and return its representation."""
    return CategoryService(db).create(payload)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Replace a category",
)
def update_category(
    category_id: CategoryId, payload: CategoryUpdate, db: DbSession
) -> CategoryResponse:
    """Replace the category fields from the validated request, or raise HTTP 404."""
    return CategoryService(db).update(category_id, payload)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a category",
)
def delete_category(category_id: CategoryId, db: DbSession) -> Response:
    """Delete the category and return an empty HTTP 204 response, or raise HTTP 404."""
    CategoryService(db).delete(category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
