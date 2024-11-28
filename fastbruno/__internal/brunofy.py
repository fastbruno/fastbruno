import datetime
from enum import Enum
import urllib.parse
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Union

from fastapi.routing import APIRoute
from fastapi._compat import ModelField
from pydantic import BaseModel

from fastbruno.__internal.brunotypes import (
    Body,
    BrunoLangV2,
    BrunoRequest,
    Header,
    Meta,
    RequestType,
)


class DataType(Enum):
    TEXT = "text"
    JSON = "json"
    NUMBER = "number"
    BOOLEAN = "boolean"
    FILE = "file"


@dataclass
class RouteInfo:
    path: str
    methods: List[str]
    name: str
    deprecated: Optional[bool]
    description: Optional[str]
    tags: Optional[List[str]]
    response_model: Optional[str]

    @property
    def default_method(self):
        return self.methods[0].lower()

    @property
    def bruno_filename(self) -> str:
        return f"{self.default_method}_{self.name}.bru"


@dataclass
class ReqParam:
    name: str
    model_field: Optional["ModelField"]
    place: Literal["query", "header", "cookie", "body", "path"] = "query"

    @property
    def which_type(self):
        if not self.model_field or not hasattr(
            self.model_field.field_info, "annotation"
        ):
            return DataType.TEXT.value

        annotation = self.model_field.field_info.annotation

        # Handle Pydantic BaseModel
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return DataType.JSON.value

        # Handle UploadFile
        if annotation.__name__ == "UploadFile":
            return DataType.FILE.value

        # Handle basic types
        basic_type_mapping = {
            str: DataType.TEXT.value,
            int: DataType.NUMBER.value,
            float: DataType.NUMBER.value,
            bool: DataType.BOOLEAN.value,
            dict: DataType.JSON.value,
        }
        if annotation in basic_type_mapping:
            return basic_type_mapping[annotation]

        # Handle typing annotations (List, Dict, Union, Optional)
        origin = getattr(annotation, "__origin__", None)
        if origin:
            if origin in (list, dict):
                return DataType.JSON.value
            if origin in (Union,):
                # For Optional[str] or Union types, use the first type
                args = getattr(annotation, "__args__", [])
                if args and args[0] != type(None):  # noqa: E721
                    return basic_type_mapping.get(args[0], DataType.TEXT.value)

        # Default fallback
        return DataType.TEXT.value

    def get_body_schema(self):
        if (
            self.model_field
            and isinstance(self.model_field.field_info.annotation, type)
            and issubclass(self.model_field.field_info.annotation, BaseModel)
        ):
            return self.model_field.field_info.annotation.model_json_schema().get(
                "properties", {}
            )
        return None


@dataclass
class Request:
    base_url: str
    route_info: RouteInfo
    path: List[ReqParam] = field(default_factory=list)
    query: List[ReqParam] = field(default_factory=list)
    header: List[ReqParam] = field(default_factory=list)
    cookie: List[ReqParam] = field(default_factory=list)
    body: Optional[ReqParam] = None
    sequence: int = 0

    _bru_nodes: Dict[
        Literal["meta", "get", "post", "put", "delete", "body"], List[str]
    ] = field(default_factory=lambda: defaultdict(list))

    @property
    def meta_name(self):
        return self.route_info.name

    @property
    def request_method(self):
        return self.route_info.default_method

    @property
    def full_path_with_params(self):
        # Use urllib.parse to encode the params
        return f"{self.base_url.strip('/')}{self.route_info.path}" + (
            ("?" + urllib.parse.urlencode([(p.name, p.which_type) for p in self.query]))
            if self.query
            else ""
        )

    def to_bru(self):
        brunoreq = BrunoRequest(
            meta=Meta(
                name=self.meta_name,
                type="http",
                seq=self.sequence,
            ),
            request=RequestType(
                url=self.full_path_with_params,
                method=self.request_method,
                body=self.body.which_type if self.body else "",
            ),
            query_params=[],
            path_params=[],
            headers=[Header(name="content-type", value="application/json")],
            body=(
                Body(
                    type=self.body.which_type, content=self.body.get_body_schema() or ""
                )
                if self.body
                else ""
            ),
        )

        return BrunoLangV2.to_bru(brunoreq)


def explore_route(route: APIRoute, base_url: str) -> Request:
    """Explore a single route and return its details"""

    request = Request(
        base_url=base_url,
        route_info=RouteInfo(
            path=route.path,
            methods=list(route.methods),
            name=route.name,
            response_model=getattr(route, "response_model", None),
            deprecated=getattr(route, "deprecated", None),
            description=route.description,
            tags=getattr(route, "tags", []),
        ),
    )

    # Get parameters info from the dependant
    if hasattr(route, "dependant"):
        # Run one loop to get all params
        for p in route.dependant.path_params:
            # print(p.field_info)
            request.path.append(ReqParam(name=p.name, place="path", model_field=p))
        for p in route.dependant.query_params:
            request.query.append(ReqParam(name=p.name, place="query", model_field=p))
        for p in route.dependant.header_params:
            request.header.append(ReqParam(name=p.name, place="header", model_field=p))
        for p in route.dependant.cookie_params:
            request.cookie.append(ReqParam(name=p.name, place="cookie", model_field=p))
        for p in route.dependant.body_params:
            request.body = ReqParam(name=p.name, place="body", model_field=p)

    return request
