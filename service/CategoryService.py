from fastapi import HTTPException, status

from payload.CategoryPayload import CategoryCreate, CategoryUpdate
from repository.CategoryRepository import CategoryRepository


class CategoryService:
    def __init__(self, db):
        self.repository = CategoryRepository(db)

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.repository.get_all(skip=skip, limit=limit)

    def get_by_id(self, category_id: int):
        category = self.repository.get_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} was not found.",
            )
        return category

    def create(self, payload: CategoryCreate):
        name = payload.name.strip()
        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name cannot be empty.",
            )

        if self.repository.get_by_name(name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category name already exists.",
            )

        return self.repository.create(name)

    def update(self, category_id: int, payload: CategoryUpdate):
        self.get_by_id(category_id)

        name = payload.name.strip()
        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name cannot be empty.",
            )

        if self.repository.get_by_name(name, exclude_id=category_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category name already exists.",
            )

        category = self.repository.update(category_id, name)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} was not found.",
            )
        return category

    def delete(self, category_id: int):
        deleted = self.repository.delete(category_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} was not found.",
            )
        return None
