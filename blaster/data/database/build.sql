CREATE TABLE IF NOT EXISTS mutes (
    user_id INTEGER PRIMARY KEY,
    guild_id INTEGER,
    until INTEGER
)