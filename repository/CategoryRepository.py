"""Category persistence."""

from typing import ClassVar

from entity.CategoryEntity import Category
from repository.BaseRepository import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Row access for `categories`."""

    model: ClassVar[type[Category]] = Category
    unique_index: ClassVar[str] = "uq_category_name_normalized"

    def create(self, name: str) -> Category:
        """Insert a category with the given name and load its server-generated fields."""
        return self.add(name=name)

    def update(self, category: Category, name: str) -> Category:
        """Persist the new name on a tracked category and refresh server-generated fields."""
        return self.save(category, name=name)
