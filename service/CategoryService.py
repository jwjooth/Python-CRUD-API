from payload.CategoryPayload import CategoryCreate, CategoryUpdate
from repository.CategoryRepository import CategoryRepository
from utils import conflict, not_found, require_string


class CategoryService:
    def __init__(self, db):
        self.repository = CategoryRepository(db)

    def get_all(self, offset: int = 0, limit: int = 100):
        return self.repository.get_all(offset=offset, limit=limit)

    def get_by_id(self, category_id: int):
        category = self.repository.get_by_id(category_id)
        if category is None:
            not_found("Category", category_id)
        return category

    def create(self, payload: CategoryCreate):
        require_string(payload.name, "Category name")
        if self.repository.get_by_name(payload.name.strip()):
            conflict("Category name already exists.")
        return self.repository.create(payload.name.strip())

    def update(self, category_id: int, payload: CategoryUpdate):
        self.get_by_id(category_id)
        require_string(payload.name, "Category name")
        if self.repository.get_by_name(payload.name.strip(), exclude_id=category_id):
            conflict("Category name already exists.")
        category = self.repository.update(category_id, payload.name.strip())
        if category is None:
            not_found("Category", category_id)
        return category

    def delete(self, category_id: int):
        deleted = self.repository.delete(category_id)
        if not deleted:
            not_found("Category", category_id)
