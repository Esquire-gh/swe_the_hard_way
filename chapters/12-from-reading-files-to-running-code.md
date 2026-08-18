# Chapter 12. From reading files to running code

## When the page is different for every visitor

The server at the end of chapter 10 hands every visitor the same bytes, because
it reads a file and the file does not change. That was the whole web for a few
years and it was enough to change the world, so it is not a small thing.

It also cannot do anything you actually use a website for. It cannot greet you.
It cannot show you your own messages and somebody else their own. It cannot
accept a single character that a visitor types. Every one of those needs the
answer to be worked out at the moment of asking, which means a program has to
run for each request rather than a file being read.

That change is one line in the server. Instead of reading a file and sending
it, call a function and send whatever it returns. This chapter is what happens
after that one line, and it is the longest chapter in part four for a reason.
Nothing in it is hard. There is a great deal of it, and the pile is the point.

## Step one: deciding which code answers

With files, the request path was a filename. With code, the path has to select
a piece of code, which means writing down the correspondence yourself.

The file is
[`code/12-from-reading-files-to-running-code/step1_routing.py`](../code/12-from-reading-files-to-running-code/step1_routing.py).

```python
def handle(request):
    """Work out which piece of code answers this request."""
    first_line = request.split(b"\r\n")[0].decode()
    method, target, _ = first_line.split(" ")

    if method != "GET":
        return response("405 Method Not Allowed", b"<h1>405 not allowed</h1>")
    if target == "/":
        return response("200 OK", b"<h1>Guestbook</h1><p>Nothing here yet.</p>")
    if target == "/about":
        return response("200 OK", b"<h1>About</h1><p>A guestbook.</p>")
    return response("404 Not Found", b"<h1>404 not found</h1>")
```

```
$ curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/about
200
$ curl -s http://127.0.0.1:8000/nope
<h1>404 not found</h1>
$ curl -s -X POST http://127.0.0.1:8000/
<h1>405 not allowed</h1>
```

Note what had to be decided rather than discovered. The method has to be
checked, because chapter 6 gave the client several and a `POST` to a page that
only reads is a different failure from a page that does not exist. A path that
matches nothing needs a 404, and a path that exists but rejects the method
needs a 405, and if you do not write both then one of them silently becomes the
other.

This is a chain of `if` statements, it is thirty five lines, and it is fine.
Hold on to the feeling that it is fine.

## Step two: reading what the visitor typed into the address

The address bar can carry more than a path. Everything after a question mark is
a list of fields, written as `name=value` joined by `&`, and it is the oldest
way for a visitor to send something.

The file is
[`code/12-from-reading-files-to-running-code/step2_query.py`](../code/12-from-reading-files-to-running-code/step2_query.py).

```python
def split_target(target):
    """Separate the path from the fields written after the question mark."""
    path, _, query = target.partition("?")
    fields = {}
    for pair in query.split("&"):
        if not pair:
            continue
        name, _, value = pair.partition("=")
        fields[unquote_plus(name)] = unquote_plus(value)
    return path, fields
```

`unquote_plus` comes from the standard library and turns `%20` and `+` back
into spaces, because the field encoding cannot contain a space, an ampersand or
an equals sign without disguising it first. Even here, in the middle of doing
everything by hand, a library is doing a job you would otherwise have to write.

Now a page can use it.

```python
    if path == "/hello":
        name = fields.get("name", "stranger")
        return response("200 OK", f"<h1>Hello, {name}</h1>".encode())
```

```
$ curl -s 'http://127.0.0.1:8000/hello?name=Ada'
<h1>Hello, Ada</h1>
$ curl -s 'http://127.0.0.1:8000/hello?name=Ada+Lovelace%21'
<h1>Hello, Ada Lovelace!</h1>
```

Then somebody who is not you asks for a page.

```
$ curl -s 'http://127.0.0.1:8000/hello?name=%3Cscript%3Ealert(1)%3C/script%3E'
<h1>Hello, <script>alert(1)</script></h1>
```

