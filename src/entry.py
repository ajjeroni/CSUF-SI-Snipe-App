import json

from workers import WorkerEntrypoint, Response
from js import crypto, TextEncoder, Uint8Array
from pyodide.ffi import to_js


def reply(content, ephemeral=False):
    """Build an immediate Discord message response (type 4).

    When ephemeral is True, only the invoking user sees the message
    (Discord flag 1 << 6 = 64).
    """
    data = {"content": content}
    if ephemeral:
        data["flags"] = 64
    return Response.json({
        "type": 4,
        "data": data
    })


# Discord Administrator permission bit.
ADMINISTRATOR = 0x8


def is_admin(interaction):
    """True if the invoking member has the Administrator permission.

    Discord sends the member's effective permissions as a decimal
    string bitfield in interaction["member"]["permissions"].
    """
    member = interaction.get("member", {})
    permissions = member.get("permissions")
    if permissions is None:
        return False
    try:
        return (int(permissions) & ADMINISTRATOR) == ADMINISTRATOR
    except (TypeError, ValueError):
        return False


async def verify_discord_request(request, public_key):
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")

    if not signature or not timestamp:
        return False

    try:
        body = await request.text()

        key_bytes = Uint8Array.new(
            to_js(list(bytes.fromhex(public_key)))
        )
        signature_bytes = Uint8Array.new(
            to_js(list(bytes.fromhex(signature)))
        )

        key = await crypto.subtle.importKey(
            "raw", key_bytes, "Ed25519", False,
            to_js(["verify"])
        )

        message = TextEncoder.new().encode(timestamp + body)

        return bool(await crypto.subtle.verify(
            "Ed25519", key, signature_bytes, message
        ))
    except Exception:
        return False


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        if request.method != "POST":
            return Response("Discord endpoint is running!")

        valid = await verify_discord_request(
            request.clone(),
            self.env.DISCORD_PUBLIC_KEY
        )

        if not valid:
            return Response("Invalid signature", status=401)

        interaction = json.loads(await request.text())

        # Discord PING
        if interaction["type"] == 1:
            return Response.json({"type": 1})

        # Application command (slash command)
        if interaction["type"] == 2:
            return await self.handle_command(interaction)

        return Response.json({
            "type": 4,
            "data": {"content": "Unsupported interaction."}
        })

    async def handle_command(self, interaction):
        db = self.env.discord_leaderboard_db
        name = interaction["data"]["name"]
        guild_id = interaction.get("guild_id")

        if guild_id is None:
            return reply("This command can only be used in a server.")

        # Restrict commands to the designated leaderboard channel.
        allowed_channel = getattr(
            self.env, "DISCORD_LEADERBOARD_CHANNEL_ID", None
        )
        channel_id = interaction.get("channel_id")
        if allowed_channel is not None and channel_id != allowed_channel:
            return reply(
                f"Please use these commands in <#{allowed_channel}>.",
                ephemeral=True
            )

        if name == "point":
            return await self.handle_point(db, interaction, guild_id)

        if name == "leaderboard":
            # Private snapshot for anyone.
            return await self.handle_leaderboard(
                db, guild_id, ephemeral=True
            )

        if name == "leaderboard_post":
            # Admin-only: post the current leaderboard publicly.
            if not is_admin(interaction):
                return reply(
                    "Only server admins can post the public leaderboard.",
                    ephemeral=True
                )
            return await self.handle_leaderboard(
                db, guild_id, ephemeral=False
            )

        return reply("Unknown command.")

    async def handle_point(self, db, interaction, guild_id):
        # The "user" option value is the target user's ID (string).
        options = interaction["data"].get("options", [])
        target_id = None
        for option in options:
            if option["name"] == "user":
                target_id = option["value"]
                break

        if target_id is None:
            return reply("You must specify a user.", ephemeral=True)

        # No self-pointing: the invoker is in interaction["member"]["user"].
        invoker_id = (
            interaction.get("member", {}).get("user", {}).get("id")
        )
        if target_id == invoker_id:
            return reply("You can't give yourself a point.", ephemeral=True)

        # No pointing the bot itself (its user ID == the application ID).
        app_id = getattr(self.env, "DISCORD_APPLICATION_ID", None)
        if app_id is not None and target_id == app_id:
            return reply("You can't give the bot a point.", ephemeral=True)

        # Idempotency: record this interaction ID. If it already exists,
        # this is a Discord retry of a point we already awarded, so skip.
        interaction_id = interaction["id"]
        try:
            await (
                db.prepare(
                    "INSERT INTO processed_interactions (interaction_id) "
                    "VALUES (?)"
                )
                .bind(interaction_id)
                .run()
            )
        except Exception:
            # Primary-key conflict => duplicate delivery. Do nothing.
            return reply(f"Point already awarded to <@{target_id}>.",
                         ephemeral=True)

        # Atomic increment: insert at 1, or add 1 if the row already exists.
        await (
            db.prepare(
                "INSERT INTO leaderboard (guild_id, user_id, points) "
                "VALUES (?, ?, 1) "
                "ON CONFLICT(guild_id, user_id) "
                "DO UPDATE SET points = points + 1"
            )
            .bind(guild_id, target_id)
            .run()
        )

        row = await (
            db.prepare(
                "SELECT points FROM leaderboard "
                "WHERE guild_id = ? AND user_id = ?"
            )
            .bind(guild_id, target_id)
            .first()
        )

        total = row.points if row else 1
        return reply(f"Point awarded to <@{target_id}> (now {total}).")

    async def handle_leaderboard(self, db, guild_id, ephemeral=True):
        query = await (
            db.prepare(
                "SELECT user_id, points FROM leaderboard "
                "WHERE guild_id = ? "
                "ORDER BY points DESC, user_id ASC "
                "LIMIT 25"
            )
            .bind(guild_id)
            .all()
        )

        rows = query.results
        if not rows:
            return reply(
                "No points yet. Use /point to get started.",
                ephemeral=ephemeral
            )

        lines = []
        for index, row in enumerate(rows, start=1):
            lines.append(f"{index}. <@{row.user_id}> — {row.points}")

        return reply(
            "**Leaderboard**\n" + "\n".join(lines),
            ephemeral=ephemeral
        )
