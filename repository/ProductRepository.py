from sqlalchemy import select, func
from sqlalchemy.orm import Session

from entity.ProductEntity import Product
from payload.ProductPayload import ProductRequest


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, offset: int = 0, limit: int = 100):
        query = select(Product).order_by(Product.id).offset(offset).limit(limit)
        return self.db.execute(query).scalars().all()

    def get_by_id(self, id: int):
        return self.db.get(Product, id)

    def get_by_name(self, name: str, exclude_id: int | None = None):
        query = select(Product).where(func.lower(Product.name) == name.lower())
        if exclude_id is not None:
            query = query.where(Product.id != exclude_id)
        return self.db.execute(query).scalar_one_or_none()

    def create(self, request: ProductRequest):
        product = Product(**request.model_dump())
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, request: ProductRequest, id: int):
        product = self.get_by_id(id)
        if product is None:
            return None
        product.name = request.model_dump()["name"]
        product.description = request.model_dump()["description"]
        product.price = request.model_dump()["price"]
        product.stock = request.model_dump()["stock"]
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, id: int):
        product = self.get_by_id(id)
        if product is None:
            return False
        self.db.delete(product)
        self.db.commit()
        return True
