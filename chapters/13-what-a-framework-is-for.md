# Chapter 13. What a framework is for

## Why does everyone use a framework

Chapter 12 ended with a hundred and three lines that are a guestbook, in the
sense that a car is a journey. About thirty of those lines are about signing a
book. The rest is machinery, the machinery is unfinished, and the unfinished
parts are the ones that let strangers take the server down.

The complaint was not that any of it was hard. It was that it was tedious, easy
to get subtly wrong, and identical in every web application ever written. That
combination is exactly what a library is for, and a **framework** is a library
large enough that your code sits inside it rather than the other way round. You
do not call a framework. It calls you.

This chapter rewrites the guestbook against one, and the rule for the chapter
is strict. Nothing appears here that is not answering something from chapter
12. If a feature cannot be pointed at a specific block of code you already
wrote by hand, it does not get mentioned.

## The first thing this tutorial installs

Twelve chapters in, nothing has been installed. That was on purpose, and it
ends here, because there is now a list of specific problems to buy solutions
for.

The file is
[`code/13-what-a-framework-is-for/requirements.txt`](../code/13-what-a-framework-is-for/requirements.txt).

```
fastapi          # routing, methods, status codes, request reading
uvicorn          # the accept loop, and reading a request without trusting it
python-multipart # form bodies
jinja2           # pages that are not built by pasting strings together
```

Every line names a section of chapter 12. Set it up the usual way:

```
$ python3 -m venv .venv
$ .venv/bin/pip install -r requirements.txt
```

A **virtual environment** is a directory holding one project's libraries so
that installing something for this tutorial cannot break something else on your
machine. It is a convention rather than a mechanism, and the mechanism is the
same directories and files from chapter 1.

## The same guestbook, again

The file is
[`code/13-what-a-framework-is-for/app.py`](../code/13-what-a-framework-is-for/app.py).
This is the whole of it, in two pieces.

```python
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
```

```python
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
```

The pages live in
[`code/13-what-a-framework-is-for/templates/`](../code/13-what-a-framework-is-for/templates/).
Here is the one that lists the messages.

```html
<!doctype html>
<h1>Guestbook</h1>
<p>Signed in as {{ who }}.</p>
<ul>
{% for who, text in messages %}<li>{{ who }}: {{ text }}</li>
{% else %}<li>nothing yet</li>
{% endfor %}</ul>
<form method="post" action="/messages">
  <input name="message"><button>sign</button>
</form>
```

Run it, and note that you do not run `app.py`.

```
$ .venv/bin/uvicorn app:app --port 8000
```

It behaves the same as chapter 12, including one page more.

```
$ curl -s -c jar http://127.0.0.1:8000/
<h1>Guestbook</h1>
<p>Say who you are before signing.</p>

$ curl -s -i -c jar -b jar -X POST -d 'name=Ada' http://127.0.0.1:8000/login
HTTP/1.1 303 See Other
location: /
set-cookie: session=3ea5dcdd0003a04646b33fb06e1f677c; HttpOnly; Path=/; SameSite=lax

$ curl -s -b jar -X POST -d 'message=<b>first</b>' http://127.0.0.1:8000/messages
$ curl -s -b jar http://127.0.0.1:8000/
<h1>Guestbook</h1>
<p>Signed in as Ada.</p>
<ul>
<li>Ada: &lt;b&gt;first&lt;/b&gt;</li>
</ul>
```

## Line by line against what it replaces

Now the point of the chapter. Every piece of that file is standing where
something you wrote used to be.

**The accept loop is gone.** The bottom of every step file in chapter 12 was
the same eight lines: make a socket, set `SO_REUSEADDR`, bind, listen, print,
loop forever, accept, close. That is now the word `uvicorn` in a command. You
do not run `app.py` because `app.py` is not a program. It is a collection of
functions that uvicorn calls, which is what it means to say your code sits
inside the framework.

**`read_request` is gone.** Chapter 12 counted bytes against `Content-Length`
in a loop, and chapter 12 admitted that the loop would happily try to collect
four billion bytes if a stranger asked it to. Uvicorn reads the request, and
also enforces limits and timeouts that chapter 12 listed as missing.

**The chain of `if` statements is gone.** `handle` decided what to do by
comparing the path against a series of strings in a function far away from the
code that answers. Now `@app.get("/")` sits directly above the function that
answers `GET /`. The routing moved to the thing being routed to.

**The 405 branches are gone.** Chapter 12 needed explicit code so that a `POST`
to a page that only reads returned 405 rather than 404. Here, registering `/`
for `GET` is enough. Anything else arriving at `/` gets a 405 that nobody
wrote.

**`split_target` and `parse_fields` are gone.** Chapter 12 pulled fields apart
on `&` and `=` and undid the percent encoding, in one place for the query
string and again for the body. Here it is `name: str = Form()` in the function
signature. The field is named where it is used, and if it is absent the
framework answers rather than the function crashing on a missing key.

**`headers_of` and `cookies_of` are gone.** Two more parsers, each with its own
separator, replaced by `session: str = Cookie(default="")`.

**The `redirect` builder is gone.** `RedirectResponse("/", status_code=303)`
does what those four lines of string joining did, and the post then redirect
then get reasoning from chapter 12 is unchanged. The framework did not remove
the need to understand that, and it should not.

