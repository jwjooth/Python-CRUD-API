"""Translation of driver-specific `IntegrityError`s into domain errors.

Unique and foreign-key violations are raised by the database engine with
backend-specific codes and messages (MySQL error numbers through PyMySQL,
SQLite text messages). Only this module knows those details; repositories and
services work with `DuplicateValueError` / `RelatedRecordMissingError`.
"""

from __future__ import annotations

import re
import sqlite3

from pymysql.err import IntegrityError as MySQLIntegrityError
from sqlalchemy.exc import IntegrityError

from utils.exceptions import DomainError, DuplicateValueError, RelatedRecordMissingError

_MYSQL_DUPLICATE_KEY = 1062
_MYSQL_FOREIGN_KEY_VIOLATION = 1452
_SQLITE_FOREIGN_KEY = "FOREIGN KEY constraint failed"


def _mysql_error_code(error: MySQLIntegrityError) -> int | None:
    """Return the integer driver error code, or None if it is unavailable."""
    args = error.args
    if args and isinstance(args[0], int):
        return args[0]
    return None


def _mysql_message(error: MySQLIntegrityError) -> str:
    """Return the driver message, falling back to the full error string."""
    return str(error.args[1]) if len(error.args) > 1 else str(error)


def is_duplicate_key_error(error: IntegrityError, index_name: str) -> bool:
    """True when `error` is a duplicate-entry failure of exactly `index_name`."""
    original = error.orig
    if isinstance(original, MySQLIntegrityError):
        if _mysql_error_code(original) != _MYSQL_DUPLICATE_KEY:
            return False
        # MySQL reports either `'index'` or `'table.index'` at the message tail.
        pattern = rf"for key ['`](?:[^'`]+\.)?{re.escape(index_name)}['`]$"
        return re.search(pattern, _mysql_message(original)) is not None
    if isinstance(original, sqlite3.IntegrityError):
        return str(original) == f"UNIQUE constraint failed: index '{index_name}'"
    return False


def is_foreign_key_error(error: IntegrityError) -> bool:
    """True when `error` was caused by a foreign-key constraint."""
    original = error.orig
    if isinstance(original, MySQLIntegrityError):
        return _mysql_error_code(original) == _MYSQL_FOREIGN_KEY_VIOLATION
    if isinstance(original, sqlite3.IntegrityError):
        return _SQLITE_FOREIGN_KEY in str(original)
    return False


def translate_integrity_error(
    error: IntegrityError, unique_index: str | None = None
) -> DomainError | None:
    """Return the domain error for `error`, or None when it is not a mapped one.

    Unmapped errors (NOT NULL violations, check constraints, ...) yield None so
    the caller can re-raise the original `IntegrityError` untouched.
    """
    if unique_index and is_duplicate_key_error(error, unique_index):
        return DuplicateValueError(unique_index)
    if is_foreign_key_error(error):
        return RelatedRecordMissingError()
    return None
