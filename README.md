# Python RESTful API

A clean, modular, and layered RESTful API built with **FastAPI**, **SQLAlchemy**, and **MySQL** for managing products, categories, and books.

---

## 🚀 Features

- **Layered Architecture**: Separation of concerns across Controller, Service, Repository, Entity, and Payload layers.
- **Full CRUD**: Manage Categories, Products and Books with strict input validation.
- **Strict Payloads**: Unknown body fields, out-of-range values and unknown query parameters are rejected with `422` instead of being silently ignored.
- **Race-Safe Uniqueness**: Case-insensitive unique indexes at the database level return `409` even under concurrent writers.
- **Automatic OpenAPI Documentation**: Swagger UI and ReDoc out of the box.
- **Relational ORM**: Database operations powered by SQLAlchemy 2.0 with PyMySQL, with a pooled engine and GZip-compressed responses.
- **Config Management**: Environment variable validation with Pydantic Settings.

---

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Database**: MySQL (driver: PyMySQL)
- **Validation**: [Pydantic](https://docs.pydantic.dev/)

---

## 📁 Project Structure

```text
├── config/             # Application configuration & environment settings
├── controller/         # API routes & request handling
├── service/            # Business logic layer (payload in, payload out)
├── repository/         # Database queries & persistence layer
├── entity/             # SQLAlchemy ORM models
├── payload/            # Pydantic schemas (create, update, response, pagination)
├── utils/              # Shared HTTP mappers, domain errors, integrity translation
├── migrations/         # One-off database migration scripts
├── tests/              # Pytest suite (SQLite-backed TestClient)
├── database.py         # Database engine & session management
├── main.py             # Application entry point (`uvicorn main:app`)
├── pyproject.toml      # Project metadata + ruff config (deps mirror requirements.txt)
├── requirements.txt    # Pinned dependencies (install source of truth)
└── .env.example        # Sample environment variables
```

### Request/response rules

- Bodies are strict: unknown fields are rejected with `422`, names and titles are
  trimmed, and every field carries its own bounds (`gt`, `ge`, `max_digits`).
- List endpoints share `offset`/`limit` (`offset >= 0`, `1 <= limit <= 100`);
  unknown query parameters are rejected with `422`.
- Status codes: `201` created, `204` deleted (empty body), `400` unknown category
  reference, `404` missing row, `409` duplicate name/title, `422` validation.

---

## ⚡ Getting Started

### 1. Prerequisites

- Python 3.13+
- MySQL Server running

### 2. Installation

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/jwjooth/Python-CRUD-API.git
cd Python-CRUD-API
```

Create and activate a virtual environment:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and fill in your database credentials:

```bash
# Windows Command Prompt
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

Example `.env`:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=products_db
```

Optional tuning (defaults shown):

```env
SQLALCHEMY_ECHO=false
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_RECYCLE=1800
DB_POOL_TIMEOUT=30
API_TITLE=Products API
API_VERSION=1.0.0
GZIP_MINIMUM_SIZE=500
```

Before starting the application, create the configured database in MySQL:

```sql
CREATE DATABASE products_db;
```

The database name must match `DB_NAME` in your `.env` file.

### 4. Upgrade an Existing Database

For an existing `categories` table, back up the database and stop all application
writers before running this migration with the configured database credentials:

```bash
python -m migrations.category_name_unique
```

The migration merges category names that compare equal under the database's
`lower(name)` expression and collation. It keeps the lowest category ID and its
name, moves all books from duplicate categories to that ID, then deletes the
duplicate category rows and creates `uq_category_name_normalized`. References
to removed category IDs outside this database must be updated separately.
It can be rerun safely; an existing index makes it a no-op. MySQL index creation
implicitly commits, so keep writers stopped until the command succeeds. If index
creation fails after merging duplicates, fix the reported error and rerun.

Fresh databases receive the index when the application creates its tables.
`Base.metadata.create_all()` does not upgrade existing tables.

### 5. Run the Application

Start the development server with hot-reload:

```bash
uvicorn main:app --reload
```

The API will be accessible at: `http://localhost:8000`

---

## 📖 API Documentation

Once the server is running, explore the interactive documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Health check / Welcome message |
| `GET` | `/api/v1/categories` | List categories (with pagination) |
| `GET` | `/api/v1/categories/{category_id}` | Get category details |
| `POST` | `/api/v1/categories` | Create a category |
| `PUT` | `/api/v1/categories/{category_id}` | Update a category |
| `DELETE` | `/api/v1/categories/{category_id}` | Delete a category |
| `GET` | `/api/v1/products` | List products (with pagination) |
| `GET` | `/api/v1/products/{product_id}` | Get product details |
| `POST` | `/api/v1/products` | Create a product |
| `PUT` | `/api/v1/products/{product_id}` | Update a product |
| `DELETE` | `/api/v1/products/{product_id}` | Delete a product |
| `GET` | `/api/v1/books` | List books (with pagination) |
| `GET` | `/api/v1/books/{book_id}` | Get book details |
| `POST` | `/api/v1/books` | Create a book |
| `PUT` | `/api/v1/books/{book_id}` | Update a book |
| `DELETE` | `/api/v1/books/{book_id}` | Delete a book |

---

## 🧪 Tests & Lint

The suite runs against an in-memory SQLite database, so no MySQL server is required:

```bash
pytest
ruff check .
ruff format --check .
```

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
