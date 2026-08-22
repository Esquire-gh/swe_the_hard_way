"""The guestbook from chapter 11, written against a framework, keeping its
messages in the database from chapter 14.

Install it with: pip install -r requirements.txt
Run it with:     uvicorn app:app --port 8000
Then visit:      http://127.0.0.1:8000/
"""

import pathlib
import secrets
import sqlite3

from fastapi import Cookie, FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
pages = Jinja2Templates(directory="templates")
BOOK = pathlib.Path(__file__).parent / "guestbook.db"

sessions = {}          # session id -> name; chapter 15 says where this belongs


def connect():
    """One connection per request. Every thread needs its own."""
    database = sqlite3.connect(BOOK, timeout=10)
    database.execute("PRAGMA journal_mode=WAL")
    return database


with connect() as setup:
    setup.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id    INTEGER PRIMARY KEY,
            who   TEXT NOT NULL,
            text  TEXT NOT NULL
        )
    """)


@app.get("/")
def guestbook(request: Request, session: str = Cookie(default="")):
    who = sessions.get(session)
    if not who:
        return pages.TemplateResponse(request, "sign_in.html")
    with connect() as book:
        messages = book.execute(
            "SELECT id, who, text FROM messages ORDER BY id").fetchall()
    return pages.TemplateResponse(
        request, "guestbook.html", {"who": who, "messages": messages})


@app.post("/login")
def log_in(name: str = Form()):
    token = secrets.token_hex(16)
    sessions[token] = name.strip()
    answer = RedirectResponse("/", status_code=303)
    answer.set_cookie("session", token, path="/", httponly=True)
    return answer


@app.post("/messages")
def sign(message: str = Form(), session: str = Cookie(default="")):
    who = sessions.get(session)
    if not who:
        return RedirectResponse("/", status_code=303)
    with connect() as book:
        book.execute("INSERT INTO messages (who, text) VALUES (?, ?)",
                     (who, message.strip()))
    return RedirectResponse("/", status_code=303)


@app.get("/messages/{number}")
def one_message(request: Request, number: int):
    with connect() as book:
        row = book.execute(
            "SELECT who, text FROM messages WHERE id = ?", (number,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="no message with that number")
    who, text = row
    return pages.TemplateResponse(request, "one.html", {"who": who, "text": text})
