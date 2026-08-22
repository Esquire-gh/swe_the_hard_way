"""Why the word is "relational": a second table, and a join.

The guestbook kept the author's name in every message. Put the same name
in a thousand messages and you have written it a thousand times, and the
day a person renames themselves you must find and change all thousand. A
relational database keeps people in one table and messages in another, and
each message points at a person by id. A join follows the pointer, so the
name lives in exactly one place.

Run it with:  python3 relational.py
"""

import sqlite3

db = sqlite3.connect(":memory:")          # a database that never touches disk
db.executescript("""
    CREATE TABLE people (
        id    INTEGER PRIMARY KEY,
        name  TEXT NOT NULL
    );
    CREATE TABLE messages (
        id        INTEGER PRIMARY KEY,
        author    INTEGER NOT NULL REFERENCES people (id),
        text      TEXT NOT NULL
    );
""")

db.execute("INSERT INTO people (id, name) VALUES (1, 'Ada'), (2, 'Grace')")
db.executemany("INSERT INTO messages (author, text) VALUES (?, ?)",
               [(1, "first"), (2, "second"), (1, "third")])
db.commit()

print("each message and its author's name, followed across the two tables:")
for name, text in db.execute("""
    SELECT people.name, messages.text
    FROM messages
    JOIN people ON people.id = messages.author
    ORDER BY messages.id
"""):
    print(f"  {name}: {text}")

print("\nAda changes her name in one row:")
db.execute("UPDATE people SET name = 'Ada Lovelace' WHERE id = 1")
db.commit()
for name, text in db.execute("""
    SELECT people.name, messages.text
    FROM messages
    JOIN people ON people.id = messages.author
    WHERE people.id = 1
    ORDER BY messages.id
"""):
    print(f"  {name}: {text}")
db.close()
