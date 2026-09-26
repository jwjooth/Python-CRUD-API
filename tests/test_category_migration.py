import pytest
from sqlalchemy import create_engine, event, insert, select
from sqlalchemy.exc import IntegrityError

from database import Base
from entity.BookEntity import Book
from entity.CategoryEntity import Category
from migrations.category_name_unique import upgrade


@pytest.mark.parametrize("legacy", [True, False])
def test_category_migration_preserves_books_and_is_repeatable(legacy):
    engine = create_engine("sqlite://")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, record):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    categories = Category.__table__
    books = Book.__table__
    if legacy:
        next(iter(categories.indexes)).drop(engine)
    with engine.begin() as connection:
        connection.execute(insert(categories), [{"id": 1, "name": "Fantasy"}])
        connection.execute(insert(categories), [{"id": 3, "name": "History"}])
        if legacy:
            connection.execute(insert(categories), [{"id": 2, "name": "FANTASY"}])
            connection.execute(insert(categories), [{"id": 4, "name": "fantasy"}])
        connection.execute(
            insert(books),
            [
                {
                    "category_id": category_id,
                    "title": f"Book {category_id}",
                    "author": "Author",
                    "price": 10,
                    "stock": 0,
                }
                for category_id in ([1, 2, 3, 4] if legacy else [1, 3])
            ],
        )

    # Reproduce application startup against an existing schema.
    Base.metadata.create_all(engine)
    upgrade(engine)
    upgrade(engine)
    with engine.connect() as connection:
        assert connection.execute(select(categories.c.id, categories.c.name)).all() == [
            (1, "Fantasy"),
            (3, "History"),
        ]
        assert connection.execute(
            select(books.c.category_id).order_by(books.c.id)
        ).scalars().all() == ([1, 1, 3, 1] if legacy else [1, 3])
    with engine.begin() as connection, pytest.raises(IntegrityError):
        connection.execute(insert(categories).values(name="FaNtAsY"))
    engine.dispose()
