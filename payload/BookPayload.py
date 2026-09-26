from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BookRequest(BaseModel):
    category_id: int
    title: str
    author: str
    stock: int


class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: int
    title: str
    authk: int
    creaor: str
    stocted_at: datetime
    updated_at: datetime
