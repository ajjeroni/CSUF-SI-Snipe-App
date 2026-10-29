# Snipe Bot

An HTTP-based Discord bot running on Cloudflare Python Workers with a D1 database.
No Gateway connection — Discord calls the Worker's interactions endpoint directly.

## Commands

| Command | Who | Effect |
|---|---|---|
| `/snipe @user` | anyone | Snipes the user (adds one to their count). No self-snipes or bot-snipes. |
| `/leaderboard` | anyone | Private (ephemeral) view of the current standings. |
| `/leaderboard_post` | admins | Posts the standings publicly in the channel. |
| `/setup` | admins | Binds the channel it's run in as this server's snipe channel. |
| `/unsetup` | admins | Removes the channel binding for this server. |

Each server (guild) has its own snipe channel, set with `/setup`. Until an admin
runs `/setup`, `/snipe`, `/leaderboard`, and `/leaderboard_post` are disabled and
tell the user to run setup. Outside the bound channel they point the user to it.
Scores are tracked per server, so leaderboards don't mix between servers.

## Architecture

- **`src/entry.py`** — the Worker. Verifies Discord's Ed25519 signature,
  handles PING, routes slash commands, and reads/writes D1.
- **`schema.sql`** — D1 tables:
  - `leaderboard` — snipe counts per guild/user.
  - `processed_interactions` — dedupes Discord retries so snipes aren't double-counted.
  - `guild_config` — the bound snipe channel per guild (set via `/setup`).
- **`scripts/register_commands.py`** — one-off script to register the slash
  commands for a guild (bulk overwrite via `PUT`).

## Configuration

Non-secret values live in `wrangler.jsonc` under `vars`:
`DISCORD_APPLICATION_ID`.

Secrets are **never** committed:
- `DISCORD_PUBLIC_KEY` — in `.dev.vars` (gitignored) locally; a Worker secret in prod.
- `DISCORD_BOT_TOKEN` — passed inline only when running the register script.

## First-time setup

```bash
# 1. Create the D1 tables (local + remote)
npx wrangler d1 execute discord-leaderboard-db --local  --file=./schema.sql
npx wrangler d1 execute discord-leaderboard-db --remote --file=./schema.sql

# 2. Register the slash commands for a guild (fill in your own values)
DISCORD_APPLICATION_ID="..." \
DISCORD_GUILD_ID="..." \
DISCORD_BOT_TOKEN="..." \
python scripts/register_commands.py

# 3. Deploy
npx wrangler deploy
```

Then, in Discord, an admin runs `/setup` in the channel that should host the bot.

## Adding the bot to another server

1. Install the app on the new server via its install link
   (Discord Developer Portal → your app → Installation).
2. Register the commands for that server — same script, new guild ID:
   ```bash
   DISCORD_APPLICATION_ID="..." \
   DISCORD_GUILD_ID="NEW_SERVER_GUILD_ID" \
   DISCORD_BOT_TOKEN="..." \
   python scripts/register_commands.py
   ```
   The application ID and bot token stay the same for every server; only the
   guild ID changes.
3. An admin runs `/setup` in the desired channel on the new server.

No redeploy or config change is needed to add a server.

## Development

```bash
npx wrangler dev
```