The visitor supplied part of the page rather than part of the text. A browser
receiving that runs the script, because there is nothing in the bytes to
suggest it was not meant to be there. Send somebody a link with that in it and
the script runs in their browser, on your site, with whatever access their
session has. The name for this is **cross site scripting**, and it is the same
mistake as the path traversal in chapter 10 wearing different clothes. Text
arrived from a stranger and was used as though you had written it.

The fix is to turn the characters that mean something in HTML into the codes
that mean the characters.

```python
def escape(text):
    """Make text safe to place inside a page."""
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))
```

```
$ curl -s 'http://127.0.0.1:8000/hello-escaped?name=%3Cscript%3Ealert(1)%3C/script%3E'
<h1>Hello, &lt;script&gt;alert(1)&lt;/script&gt;</h1>
```

Read that fix again and notice its shape, because the shape is the problem.
`escape` has to be called at every single place where anything from outside is
put into a page. Not most places. Every place. The one you forget is the bug,
it will not show up in testing because you will type your own name into the
form, and the file is now fifty two lines.

## Step three: accepting something and keeping it

A guestbook needs a form, and a form needs a method other than `GET`, because
`GET` puts the fields in the address where they get bookmarked, logged and
shared.

The file is
[`code/12-from-reading-files-to-running-code/step3_form.py`](../code/12-from-reading-files-to-running-code/step3_form.py).

Three separate pieces of work arrive at once here, and each one looks small.

The first is reading the body at all. Chapter 6 made the point that a stream
has no message boundaries and that the length is stated in a header. Chapter 10
ignored it and took one bufferful. Once there are bodies, ignoring it stops
being survivable.

```python
def read_request(conversation):
    """Read one whole request off the connection, headers and body."""
    data = conversation.recv(65536)
    head, separator, rest = data.partition(b"\r\n\r\n")
    if not separator:
        return head, b""

    length = 0
    for line in head.split(b"\r\n")[1:]:
        name, _, value = line.partition(b": ")
        if name.lower() == b"content-length":
            length = int(value)

    while len(rest) < length:          # the body may not have all arrived yet
        rest += conversation.recv(65536)
    return head, rest[:length]
```

The second is that a form body is encoded exactly like a query string, so the
field parser from step two is needed again, in a second place, for a different
reason.

The third is what to do after the visitor has posted something. The obvious
answer is to return the updated page. The correct answer is to send a redirect.

```python
def redirect(where):
    lines = ["HTTP/1.1 303 See Other", f"Location: {where}",
             "Content-Length: 0", "Connection: close"]
    return ("\r\n".join(lines) + "\r\n\r\n").encode()
```

The reason is that a browser remembers the request that produced the page it is
showing. If a `POST` produced it, then reloading repeats the `POST` and signs
the guestbook again, and so does the back button. Answering with a 303 makes
the browser fetch the page with a fresh `GET`, and that is the request it
remembers. This has a name, post then redirect then get, and every person who
has not done it has shipped a form that duplicates entries.

```
$ curl -s -i -X POST -d 'message=Ada was here' http://127.0.0.1:8000/messages
HTTP/1.1 303 See Other
Location: /
Content-Length: 0
Connection: close

$ curl -s http://127.0.0.1:8000/
<!doctype html>
<h1>Guestbook</h1>
<ul><li>Ada was here</li><li>&lt;b&gt;Grace&lt;/b&gt; too</li></ul>
```

The escaping is being remembered, this time. Seventy three lines.

## Step four: knowing who is on the other end

Now the part that most people find genuinely surprising the first time.

Chapter 6's protocol has no notion of a visitor. Every request is complete on
its own, arrives on its own connection, and carries no relationship to any
request before it. The server has no memory of you between one request and the
next, and cannot have, because there is nowhere for that memory to live in the
message. This property has a name, and HTTP is described as **stateless**.

So being logged in has to be built out of nothing. The method the web settled
on is to have the server hand the visitor a piece of text and have the browser
send it back on every subsequent request. That piece of text is a **cookie**.

The server side of it is in
[`code/12-from-reading-files-to-running-code/step4_session.py`](../code/12-from-reading-files-to-running-code/step4_session.py).

```python
    if method == "POST" and path == "/login":
        name = parse_fields(body.decode()).get("name", "").strip()
        if not name:
            return redirect("/")
        token = secrets.token_hex(16)
        sessions[token] = name
        return redirect("/", [f"Set-Cookie: session={token}; Path=/; HttpOnly"])
```

