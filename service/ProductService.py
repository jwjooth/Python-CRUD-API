from fastapi import HTTPException, status

from payload.ProductPayload import ProductRequest
from repository.ProductRepository import ProductRepository


class ProductService:
    def __init__(self, db):
        self.repository = ProductRepository(db)

    def get_all(self, offset: int = 0, limit: int = 100):
        return self.repository.get_all(offset, limit)

    def get_by_id(self, id: int):
        product = self.repository.get_by_id(id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {id} was not found."
            )
        return product

    def get_by_name(self, name: str, exclude_id: int):
        product = self.repository.get_by_name(name, exclude_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with name {name} was not found."
            )
        return product

    def create(self, request: ProductRequest):
        if not request.name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product name is required."
            )
        if request.price is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product price is required."
            )
        if request.price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product price is must be greater than zero."
            )
        if request.stock is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product stock is required."
            )
        if request.stock <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product stock is must be greater than zero."
            )
        if self.repository.get_by_name(request.name.strip()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with name {request.name.strip()} already exists."
            )
        return self.repository.create(request)

    def update(self, id: int, request: ProductRequest):
        self.get_by_id(id)

        if not request.name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product name is required."
            )
        if request.price is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product price is required."
            )
        if request.stock is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product stock is required."
            )

        if self.repository.get_by_name(request.name.strip(), id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with name {request.name.strip()} already exists."
            )

        product = self.repository.update(request, id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {id} was not found."
            )

        return product

    def delete(self, id: int):
        deleted = self.repository.delete(id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {id} was not found."
            )
        return None
