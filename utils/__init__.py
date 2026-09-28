"""Shared, framework-agnostic helpers: HTTP error mappers and domain errors."""

from utils.errors import bad_request, conflict, not_found
from utils.exceptions import DomainError, DuplicateValueError, RelatedRecordMissingError
from utils.integrity import is_duplicate_key_error, is_foreign_key_error, translate_integrity_error

__all__ = [
    "DomainError",
    "DuplicateValueError",
    "RelatedRecordMissingError",
    "bad_request",
    "conflict",
    "is_duplicate_key_error",
    "is_foreign_key_error",
    "not_found",
    "translate_integrity_error",
]