And reading it back requires pulling apart a header with its own separate
format, which is a third parser in the same file:

```python
def cookies_of(headers):
    found = {}
    for pair in headers.get("cookie", "").split(";"):
        name, _, value = pair.strip().partition("=")
        if name:
            found[name] = value
    return found
```

The cookie holds a random number and nothing else. The name lives in a
dictionary on the server, and the cookie is only the key to it. That
arrangement is a **session**, and doing it the other way, putting the name in
the cookie, means any visitor can edit the cookie and become anybody.

`secrets.token_hex` is used rather than anything simpler because the token is
the only thing standing between a stranger and somebody else's account. A
guessable session id is an account anybody can take. `HttpOnly` tells the
browser not to let scripts on the page read the cookie, which limits the damage
from the mistake in step two.

```
$ curl -s -c jar http://127.0.0.1:8000/
<h1>Guestbook</h1>
<p>Say who you are before signing.</p>

$ curl -s -i -c jar -b jar -X POST -d 'name=Ada' http://127.0.0.1:8000/login
HTTP/1.1 303 See Other
Location: /
Set-Cookie: session=3776b04677b9c301d403fc533b4177df; Path=/; HttpOnly

$ curl -s -b jar -X POST -d 'message=first!' http://127.0.0.1:8000/messages
$ curl -s -b jar http://127.0.0.1:8000/
<h1>Guestbook</h1>
<p>Signed in as Ada.</p>
<ul><li>Ada: first!</li></ul>

$ curl -s http://127.0.0.1:8000/
<h1>Guestbook</h1>
<p>Say who you are before signing.</p>
```

Two visitors, one server, two different pages. That is the thing chapter 10
could not do, and it took a hundred and three lines to get here.

## Check it yourself: read the file you now have

Open `step4_session.py` and read it from the top, without skipping.

Count how much of it is about a guestbook. There is a list of messages, a
dictionary of sessions, two functions that produce pages, and about fifteen
lines inside `handle` that decide what to do. Call that a third of the file
being generous.

Everything else is machinery, and none of it is specific to this program. The
response builder. The redirect builder. The escaper. The field parser. The
header parser. The cookie parser. The request reader that counts bytes against
`Content-Length`. The socket setup, the accept loop, and the close.

Now imagine the next page. Not a hard one. A page that shows one message by
number, at `/messages/3`. The chain of `if` statements cannot express it,
because the number is part of the path, so the routing has to grow a way to
match patterns and pull pieces out. That is a new subsystem, and it will be
written badly the first time.

Then imagine the twentieth page.

## The things that are still wrong

The file works, and a fair description of it is that it is a hundred lines of
machinery holding thirty lines of guestbook. That would be tolerable if the
machinery were finished. It is not, and here is what is still missing from it.

Nothing limits the size of a body. A visitor who claims a `Content-Length` of
four billion will have the `while` loop in `read_request` cheerfully try to
collect it, and the process will run out of memory. That is one line to send
and a whole server to take down.

Nothing handles a request that never finishes arriving. Open a connection,
send half a header, and go for lunch, and the server waits, because chapter 8's
blocking is doing exactly what it was asked.

Escaping is a rule in your head. There is nothing in the design that stops you
forgetting it once.

Every page builds HTML by pasting strings together. The moment a page has a
loop, a condition and a heading, that becomes hard to read and easy to break.

There is no logging, so when something is wrong you have no way of knowing what
was asked for.

Anything the process is holding disappears when it stops. Sign the guestbook,
press control C, and the guestbook is empty. Sessions go too, so everyone is
logged out.

And the whole thing still answers one visitor at a time.

Every one of those has a standard answer, every standard answer is a known
amount of work, and none of it has anything to do with the guestbook. That is
the situation the next chapter is about, and it is worth stating exactly what
the complaint is, because it is not that this was difficult.

It was not difficult. It was tedious, it is easy to get subtly wrong, and it is
identical in every web application anybody has ever written.

---

[Previous chapter](./11-server-as-hardware-server-as-software.md) | [Next chapter](./13-what-a-framework-is-for.md)
