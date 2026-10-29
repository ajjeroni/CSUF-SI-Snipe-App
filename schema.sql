-- Leaderboard scores: one row per user per guild.
CREATE TABLE IF NOT EXISTS leaderboard (
    guild_id TEXT NOT NULL,
    user_id  TEXT NOT NULL,
    points   INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (guild_id, user_id)
);

-- Processed interactions, to make /point idempotent against Discord retries.
CREATE TABLE IF NOT EXISTS processed_interactions (
    interaction_id TEXT PRIMARY KEY
);
