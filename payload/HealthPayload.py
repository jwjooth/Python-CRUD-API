"""Response payload for the service health check."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Body of `GET /`."""

    status: str = Field(..., examples=["ok"])
    message: str = Field(..., examples=["Welcome to the Products API"])
