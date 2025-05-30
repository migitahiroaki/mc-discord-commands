import json
from os import environ
from typing import Any
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.data_classes import (
    APIGatewayProxyEventV2,
    event_source,
)
from aws_lambda_powertools.event_handler.content_types import APPLICATION_JSON
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from interactions.models.discord.application import Application

from exception.bad_request import BadRequest
from model.api_proxy_response import ApiProxyResponse


# token = environ["APP_BOT_TOKEN"]
verify_key = VerifyKey(bytes.fromhex(environ["APP_PUBLIC_KEY"]))


"""
verify request


Raises:
    BadSignatureError
"""


def verify(headers: dict[str, str], body: str | None) -> None:
    try:
        signature = headers.get("x-signature-ed25519")
        timestamp = headers.get("x-signature-timestamp")
        verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
    except (TypeError, BadSignatureError) as e:
        raise BadRequest(e)


logger = Logger(service="hello")

app = APIGatewayHttpResolver()


@app.exception_handler(BadRequest)
def handle_bad_request(e: BadRequest):
    logger.exception(e)
    return Response(
        status_code=400,
        content_type=APPLICATION_JSON,
        body=json.dumps({"message": "Bad Request"}),
        headers={},
        cookies=[],
        isBase64Encoded=False,
    )


@app.exception_handler(Exception)
def handle_bad_request(e: Exception):
    logger.exception(e)
    return Response(
        status_code=500,
        content_type=APPLICATION_JSON,
        body=json.dumps({"message": "Bad Request"}),
        headers={},
        cookies=[],
        isBase64Encoded=False,
    )


@app.post("/start")
def start() -> ApiProxyResponse:
    event: APIGatewayProxyEventV2 = app.current_event
    verify(event.headers, event.body)
    logger.info("start called")
    return ApiProxyResponse(
        status_code=200,
        content_type=APPLICATION_JSON,
        body=json.dumps({"message": "start!"}),
        headers={},
        cookies=[],
        isBase64Encoded=False,
    )


@app.post("/stop")
def stop() -> ApiProxyResponse:
    event: APIGatewayProxyEventV2 = app.current_event
    verify(event.headers, event.body)
    logger.info("stop called")
    return ApiProxyResponse(
        status_code=200,
        content_type=APPLICATION_JSON,
        body=json.dumps({"message": "stop!"}),
        headers={},
        cookies=[],
        isBase64Encoded=False,
    )


@app.post("/")
def root() -> ApiProxyResponse:
    logger.info("root")
    event: APIGatewayProxyEventV2 = app.current_event
    verify(event.headers, event.body)
    req: dict = json.loads(event.body)
    if req["type"] == 0:  # InteractionType.Ping
        # Pong
        return ApiProxyResponse(
            status_code=204,
            content_type=APPLICATION_JSON,
            headers={},
            body="",
            isBase64Encoded=False,
            cookies=[],
        )
    else:
        raise BadRequest


# @event_source(data_class=APIGatewayProxyEventV2)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> ApiProxyResponse:
    """Sample pure Lambda function

    Parameters
    ----------
    event: HTTP API Proxy Event
    context: Lambda Context runtime methods and attributes

    Returns
    ------
    HTTP API Proxy Response

    """

    logger.info(event)
    # API Gateway has weird case conversion, so we need to make them lowercase.
    # See https://github.com/aws/aws-sam-cli/issues/1860
    # headers: dict = {k.lower(): v for k, v in event["headers"].items()}

    return app.resolve(event, context)
