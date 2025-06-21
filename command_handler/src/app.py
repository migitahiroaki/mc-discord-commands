from os import environ, getenv
from typing import Any
from nacl.signing import VerifyKey
from logging import getLogger, INFO


from utils.decorator import discord_command
from typedefs.enums import (
    InteractionCallbackType,
    InteractionType,
)
from typedefs.models import (
    DiscordInteractionResponse,
    InteractionCommandData,
    InteractionResponseBody,
    InteractionCallbackData,
    InteractionRequestBody,
)
from typedefs.exceptions import BadRequest
from utils.ec2 import Ec2Instance
from utils.verify import get_verified


getLogger().setLevel(getenv("LOG_LEVEL", INFO))
logger = getLogger(__name__)


@discord_command
def lambda_handler(
    event: dict[str, Any], context: dict[str, Any]
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
        server_instance_id = environ["SERVER_INSTANCE_ID"]
        server_region_name = environ["SERVER_REGION_NAME"]
        verify_key = VerifyKey(bytes.fromhex(environ["APP_PUBLIC_KEY"]))

        logger.info(event)
        body: InteractionRequestBody = get_verified(
            event, verify_key, InteractionRequestBody
        )
        interaction_type = body.type

        if interaction_type == InteractionType.PING:
            # Pong
            return DiscordInteractionResponse(
                body=InteractionResponseBody(
                    type=InteractionCallbackType.PONG,
                )
            )

        elif interaction_type == InteractionType.APPLICATION_COMMAND:
            command_data: InteractionCommandData | None = body.data

            # validate command
            if (
                command_data
                and "be" == command_data.name
                and command_data.options
                and 1 == len(command_data.options)
            ):
                logger.debug(command_data)
                option = command_data.options[0]

                server_instance = Ec2Instance(
                    instance_id=server_instance_id, region_name=server_region_name
                )

                if "start" == option.value:
                    logger.info("(BE) Starting server instance")
                    result = server_instance.start()
                    return DiscordInteractionResponse(
                        body=InteractionResponseBody(
                            type=InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                            data=InteractionCallbackData(
                                content=f'State changed: {result["previous_state_name"]} -> {result["current_state_name"]}'
                            ),
                        )
                    )
                elif "stop" == option.value:
                    logger.info("(BE) Stopping server instance")
                    result = server_instance.stop()
                    return DiscordInteractionResponse(
                        body=InteractionResponseBody(
                            type=InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                            data=InteractionCallbackData(
                                content=f'State changed: {result["previous_state_name"]} -> {result["current_state_name"]}'
                            ),
                        )
                    )

        raise BadRequest(f"Command is invalid: {body.data=}")

    except BadRequest as e:
        # Log as warning. Do not give reason to the client.
        logger.warning(e, exc_info=True)
        return DiscordInteractionResponse(
            statusCode=401,
            body=InteractionResponseBody(
                type=InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                data=InteractionCallbackData(
                    content="Bad Request. For security reasons, the reason is not given.",
                ),
            ),
        )

    except Exception as e:
        # Log as error. Do not give reason to the client.
        logger.error(e, exc_info=True)
        return DiscordInteractionResponse(
            statusCode=200,
            body=InteractionResponseBody(
                type=InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                data=InteractionCallbackData(
                    content="Technical error. Please contact author.",
                ),
            ),
        )
