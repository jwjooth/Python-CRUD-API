from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from decimal import Decimal

class ProductRequest(BaseModel):
    name: str
    description: str
    price: Decimal = Field(..., decimal_places=2)
    stock: int


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    created_at: datetime
    updated_at: datetime
