"""Domain errors raised below the service layer.

Repositories translate driver-specific `IntegrityError`s into these types so the
persistence layer stays free of HTTP concerns; the service layer maps them to
responses with the helpers in `utils.errors`.
"""

from __future__ import annotations


class DomainError(Exception):
    """Base class for business-rule violations detected by the data layer."""


class DuplicateValueError(DomainError):
    """A unique index rejected a write (duplicate name/title)."""

    def __init__(self, index_name: str) -> None:
        super().__init__(f"value violates unique index '{index_name}'")
        self.index_name = index_name


class RelatedRecordMissingError(DomainError):
    """A foreign key rejected a write because the referenced row does not exist."""

    def __init__(self, message: str = "referenced record does not exist") -> None:
        super().__init__(message)
