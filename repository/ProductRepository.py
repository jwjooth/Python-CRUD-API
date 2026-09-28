"""Product persistence."""

from typing import ClassVar

from entity.ProductEntity import Product
from payload.ProductPayload import ProductCreate, ProductUpdate
from repository.BaseRepository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Row access for `products`."""

    model: ClassVar[type[Product]] = Product
    unique_index: ClassVar[str] = "uq_product_name_normalized"

    def create(self, payload: ProductCreate) -> Product:
        return self.add(**payload.model_dump())

    def update(self, product: Product, payload: ProductUpdate) -> Product:
        return self.save(product, **payload.model_dump())
