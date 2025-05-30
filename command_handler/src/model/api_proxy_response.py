from typing import NotRequired, TypedDict


class ApiProxyResponse(TypedDict):
    status_code: int
    content_type: str
    headers: dict[str, str]
    body: str
    isBase64Encoded: bool
    cookies: NotRequired[list[str]]
