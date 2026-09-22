from pydantic import BaseModel
from datetime import datetime

class ProductRequest(BaseModel):
    name: str
    description: str
    price: float
    stock: int

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    created_at: datetime
    updated_at: datetime
