from fastapi import FastAPI
from .subroute import router as subroute_router

app = FastAPI()

app.include_router(subroute_router)

@app.get("/")
def read_root():
    return {"message": "Hello World"}
