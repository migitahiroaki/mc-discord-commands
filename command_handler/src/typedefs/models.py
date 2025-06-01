from typing import Literal, Optional, TypeVar, Generic
from aws_lambda_powertools.event_handler.content_types import APPLICATION_JSON
from pydantic import BaseModel
from typedefs.enums import (
    CommandOptionType,
    InteractionCallbackType,
    InteractionCommandType,
    InteractionType,
)

BodyT = TypeVar("BodyT", bound=BaseModel)


# for Request


class CommandOptions(BaseModel):
    name: str
    type: CommandOptionType
    value: str
    model_config = {"extra": "ignore"}


class InteractionCommandData(BaseModel):
    name: str
    id: str
    options: Optional[list[CommandOptions]]
    type: InteractionCommandType

    model_config = {"extra": "ignore"}


class InteractionRequestBody(BaseModel):
    id: str
    application_id: str
    channel_id: Optional[str] = None
    guild_id: Optional[str] = None
    data: InteractionCommandData
    type: InteractionType

    model_config = {"extra": "ignore"}


# for Response


class Embed(BaseModel):
    title: Optional[str] = None
    type: Optional[Literal["rich", "image", "link"]] = None
    description: Optional[str] = None
    url: Optional[str] = None
    color: Optional[int] = None
    image: Optional[dict[str, str]] = None
    thumbnail: Optional[dict[str, str]] = None


class InteractionCallbackData(BaseModel):
    tts: Optional[bool] = False
    content: Optional[str] = None
    embeds: Optional[list[Embed]] = None
    flags: Optional[int] = None


class InteractionResponseBody(BaseModel):
    type: InteractionCallbackType
    data: Optional[InteractionCallbackData] = None


class ApiProxyResponse(BaseModel, Generic[BodyT]):
    statusCode: int = 200
    headers: dict[str, str] = {"Content-Type": APPLICATION_JSON}
    body: Optional[BodyT] = None

    def to_dict(self) -> dict[str, str | int | bool]:
        d = self.model_dump(exclude={"body"}, exclude_none=True)
        d["body"] = (
            None if self.body is None else self.body.model_dump_json(exclude_none=True)
        )
        d["isBase64Encoded"] = False
        return d


DiscordInteractionResponse = ApiProxyResponse[InteractionResponseBody]
