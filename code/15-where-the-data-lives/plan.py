"""Ask the database how it intends to answer, with and without an index.

Run it with: python3 plan.py
"""

import pathlib
import sqlite3

BOOK = pathlib.Path(__file__).parent / "plan.db"
BOOK.unlink(missing_ok=True)

database = sqlite3.connect(BOOK)
database.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, who TEXT, text TEXT)")
database.executemany("INSERT INTO messages (who, text) VALUES (?, ?)",
                     ((f"person {n}", str(n)) for n in range(50_000)))
database.commit()

QUESTION = "SELECT text FROM messages WHERE who = ?"

print("with no index on who:")
for row in database.execute(f"EXPLAIN QUERY PLAN {QUESTION}", ("person 7",)):
    print("   ", row[-1])

database.execute("CREATE INDEX messages_by_who ON messages (who)")
print("\nafter adding one:")
for row in database.execute(f"EXPLAIN QUERY PLAN {QUESTION}", ("person 7",)):
    print("   ", row[-1])

database.close()
BOOK.unlink()
