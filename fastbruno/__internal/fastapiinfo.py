# Define a singleton class to store FastAPI information
from fastapi import FastAPI

class FastAPIInfo:
    __instance = None

    def __init__(self, app: "FastAPI"):
        if FastAPIInfo.__instance is not None:
            return FastAPIInfo.__instance
        else:
            FastAPIInfo.__instance = self

        self._version = app.version

    @property
    def version(self):
        return self._version
