"""Category request/response payloads."""

from datetime import datetime

from pydantic import Field

from payload.BasePayload import RequestPayload, ResponsePayload


class CategoryNamePayload(RequestPayload):
    """Fields shared by category creation and update."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique display name, compared case-insensitively.",
        examples=["Fiction"],
    )


class CategoryCreate(CategoryNamePayload):
    """Body of `POST /api/v1/categories`."""


class CategoryUpdate(CategoryNamePayload):
    """Body of `PUT /api/v1/categories/{category_id}`."""


class CategoryResponse(ResponsePayload):
    """Representation of a category."""

    id: int
    name: str
    created_at: datetime
    updated_at: datetime
