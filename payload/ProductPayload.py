"""Product request/response payloads."""

from datetime import datetime
from decimal import Decimal

from pydantic import Field

from payload.BasePayload import RequestPayload, ResponsePayload


class ProductFields(RequestPayload):
    """Fields shared by product creation and update."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique display name, compared case-insensitively.",
        examples=["Mechanical Keyboard"],
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional free-form description.",
        examples=["Mechanical keyboard"],
    )
    price: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=2,
        description="Unit price with at most two decimal places.",
        examples=["49.99"],
    )
    stock: int = Field(..., gt=0, description="Units currently in stock.")


class ProductCreate(ProductFields):
    """Body of `POST /api/v1/products`."""


class ProductUpdate(ProductFields):
    """Body of `PUT /api/v1/products/{product_id}`."""


class ProductResponse(ResponsePayload):
    """Representation of a product."""

    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    created_at: datetime
    updated_at: datetime
