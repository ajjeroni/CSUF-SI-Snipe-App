-- Leaderboard scores: one row per user per guild.
CREATE TABLE IF NOT EXISTS leaderboard (
    guild_id TEXT NOT NULL,
    user_id  TEXT NOT NULL,
    points   INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (guild_id, user_id)
);

-- Processed interactions, to make /snipe idempotent against Discord retries.
CREATE TABLE IF NOT EXISTS processed_interactions (
    interaction_id TEXT PRIMARY KEY
);

-- Per-guild config: which channel the bot's commands are allowed in.
-- Set via the admin-only /setup command.
CREATE TABLE IF NOT EXISTS guild_config (
    guild_id   TEXT PRIMARY KEY,
    channel_id TEXT NOT NULL
);
