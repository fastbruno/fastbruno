from fastbruno.__internal.logger import bruno_logger


IS_FASTAPI_INSTALLED = False

try:
    from fastapi import FastAPI
    from fastapi.routing import APIRoute

    IS_FASTAPI_INSTALLED = True
except ImportError:
    bruno_logger.warning("FastAPI is not installed. FastBruno will not work.")
