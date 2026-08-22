"""What survives a kill -9 in the middle of writing, with and without commit.

A transaction that has committed is durable: once the database says yes,
a power cut cannot undo it. To see that, this starts a worker that inserts
one message at a time, kills it dead with SIGKILL partway through, and then
reopens the database and counts what is left. It does this twice: once
committing after every insert, and once committing only at the very end.

Run it with:  python3 kill_survival.py
"""

import os
import pathlib
import signal
import sqlite3
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).parent
DB = HERE / "survival.db"

WORKER = '''
import sqlite3, sys, time
db = sqlite3.connect(sys.argv[1], timeout=10)
db.execute("PRAGMA journal_mode=WAL")
db.execute("CREATE TABLE IF NOT EXISTS m (id INTEGER PRIMARY KEY, n INTEGER)")
db.commit()
commit_each = sys.argv[2] == "each"
for n in range(1000):
    db.execute("INSERT INTO m (n) VALUES (?)", (n,))
    if commit_each:
        db.commit()
    time.sleep(0.002)
db.commit()
'''


def run_and_kill(mode):
    DB.unlink(missing_ok=True)
    for suffix in ("-wal", "-shm"):
        pathlib.Path(str(DB) + suffix).unlink(missing_ok=True)
    worker = subprocess.Popen([sys.executable, "-c", WORKER, str(DB), mode])
    time.sleep(0.5)                      # let it get well into the writing
    worker.send_signal(signal.SIGKILL)   # no cleanup, no flush, just gone
    worker.wait()
    db = sqlite3.connect(DB, timeout=10)
    try:
        survived = db.execute("SELECT count(*) FROM m").fetchone()[0]
    except sqlite3.OperationalError:
        survived = 0               # the table never reached the disk
    db.close()
    return survived


each = run_and_kill("each")
end = run_and_kill("end")
print(f"committing after each insert: {each} messages survived")
print(f"committing only at the end:   {end} messages survived")

DB.unlink(missing_ok=True)
for suffix in ("-wal", "-shm"):
    pathlib.Path(str(DB) + suffix).unlink(missing_ok=True)
