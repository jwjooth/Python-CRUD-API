import pytest
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.exc import IntegrityError

from migrations.book_price_nullable import upgrade


def test_sqlite_rebuild_preserves_book_constraints_and_data():
    engine = create_engine("sqlite://")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, record):
        connection.execute("PRAGMA foreign_keys=ON")

    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE categories (id INTEGER PRIMARY KEY)"))
        connection.execute(
            text("""
                CREATE TABLE books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL REFERENCES categories(id),
                    title VARCHAR(255) NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    stock INTEGER NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
        )
        connection.execute(
            text("CREATE UNIQUE INDEX uq_book_title_normalized ON books (lower(title))")
        )
        connection.execute(text("INSERT INTO categories (id) VALUES (1)"))
        connection.execute(
            text("""
                INSERT INTO books (category_id, title, author, stock, price)
                VALUES (1, 'Dune', 'Frank Herbert', 3, 12.50)
            """)
        )

    upgrade(engine)
    upgrade(engine)

    with engine.connect() as connection:
        assert connection.execute(
            text("SELECT category_id, title, author, stock, price FROM books")
        ).one() == (1, "Dune", "Frank Herbert", 3, 12.5)
        assert inspect(connection).get_foreign_keys("books")[0]["referred_table"] == "categories"
        assert connection.execute(
            text("SELECT name FROM sqlite_master WHERE type = 'index' AND tbl_name = 'books'")
        ).scalars().all() == ["uq_book_title_normalized"]

    with engine.begin() as connection:
        connection.execute(
            text("""
                INSERT INTO books (category_id, title, author, stock)
                VALUES (1, 'Foundation', 'Isaac Asimov', 2)
            """)
        )
        assert (
            connection.execute(
                text("SELECT price FROM books WHERE title = 'Foundation'")
            ).scalar_one()
            is None
        )

    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        with engine.begin() as connection:
            connection.execute(
                text("""
                    INSERT INTO books (category_id, title, author, stock)
                    VALUES (999, 'Other', 'Author', 1)
                """)
            )

    with pytest.raises(IntegrityError, match="UNIQUE constraint failed"):
        with engine.begin() as connection:
            connection.execute(
                text("""
                    INSERT INTO books (category_id, title, author, stock)
                    VALUES (1, 'dUnE', 'Author', 1)
                """)
            )

    engine.dispose()
