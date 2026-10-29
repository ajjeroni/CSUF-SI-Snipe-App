
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
        "name": "snipe",
        "type": 1,
        "description": "Snipe a user (adds one to their leaderboard count)",
        "options": [
            {
                "name": "user",
                "description": "User to snipe",
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
    },
    {
        "name": "setup",
        "type": 1,
        "description": "Admins only: set this channel as the snipe channel"
    },
    {
        "name": "unsetup",
        "type": 1,
        "description": "Admins only: unbind the snipe channel"
    }
]

# Bulk overwrite: PUT replaces the guild's entire command set with this
# list, so any command not included here (e.g. an old /point) is removed.
request = urllib.request.Request(
    url,
    data=json.dumps(commands).encode("utf-8"),
    headers={
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (https://github.com/example/discord-leaderboard, 1.0)"
    },
    method="PUT"
)

try:
    with urllib.request.urlopen(request) as response:
        results = json.load(response)
        names = ", ".join(f"/{c['name']}" for c in results)
        print(f"Registered {len(results)} commands: {names}")
except urllib.error.HTTPError as error:
    print(f"Failed: {error.code}")
    print(error.read().decode())
