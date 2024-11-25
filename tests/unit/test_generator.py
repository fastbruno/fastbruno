from fastapi import FastAPI

from fastbruno import FastBruno, Request


def test_generator(fastapi_app):
    assert isinstance(fastapi_app, FastAPI)
    for route_info in FastBruno(fastapi_app).generate():
        assert isinstance(route_info, Request)
