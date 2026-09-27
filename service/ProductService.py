from payload.ProductPayload import ProductRequest
from repository.ProductRepository import ProductRepository
from utils import conflict, not_found, require_positive, require_string


class ProductService:
    def __init__(self, db):
        self.repository = ProductRepository(db)

    def get_all(self, offset: int = 0, limit: int = 100):
        return self.repository.get_all(offset, limit)

    def get_by_id(self, id: int):
        product = self.repository.get_by_id(id)
        if product is None:
            not_found("Product", id)
        return product

    def create(self, request: ProductRequest):
        require_string(request.name, "Product name")
        require_positive(request.price, "Product price")
        require_positive(request.stock, "Product stock")
        if self.repository.get_by_name(request.name.strip()):
            conflict(f"Product with name {request.name.strip()} already exists.")
        return self.repository.create(request)

    def update(self, id: int, request: ProductRequest):
        self.get_by_id(id)
        require_string(request.name, "Product name")
        require_positive(request.price, "Product price")
        require_positive(request.stock, "Product stock")
        if self.repository.get_by_name(request.name.strip(), id):
            conflict(f"Product with name {request.name.strip()} already exists.")
        product = self.repository.update(request, id)
        if product is None:
            not_found("Product", id)
        return product

    def delete(self, id: int):
        deleted = self.repository.delete(id)
        if not deleted:
            not_found("Product", id)
