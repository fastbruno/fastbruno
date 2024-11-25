from collections import defaultdict
from dataclasses import dataclass, field
import datetime
from pydantic import BaseModel
from typing import Any, Dict, List, Literal, Optional
from fastapi.routing import APIRoute
import urllib.parse

from fastbruno.__internal.brunotypes import (
    BrunoLangV2,
    BrunoRequest,
    Meta,
    RequestType,
    Header,
    Body,
)


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
    annotation: Any
    place: Literal["query", "header", "cookie", "body", "path"] = "query"

    @property
    def which_type(self):
        if issubclass(self.annotation, BaseModel):
            return "json"
        if isinstance(self.annotation, list):
            return "list"
        if isinstance(self.annotation, dict):
            return "dict"
        if isinstance(self.annotation, bool):
            return "bool"
        if isinstance(self.annotation, int):
            return "int"
        if isinstance(self.annotation, float):
            return "float"
        if isinstance(self.annotation, str):
            return "text"
        if isinstance(self.annotation, datetime.datetime):
            return "datetime"

        # print(self.annotation)
        return "text"

    def get_body_schema(self):
        if issubclass(self.annotation, BaseModel):
            return self.annotation.model_json_schema().get("properties", {})
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
            request.path.append(
                ReqParam(name=p.name, annotation=p.field_info.annotation, place="path")
            )
        for p in route.dependant.query_params:
            request.query.append(
                ReqParam(name=p.name, annotation=p.field_info.annotation, place="query")
            )
        for p in route.dependant.header_params:
            request.header.append(
                ReqParam(
                    name=p.name, annotation=p.field_info.annotation, place="header"
                )
            )
        for p in route.dependant.cookie_params:
            request.cookie.append(
                ReqParam(
                    name=p.name, annotation=p.field_info.annotation, place="cookie"
                )
            )
        for p in route.dependant.body_params:
            request.body = ReqParam(
                name=p.name, annotation=p.field_info.annotation, place="body"
            )

    return request
