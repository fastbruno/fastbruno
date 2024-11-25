from collections import defaultdict
import json
from typing import Any, Dict, List, Literal, NamedTuple, Optional, Union
from dataclasses import dataclass, field


# Basic types
AuthType = Literal["none", "basic", "bearer", "digest", "oauth2", "awsv4", "wsse"]
BodyType = Literal[
    "json", "text", "xml", "sparql", "form-urlencoded", "multipart-form", "graphql"
]
HttpMethod = Literal["get", "post", "put", "delete", "patch", "head", "options"]


class Meta(NamedTuple):
    name: str
    type: Literal["http"]
    seq: int


class RequestType(NamedTuple):
    url: str
    method: HttpMethod
    body: Optional[BodyType] = None
    auth: AuthType = "none"


@dataclass
class QueryParam:
    name: str
    value: str
    enabled: bool = True


@dataclass
class PathParam:
    name: str
    value: str


@dataclass
class Header:
    name: str
    value: str
    enabled: bool = field(default=True)


class AuthBasic(NamedTuple):
    username: str
    password: str


class AuthBearer(NamedTuple):
    token: str


class AuthDigest(NamedTuple):
    username: str
    password: str


class AuthWSSE(NamedTuple):
    username: str
    password: str


class AuthAWSv4(NamedTuple):
    accessKeyId: str
    secretAccessKey: str
    sessionToken: Optional[str]
    service: str
    region: str
    profileName: Optional[str]


class AuthOAuth2(NamedTuple):
    grant_type: str
    callback_url: str
    authorization_url: str
    access_token_url: str
    client_id: str
    client_secret: str
    scope: str
    state: str
    pkce: bool = False


Auth = Union[AuthBasic, AuthBearer, AuthDigest, AuthWSSE, AuthAWSv4, AuthOAuth2]


@dataclass
class Body:
    type: BodyType
    content: str
    vars: Optional[Dict[str, Any]] = None  # For GraphQL variables


@dataclass
class Variables:
    name: str
    value: str
    enabled: bool = True
    is_environment: bool = False  # Denoted by @ prefix


@dataclass
class Assertion:
    target: str  # e.g. "$res.status" or "$res.body.message"
    expected: Any
    enabled: bool = True


@dataclass
class Script:
    type: Literal["pre-request", "tests"]
    content: str


@dataclass
class BrunoRequest:
    meta: Meta
    request: RequestType
    query_params: List[QueryParam] = field(default_factory=list)
    path_params: List[PathParam] = field(default_factory=list)
    headers: List[Header] = field(default_factory=list)
    auth: Optional[Auth] = None
    body: Optional[Body] = None
    pre_request_vars: List[Variables] = field(default_factory=list)
    post_response_vars: List[Variables] = field(default_factory=list)
    assertions: List[Assertion] = field(default_factory=list)
    scripts: List[Script] = field(default_factory=list)
    docs: Optional[str] = None


class BrunoLangV2:
    @staticmethod
    def indent_string(text: str, spaces: int = 2) -> str:
        """Indent each line of text by specified number of spaces"""
        if not text:
            return text
        return "\n".join(" " * spaces + line for line in text.splitlines())

    @staticmethod
    def strip_last_line(text: str) -> str:
        """Remove trailing newlines"""
        if not text:
            return text
        return text.rstrip()

    @staticmethod
    def get_value_string(value: str) -> str:
        """Handle multiline strings with proper indentation"""
        if not value or "\n" not in value:
            return value

        indented_lines = "\n".join(f"  {line}" for line in value.splitlines())
        return f"'''\n{indented_lines}\n'''"

    @staticmethod
    def to_bru(request: BrunoRequest) -> str:
        """Convert a BrunoRequest object to .bru format"""
        bru = ""

        # Meta section
        bru += "meta {\n"
        bru += f"  name: {request.meta.name}\n"
        bru += f"  type: {request.meta.type}\n"
        bru += f"  seq: {request.meta.seq}\n"
        bru += "}\n\n"

        # HTTP section
        bru += f"{request.request.method} {{\n"
        bru += f"  url: {request.request.url}"
        if request.request.body:
            bru += f"\n  body: {request.request.body}"
        if request.request.auth != "none":
            bru += f"\n  auth: {request.request.auth}"
        bru += "\n}\n\n"

        # Query Parameters
        if request.query_params:
            bru += "params:query {\n"
            enabled_params = [p for p in request.query_params if p.enabled]
            disabled_params = [p for p in request.query_params if not p.enabled]

            if enabled_params:
                bru += BrunoLangV2.indent_string(
                    "\n".join(f"{p.name}: {p.value}" for p in enabled_params)
                )
                bru += "\n"
            if disabled_params:
                bru += BrunoLangV2.indent_string(
                    "\n".join(f"~{p.name}: {p.value}" for p in disabled_params)
                )
                bru += "\n"
            bru += "}\n\n"

        # Headers
        if request.headers:
            bru += "headers {\n"
            enabled_headers = [h for h in request.headers if h.enabled]
            disabled_headers = [h for h in request.headers if not h.enabled]

            if enabled_headers:
                bru += BrunoLangV2.indent_string(
                    "\n".join(f"{h.name}: {h.value}" for h in enabled_headers)
                )
                bru += "\n"
            if disabled_headers:
                bru += BrunoLangV2.indent_string(
                    "\n".join(f"~{h.name}: {h.value}" for h in disabled_headers)
                )
                bru += "\n"
            bru += "}\n\n"

        # Auth sections
        if request.auth:
            if isinstance(request.auth, AuthBasic):
                bru += "auth:basic {\n"
                bru += f"  username: {request.auth.username}\n"
                bru += f"  password: {request.auth.password}\n"
                bru += "}\n\n"
            elif isinstance(request.auth, AuthBearer):
                bru += "auth:bearer {\n"
                bru += f"  token: {request.auth.token}\n"
                bru += "}\n\n"
            # Add other auth types as needed...

        # Body section
        if request.body:
            bru += f"body:{request.body.type} {{\n"
            bru += BrunoLangV2.indent_string(json.dumps(request.body.content, indent=2))
            bru += "\n}\n\n"

            if request.body.type == "graphql" and request.body.vars:
                bru += "body:graphql:vars {\n"
                bru += BrunoLangV2.indent_string(
                    json.dumps(request.body.vars, indent=2)
                )
                bru += "\n}\n\n"

        # Variables
        if request.pre_request_vars:
            bru += "vars:pre-request {\n"
            for var in request.pre_request_vars:
                prefix = "~" if not var.enabled else ""
                env_prefix = "@" if var.is_environment else ""
                bru += f"  {prefix}{env_prefix}{var.name}: {var.value}\n"
            bru += "}\n\n"

        # Assertions
        if request.assertions:
            bru += "assert {\n"
            for assertion in request.assertions:
                prefix = "~" if not assertion.enabled else ""
                bru += f"  {prefix}{assertion.target}: {assertion.expected}\n"
            bru += "}\n\n"

        # Scripts
        for script in request.scripts:
            if script.type == "pre-request":
                bru += "script:pre-request {\n"
                bru += BrunoLangV2.indent_string(script.content)
                bru += "\n}\n\n"
            elif script.type == "tests":
                bru += "script:post-response {\n"
                bru += BrunoLangV2.indent_string(script.content)
                bru += "\n}\n\n"

        # Docs
        if request.docs:
            bru += "docs {\n"
            bru += BrunoLangV2.indent_string(request.docs)
            bru += "\n}\n\n"

        return BrunoLangV2.strip_last_line(bru)
