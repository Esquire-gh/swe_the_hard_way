"""Finding one record among many, in a file and in a database.

Run it with: python3 scanning.py
"""

import json
import pathlib
import sqlite3
import time

HERE = pathlib.Path(__file__).parent
LINES = HERE / "many.jsonl"
DATABASE = HERE / "many.db"


def build(count):
    """The same records twice, once as lines in a file and once in a table."""
    with open(LINES, "w") as out:
        for number in range(count):
            out.write(json.dumps({"id": number, "who": f"person {number}"}) + "\n")

    DATABASE.unlink(missing_ok=True)
    database = sqlite3.connect(DATABASE)
    database.execute("CREATE TABLE people (id INTEGER, who TEXT)")
    database.executemany("INSERT INTO people VALUES (?, ?)",
                         ((n, f"person {n}") for n in range(count)))
    database.execute("CREATE INDEX people_by_id ON people (id)")
    database.commit()
    return database


def find_in_file(wanted):
    with open(LINES) as lines:
        for line in lines:
            if json.loads(line)["id"] == wanted:
                return line


def seconds(work):
    started = time.perf_counter()
    work()
    return time.perf_counter() - started


for count in (10_000, 100_000, 1_000_000):
    database = build(count)
    last = count - 1
    by_hand = seconds(lambda: find_in_file(last))
    by_index = seconds(
        lambda: database.execute("SELECT who FROM people WHERE id = ?", (last,)).fetchone()
    )
    print(f"{count:>9} records    file {by_hand * 1000:8.1f} ms"
          f"    database {by_index * 1000:7.3f} ms")
    database.close()

LINES.unlink()
DATABASE.unlink()
