from typing import Any, TypeVar
from venv import logger
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from pydantic import BaseModel, ValidationError

from typedefs.exceptions import BadRequest

ModelT = TypeVar("ModelT", bound=BaseModel)


def deserialize(json_text: str, Model: type[ModelT]) -> ModelT:
    print(type(json_text))
    print(json_text)
    return Model.model_validate_json(json_text)


def get_verified(
    event: dict[str, Any], verify_key: VerifyKey, Model: type[ModelT]
) -> ModelT:
    try:

        # proxy_event = APIGatewayProxyEventV2(event)
        headers: dict[str, str] | None = event["headers"]
        if not headers:
            raise BadRequest("Request headers are missing")

        body: str | None = event["body"]
        if not body:
            raise BadRequest("Request body is missing")

        signature = headers["x-signature-ed25519"]
        timestamp = headers["x-signature-timestamp"]
        # Verify the signature here.
        verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
        return deserialize(body, Model)

    except (KeyError, ValueError, TypeError, BadSignatureError, ValidationError) as e:
        logger.warning(e)
        raise BadRequest(e)
