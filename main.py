from fastapi import FastAPI, logger

from controller.BookController import router as book_router
from controller.CategoryController import router as category_router
from controller.ProductController import router as product_router
from database import Base, engine

app = FastAPI(
    title="Products API",
    version="1.0.0",
    description="CRUD API for managing categories in the products database.",
)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.error(f"Error occurred while creating database tables: {e}")
    raise


@app.get("/")
def read_root():
    return {"message": "Welcome to the Products API"}


app.include_router(category_router)
app.include_router(product_router)
app.include_router(book_router)
