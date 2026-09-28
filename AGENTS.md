# AGENTS.md — Python-CRUD-API

## Setup & run (exact commands, from repo root)
- `pip install -r requirements.txt` is the install source of truth. `pyproject.toml`
  mirrors the pins but `uv.lock` is stub-only — do not use `uv sync`.
- Requires Python 3.13+ (`pyproject.toml`, `.python-version`) and a running MySQL server.
- `cp .env.example .env`, fill `DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME` (all required,
  no defaults; `config/config.py`). Optional knobs: `SQLALCHEMY_ECHO`, `DB_POOL_SIZE`,
  `DB_MAX_OVERFLOW`, `DB_POOL_RECYCLE`, `DB_POOL_TIMEOUT`, `API_TITLE`, `API_VERSION`,
  `GZIP_MINIMUM_SIZE`.
- Create the DB first: `CREATE DATABASE <DB_NAME>;` — must match `.env`, tables are
  auto-created via `Base.metadata.create_all` in the `lifespan` handler (`main.py`).
  No Alembic; one-off migration scripts live in `migrations/`.
- `uvicorn main:app --reload` (must run from repo root — imports are flat top-level
  like `from database import`, `from entity...`). Docs at `/docs`, `/redoc`.

## Architecture (controller → service → repository → entity, payloads at the edges)
- Entrypoint: `main.py` (`app`, GZip middleware, lifespan table creation, 3 routers).
- `controller/` — thin `APIRouter`s (`/api/v1/{categories,products,books}`), per-request
  `Service(db)` via `Depends(get_db)`. Only binding, delegation and `response_model`.
- `service/` — payload in, response payload out. Owns error mapping: `not_found` (404),
  `conflict` (409), `bad_request` (400) from `utils`, plus `DuplicateValueError` /
  `RelatedRecordMissingError` translation. No SQL, no `HTTPException` literals.
- `repository/` — SQLAlchemy only. `BaseRepository[Model]` (`repository/BaseRepository.py`)
  holds every statement; each resource repository only declares `model`, `unique_index`
  and its typed `create`/`update`. `get_by_id` returns-or-`None`; never raises HTTP errors
  and never raises domain errors on its own — it re-raises unmapped `IntegrityError`s.
- `entity/` — SQLAlchemy 2.0 `Mapped`/`mapped_column` models, `database.Base`.
- `payload/` — `BasePayload.py` (shared `RequestPayload` / `ResponsePayload` /
  `PaginationPayload`) plus one `*Payload.py` per resource: `*Create`, `*Update`, `*Response`.
- `utils/` — cross-cutting helpers only: `errors.py` (HTTP mappers), `exceptions.py`
  (domain errors), `integrity.py` (driver-specific `IntegrityError` translation).
  `utils` must not import from `controller`, `service`, `repository` or `payload`.
- `database.py` — engine + `get_db()`; `config/config.py` — `CommonSettings` and the
  escaped `settings.database_url`.

## Conventions that differ from defaults
- Filenames are `PascalCase` (`ProductController.py`, `BookService.py`, …) — keep it.
- Type hints everywhere, including the controller return types and the route handler
  parameter names (`product_id`, not `id`, which shadows the builtin).
- Pagination is always the shared `PaginationPayload` (`offset>=0`, `1<=limit<=100`),
  bound with `Annotated[PaginationPayload, Query()]`; list queries `order_by(id)`.
  DELETE returns `204` with empty body; POST returns `201`.
- Names/titles are trimmed by the payload (`str_strip_whitespace=True`) and unique
  **case-insensitively**, enforced by `func.lower(...)` unique indexes
  (`uq_category_name_normalized`, `uq_product_name_normalized`,
  `uq_book_title_normalized`). The database index is the single source of truth:
  there is no duplicate pre-check SELECT on writes, so a create/update costs one
  INSERT/UPDATE, and concurrent writers still get a 409. Never compare names in Python.
- Field validation lives in Pydantic payloads (`gt/ge/min_length/max_digits`,
  `extra="forbid"`). Unknown body fields and unknown query parameters are 422.
  Services only add existence (404), uniqueness (409) and reference (400) checks.
  `Book.category_id` is a real `FK → categories.id`, checked by `BookService` so the
  behaviour is identical on backends that do not enforce FKs (SQLite).
- `ruff` config in `pyproject.toml` (`E,F,I,UP`, line-length 100, py313) plus a matching
  `.flake8` for CI. Run `ruff check .` && `ruff format --check .` from root.

## Performance notes (why the code looks like this)
- `SessionLocal` uses `expire_on_commit=False`, so a write is one INSERT/UPDATE plus a
  *narrow* `refresh` of only `created_at`/`updated_at` (declared in
  `BaseRepository.server_generated_fields`) instead of re-selecting the whole row.
  `_commit` calls `expire_all()` after a rollback so uncommitted values never leak.
- Statement counts per request: create 2, update 3, delete 2, get 1, list 1.
  `updated_at` stays server-generated on purpose (MySQL has no `RETURNING`), so the
  extra `SELECT` after an UPDATE is the price of correct, server-side timestamps.
- The engine is pooled (`pool_pre_ping`, `pool_recycle`, `pool_size`, `max_overflow`,
  `pool_timeout` from settings) and the URL is built with `URL.create`, so passwords
  containing `@`, `/` or `#` no longer corrupt the DSN.
- GZip is enabled app-wide (`GZipMiddleware`, `GZIP_MINIMUM_SIZE` bytes).

## Testing
- `pytest` runs unit + integration tests from `tests/` using FastAPI `TestClient`.
- Tests use **in-memory SQLite** (see `tests/conftest.py`), not MySQL.
  Dummy `DB_*` env vars are set before imports; lifespan is overridden to no-op.
- Run: `pytest` (all), `pytest tests/test_categories.py` (single file), `pytest -k "test_category"` (filter).
- Fixtures: `client` (fresh TestClient per test, empty tables, one session per request),
  `db_session` (session for service/repository tests), `category_id` (pre-created category).
  Payload helpers `_product_payload` / `_book_payload` live in `conftest.py`.
- `tests/test_services.py` pins the payload-in/payload-out contract and the error codes;
  `tests/test_api_contract.py` pins strictness (extra field/query param, bounds, gzip).

## CI / Linting
- `.github/workflows/python-app.yml`: runs on push/PR to `main`.
  - Installs deps via `pip install -r requirements.txt`
  - Lints with **flake8** (not ruff) — see workflow for exact flags; `.flake8` aligns it
    with the local ruff config
  - Runs `pytest`
- `.github/workflows/codeql.yml`: scheduled CodeQL analysis (Python).
- Local lint: `ruff check .` && `ruff format --check .` (matches `pyproject.toml` config).

## Gotchas
- `src/python_restful_api/` is an unrelated `Hello` stub — ignore it; the app is `main.py`.
- `Book` has no `price` field; books reject a `price` body field with 422. Use
  Product/Category as the pattern for new resources, not git history.
- Migration `migrations/category_name_unique.py` merges case-insensitive duplicates
  and creates `uq_category_name_normalized`. Run manually: `python -m migrations.category_name_unique`
  (requires DB credentials, writers stopped). Fresh DBs get the index via `create_all`.
- `migrations/book_price_nullable.py` still exists for databases created before `price`
  was dropped from `Book`.
- Repository-level failures raise `DuplicateValueError` / `RelatedRecordMissingError`
  (`utils.exceptions`), **not** `HTTPException`; only services build HTTP responses.
