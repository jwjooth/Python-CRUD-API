"""Category business rules: existence (404) and unique-name conflicts (409)."""

from sqlalchemy.orm import Session

from entity.CategoryEntity import Category
from payload.CategoryPayload import CategoryCreate, CategoryResponse, CategoryUpdate
from repository.CategoryRepository import CategoryRepository
from utils import DuplicateValueError, conflict, not_found

_DUPLICATE_MESSAGE = "Category name already exists."


class CategoryService:
    def __init__(self, db: Session) -> None:
        self.repository = CategoryRepository(db)

    def get_all(self, *, offset: int = 0, limit: int = 100) -> list[CategoryResponse]:
        categories = self.repository.get_all(offset=offset, limit=limit)
        return [CategoryResponse.model_validate(category) for category in categories]

    def get_by_id(self, category_id: int) -> CategoryResponse:
        return CategoryResponse.model_validate(self._require(category_id))

    def create(self, payload: CategoryCreate) -> CategoryResponse:
        try:
            category = self.repository.create(payload.name)
        except DuplicateValueError:
            conflict(_DUPLICATE_MESSAGE)
        return CategoryResponse.model_validate(category)

    def update(self, category_id: int, payload: CategoryUpdate) -> CategoryResponse:
        category = self._require(category_id)
        try:
            category = self.repository.update(category, payload.name)
        except DuplicateValueError:
            conflict(_DUPLICATE_MESSAGE)
        return CategoryResponse.model_validate(category)

    def delete(self, category_id: int) -> None:
        self.repository.delete(self._require(category_id))

    def _require(self, category_id: int) -> Category:
        category = self.repository.get_by_id(category_id)
        if category is None:
            not_found("Category", category_id)
        return category
