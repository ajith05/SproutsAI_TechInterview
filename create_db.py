#!/usr/bin/env python
"""
create_db.py – create `movies.db` and load the schema.
"""

import sqlite3
from pathlib import Path

DB_FILE = Path("movies.db")
SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS movies (
    id          INTEGER PRIMARY KEY,
    title       TEXT NOT NULL,
    year        INTEGER,
    runtime_min INTEGER,
    rating      REAL,
    overview    TEXT
);

CREATE TABLE IF NOT EXISTS genres (
    id    INTEGER PRIMARY KEY,
    name  TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS movie_genres (
    movie_id INTEGER REFERENCES movies(id),
    genre_id INTEGER REFERENCES genres(id),
    PRIMARY KEY (movie_id, genre_id)
);

CREATE TABLE IF NOT EXISTS actors (
    id   INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS movie_actors (
    movie_id INTEGER REFERENCES movies(id),
    actor_id INTEGER REFERENCES actors(id),
    role     TEXT,
    PRIMARY KEY (movie_id, actor_id)
);
"""

def main() -> None:
    # Creates the file if it does not yet exist.
    with sqlite3.connect(DB_FILE) as conn:
        conn.executescript(SCHEMA)
        conn.commit()

    # Sanity-check: list tables.
    with sqlite3.connect(DB_FILE) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        ).fetchall()
        print("Created tables:", [t[0] for t in tables])

if __name__ == "__main__":
    main()
