from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None)
    price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(..., ge=0)

    model_config = ConfigDict(str_strip_whitespace=True)


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    created_at: datetime
    updated_at: datetime
