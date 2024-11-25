import pytest
from .app.main import app


@pytest.fixture(scope="session")
def fastapi_app():
    return app
