from typing import Annotated, List
import uuid

from fastapi import APIRouter, Body, Depends, File, Form, Header, Query, UploadFile
from pydantic import BaseModel

router = APIRouter(prefix="/subroute")


@router.get("/")
def subroute_root():
    return {"message": "Hello World"}


@router.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}


def get_cookie_params(route):
    return [p.name for p in route.dependant.cookie_params]


class HelloPayload(BaseModel):
    hello: str


@router.post("/hello")
def hello(
    payload: dict = Body(...), cookie_params: List[str] = Depends(get_cookie_params)
):
    return {"message": cookie_params}


@router.post("/hello-with-payload")
def hello_with_payload(
    payload: HelloPayload,
    cookie_params: List[str] = Depends(get_cookie_params),
):
    return {"message": cookie_params}


# Routes with a log of params and response model
class LogResponse(BaseModel):
    message: str


@router.get("/log", response_model=LogResponse, response_description="Log response")
def log(limit: int, query: str = Query(..., description="Query string")):
    return {"message": f"Hello {query}"}


@router.get("/log-with-response-model/:id")
def log_with_response_model(param: str, id: int, x_ip: str = Header(...)):
    return {"message": f"Hello {param}"}


class LogResponseWithModel(BaseModel):
    uid: uuid.UUID


@router.put("/put/{random_id}/update")
def put_router(
    random_id: uuid.UUID,
    body: LogResponseWithModel,
    dep: str = Depends(get_cookie_params),
):
    return {"put": random_id, "body": body, "dep": dep}


@router.post("/file")
def file(file: UploadFile = File(...)):
    return {"filename": file.filename}
