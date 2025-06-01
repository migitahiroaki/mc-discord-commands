import json
from typing import Any, Generator

from unittest.mock import patch
import pytest

from nacl.signing import SigningKey, VerifyKey
from command_handler.tests.integration.resources.context import CONTEXT
from integration.resources.ping import PING_BODY


@pytest.fixture(scope="function")
def mocked_signing_key() -> Generator[SigningKey, None, None]:
    # Key pair for testing
    signing_key: SigningKey = SigningKey(b"0123456789abcdef0123456789abcdef")
    verify_key: VerifyKey = signing_key.verify_key
    # getting env APP_PUBLIC_KEY returns mocked value.
    with patch.dict("os.environ", {"APP_PUBLIC_KEY": verify_key.encode().hex()}):
        yield signing_key
    # patch.dict("os.environ", {"APP_PUBLIC_KEY": verify_key.encode().hex()})
    # # from app import lambda_handler

    # yield signing_key


def test_lambda_handler_ping_positive(mocked_signing_key: SigningKey):
    """Discord sends ping requests with an empty signature that expects 2XX."""
    from app import lambda_handler

    body: str = json.dumps(PING_BODY)
    timestamp = "1748698092919"
    message = f"{timestamp}{body}".encode()
    signature = mocked_signing_key.sign(message).signature.hex()
    headers = {
        "content-type": "application/json",
        "accept-encoding": "gzip, deflate, sdch",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "user-agent": "Discord-Interactions/1.0 (+https://discord.com)",
        "x-signature-ed25519": signature,
        "x-signature-timestamp": timestamp,
    }
    event: dict[str, Any] = {
        "body": body,
        "cookies": [],
        "headers": headers,
        "http_method": "POST",
        "isBase64Encoded": False,
        "multi_value_query_string_parameters": {},
        "path": "/commands",
        "path_parameters": {},
        "query_string_parameters": {},
        "raw_event": "[SENSITIVE]",
        "raw_path": "/v1/commands",
        "raw_query_string": "",
        "request_context": CONTEXT,
        "route_key": "POST /commands",
        "stage_variables": {},
        "version": "2.0",
    }

    response: dict[str, Any] = lambda_handler(event, CONTEXT)
    assert response["statusCode"] == 200


def test_lambda_handler_ping_no_signature(mocked_signing_key: SigningKey):
    """Discord also sends ping requests with an empty signature that expects 4XX."""
    from app import lambda_handler

    body: str = json.dumps(PING_BODY)
    timestamp = "1748698092919"
    headers = {
        "content-type": "application/json",
        "accept-encoding": "gzip, deflate, sdch",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "user-agent": "Discord-Interactions/1.0 (+https://discord.com)",
        "x-signature-ed25519": "",
        "x-signature-timestamp": timestamp,
    }
    event: dict[str, Any] = {
        "body": body,
        "cookies": [],
        "headers": headers,
        "http_method": "POST",
        "isBase64Encoded": False,
        "multi_value_query_string_parameters": {},
        "path": "/commands",
        "path_parameters": {},
        "query_string_parameters": {},
        "raw_event": "[SENSITIVE]",
        "raw_path": "/v1/commands",
        "raw_query_string": "",
        "request_context": CONTEXT,
        "route_key": "POST /commands",
        "stage_variables": {},
        "version": "2.0",
    }

    response: dict[str, Any] = lambda_handler(event, CONTEXT)
    assert response["statusCode"] == 400


def test_lambda_handler_be_start_positive(mocked_signing_key: SigningKey):
    """Command /be start"""
    from app import lambda_handler

    body: str = json.dumps(PING_BODY)
    timestamp = "1748698092919"
    message = f"{timestamp}{body}".encode()
    signature = mocked_signing_key.sign(message).signature.hex()
    headers = {
        "content-type": "application/json",
        "accept-encoding": "gzip, deflate, sdch",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "user-agent": "Discord-Interactions/1.0 (+https://discord.com)",
        "x-signature-ed25519": signature,
        "x-signature-timestamp": timestamp,
    }
    event: dict[str, Any] = {
        "body": body,
        "cookies": [],
        "headers": headers,
        "http_method": "POST",
        "isBase64Encoded": False,
        "multi_value_query_string_parameters": {},
        "path": "/commands",
        "path_parameters": {},
        "query_string_parameters": {},
        "raw_event": "[SENSITIVE]",
        "raw_path": "/v1/commands",
        "raw_query_string": "",
        "request_context": CONTEXT,
        "route_key": "POST /commands",
        "stage_variables": {},
        "version": "2.0",
    }

    response: dict[str, Any] = lambda_handler(event, CONTEXT)
    assert response["statusCode"] == 200
