"""Application entry point: middleware, lifespan table creation, routers."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from config.config import CommonSettings
from controller.BookController import router as book_router
from controller.CategoryController import router as category_router
from controller.ProductController import router as product_router
from database import Base, engine
from payload.HealthPayload import HealthResponse

settings = CommonSettings()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        logger.exception("Failed to create database tables")
        raise
    yield


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="CRUD API for managing categories, products, and books.",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "health", "description": "Service availability."},
        {"name": "categories", "description": "Category CRUD."},
        {"name": "products", "description": "Product CRUD."},
        {"name": "books", "description": "Book CRUD."},
    ],
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=settings.gzip_minimum_size,
)


@app.get("/", response_model=HealthResponse, tags=["health"], summary="Health check")
def read_root() -> HealthResponse:
    """Return service availability and a welcome message using the configured API title."""
    return HealthResponse(status="ok", message=f"Welcome to the {settings.api_title}")


app.include_router(category_router)
app.include_router(product_router)
app.include_router(book_router)
