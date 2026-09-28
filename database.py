"""Engine, session factory and the per-request session dependency."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config.config import CommonSettings


class Base(DeclarativeBase):
    """Declarative base shared by every entity."""


settings = CommonSettings()

engine = create_engine(
    settings.database_url,
    echo=settings.db_echo,
    future=True,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_recycle=settings.db_pool_recycle,
    pool_timeout=settings.db_pool_timeout,
)

# expire_on_commit=False keeps loaded attributes usable after commit, so writes
# stay a single statement plus one narrow refresh of the server-managed columns
# (created_at/updated_at) instead of re-selecting the whole row.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Iterator[Session]:
    """Yield one session per request and always release it."""
    with SessionLocal() as db:
        yield db
