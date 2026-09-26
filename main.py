import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from controller.BookController import router as book_router
from controller.CategoryController import router as category_router
from controller.ProductController import router as product_router
from database import Base, engine

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
    title="Products API",
    version="1.0.0",
    description="CRUD API for managing categories, products, and books.",
    lifespan=lifespan,
)


@app.get("/", tags=["health"])
def read_root():
    return {"status": "ok", "message": "Welcome to the Products API"}


app.include_router(category_router)
app.include_router(product_router)
app.include_router(book_router)
