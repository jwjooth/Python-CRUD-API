"""HTTP error mappers shared by the service layer.

Each helper raises, so a call site reads as a guard clause and static analysers
know control flow stops there.
"""

from __future__ import annotations

from typing import NoReturn

from fastapi import HTTPException, status


def not_found(entity_name: str, entity_id: int) -> NoReturn:
    """404 for a missing row."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{entity_name} with id {entity_id} was not found.",
    )


def conflict(message: str) -> NoReturn:
    """409 for a write that collides with existing data."""
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=message,
    )


def bad_request(message: str) -> NoReturn:
    """400 for input that is well formed but not usable."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message,
    )
