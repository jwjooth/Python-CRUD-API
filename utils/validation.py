from fastapi import HTTPException, status


def require_field(value, field_name: str, http_status: int = status.HTTP_400_BAD_REQUEST) -> None:
    if value is None or (isinstance(value, str) and not value.strip()):
        raise HTTPException(
            status_code=http_status,
            detail=f"{field_name} is required",
        )


def require_string(
    value: str, field_name: str, http_status: int = status.HTTP_400_BAD_REQUEST
) -> None:
    if not value or not value.strip():
        raise HTTPException(
            status_code=http_status,
            detail=f"{field_name} is required",
        )


def require_positive(
    value, field_name: str, http_status: int = status.HTTP_400_BAD_REQUEST
) -> None:
    if value is None or value <= 0:
        raise HTTPException(
            status_code=http_status,
            detail=f"{field_name} must be greater than zero",
        )


def not_found(entity_name: str, entity_id: int) -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{entity_name} with id {entity_id} was not found.",
    )


def conflict(message: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=message,
    )


def bad_request(message: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message,
    )
