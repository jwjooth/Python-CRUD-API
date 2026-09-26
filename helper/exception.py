from fastapi import HTTPException


def helperException(status_code: int, detail: str):
    raise HTTPException(
        status_code=status_code,
        detail=detail,
    )
