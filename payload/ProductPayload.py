from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ProductRequest(BaseModel):
    name: str
    description: str
    price: float
    stock: int


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    price: float
    stock: int
    created_at: datetime
    updated_at: datetime
