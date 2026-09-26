"""Merge legacy duplicate categories and enforce case-insensitive uniqueness."""

from sqlalchemy import delete, func, inspect, select, text, update
from sqlalchemy.engine import Engine

from entity.BookEntity import Book
from entity.CategoryEntity import Category

INDEX_NAME = "uq_category_name_normalized"


def upgrade(engine: Engine):
    # Run with application writers stopped: MySQL index DDL implicitly commits.
    with engine.begin() as connection:
        if connection.dialect.name == "sqlite":
            exists = connection.execute(
                text("SELECT 1 FROM sqlite_master WHERE type = 'index' AND name = :name"),
                {"name": INDEX_NAME},
            ).scalar()
        else:
            exists = inspect(connection).has_index("categories", INDEX_NAME)
        if exists:
            return

        categories = Category.__table__
        books = Book.__table__
        normalized_name = func.lower(categories.c.name)
        duplicates = (
            connection.execute(
                select(normalized_name).group_by(normalized_name).having(func.count() > 1)
            )
            .scalars()
            .all()
        )
        for name in duplicates:
            ids = (
                connection.execute(
                    select(categories.c.id).where(normalized_name == name).order_by(categories.c.id)
                )
                .scalars()
                .all()
            )
            # Preserve the oldest category and every book referencing its duplicates.
            connection.execute(
                update(books).where(books.c.category_id.in_(ids[1:])).values(category_id=ids[0])
            )
            connection.execute(delete(categories).where(categories.c.id.in_(ids[1:])))

        index = next(index for index in categories.indexes if index.name == INDEX_NAME)
        index.create(connection)


if __name__ == "__main__":
    from database import engine

    upgrade(engine)
