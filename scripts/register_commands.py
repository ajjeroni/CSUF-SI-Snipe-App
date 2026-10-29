
import os
import json
import urllib.request
import urllib.error

APPLICATION_ID = os.environ["DISCORD_APPLICATION_ID"]
GUILD_ID = os.environ["DISCORD_GUILD_ID"]
BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

url = (
    f"https://discord.com/api/v10/applications/"
    f"{APPLICATION_ID}/guilds/{GUILD_ID}/commands"
)

commands = [
    {
        "name": "point",
        "type": 1,
        "description": "Award one leaderboard point to a user",
        "options": [
            {
                "name": "user",
                "description": "User receiving the point",
                "type": 6,
                "required": True
            }
        ]
    },
    {
        "name": "leaderboard",
        "type": 1,
        "description": "Privately view the current leaderboard"
    },
    {
        "name": "leaderboard_post",
        "type": 1,
        "description": "Admins only: post the leaderboard publicly"
    }
]

for command in commands:
    request = urllib.request.Request(
        url,
        data=json.dumps(command).encode("utf-8"),
        headers={
            "Authorization": f"Bot {BOT_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "DiscordBot (https://github.com/example/discord-leaderboard, 1.0)"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request) as response:
            result = json.load(response)
            print(f"Registered /{result['name']}")
    except urllib.error.HTTPError as error:
        print(f"Failed: {error.code}")
        print(error.read().decode())
