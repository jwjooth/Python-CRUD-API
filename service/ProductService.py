"""Product business rules: existence (404) and unique-name conflicts (409)."""

from sqlalchemy.orm import Session

from entity.ProductEntity import Product
from payload.ProductPayload import ProductCreate, ProductResponse, ProductUpdate
from repository.ProductRepository import ProductRepository
from utils import DuplicateValueError, conflict, not_found


class ProductService:
    def __init__(self, db: Session) -> None:
        self.repository = ProductRepository(db)

    def get_all(self, *, offset: int = 0, limit: int = 100) -> list[ProductResponse]:
        products = self.repository.get_all(offset=offset, limit=limit)
        return [ProductResponse.model_validate(product) for product in products]

    def get_by_id(self, product_id: int) -> ProductResponse:
        return ProductResponse.model_validate(self._require(product_id))

    def create(self, payload: ProductCreate) -> ProductResponse:
        try:
            product = self.repository.create(payload)
        except DuplicateValueError:
            conflict(self._duplicate_message(payload.name))
        return ProductResponse.model_validate(product)

    def update(self, product_id: int, payload: ProductUpdate) -> ProductResponse:
        product = self._require(product_id)
        try:
            product = self.repository.update(product, payload)
        except DuplicateValueError:
            conflict(self._duplicate_message(payload.name))
        return ProductResponse.model_validate(product)

    def delete(self, product_id: int) -> None:
        self.repository.delete(self._require(product_id))

    @staticmethod
    def _duplicate_message(name: str) -> str:
        return f"Product with name {name} already exists."

    def _require(self, product_id: int) -> Product:
        product = self.repository.get_by_id(product_id)
        if product is None:
            not_found("Product", product_id)
        return product
