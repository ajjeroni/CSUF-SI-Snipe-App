# Discord Leaderboard Bot

An HTTP-based Discord bot running on Cloudflare Python Workers with a D1 database.
No Gateway connection — Discord calls the Worker's interactions endpoint directly.

## Commands

| Command | Who | Effect |
|---|---|---|
| `/snipe @user` | anyone | Snipes the user (adds one to their count). No self-snipes or bot-snipes. |
| `/leaderboard` | anyone | Private (ephemeral) view of the current standings. |
| `/leaderboard_post` | admins | Posts the standings publicly in the channel. |

Commands only work in the designated channel (`DISCORD_LEADERBOARD_CHANNEL_ID`).

## Architecture

- **`src/entry.py`** — the Worker. Verifies Discord's Ed25519 signature,
  handles PING, routes slash commands, and reads/writes D1.
- **`schema.sql`** — D1 tables: `leaderboard` (scores per guild/user) and
  `processed_interactions` (dedupes Discord retries so snipes aren't double-counted).
- **`scripts/register_commands.py`** — one-off script to register the slash commands.

## Configuration

Non-secret values live in `wrangler.jsonc` under `vars`:
`DISCORD_APPLICATION_ID`, `DISCORD_LEADERBOARD_CHANNEL_ID`.

Secrets are **never** committed:
- `DISCORD_PUBLIC_KEY` — in `.dev.vars` (gitignored) locally; a Worker secret in prod.
- `DISCORD_BOT_TOKEN` — passed inline only when running the register script.

## Setup

```bash
# 1. Create the D1 tables (local + remote)
npx wrangler d1 execute discord-leaderboard-db --local  --file=./schema.sql
npx wrangler d1 execute discord-leaderboard-db --remote --file=./schema.sql

# 2. Register the slash commands (fill in your own values)
DISCORD_APPLICATION_ID="..." \
DISCORD_GUILD_ID="..." \
DISCORD_BOT_TOKEN="..." \
python scripts/register_commands.py

# 3. Deploy
npx wrangler deploy
```

## Development

```bash
npx wrangler dev
```
