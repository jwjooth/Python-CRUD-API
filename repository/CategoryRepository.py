import re
import sqlite3

from fastapi import HTTPException, status
from pymysql.err import IntegrityError as MySQLIntegrityError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from entity.CategoryEntity import Category


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, offset: int = 0, limit: int = 100):
        statement = select(Category).order_by(Category.id).offset(offset).limit(limit)
        return self.db.execute(statement).scalars().all()

    def get_by_id(self, category_id: int):
        return self.db.get(Category, category_id)

    def get_by_name(self, name: str, exclude_id: int | None = None):
        statement = select(Category).where(func.lower(Category.name) == name.lower())
        if exclude_id is not None:
            statement = statement.where(Category.id != exclude_id)
        return self.db.execute(statement).scalar_one_or_none()

    def create(self, name: str):
        category = Category(name=name)
        self.db.add(category)
        self._commit_name_change()
        self.db.refresh(category)
        return category

    def update(self, category_id: int, name: str):
        category = self.get_by_id(category_id)
        if category is None:
            return None
        category.name = name
        self._commit_name_change()
        self.db.refresh(category)
        return category

    def delete(self, category_id: int):
        category = self.get_by_id(category_id)
        if category is None:
            return False
        self.db.delete(category)
        self.db.commit()
        return True

    def _commit_name_change(self):
        try:
            self.db.commit()
        except IntegrityError as exc:
            original = exc.orig
            sqlite_conflict = isinstance(original, sqlite3.IntegrityError) and str(original) == (
                "UNIQUE constraint failed: index 'uq_category_name_normalized'"
            )
            mysql_conflict = (
                isinstance(original, MySQLIntegrityError)
                and original.args[0] == 1062
                and re.search(
                    r"for key ['`](?:[^'`]+\.)?uq_category_name_normalized['`]$",
                    str(original.args[1]),
                )
            )
            if not (sqlite_conflict or mysql_conflict):
                raise
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category name already exists.",
            ) from exc
