"""Make books.price nullable or drop it for existing databases.

The Book entity no longer has a price field. Existing databases may have a
NOT NULL price column with no default, which would cause INSERT to fail
when BookRepository.create() omits price.
"""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def upgrade(engine: Engine):
    with engine.begin() as connection:
        inspector = inspect(connection)
        columns = {col["name"]: col for col in inspector.get_columns("books")}

        if "price" not in columns:
            return

        price_col = columns["price"]
        # If price is NOT NULL and has no default, make it nullable
        if price_col.get("nullable") is False and price_col.get("default") is None:
            if connection.dialect.name == "mysql":
                connection.execute(text("ALTER TABLE books MODIFY price DECIMAL(10,2) NULL"))
            elif connection.dialect.name == "sqlite":
                # SQLite doesn't support ALTER COLUMN directly; recreate table
                connection.execute(
                    text("""
                    CREATE TABLE books_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category_id INTEGER NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        author VARCHAR(255) NOT NULL,
                        stock INTEGER NOT NULL,
                        price DECIMAL(10,2),
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                )
                connection.execute(
                    text("""
                    INSERT INTO books_new (id, category_id, title, author, stock,
                                          price, created_at, updated_at)
                    SELECT id, category_id, title, author, stock,
                           price, created_at, updated_at FROM books
                """)
                )
                connection.execute(text("DROP TABLE books"))
                connection.execute(text("ALTER TABLE books_new RENAME TO books"))
            else:
                connection.execute(text("ALTER TABLE books ALTER COLUMN price DROP NOT NULL"))


if __name__ == "__main__":
    from database import engine

    upgrade(engine)
