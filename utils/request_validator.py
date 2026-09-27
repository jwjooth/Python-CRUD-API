from __future__ import annotations

from fastapi import HTTPException, status
from pydantic import BaseModel


class RequestValidator:
    def __init__(self, request: BaseModel) -> None:
        self._request = request

    def require(
        self, field_name: str, http_status: int = status.HTTP_400_BAD_REQUEST
    ) -> RequestValidator:
        value = getattr(self._request, field_name, None)
        if value is None or (isinstance(value, str) and not value.strip()):
            raise HTTPException(
                status_code=http_status,
                detail=f"{field_name} is required",
            )
        return self

    def require_positive(
        self, field_name: str, http_status: int = status.HTTP_400_BAD_REQUEST
    ) -> RequestValidator:
        value = getattr(self._request, field_name, None)
        if value is None or value <= 0:
            raise HTTPException(
                status_code=http_status,
                detail=f"{field_name} must be greater than zero",
            )
        return self

    def require_string(
        self, field_name: str, http_status: int = status.HTTP_400_BAD_REQUEST
    ) -> RequestValidator:
        value = getattr(self._request, field_name, None)
        if not value or not value.strip():
            raise HTTPException(
                status_code=http_status,
                detail=f"{field_name} is required",
            )
        return self

    def get(self, field_name: str, default=None):
        return getattr(self._request, field_name, default)

    @property
    def request(self) -> BaseModel:
        return self._request

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._request, name)
