from os.path import join, dirname
from typing import Any
from dotenv import load_dotenv
import requests
import json
from os import environ

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(verbose=True)

# Authorization info
DISCORD_BOT_TOKEN = environ["DISCORD_BOT_TOKEN"]
APPLICATION_ID = environ["APPLICATION_ID"]

commands: dict[str, Any] = {
    "name": "be",
    "description": "BEサーバの起動や確認",
    "options": [
        {
            "name": "action",
            "description": "開始(start)・停止(stop)・状態確認(status)",
            "type": 3,
            "required": True,
            "choices": [
                {"name": "start", "value": "start"},
                {"name": "stop", "value": "stop"},
                {"name": "status", "value": "status"},
            ],
        },
    ],
}


def main():
    url = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/commands"
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json",
    }
    res = requests.post(url, headers=headers, data=json.dumps(commands))
    res.raise_for_status()
    print(res.text)


if __name__ == "__main__":
    main()
