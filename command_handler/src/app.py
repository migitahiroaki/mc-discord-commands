from os import environ
from typing import Any
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import Logger
from nacl.signing import VerifyKey


from utils.decorator import discord_command
from typedefs.enums import InteractionCallbackType, InteractionType
from typedefs.models import (
    DiscordInteractionResponse,
    InteractionCommandData,
    InteractionResponseBody,
    InteractionCallbackData,
    InteractionRequestBody,
)
from typedefs.exceptions import BadRequest
from utils.verify import get_verified


verify_key = VerifyKey(bytes.fromhex(environ["APP_PUBLIC_KEY"]))
logger = Logger(service="hello")


@discord_command
def lambda_handler(
    event: dict[str, Any], context: LambdaContext
) -> DiscordInteractionResponse:
    """Sample pure Lambda function

    Parameters
    ----------
    event: HTTP API Proxy Event
    context: Lambda Context runtime methods and attributes

    Returns
    ------
    HTTP API Proxy Response

    """

    try:

        logger.info(event)
        body: InteractionRequestBody = get_verified(
            event, verify_key, InteractionRequestBody
        )
        data: InteractionCommandData = body.data
        interaction_type = data.type

        if interaction_type == InteractionType.PING:
            # Pong
            return DiscordInteractionResponse(
                body=InteractionResponseBody(
                    type=InteractionCallbackType.PONG,
                )
            )

        elif interaction_type == InteractionType.APPLICATION_COMMAND:
            logger.info(data.name)
            return DiscordInteractionResponse(
                body=InteractionResponseBody(
                    type=InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                    data=InteractionCallbackData(content="Command accepted!"),
                )
            )

        else:
            raise BadRequest(f"Unsupported interaction type: {interaction_type}")

    except BadRequest as e:
        # Log as warning. Do not give reason to the client.
        logger.warning(e)
        return DiscordInteractionResponse(
            statusCode=400,
            body=InteractionResponseBody(
                type=InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                data=InteractionCallbackData(
                    content="Bad Request. For security reasons, the reason is not given.",
                ),
            ),
        )

    except Exception as e:
        # Log as error. Do not give reason to the client.
        logger.error(e)
        return DiscordInteractionResponse(
            statusCode=500,
            body=InteractionResponseBody(
                type=InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                data=InteractionCallbackData(
                    content="Technical error. Please contact author.",
                ),
            ),
        )

    # API Gateway has weird case conversion, so we need to make them lowercase.
    # See https://github.com/aws/aws-sam-cli/issues/1860
    # headers: dict = {k.lower(): v for k, v in event["headers"].items()}
