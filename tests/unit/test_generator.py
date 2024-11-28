from fastapi import FastAPI

from fastbruno import FastBruno, Request


def test_generator(fastapi_app):
    assert isinstance(fastapi_app, FastAPI)
    for route_info in FastBruno(fastapi_app).generate():
        assert isinstance(route_info, Request)
        assert isinstance(route_info.to_bru(), str)
        print(route_info.to_bru())
