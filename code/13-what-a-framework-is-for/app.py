"""The guestbook from chapter 12, written against a framework.

Install it with: pip install -r requirements.txt
Run it with:     uvicorn app:app --port 8000
Then visit:      http://127.0.0.1:8000/
"""

import secrets

from fastapi import Cookie, FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
pages = Jinja2Templates(directory="templates")

messages = []
sessions = {}


@app.get("/")
def guestbook(request: Request, session: str = Cookie(default="")):
    who = sessions.get(session)
    template = "guestbook.html" if who else "sign_in.html"
    return pages.TemplateResponse(request, template, {"who": who, "messages": messages})


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
    messages.append((who, message.strip()))
    return RedirectResponse("/", status_code=303)


@app.get("/messages/{number}")
def one_message(request: Request, number: int):
    if not 0 <= number < len(messages):
        raise HTTPException(status_code=404, detail="no message with that number")
    who, text = messages[number]
    return pages.TemplateResponse(request, "one.html", {"who": who, "text": text})
