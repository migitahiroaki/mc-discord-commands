from typing import Any, TypeVar
from venv import logger
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from aws_lambda_powertools.utilities.data_classes import (
    APIGatewayProxyEventV2,
)
from pydantic import BaseModel, ValidationError

from typedefs.exceptions import BadRequest

ModelT = TypeVar("ModelT", bound=BaseModel)


def get_verified(
    event: dict[str, Any], verify_key: VerifyKey, Model: type[ModelT]
) -> ModelT:
    try:
        proxy_event = APIGatewayProxyEventV2(event)
        headers = proxy_event.headers
        if (body := proxy_event.body) is None:
            raise BadRequest("Request body is missing")

        signature = headers["x-signature-ed25519"]
        timestamp = headers["x-signature-timestamp"]
        # Verify the signature here.
        verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
        return Model.model_validate(body)

    except (KeyError, ValueError, TypeError, BadSignatureError, ValidationError) as e:
        logger.warning(e)
        raise BadRequest(e)
