from fastapi import FastAPI

app = FastAPI(title="Product CRUD API", version="1.0.0")

@app.get("/")
def read_root():
    return{"message":"welcome to fastapi product crud api"}

@app.get("/products")
def get_all():
    return {"message":"success get all data", "data":"iPhone cook dih"}
