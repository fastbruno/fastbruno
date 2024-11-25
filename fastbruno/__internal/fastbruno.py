import os
from fastbruno.__internal.brunofy import Request, explore_route
from fastbruno.__internal.fastapiinfo import FastAPIInfo
from fastbruno.__internal.logger import bruno_logger
from fastbruno.__internal.fastapi import FastAPI, APIRoute, IS_FASTAPI_INSTALLED


class FastBruno:
    def __init__(
        self,
        app: "FastAPI",
        base_url: str = "http://localhost:8000",
        path: str = "bruno",
    ):
        if not IS_FASTAPI_INSTALLED:
            raise ValueError("FastAPI is not installed. FastBruno will not work.")

        self.app = app

        self.fastapi_info = FastAPIInfo(app)

        bruno_logger.debug(
            f"FastBruno initialized with FastAPI version: {self.fastapi_info.version}"
        )

        self.base_url = base_url
        self.path = os.path.join(path)

    def save_collection(self, req: Request):
        bru_file_path = os.path.join(self.path, f"{req.route_info.name}.bru")

        # Create file and dirs if not exist
        os.makedirs(self.path, exist_ok=True)

        with open(bru_file_path, "w") as f:
            f.write(req.to_bru())

    def generate(self):
        print("🔍 Exploring FastAPI Routes:")
        print("=" * 50)

        for route in self.app.routes:
            if isinstance(route, APIRoute):
                route_info = explore_route(route, self.base_url)
                yield route_info

    def brunofy(self):
        for route_info in self.generate():
            self.save_collection(route_info)
