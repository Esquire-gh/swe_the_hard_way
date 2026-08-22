"""Meet "database is locked", the error the WAL line and the timeout hide.

guestbook_db.py opens its connections two ways you may have skipped over:
with a timeout, and in WAL mode. Both are there to make four writers work.
This runs the four writers with those two lines removed, so the default
behaviour shows through: a writer that cannot get in at once gives up
instead of waiting, and the concurrency you took for granted turns out to
be a policy somebody chose.

Run it with:  python3 locked.py
"""

import pathlib
import sqlite3
import threading

BOOK = pathlib.Path(__file__).parent / "locked.db"
WRITERS, EACH = 4, 50
failures = []


def connect():
    # No timeout, so a blocked writer fails at once instead of waiting.
    # No WAL, so writers cannot proceed while another is writing.
    return sqlite3.connect(BOOK, timeout=0)


BOOK.unlink(missing_ok=True)
setup = connect()
setup.execute("CREATE TABLE messages "
              "(id INTEGER PRIMARY KEY, who TEXT, text TEXT)")
setup.commit()
setup.close()


def writer(number):
    db = connect()
    for line in range(EACH):
        try:
            db.execute("INSERT INTO messages (who, text) VALUES (?, ?)",
                       (f"writer {number}", str(line)))
            db.commit()
        except sqlite3.OperationalError as why:
            failures.append(str(why))
    db.close()


threads = [threading.Thread(target=writer, args=(n,)) for n in range(WRITERS)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

stored = connect().execute("SELECT count(*) FROM messages").fetchone()[0]
print(f"messages the program tried to write: {WRITERS * EACH}")
print(f"messages actually stored: {stored}")
print(f"times a writer was turned away: {len(failures)}")
if failures:
    print(f"    the error was: {failures[0]}")
BOOK.unlink(missing_ok=True)
