from typing import Callable, Optional
from os import environ
from discord_typings import ApplicationCommandPayload
from typeguard import typechecked

import requests
import json
import sys

DISCORD_BOT_TOKEN = environ["DISCORD_BOT_TOKEN"]
GUILD_ID = environ["GUILD_ID"]
APPLICATION_ID = environ["APPLICATION_ID"]
base_url = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/guilds/{GUILD_ID}/commands"
headers = {
    "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
    "Content-Type": "application/json",
}

# modify this dictionary to change the command
commands: ApplicationCommandPayload = {
    "type": 1,
    "name": "be",
    "description": "BEサーバの起動や確認",
    "options": [
        {
            "type": 3,
            "name": "action",
            "description": "開始(start)・停止(stop)・状態確認(status)",
            "required": True,
            "choices": [
                {"name": "start", "value": "start"},
                {"name": "stop", "value": "stop"},
                {"name": "status", "value": "status"},
            ],
        },
    ],
}


@typechecked
def list_commands() -> requests.Response:
    return requests.get(base_url, headers=headers)


@typechecked
def get_command(command_id: str):
    return requests.get(f"{base_url}/{command_id}", headers=headers)


@typechecked
def register_command() -> requests.Response:
    return requests.post(base_url, headers=headers, data=json.dumps(commands))


# @typechecked
# def update_command(command_id: str) -> requests.Response:
#     return requests.put(
#         f"{base_url}/{command_id}", headers=headers, data=json.dumps(commands)
#     )


@typechecked
def delete_command(command_id: str) -> requests.Response:
    return requests.delete(f"{base_url}/{command_id}", headers=headers)


def execute(
    command: Callable[..., requests.Response],
    command_id: Optional[str] = None,
):
    try:
        res = command(command_id) if command_id else command()
        print(res.status_code)
        if res.content:
            print(json.dumps(res.json(), indent=2))
    except TypeError as e:
        print(e)


def main():

    command = sys.argv[1]
    command_id = sys.argv[2] if len(sys.argv) > 2 else None

    if command == "list":
        execute(list_commands)
    elif command == "get":
        execute(get_command, command_id)
    elif command == "register":
        execute(register_command)
    # Not implemented for guild command. Use register instead.
    # elif command == "update":
    #     execute(update_command, command_id)
    elif command == "delete":
        execute(delete_command, command_id)
    else:
        print("Invalid command")


if __name__ == "__main__":
    main()
