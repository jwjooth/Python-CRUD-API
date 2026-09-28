"""Base Pydantic configurations shared by every request/response payload."""

from pydantic import BaseModel, ConfigDict, Field


class RequestPayload(BaseModel):
    """Strict input model.

    `extra="forbid"` rejects unknown fields instead of silently dropping them, so
    typos and stale clients fail fast with 422. `str_strip_whitespace` normalises
    names/titles once, at the edge, so services and repositories never re-trim.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class ResponsePayload(BaseModel):
    """Output model serialised straight from ORM entities."""

    model_config = ConfigDict(from_attributes=True)


class PaginationPayload(BaseModel):
    """Shared `offset`/`limit` query parameters for list endpoints."""

    model_config = ConfigDict(extra="forbid")

    offset: int = Field(0, ge=0, description="Rows to skip before collecting results.")
    limit: int = Field(100, ge=1, le=100, description="Maximum rows to return (1-100).")
