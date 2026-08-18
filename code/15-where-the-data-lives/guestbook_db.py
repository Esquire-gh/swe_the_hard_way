"""The guestbook, kept somewhere that outlives the process and knows what to do
when several threads write at once.

Run it with: python3 guestbook_db.py
"""

import pathlib
import sqlite3
import threading

BOOK = pathlib.Path(__file__).parent / "guestbook.db"
WRITERS = 4
EACH = 50


def connect():
    """One connection. Every thread needs its own."""
    database = sqlite3.connect(BOOK, timeout=10)
    database.execute("PRAGMA journal_mode=WAL")
    return database


BOOK.unlink(missing_ok=True)
setup = connect()
setup.execute("""
    CREATE TABLE messages (
        id    INTEGER PRIMARY KEY,
        who   TEXT NOT NULL,
        text  TEXT NOT NULL
    )
""")
setup.execute("CREATE INDEX messages_by_who ON messages (who)")
setup.commit()


def writer(number):
    database = connect()
    for line in range(EACH):
        database.execute("INSERT INTO messages (who, text) VALUES (?, ?)",
                         (f"writer {number}", str(line)))
        database.commit()
    database.close()


threads = [threading.Thread(target=writer, args=(n,)) for n in range(WRITERS)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

total = setup.execute("SELECT count(*) FROM messages").fetchone()[0]
print(f"messages the program tried to write: {WRITERS * EACH}")
print(f"messages actually stored: {total}")

print("\ntwo of them, newest first:")
for who, text in setup.execute(
        "SELECT who, text FROM messages ORDER BY id DESC LIMIT 2"):
    print(f"  {who}: {text}")

# Text from a stranger, used two different ways.
pretend_name = "writer 1' OR '1'='1"
unsafe = setup.execute(
    f"SELECT count(*) FROM messages WHERE who = '{pretend_name}'").fetchone()[0]
safe = setup.execute(
    "SELECT count(*) FROM messages WHERE who = ?", (pretend_name,)).fetchone()[0]
print(f"\npasted into the query: {unsafe} rows")
print(f"passed as a value:     {safe} rows")

setup.close()
BOOK.unlink()
