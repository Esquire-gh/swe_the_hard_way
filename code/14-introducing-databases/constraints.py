"""Three promises a table keeps that a file does not, each in a few lines.

A schema is not decoration. It refuses bad data, it undoes a group of
changes that cannot all succeed, and it charges you for the index that
makes reads fast. This shows each one happening.

Run it with:  python3 constraints.py
"""

import sqlite3
import time

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")

print("NOT NULL refuses a row with no name:")
try:
    db.execute("INSERT INTO people (name) VALUES (?)", (None,))
except sqlite3.IntegrityError as refused:
    print(f"    {type(refused).__name__}: {refused}")

print("\na transaction is all or nothing:")
db.execute("INSERT INTO people (name) VALUES ('Ada')")
db.commit()
try:
    with db:                        # commit if all ok, else roll back
        db.execute("INSERT INTO people (name) VALUES ('Grace')")
        db.execute("INSERT INTO people (name) VALUES (NULL)")  # fails
except sqlite3.IntegrityError:
    pass
names = [row[0] for row in db.execute("SELECT name FROM people ORDER BY id")]
print(f"    after the failed transaction, the table holds: {names}")
print("    Grace is gone too: the good insert was undone with the bad one")
db.close()


def time_inserts(with_index):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, who TEXT)")
    if with_index:
        db.execute("CREATE INDEX t_by_who ON t (who)")
    rows = [(f"person {n}",) for n in range(200_000)]
    start = time.perf_counter()
    db.executemany("INSERT INTO t (who) VALUES (?)", rows)
    db.commit()
    db.close()
    return time.perf_counter() - start


print("\nthe price of an index, paid on every write:")
without = time_inserts(False)
withidx = time_inserts(True)
print(f"    200,000 inserts, no index    {without * 1000:6.0f} ms")
print(f"    200,000 inserts, one index   {withidx * 1000:6.0f} ms")
print(f"    the index made writing {withidx / without:.1f} times slower")
