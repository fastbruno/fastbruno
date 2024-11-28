from enum import Enum
from typing import Dict, List, Optional, Union
import uuid
from fastapi import Body, FastAPI, Path, Query
from pydantic import BaseModel

from .subroute import router as subroute_router

app = FastAPI()

app.include_router(subroute_router)


class Model(BaseModel):
    a: int
    b: str
    c: bool
    d: float
    e: uuid.UUID


@app.get("/")
def read_root():
    return {"message": "Hello World"}


# A route with a lot of query parameters
@app.get("/query")
def query(
    q: str = Query(..., description="A query string"),
    page: int = Query(1, ge=1, description="The page number"),
):
    return {"query": q, "page": page}


# A route with a body
@app.post("/body")
def body(body=Body(..., description="A body")):
    return {"body": body}


# A route with a path parameter
@app.get("/path/{path}")
def path(path: str = Path(..., description="A path")):
    return {"path": path}


@app.put("/put/{random_id}/update")
def put(random_id: uuid.UUID, body: Model):
    return {"put": random_id, "body": body}


@app.get("/enum")
def enum(enum=Enum("Enum", ["a", "b", "c"])):
    return {"enum": enum}


@app.get("/optional")
def optional(optional: Optional[str] = None):
    return {"optional": optional}


@app.get("/union")
def union(union: Union[int, str]):
    return {"union": union}


@app.get("/list")
def list(list: List[int]):
    return {"list": list}


@app.get("/dict")
def dict(dict: Dict[str, int]):
    return {"dict": dict}


@app.get("/model")
def model(model: Model):
    return {"model": model}


@app.get("/model_list")
def model_list(model_list: List[Model]):
    return {"model_list": model_list}


@app.get("/model_dict")
def model_dict(model_dict: Dict[str, Model]):
    return {"model_dict": model_dict}


@app.post("/model_body")
def model_body(model_body: Model = Body(..., description="A model body")):
    return {"model_body": model_body}


@app.post("/model_body_list")
def model_body_list(
    model_body_list: List[Model] = Body(..., description="A list of model bodies")
):
    return {"model_body_list": model_body_list}


@app.post("/model_body_dict")
def model_body_dict(
    model_body_dict: Dict[str, Model] = Body(
        ..., description="A dictionary of model bodies"
    )
):
    return {"model_body_dict": model_body_dict}
