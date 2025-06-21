PRAGMA foreign_keys = ON;

CREATE TABLE movies (
    id          INTEGER PRIMARY KEY,
    title       TEXT NOT NULL,
    year        INTEGER,
    runtime_min INTEGER,
    rating      REAL,
    overview    TEXT
);

CREATE TABLE genres (
    id    INTEGER PRIMARY KEY,
    name  TEXT UNIQUE
);

CREATE TABLE movie_genres (
    movie_id INTEGER REFERENCES movies(id),
    genre_id INTEGER REFERENCES genres(id),
    PRIMARY KEY (movie_id, genre_id)
);

CREATE TABLE actors (
    id   INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE movie_actors (
    movie_id INTEGER REFERENCES movies(id),
    actor_id INTEGER REFERENCES actors(id),
    role     TEXT,
    PRIMARY KEY (movie_id, actor_id)
);
