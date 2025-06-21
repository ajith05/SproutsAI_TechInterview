#!/usr/bin/env python
"""
populate_db.py — add sample data to movies.db so you can demo your RAG pipeline.
"""

import sqlite3
import random
from pathlib import Path

DB_FILE = Path("movies.db")
random.seed(42)               # deterministic for repeatable demos

# ----------------------------------------------------------------------
# 1. Core reference data
# ----------------------------------------------------------------------

movies = [
    # id, title, year, runtime_min, rating, overview
    (1,  "The Shawshank Redemption",                 1994, 142, 9.3,
     "Two imprisoned men bond over years, finding solace and redemption."),
    (2,  "The Godfather",                            1972, 175, 9.2,
     "Patriarch of an organized-crime dynasty transfers control to his son."),
    (3,  "The Dark Knight",                          2008, 152, 9.0,
     "Batman faces the Joker’s reign of chaos in Gotham City."),
    (4,  "Pulp Fiction",                             1994, 154, 8.9,
     "Interlocking stories of crime, redemption, and a mysterious briefcase."),
    (5,  "Inception",                                2010, 148, 8.8,
     "A thief enters dreams to plant an idea in a target’s mind."),
    (6,  "Forrest Gump",                             1994, 142, 8.8,
     "Simple-minded Forrest unwittingly influences historic events."),
    (7,  "Fight Club",                               1999, 139, 8.8,
     "An insomniac and a soap salesman start an underground fight club."),
    (8,  "The Matrix",                               1999, 136, 8.7,
     "A hacker discovers reality is a simulation controlled by machines."),
    (9,  "Interstellar",                             2014, 169, 8.6,
     "Explorers travel through a wormhole to save humanity."),
    (10, "Parasite",                                 2019, 132, 8.5,
     "A poor family infiltrates a wealthy household—until things go awry."),
    (11, "The Lord of the Rings: Fellowship",        2001, 178, 8.8,
     "Frodo begins his quest to destroy the One Ring."),
    (12, "The Lord of the Rings: Two Towers",        2002, 179, 8.8,
     "The Fellowship is broken, but the quest to destroy the Ring continues."),
    (13, "The Lord of the Rings: Return of the King",2003, 201, 9.0,
     "Gondor faces Sauron while Frodo approaches Mount Doom."),
    (14, "Gladiator",                                2000, 155, 8.5,
     "A betrayed Roman general seeks vengeance in the arena."),
    (15, "Titanic",                                  1997, 194, 7.9,
     "A romance blossoms aboard the ill-fated RMS Titanic."),
    (16, "The Social Network",                       2010, 120, 7.8,
     "Harvard student builds Facebook and is sued by former friends."),
    (17, "Whiplash",                                 2014, 106, 8.5,
     "A jazz drummer faces an abusive instructor in pursuit of greatness."),
    (18, "La La Land",                               2016, 128, 8.0,
     "An aspiring actress and a jazz pianist chase their dreams in LA."),
    (19, "Mad Max: Fury Road",                       2015, 120, 8.1,
     "In a post-apocalyptic wasteland, rebels flee a tyrant in a war rig."),
    (20, "Joker",                                    2019, 122, 8.4,
     "A mentally troubled comedian descends into violent madness."),
]

genres = [
    (1,  "Drama"),      (2,  "Crime"),      (3,  "Action"),      (4,  "Thriller"),
    (5,  "Sci-Fi"),     (6,  "Adventure"),  (7,  "Fantasy"),     (8,  "Mystery"),
    (9,  "Romance"),    (10, "Comedy"),     (11, "Biography"),   (12, "Music"),
    (13, "History"),    (14, "War"),        (15, "Western"),     (16, "Animation"),
    (17, "Horror"),     (18, "Family"),     (19, "Sport"),       (20, "Musical"),
]

actors = [
    (1,  "Tim Robbins"),       (2,  "Marlon Brando"),    (3,  "Christian Bale"),
    (4,  "John Travolta"),     (5,  "Leonardo DiCaprio"),(6,  "Tom Hanks"),
    (7,  "Brad Pitt"),         (8,  "Keanu Reeves"),     (9,  "Matthew McConaughey"),
    (10, "Song Kang-ho"),      (11, "Elijah Wood"),      (12, "Viggo Mortensen"),
    (13, "Sean Astin"),        (14, "Russell Crowe"),    (15, "Kate Winslet"),
    (16, "Jesse Eisenberg"),   (17, "Miles Teller"),     (18, "Emma Stone"),
    (19, "Tom Hardy"),         (20, "Joaquin Phoenix"),
]

# ----------------------------------------------------------------------
# 2. Generate junction-table rows programmatically
#    • 1–3 genres per movie
#    • 2–4 actors per movie
# ----------------------------------------------------------------------

movie_genres  = []   # (movie_id, genre_id)
movie_actors  = []   # (movie_id, actor_id, role)

for movie_id, *_ in movies:
    # assign genres
    for genre in random.sample(genres, k=random.randint(1, 3)):
        movie_genres.append((movie_id, genre[0]))

    # assign actors with placeholder roles
    for actor in random.sample(actors, k=random.randint(2, 4)):
        role = f"Role for {actor[1].split()[0]}"     # simple placeholder
        movie_actors.append((movie_id, actor[0], role))

# ----------------------------------------------------------------------
# 3. Insert everything
# ----------------------------------------------------------------------

def main() -> None:
    if not DB_FILE.exists():
        raise FileNotFoundError(
            f"{DB_FILE} not found. Run create_db.py first to create the schema."
        )

    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")

        conn.executemany(
            "INSERT OR IGNORE INTO movies VALUES (?,?,?,?,?,?)",
            movies,
        )
        conn.executemany(
            "INSERT OR IGNORE INTO genres VALUES (?,?)",
            genres,
        )
        conn.executemany(
            "INSERT OR IGNORE INTO actors VALUES (?,?)",
            actors,
        )
        conn.executemany(
            "INSERT OR IGNORE INTO movie_genres VALUES (?,?)",
            movie_genres,
        )
        conn.executemany(
            "INSERT OR IGNORE INTO movie_actors VALUES (?,?,?)",
            movie_actors,
        )

        conn.commit()

    # Quick confirmation
    with sqlite3.connect(DB_FILE) as conn:
        for table in ("movies", "genres", "actors",
                      "movie_genres", "movie_actors"):
            cnt = conn.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]
            print(f"{table:15} → {cnt} rows inserted.")

if __name__ == "__main__":
    main()