**The `response` builder is gone.** Chapter 12 assembled a status line,
`Content-Type`, `Content-Length` and `Connection` for every reply. Returning a
value now does it.

**`escape` is gone, and this is the important one.** Chapter 12's fix was a
function you had to remember to call at every single place text from outside
entered a page, and the chapter said plainly that the one you forget is the
bug. Look at `app.py` and the templates and find the call. There is not one.
Jinja2 escapes everything placed into a page unless it is explicitly told not
to, which is why `<b>first</b>` came back as `&lt;b&gt;first&lt;/b&gt;` above.
The rule moved out of your memory and into the tool. That is the difference
between a habit and a property.

**String pasting is gone.** Chapter 12's `guestbook_page` built HTML with an
f-string wrapped around a generator expression. The template has a loop, an
empty case, and readable HTML, and a person who writes pages rather than
Python can edit it.

## The page chapter 12 could not write

Chapter 12 finished by asking you to imagine a page showing one message by
number at `/messages/3`, and pointed out that a chain of equality checks cannot
express it. Here it is, and it is four lines.

```python
@app.get("/messages/{number}")
def one_message(request: Request, number: int):
    if not 0 <= number < len(messages):
        raise HTTPException(status_code=404, detail="no message with that number")
```

The `{number}` in the path is the pattern matching chapter 12 said would have
to be written from scratch. The `number: int` is the part worth stopping on. It
is an ordinary Python type annotation, and the framework reads it and enforces
it before your function runs.

```
$ curl -s http://127.0.0.1:8000/messages/0
<p>Ada wrote: &lt;b&gt;first&lt;/b&gt;</p>

$ curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/messages/99
404

$ curl -s http://127.0.0.1:8000/messages/banana
{"detail":[{"type":"int_parsing","loc":["path","number"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"banana"}]}
```

Three different wrong things, three different answers. The 404 is yours, since
only your code knows how many messages there are. The 422 for `banana` is the
framework's, and your function never ran, because a value that cannot be an
integer never reached it.

## Check it yourself: send it something that is not a request

Chapter 12's list of unfinished machinery was not decoration. Here is what one
missing piece costs.

Run chapter 12's `step4_session.py` and send it nonsense. Uvicorn is on port
8000, so change the port in that file to 8200 first, and leave both running.

```
$ curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8200/
200
$ printf 'not a request at all\r\n\r\n' | nc 127.0.0.1 8200
$ curl -s -o /dev/null -w "%{http_code}\n" --max-time 3 http://127.0.0.1:8200/
000
```

The server printed a traceback and exited.

```
ValueError: too many values to unpack (expected 3)
```

One line, from any stranger, and the site is off. The line that failed is the
one that splits a request line into three parts and assumes there are three.

Now the same thing to the framework.

```
$ printf 'not a request at all\r\n\r\n' | nc 127.0.0.1 8000
HTTP/1.1 400 Bad Request
content-type: text/plain; charset=utf-8
Connection: close

$ curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/
200
```

A 400, and still serving.

Two smaller things you did not ask for are worth noticing while you are here.
The cookie came back with `SameSite=lax` on it, which is a protection against a
different site causing a visitor's browser to make requests to yours, and
nothing in `app.py` requested it. And because the routes are now declarations
rather than `if` statements, they can be read by other code, so the framework
can describe its own interface:

```
$ curl -s http://127.0.0.1:8000/openapi.json \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print(sorted((p, m) for p, v in d['paths'].items() for m in v))"
[('/', 'get'), ('/login', 'post'), ('/messages', 'post'), ('/messages/{number}', 'get')]

$ curl -s -o /dev/null -w "/docs -> %{http_code}\n" http://127.0.0.1:8000/docs
/docs -> 200
```

There is a browsable page of documentation for a program you did not document.
That is not magic. It is the direct consequence of having written the routing
down as data instead of burying it in control flow.

## What the framework did not fix

This should feel like relief rather than like cleverness. Every line of it is
doing something you did by hand and can still describe.

Two things did not move.

The guestbook still forgets everything. `messages` and `sessions` are a list
and a dictionary held in a process, exactly as they were in chapter 12. Stop
uvicorn, start it again, and the book is empty and everyone is logged out. No
framework can fix that, because it is not a web problem. It is chapter 1's
observation that a process's memory dies with the process, and chapter 15 is
about where things go instead.

And there is one thing the framework did fix, quietly, which is the reason for
the next chapter.

Chapter 12's server answers one visitor at a time, and chapter 10 listed that
as its first limit. The version you just ran does not have that problem. Two
people can use it at once, and nothing in `app.py` says a word about how.

That is the one piece of help you cannot afford to accept without
understanding. Everything else the framework took over was tedious and
mechanical, and knowing how it works is optional in the way that knowing how a
compiler works is optional. Concurrency is not like that. It changes what your
own code is allowed to do, it introduces failures that appear only sometimes,
and a person who has never seen those failures will write code that causes them
and then be unable to explain what happened.

So the next chapter puts the framework down, goes back to the hand written
server, and lets a second visitor arrive.

---

[Previous chapter](./12-from-reading-files-to-running-code.md) | [Next chapter](./14-two-people-at-once.md)
