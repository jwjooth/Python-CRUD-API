"""Generic SQLAlchemy CRUD helpers shared by every resource repository.

Subclasses declare the mapped class and the case-insensitive unique index that
guards their natural key; the base class owns statement construction, the write
round trips and the translation of database integrity errors.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, ClassVar

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import Base
from utils.integrity import translate_integrity_error


class BaseRepository[ModelT: Base]:
    """Read/write primitives for one mapped class."""

    model: ClassVar[type[ModelT]]
    unique_index: ClassVar[str] = ""
    server_generated_fields: ClassVar[tuple[str, ...]] = ("created_at", "updated_at")

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self, *, offset: int = 0, limit: int = 100) -> Sequence[ModelT]:
        """Return one ordered page of rows (primary-key order keeps paging stable)."""
        statement = select(self.model).order_by(self.model.id).limit(limit).offset(offset)
        return self.db.execute(statement).scalars().all()

    def get_by_id(self, entity_id: int) -> ModelT | None:
        """Return the row with `entity_id`, or None. One primary-key lookup."""
        return self.db.get(self.model, entity_id)

    def add(self, **values: Any) -> ModelT:
        """Insert a row and return it with the server-generated columns loaded."""
        entity = self.model(**values)
        self.db.add(entity)
        self._commit()
        self._load_server_generated(entity)
        return entity

    def save(self, entity: ModelT, **values: Any) -> ModelT:
        """Apply `values` to a tracked row and return it refreshed."""
        for field, value in values.items():
            setattr(entity, field, value)
        self._commit()
        self._load_server_generated(entity)
        return entity

    def delete(self, entity: ModelT) -> None:
        """Delete a tracked row."""
        self.db.delete(entity)
        self._commit()

    def _load_server_generated(self, entity: ModelT) -> None:
        # A targeted refresh fetches only the server-managed columns; the values
        # written by the request are already present in memory.
        self.db.refresh(entity, list(self.server_generated_fields))

    def _commit(self) -> None:
        try:
            self.db.commit()
        except IntegrityError as exc:
            violation = translate_integrity_error(exc, self.unique_index or None)
            if violation is None:
                raise
            self.db.rollback()
            # expire_on_commit=False keeps the identity map populated, so a failed
            # write must be expired explicitly to avoid leaking uncommitted values.
            self.db.expire_all()
            raise violation from exc
