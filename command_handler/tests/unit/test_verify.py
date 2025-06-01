import json
import pytest
from typing import Any, Final, TypedDict

from pydantic import BaseModel, ValidationError
from typedefs.exceptions import BadRequest
from typedefs.models import (
    CommandOptions,
    InteractionCommandData,
    InteractionRequestBody,
)
from utils.verify import deserialize, get_verified
from nacl.signing import SigningKey, VerifyKey


class DummyEvent(TypedDict):
    headers: dict[str, str]
    body: str


class DummyModel(BaseModel):
    name: str


DUMMY_MODEL: Final[DummyModel] = DummyModel(name="test")


# Key pair for testing
signing_key: SigningKey = SigningKey(b"0123456789abcdef0123456789abcdef")
verify_key: VerifyKey = signing_key.verify_key

# DUMMY_EVENT: Final[DummyEvent] = {
#     "headers": {

ID_0000000000000000000: Final[str] = "0000000000000000000"
ID_1111111111111111111: Final[str] = "1111111111111111111"
ID_2222222222222222222: Final[str] = "2222222222222222222"
ID_3333333333333333333: Final[str] = "3333333333333333333"

DATA_BE_START: Final[dict[str, Any]] = {
    "id": ID_0000000000000000000,
    "name": "be",
    "options": [
        {"name": "action", "type": 3, "value": "start"}  # CommandOptionType.STRING
    ],
    "type": 1,  # InteractionCommandType.CHAT_INPUT
}
DATA_MISSING_TYPE: Final[dict[str, Any]] = {
    "id": ID_0000000000000000000,
    "name": "be",
    "options": None,
}

REQUEST_BE_START: Final[dict[str, Any]] = {
    "id": ID_0000000000000000000,
    "application_id": ID_1111111111111111111,
    "channel_id": ID_2222222222222222222,
    "guild_id": ID_3333333333333333333,
    "context": 0,
    "data": DATA_BE_START,
    "type": 2,  # InteractionType.APPLICATION_COMMAND
    "version": 1,
}
REQUEST_DATA_MISSING_TYPE: Final[dict[str, Any]] = {
    "id": ID_0000000000000000000,
    "application_id": ID_1111111111111111111,
    "channel_id": ID_2222222222222222222,
    "guild_id": ID_3333333333333333333,
    "context": 0,
    "data": DATA_MISSING_TYPE,
    "type": 2,  # InteractionType.APPLICATION_COMMAND
    "version": 1,
}


def test_deserialize_data_positive():
    json_text: str = json.dumps(DATA_BE_START)
    data: InteractionCommandData = deserialize(json_text, InteractionCommandData)

    assert ID_0000000000000000000 == data.id
    assert isinstance(data.options, list)
    assert all(isinstance(o, CommandOptions) for o in data.options)


def test_deserialize_data_invalid():
    json_text: str = json.dumps(DATA_MISSING_TYPE)
    with pytest.raises(ValidationError) as e:
        deserialize(json_text, InteractionCommandData)


def test_deserialize_request_positive():
    json_text: str = json.dumps(REQUEST_BE_START)
    body: InteractionRequestBody = deserialize(json_text, InteractionRequestBody)
    assert ID_0000000000000000000 == body.id
    assert ID_1111111111111111111 == body.application_id
    assert ID_2222222222222222222 == body.channel_id
    assert ID_3333333333333333333 == body.guild_id
    assert isinstance(body.data, InteractionCommandData)


def test_deserialize_request_data_invalid():
    json_text: str = json.dumps(REQUEST_DATA_MISSING_TYPE)
    with pytest.raises(ValidationError) as e:
        deserialize(json_text, InteractionRequestBody)


def test_get_verified_positive():
    body: str = DUMMY_MODEL.model_dump_json()
    timestamp = "1234567890"
    message = f"{timestamp}{body}".encode()
    signature = signing_key.sign(message).signature.hex()
    headers = {
        "x-signature-ed25519": signature,
        "x-signature-timestamp": timestamp,
    }
    event: dict[str, Any] = {
        "headers": headers,
        "body": body,
    }

    dummy_model: DummyModel = get_verified(event, verify_key, DummyModel)
    assert isinstance(dummy_model, DummyModel)


def test_get_verified_missing_body():
    timestamp = "1234567890"
    # Only timestamp is provided, body is missing
    message = timestamp.encode()
    signature = signing_key.sign(message).signature.hex()
    headers = {
        "x-signature-ed25519": signature,
        "x-signature-timestamp": timestamp,
    }
    event: dict[str, Any] = {
        "headers": headers,
        "body": None,
    }

    # Should be wrapped in BadRequest
    with pytest.raises(BadRequest) as e:
        get_verified(event, verify_key, DummyModel)


def test_get_verified_missing_headers():
    body: str = DUMMY_MODEL.model_dump_json()
    event: dict[str, Any] = {
        "body": body,
    }

    # Should be wrapped in BadRequest
    with pytest.raises(BadRequest) as e:
        get_verified(event, verify_key, DummyModel)


def test_get_verified_wrong_signature():
    body: str = DUMMY_MODEL.model_dump_json()
    timestamp = "1234567890"
    headers = {
        "x-signature-ed25519": "123",  # Wrong signature
        "x-signature-timestamp": timestamp,
    }
    event: dict[str, Any] = {
        "headers": headers,
        "body": body,
    }

    # Should be wrapped in BadRequest
    with pytest.raises(BadRequest) as e:
        get_verified(event, verify_key, DummyModel)
