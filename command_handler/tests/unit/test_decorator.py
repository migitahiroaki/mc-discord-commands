from typing import Any

from typedefs.enums import InteractionCallbackType
from typedefs.models import (
    DiscordInteractionResponse,
    InteractionCallbackData,
    InteractionResponseBody,
)
from utils.decorator import discord_command


def test_discord_command():

    @discord_command
    def handler(event: dict[str, Any], _: Any) -> DiscordInteractionResponse:
        return DiscordInteractionResponse(
            statusCode=200,
            body=InteractionResponseBody(
                type=InteractionCallbackType.PONG,
                data=InteractionCallbackData(),
            ),
            headers={"Content-Type": "application/json"},
        )

    res = handler({"key": "value"}, None)
    assert isinstance(res, dict)
