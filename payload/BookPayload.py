from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookRequest(BaseModel):
    category_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    stock: int = Field(..., ge=0)

    model_config = ConfigDict(str_strip_whitespace=True)


class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: int
    title: str
    author: str
    stock: int
    created_at: datetime
    updated_at: datetime
