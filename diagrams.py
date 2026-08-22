"""Hand-rolled inline SVG diagrams, one function per picture, registered by name.

No drawing library and no images on disk, on purpose: the diagrams are text, so
they diff cleanly, scale to any width, and follow the page's own colours through
the CSS classes in style.css. A page asks for one with {{ diagram:name }} and
build.py drops the markup in.

The two colours mean the same thing here as everywhere on the site. Indigo, the
`learn` class, is a thing you built. Magenta, the `brk` class, is a thing that
broke.
"""
from __future__ import annotations

from html import escape

REGISTRY: dict[str, callable] = {}


def diagram(name: str):
    def deco(fn):
        REGISTRY[name] = fn
        return fn
    return deco


# --------------------------------------------------------------------------
# a very small drawing toolkit
# --------------------------------------------------------------------------

_MARKERS = (
    '<defs>'
    '<marker id="arw" markerWidth="7" markerHeight="7" refX="6" refY="3" '
    'orient="auto" markerUnits="userSpaceOnUse">'
    '<path d="M0,0 L6,3 L0,6 z" fill="context-stroke"/></marker>'
    '</defs>'
)


def _svg(w: int, h: int, body: str, min_width: int = 560) -> str:
    return (
        f'<svg viewBox="0 0 {w} {h}" role="img" '
        f'style="min-width:{min_width}px" xmlns="http://www.w3.org/2000/svg">'
        f'{_MARKERS}{body}</svg>'
    )


def _box(x, y, w, h, cls="box", rx=3):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>'


def _t(x, y, s, cls="lbl"):
    return f'<text x="{x}" y="{y}" class="{cls}">{escape(str(s))}</text>'


def _line(x1, y1, x2, y2, cls="flow", arrow=True):
    a = ' marker-end="url(#arw)"' if arrow else ''
    return f'<path d="M{x1},{y1} L{x2},{y2}" class="{cls}"{a}/>'


def _labelled_box(x, y, w, h, title, sub="", cls="box"):
    out = [_box(x, y, w, h, cls)]
    cx = x + w / 2
    if sub:
        out.append(_t(cx, y + h / 2 - 2, title, "lbl b mid"))
        out.append(_t(cx, y + h / 2 + 13, sub, "lbl sm mut mid"))
    else:
        out.append(_t(cx, y + h / 2 + 4, title, "lbl b mid"))
    return "".join(out)


# --------------------------------------------------------------------------
# front page: the whole journey as one descent and return
# --------------------------------------------------------------------------

@diagram("journey-map")
def journey_map(_=None) -> str:
    rows = [
        ("Part one", "one computer", "a process, memory, the CPU taking turns"),
        ("Part two", "the machines get connected", "packets, addresses, names"),
        ("Part three", "the conversation", "client and server, request and response as text"),
        ("Part four", "building the server", "sockets, one file, frameworks, many at once"),
        ("Part five", "more users, more machines", "two users, the data, ten thousand, frameworks, machines, AI"),
    ]
    w, h = 720, 60 + len(rows) * 62
    body = [_t(24, 34, "pressing enter", "lbl b learn"),
            _t(w - 24, 34, "seeing a page", "lbl b learn end")]
    body.append(_line(w / 2, 42, w / 2, 52, "flow mut", arrow=False))
    y = 58
    for i, (part, name, sub) in enumerate(rows):
        body.append(_labelled_box(150, y, w - 300, 46, f"{part}: {name}", sub))
        body.append(_t(140, y + 27, part.split()[1], "lbl sm mut end"))
        if i < len(rows) - 1:
            body.append(_line(w / 2, y + 46, w / 2, y + 62, "flow", arrow=True))
        y += 62
    return _svg(w, h, "".join(body), min_width=600)


# --------------------------------------------------------------------------
# chapter 1: the fetch, do, advance loop and the jump that makes a loop
# --------------------------------------------------------------------------

@diagram("fetch-execute")
def fetch_execute(_=None) -> str:
    w, h = 720, 250
    body = []
    steps = [("fetch", "read the instruction\nthe counter points at"),
             ("do", "carry it out"),
             ("advance", "counter = counter + 1")]
    xs = [70, 300, 530]
    bw = 150
    for (title, sub), x in zip(steps, xs):
        body.append(_box(x, 60, bw, 60, "box learn"))
        body.append(_t(x + bw / 2, 85, title, "lbl b mid learn"))
        for j, ln in enumerate(sub.split("\n")):
            body.append(_t(x + bw / 2, 102 + j * 12, ln, "lbl sm mut mid"))
    body.append(_line(xs[0] + bw, 90, xs[1], 90))
    body.append(_line(xs[1] + bw, 90, xs[2], 90))
    # the normal advance loops back to fetch
    body.append('<path d="M655,120 L655,175 L145,175 L145,120" class="flow" '
                'marker-end="url(#arw)"/>')
    body.append(_t(400, 170, "next instruction", "lbl sm mut mid"))
    # the jump: one instruction writes a smaller number into the counter
    body.append(_box(250, 200, 220, 34, "box brk"))
    body.append(_t(360, 221, "jump: write a new counter", "lbl b mid brk"))
    body.append('<path d="M360,200 C360,150 300,150 300,120" class="flow brk" '
                'marker-end="url(#arw)"/>')
    body.append(_t(700, 150, "a loop is only", "lbl sm mut end"))
    body.append(_t(700, 164, "this arrow", "lbl sm brk end"))
    return _svg(w, h, "".join(body), min_width=600)


@diagram("turns")
def turns(_=None) -> str:
    """Two processors, more work than processors, taking turns."""
    w, h = 720, 210
    body = [_t(20, 24, "one processor, four jobs, sliced into turns", "lbl b")]
    lane_y = 70
    lane_h = 34
    x0, x1 = 130, 690
    total = x1 - x0
    # four jobs, each a colour band repeated in slices across the timeline
    jobs = ["A", "B", "C", "D"]
    slices = 16
    sw = total / slices
    for s in range(slices):
        j = s % 4
        x = x0 + s * sw
        cls = "box learn" if j % 2 == 0 else "box sunk"
        body.append(_box(x, lane_y, sw - 1, lane_h, cls, rx=0))
        body.append(_t(x + sw / 2, lane_y + 22, jobs[j], "lbl sm mid"))
    body.append(_t(x0 - 12, lane_y + 22, "CPU", "lbl sm mut end"))
    body.append(_line(x0, lane_y + lane_h + 16, x1, lane_y + lane_h + 16, "tick", arrow=False))
    body.append(_t(x0, lane_y + lane_h + 34, "time", "lbl sm mut"))
    body.append(_t(x1, lane_y + lane_h + 34, "a few thousandths of a second each", "lbl sm mut end"))
    body.append(_t(20, 168, "Each job is stopped, its place saved, and resumed later. "
                            "Fast enough that all four look like they run at once.",
                  "lbl sm mut"))
    body.append(_t(20, 188, "That saving and restoring is the context switch.", "lbl sm mut"))
    return _svg(w, h, "".join(body), min_width=600)


# --------------------------------------------------------------------------
# chapter 2: packet switching, and the layer stack
# --------------------------------------------------------------------------

@diagram("packet-switching")
def packet_switching(_=None) -> str:
    w, h = 720, 250
    body = [_t(20, 24, "one message, cut into packets that travel separately", "lbl b")]
    body.append(_labelled_box(20, 108, 108, 48, "sender", "", "box learn"))
    body.append(_labelled_box(592, 108, 108, 48, "receiver", "", "box learn"))
    # four routers at the bends of two distinct paths
    routers = [(238, 62), (388, 58), (238, 168), (430, 150)]
    for (x, y) in routers:
        body.append(_box(x, y, 58, 30, "box"))
        body.append(_t(x + 29, y + 19, "router", "lbl sm mut mid"))
    # upper path (indigo) and lower path (grey), each a clear polyline
    body.append('<path d="M128,120 L238,77 M296,77 L388,73 M446,73 L592,120" '
                'class="flow learn" fill="none"/>')
    body.append('<path d="M128,140 L238,183 M296,183 L430,165 M488,165 L592,140" '
                'class="flow mut" fill="none"/>')
    # three packets in flight, each on an open stretch of a path
    for (x, y, n) in [(180, 90, "3"), (330, 176, "1"), (520, 142, "2")]:
        body.append(_box(x, y - 9, 18, 18, "box brk", rx=2))
        body.append(_t(x + 9, y + 4, n, "lbl sm b mid brk"))
    body.append(_t(20, 232, "Packets take whatever route is free and are put back in "
                            "order at the far end. No wire is reserved for the call.",
                  "lbl sm mut"))
    return _svg(w, h, "".join(body), min_width=620)


@diagram("layers")
def layers(_=None) -> str:
    rows = [
        ("application", "HTTP: what the bytes mean", "GET / HTTP/1.1 ..."),
        ("transport", "TCP: a reliable ordered stream", "put the packets in order"),
        ("internet", "IP: move a packet toward an address", "hop from router to router"),
        ("link", "the wire or the radio", "one cable, one step"),
    ]
    bh, gap, top = 46, 10, 40
    w = 720
    h = top + len(rows) * (bh + gap) + 26
    body = [_t(20, 24, "each layer trusts the one below and ignores the ones above", "lbl b")]
    y = top
    for i, (name, what, eg) in enumerate(rows):
        cls = "box learn" if i == 0 else "box"
        body.append(_box(150, y, 380, bh, cls))
        body.append(_t(340, y + 21, name, "lbl b mid"))
        body.append(_t(340, y + 37, what, "lbl sm mut mid"))
        body.append(_t(140, y + 27, f"layer {4 - i}", "lbl sm mut end"))
        body.append(_t(548, y + 27, eg, "lbl sm mut"))
        y += bh + gap
    body.append(_t(340, y + 8, "each layer adds its own header on the way down; the far "
                              "side peels them off in reverse", "lbl sm mut mid"))
    return _svg(w, h, "".join(body), min_width=600)


# --------------------------------------------------------------------------
# chapter 10: the request flow, and the path-traversal escape
# --------------------------------------------------------------------------

@diagram("server-flow")
def server_flow(_=None) -> str:
    w, h = 720, 150
    steps = [("accept", "a connection\narrives"),
             ("recv", "read the\nrequest bytes"),
             ("parse", "pull the path\nfrom the line"),
             ("read file", "off the disk"),
             ("sendall", "write the\nresponse back")]
    n = len(steps)
    bw, gap = 116, 20
    x = 20
    body = [_t(20, 24, "one trip through the loop, one visitor", "lbl b")]
    for i, (title, sub) in enumerate(steps):
        cls = "box learn"
        body.append(_box(x, 50, bw, 56, cls))
        body.append(_t(x + bw / 2, 73, title, "lbl b mid learn"))
        for j, ln in enumerate(sub.split("\n")):
            body.append(_t(x + bw / 2, 88 + j * 11, ln, "lbl sm mut mid"))
        if i < n - 1:
            body.append(_line(x + bw, 78, x + bw + gap, 78))
        x += bw + gap
    body.append('<path d="M662,106 L662,132 L78,132 L78,106" class="flow" '
                'marker-end="url(#arw)"/>')
    body.append(_t(370, 128, "close, then back to accept for the next one", "lbl sm mut mid"))
    return _svg(w, h, "".join(body), min_width=640)


@diagram("path-traversal")
def path_traversal(_=None) -> str:
    w, h = 720, 230
    body = [_t(20, 24, "what ../ does to a path you trusted", "lbl b")]
    # the intended root and the file that escapes it
    body.append(_labelled_box(230, 60, 260, 40, "site/  (what you meant to serve)", "", "box learn"))
    body.append(_labelled_box(255, 112, 210, 34, "index.html   style.css", "", "box sunk"))
    body.append(_line(360, 100, 360, 112, "flow", arrow=False))
    # the secret file sitting next to the root
    body.append(_labelled_box(520, 112, 180, 34, "not-for-the-public.txt", "", "box brk"))
    # the malicious request path climbing out
    body.append(_t(20, 180, "GET /../not-for-the-public.txt", "lbl b brk"))
    body.append('<path d="M255,132 C120,132 120,60 230,80" class="flow brk" '
                'marker-end="url(#arw)"/>')
    body.append('<path d="M330,175 L470,146" class="flow brk" fill="none" '
                'marker-end="url(#arw)"/>')
    body.append(_t(20, 200, "The .. climbs out of site/ into the parent folder. The fix: "
                            "resolve the real path and refuse anything not inside site/.",
                  "lbl sm mut"))
    return _svg(w, h, "".join(body), min_width=620)


# --------------------------------------------------------------------------
# chapter three: a library whose links are allowed to break
# --------------------------------------------------------------------------

@diagram("hypertext-library")
def hypertext_library(_=None) -> str:
    b = [_t(20, 24, "four documents, three of which exist; every arrow is one link", "lbl b")]
    b.append(_labelled_box(40, 100, 130, 44, "welcome", "start here", "box learn"))
    b.append(_labelled_box(300, 46, 130, 44, "networks", "", "box"))
    b.append(_labelled_box(300, 154, 130, 44, "packets", "", "box"))
    b.append('<rect x="540" y="100" width="150" height="44" rx="3" class="box brk" '
             'stroke-dasharray="5 4"/>')
    b.append(_t(615, 118, "the-one-that-moved", "lbl sm b mid brk"))
    b.append(_t(615, 133, "no such document", "lbl sm mut mid"))
    b.append(_line(170, 114, 300, 72))
    b.append(_line(170, 130, 300, 172))
    b.append('<path d="M105,144 L105,222 L615,222 L615,144" class="flow brk" '
             'marker-end="url(#arw)"/>')
    b.append(_t(360, 240, "one link points at nothing, and nothing noticed "
                          "when it was written", "lbl sm mut mid"))
    b.append(_line(352, 90, 352, 154))
    b.append(_line(378, 154, 378, 90))
    b.append(_t(392, 126, "one link each way", "lbl sm mut"))
    return _svg(720, 252, "".join(b), 600)


# --------------------------------------------------------------------------
# chapter four: what an address carries, and who answers a name
# --------------------------------------------------------------------------

@diagram("url-anatomy")
def url_anatomy(_=None) -> str:
    b = [_t(20, 24, "one address, three parts, two questions", "lbl b")]
    parts = [
        (40, 130, "https://", "scheme", "which rules to speak", "box"),
        (170, 210, "example.com", "host", "which machine to ask", "box learn"),
        (380, 190, "/about.html", "path", "what to ask it for", "box"),
    ]
    for x, w, text, name, sub, cls in parts:
        cx = x + w / 2
        b.append(_box(x, 44, w, 40, cls))
        b.append(_t(cx, 69, text, "lbl b mid"))
        b.append(_line(cx, 84, cx, 104, "flow mut", arrow=False))
        b.append(_t(cx, 120, name, "lbl b mid"))
        b.append(_t(cx, 136, sub, "lbl sm mut mid"))
    b.append(_t(20, 164, "the host is the hard part: it has to become a number "
                         "that routers can move packets toward", "lbl sm mut"))
    return _svg(720, 176, "".join(b), 600)


@diagram("dns-delegation")
def dns_delegation(_=None) -> str:
    b = [_t(20, 24, "en.wikipedia.org, read backwards: each level knows only "
                    "who to ask next", "lbl b")]
    b.append(_labelled_box(20, 64, 120, 164, "resolver", "asks for you", "box learn"))
    rows = [
        (64, "root servers", "who runs org?", "ask the org servers"),
        (124, "org servers", "who runs wikipedia.org?", "ask wikimedia's servers"),
        (184, "wikimedia's servers", "en.wikipedia.org?", "208.80.154.224"),
    ]
    for i, (y, who, q, a) in enumerate(rows):
        last = i == len(rows) - 1
        b.append(_labelled_box(440, y, 240, 44, who, "", "box learn" if last else "box"))
        b.append(_line(140, y + 12, 440, y + 12))
        b.append(_t(290, y + 7, q, "lbl sm mid"))
        b.append(_line(440, y + 34, 140, y + 34, "flow learn" if last else "flow mut"))
        b.append(_t(290, y + 47, a, "lbl sm mid learn" if last else "lbl sm mut mid"))
    b.append(_t(20, 252, "the answer is kept for its time to live, so the next "
                         "thousand lookups never leave the resolver", "lbl sm mut"))
    return _svg(720, 264, "".join(b), 620)


# --------------------------------------------------------------------------
# chapter five: who was there first
# --------------------------------------------------------------------------

@diagram("client-server")
def client_server(_=None) -> str:
    b = [_t(20, 24, "two programs, one conversation, and who was there first", "lbl b")]
    b.append(_line(40, 76, 40, 224, "flow mut"))
    b.append(_t(48, 228, "time", "lbl sm mut"))
    b.append(_t(520, 52, "server", "lbl b mid"))
    b.append(_t(520, 66, "already running", "lbl sm mut mid"))
    b.append(_line(520, 72, 520, 236, "flow learn", arrow=False))
    b.append(_t(532, 94, "waiting, and it costs nothing", "lbl sm mut"))
    b.append(_t(200, 52, "client", "lbl b mid"))
    b.append(_t(200, 66, "starts because it wants something", "lbl sm mut mid"))
    b.append(_line(200, 100, 200, 180, "flow", arrow=False))
    b.append(_line(206, 118, 514, 118))
    b.append(_t(360, 112, "request: the client speaks first", "lbl sm mid"))
    b.append(_line(514, 160, 206, 160, "flow learn"))
    b.append(_t(360, 176, "response", "lbl sm mid learn"))
    b.append(_t(200, 196, "exits", "lbl sm mut mid"))
    b.append(_t(532, 206, "waiting for the next one", "lbl sm mut"))
    b.append(_t(20, 254, "whoever sent the first arrow is the client; the role "
                         "belongs to the conversation, not the machine", "lbl sm mut"))
    return _svg(720, 266, "".join(b), 600)


# --------------------------------------------------------------------------
# chapter six: the shape of a message, and where the stream has no edges
# --------------------------------------------------------------------------

@diagram("http-anatomy")
def http_anatomy(_=None) -> str:
    b = [_t(20, 24, "a request and a response, line by line", "lbl b")]
    cols = [
        (20, "request", [
            ("GET /about.html HTTP/1.1", "request line", "lbl b"),
            ("Host: example.com", "header", "lbl"),
            ("Accept: text/html", "header", "lbl"),
            ("", "blank line: headers end", "lbl"),
            ("(no body: a GET has nothing to send)", "", "lbl sm mut"),
        ]),
        (370, "response", [
            ("HTTP/1.1 200 OK", "status line", "lbl b"),
            ("Content-Type: text/html", "header", "lbl"),
            ("Content-Length: 559", "how long the body is", "lbl"),
            ("", "blank line: headers end", "lbl"),
            ("<!doctype html><html>...", "body, 559 bytes", "lbl"),
        ]),
    ]
    for x, title, lines in cols:
        b.append(_t(x, 52, title, "lbl b"))
        b.append(_box(x, 60, 330, 132, "box"))
        for i, (text, note, cls) in enumerate(lines):
            y = 84 + i * 24
            if text:
                b.append(_t(x + 12, y, text, cls))
            else:
                b.append(_line(x + 12, y - 4, x + 120, y - 4, "flow brk", arrow=False))
            if note:
                b.append(_t(x + 318, y, note, "lbl sm mut end"))
    b.append(_t(20, 216, "the same shape both ways: a first line, headers, a "
                         "blank line, and sometimes a body", "lbl sm mut"))
    return _svg(720, 228, "".join(b), 640)


@diagram("stream-boundaries")
def stream_boundaries(_=None) -> str:
    b = [_t(20, 24, "two requests arrive back to back on one connection", "lbl b")]
    segs = [
        (200, "request A: headers", "box learn"),
        (30, "", "box sunk"),
        (110, "body A", "box learn"),
        (200, "request B: headers", "box"),
        (30, "", "box sunk"),
        (110, "body B", "box"),
    ]
    x = 20
    edges = []
    for w, label, cls in segs:
        b.append(_box(x, 64, w, 36, cls, rx=0))
        if label:
            b.append(_t(x + w / 2, 86, label, "lbl sm b mid"))
        x += w
        edges.append(x)
    b.append(_t(35, 56, "bytes, in order, with no edges of their own", "lbl sm mut"))
    b.append(_line(235, 100, 235, 118, "flow", arrow=False))
    b.append(_t(235, 132, "a blank line ends the headers", "lbl sm mid"))
    b.append(_line(360, 100, 360, 150, "flow learn", arrow=False))
    b.append(_t(360, 164, "Content-Length: 11 says where the body ends", "lbl sm mid learn"))
    b.append('<path d="M360,44 L360,64" class="flow brk"/>')
    b.append(_t(372, 48, "nothing in the stream marks this edge", "lbl sm brk"))
    return _svg(720, 176, "".join(b), 640)


# --------------------------------------------------------------------------
# chapter seven: the three jobs a browser does, by size
# --------------------------------------------------------------------------

@diagram("three-jobs")
def three_jobs(_=None) -> str:
    b = [_t(20, 24, "what a browser does, drawn to scale", "lbl b")]
    jobs = [
        (40, 28, "speak the protocol", "one line with nc", "box learn"),
        (260, 96, "draw the page", "serious engineering", "box"),
        (480, 164, "agree about broken pages", "the largest of the three", "box brk"),
    ]
    base = 204
    for x, h, title, sub, cls in jobs:
        b.append(_box(x, base - h, 200, h, cls))
        b.append(_t(x + 100, base + 20, title, "lbl b mid"))
        b.append(_t(x + 100, base + 35, sub, "lbl sm mut mid"))
    b.append(_line(30, base, 690, base, "flow mut", arrow=False))
    return _svg(720, 248, "".join(b), 600)


# --------------------------------------------------------------------------
# chapter eight: the loop, and the two ways to wait
# --------------------------------------------------------------------------

@diagram("server-loop")
def server_loop(_=None) -> str:
    b = [_t(20, 24, "a web server, in six lines", "lbl b")]
    rows = [
        ("tell the operating system you want to be reachable", "a request you cannot make yet", "box"),
        ("wait until somebody connects", "no instruction means this", "box brk"),
        ("read the text they sent", "you could write this today", "box learn"),
        ("work out what they are asking for", "chapter six, thirty lines", "box learn"),
        ("write the answer back", "you could write this today", "box learn"),
        ("close the connection", "ordinary", "box learn"),
    ]
    for i, (text, note, cls) in enumerate(rows):
        y = 44 + i * 34
        x = 40 if i == 0 else 70
        b.append(_box(x, y, 400, 26, cls))
        b.append(_t(x + 12, y + 17, text, "lbl"))
        b.append(_t(490, y + 17, note, "lbl sm brk" if "brk" in cls else "lbl sm mut"))
    # the forever loop: a bracket down the left of rows 1..5 with an arrow back up
    b.append('<path d="M60,96 L48,96 L48,236 L60,236" class="flow mut"/>')
    b.append(_t(46, 252, "forever", "lbl sm mut"))
    b.append(_line(48, 230, 48, 100, "flow mut"))
    return _svg(720, 262, "".join(b), 640)


@diagram("polling-vs-blocking")
def polling_vs_blocking(_=None) -> str:
    b = [_t(20, 24, "ten seconds of waiting, two ways", "lbl b")]
    # polling row
    b.append(_t(20, 60, "polling", "lbl b"))
    b.append(_line(100, 56, 620, 56, "flow mut", arrow=False))
    for i in range(17):
        x = 100 + i * 30
        b.append(_line(x, 50, x, 62, "flow brk", arrow=False))
    b.append(_t(100, 80, "look, nothing. look, nothing. look, nothing...", "lbl sm mut"))
    b.append(_t(640, 60, "1,632 looks", "lbl sm brk"))
    # blocking row
    b.append(_t(20, 124, "blocking", "lbl b"))
    b.append(_line(100, 120, 500, 120, "flow learn", arrow=False))
    b.append(_t(100, 144, "stopped: no instructions run, no processor time spent", "lbl sm mut"))
    b.append(_t(640, 124, "1 look", "lbl sm learn"))
    # the arrival
    b.append('<path d="M500,36 L500,130" class="flow" stroke-dasharray="3 3"/>')
    b.append(_t(500, 32, "the message arrives", "lbl sm mid"))
    b.append(_line(500, 120, 620, 120, "flow learn", arrow=False))
    b.append(_t(510, 112, "woken at once", "lbl sm learn"))
    b.append(_t(20, 176, "polling pays for every look and notices late; blocking "
                         "pays nothing and is woken at once", "lbl sm mut"))
    return _svg(720, 188, "".join(b), 640)


# --------------------------------------------------------------------------
# chapter nine: the calls, and how conversations are told apart
# --------------------------------------------------------------------------

@diagram("socket-lifecycle")
def socket_lifecycle(_=None) -> str:
    b = [_t(20, 24, "the server's calls and the client's, and where they meet", "lbl b")]
    b.append(_t(150, 52, "server", "lbl b mid"))
    srv = [("socket", "a descriptor, attached to nothing"),
           ("bind", "claim a port on this machine"),
           ("listen", "this side answers"),
           ("accept", "block until somebody arrives")]
    for i, (name, sub) in enumerate(srv):
        y = 64 + i * 44
        cls = "box learn" if name == "accept" else "box"
        b.append(_labelled_box(60, y, 180, 34, name, "", cls))
        b.append(_t(250, y + 21 if i < 3 else y + 8, sub, "lbl sm mut"))
        if i < 3:
            b.append(_line(150, y + 34, 150, y + 44, "flow mut", arrow=False))
    b.append(_line(150, 230, 150, 250))
    b.append(_labelled_box(60, 250, 180, 34, "read, write, close", "", "box learn"))
    b.append(_t(250, 271, "a new descriptor, this visitor only", "lbl sm mut"))
    b.append('<path d="M40,267 L30,267 L30,213 L58,213" class="flow mut" marker-end="url(#arw)"/>')
    b.append(_t(20, 300, "back to accept", "lbl sm mut"))
    b.append(_t(610, 52, "client", "lbl b mid"))
    for name, y in [("socket", 108), ("connect", 196), ("write, read, close", 250)]:
        b.append(_labelled_box(520, y, 180, 34, name, "", "box"))
    b.append(_line(610, 142, 610, 196, "flow mut", arrow=False))
    b.append(_line(610, 230, 610, 250, "flow mut", arrow=False))
    b.append(_line(520, 218, 240, 218, "flow learn"))
    b.append(_t(380, 232, "the connection", "lbl sm mid learn"))
    return _svg(720, 312, "".join(b), 640)


@diagram("four-tuple")
def four_tuple(_=None) -> str:
    b = [_t(20, 24, "three conversations with one port, told apart by the other end", "lbl b")]
    b.append(_labelled_box(460, 90, 220, 60, "188.184.67.127 : 80", "the server's end, the same for all", "box learn"))
    rows = [(56, "fd 3", "192.168.1.182 : 59381"),
            (112, "fd 6", "192.168.1.182 : 59382"),
            (168, "fd 7", "192.168.1.182 : 59383")]
    for y, fd, addr in rows:
        b.append(_labelled_box(80, y, 220, 36, addr, "", "box"))
        b.append(_t(70, y + 22, fd, "lbl sm mut end"))
        b.append(_line(300, y + 18, 460, 120, "flow"))
    b.append(_t(20, 232, "four numbers, unique as a group, decide which socket a packet "
                         "belongs to", "lbl sm mut"))
    return _svg(720, 244, "".join(b), 640)


# --------------------------------------------------------------------------
# chapter ten: the path names a file
# --------------------------------------------------------------------------

@diagram("path-mapping")
def path_mapping(_=None) -> str:
    b = [_t(20, 24, "a static web server: the request path, joined onto one folder", "lbl b")]
    b.append(_t(20, 52, "site/  (the document root)", "lbl b"))
    files = ["index.html", "about.html", "style.css"]
    for i, f in enumerate(files):
        b.append(_t(40, 72 + i * 18, f, "lbl sm mut"))
    rows = [
        (60, "GET /about.html", "site/about.html", "200, the file's bytes", "box learn", "flow learn"),
        (104, "GET /", "site/index.html", "200, a folder means index.html", "box learn", "flow learn"),
        (148, "GET /missing.html", "site/missing.html", "404, there is no such file", "box brk", "flow brk"),
    ]
    for y, req, path, result, cls, fcls in rows:
        b.append(_box(250, y, 160, 30, "box"))
        b.append(_t(330, y + 19, req, "lbl mid"))
        b.append(_line(410, y + 15, 450, y + 15, fcls))
        b.append(_box(450, y, 150, 30, cls))
        b.append(_t(525, y + 19, path, "lbl sm mid"))
        b.append(_t(610, y + 19, result, "lbl sm brk" if "brk" in cls else "lbl sm learn"))
    b.append(_t(20, 206, "the path is joined onto the folder; what is there is sent, and what is not is a 404", "lbl sm mut"))
    return _svg(840, 218, "".join(b), 600)


# --------------------------------------------------------------------------
# chapter eleven: the redirect, and the cookie
# --------------------------------------------------------------------------

@diagram("post-redirect-get")
def post_redirect_get(_=None) -> str:
    b = [_t(20, 24, "post, then redirect, then get", "lbl b")]
    b.append(_t(160, 52, "browser", "lbl b mid"))
    b.append(_t(560, 52, "server", "lbl b mid"))
    b.append(_line(160, 60, 160, 220, "flow mut", arrow=False))
    b.append(_line(560, 60, 560, 220, "flow mut", arrow=False))
    b.append(_line(166, 84, 554, 84))
    b.append(_t(360, 78, "POST /messages  message=Ada was here", "lbl sm mid"))
    b.append(_line(554, 120, 166, 120, "flow learn"))
    b.append(_t(360, 114, "303 See Other  Location: /", "lbl sm mid learn"))
    b.append(_line(166, 156, 554, 156))
    b.append(_t(360, 150, "GET /", "lbl sm mid"))
    b.append(_line(554, 192, 166, 192, "flow learn"))
    b.append(_t(360, 186, "200 OK  the page, with the new entry", "lbl sm mid learn"))
    b.append(_t(20, 240, "after the 303 the browser's last request is GET /, so reload "
                         "and back are harmless", "lbl sm mut"))
    return _svg(720, 252, "".join(b), 640)


@diagram("cookie-session")
def cookie_session(_=None) -> str:
    b = [_t(20, 24, "a session: the name stays on the server, and the browser carries only a key to it", "lbl b")]
    b.append(_t(160, 52, "browser", "lbl b mid"))
    b.append(_t(560, 52, "server", "lbl b mid"))
    b.append(_line(160, 60, 160, 250, "flow mut", arrow=False))
    b.append(_line(560, 60, 560, 250, "flow mut", arrow=False))
    b.append(_line(166, 84, 554, 84))
    b.append(_t(360, 78, "POST /login  name=Ada", "lbl sm mid"))
    b.append(_box(580, 92, 130, 34, "box learn"))
    b.append(_t(645, 106, "sessions[3776b0...]", "lbl sm mid"))
    b.append(_t(645, 120, "= \"Ada\"", "lbl sm mid"))
    b.append(_line(554, 136, 166, 136, "flow learn"))
    b.append(_t(360, 130, "303  Set-Cookie: session=3776b0...", "lbl sm mid learn"))
    b.append(_box(20, 144, 120, 30, "box"))
    b.append(_t(80, 163, "cookie jar", "lbl sm mid"))
    b.append(_line(166, 196, 554, 196))
    b.append(_t(360, 190, "GET /  Cookie: session=3776b0...", "lbl sm mid"))
    b.append(_line(554, 232, 166, 232, "flow learn"))
    b.append(_t(360, 226, "200  Signed in as Ada", "lbl sm mid learn"))
    b.append(_t(20, 272, "nothing links two requests except a token the browser sends back", "lbl sm mut"))
    return _svg(720, 284, "".join(b), 640)


# --------------------------------------------------------------------------
# chapter twelve: what usually stands in front of what
# --------------------------------------------------------------------------

@diagram("web-vs-app-server")
def web_vs_app_server(_=None) -> str:
    b = [_t(20, 24, "two programs called a server, and where each one sits", "lbl b")]
    b.append(_labelled_box(30, 70, 130, 60, "browsers", "many, from anywhere", "box"))
    b.append(_labelled_box(230, 70, 200, 60, "web server", "nginx or Apache", "box"))
    b.append(_labelled_box(500, 70, 190, 60, "application server", "your code runs here", "box learn"))
    b.append(_line(160, 100, 230, 100))
    b.append(_t(195, 92, "HTTP", "lbl sm mid mut"))
    b.append(_line(430, 100, 500, 100))
    b.append(_t(465, 92, "the rest", "lbl sm mid mut"))
    b.append(_t(330, 156, "files, encryption, connections; answers /style.css itself", "lbl sm mid mut"))
    b.append(_t(595, 156, "answers /messages", "lbl sm mid learn"))
    b.append('<path d="M330,136 L330,142" class="flow mut"/>')
    b.append('<path d="M595,136 L595,142" class="flow mut"/>')
    b.append(_t(20, 192, "a rack in a building is a third thing with the same name; "
                         "the laptop this runs on today is a fourth", "lbl sm mut"))
    return _svg(720, 204, "".join(b), 620)


# --------------------------------------------------------------------------
# chapter thirteen: one at a time, then a thread each, then the race
# --------------------------------------------------------------------------

@diagram("serialized-vs-threaded")
def serialized_vs_threaded(_=None) -> str:
    b = [_t(20, 24, "a slow visitor and a fast one, two ways", "lbl b")]
    b.append(_t(20, 60, "one loop", "lbl b"))
    b.append(_box(120, 46, 400, 22, "box brk", rx=2))
    b.append(_t(320, 61, "slow page, 2 s", "lbl sm mid"))
    b.append(_box(520, 46, 40, 22, "box", rx=2))
    b.append(_t(540, 61, "fast", "lbl sm mid"))
    b.append(_line(240, 80, 520, 80, "flow brk"))
    b.append(_t(380, 94, "the fast visitor waits 1.7 s for somebody else's page", "lbl sm mid brk"))
    b.append(_t(20, 140, "a thread each", "lbl b"))
    b.append(_box(120, 126, 400, 22, "box", rx=2))
    b.append(_t(320, 141, "slow page, 2 s", "lbl sm mid"))
    b.append(_box(240, 154, 40, 22, "box learn", rx=2))
    b.append(_t(260, 169, "fast", "lbl sm mid"))
    b.append(_t(290, 169, "answered in 0.0006 s, while the slow one is still asleep", "lbl sm learn"))
    b.append(_line(120, 200, 640, 200, "flow mut"))
    b.append(_t(648, 204, "time", "lbl sm mut"))
    b.append(_t(20, 232, "the loop only goes back to accept when it has finished; a thread "
                         "per visitor lets accept run again at once", "lbl sm mut"))
    return _svg(720, 244, "".join(b), 640)


@diagram("race")
def race(_=None) -> str:
    b = [_t(20, 24, "two threads, one shared total, and an addition that vanishes", "lbl b")]
    b.append(_t(90, 56, "thread one", "lbl b mid"))
    b.append(_t(360, 56, "total", "lbl b mid"))
    b.append(_t(630, 56, "thread two", "lbl b mid"))
    steps = [
        (84, "read 5", None, None),
        (116, None, None, "read 5"),
        (148, "write 6", "6", None),
        (180, None, "6", "write 6"),
    ]
    b.append(_line(360, 64, 360, 210, "flow mut", arrow=False))
    b.append(_t(372, 78, "5", "lbl b"))
    for y, left, mid, right in steps:
        if left:
            cls = "flow learn" if "write" in left else "flow"
            if "read" in left:
                b.append(_line(350, y, 130, y, cls))
            else:
                b.append(_line(130, y, 350, y, cls))
            b.append(_t(240, y - 6, left, "lbl sm mid"))
        if right:
            cls = "flow brk" if "write" in right else "flow"
            if "read" in right:
                b.append(_line(370, y, 590, y, cls))
            else:
                b.append(_line(590, y, 370, y, cls))
            b.append(_t(480, y - 6, right, "lbl sm mid"))
        if mid:
            b.append(_t(372, y + 18, mid, "lbl b"))
    b.append(_t(20, 236, "two additions happened and the total went up by one; the scheduler "
                         "chose the moment, and nothing reported it", "lbl sm mut"))
    return _svg(720, 248, "".join(b), 640)


# --------------------------------------------------------------------------
# chapter fourteen: reading everything against looking it up
# --------------------------------------------------------------------------

@diagram("index-scan-vs-search")
def index_scan_vs_search(_=None) -> str:
    b = [_t(20, 24, "finding record 999,999 two ways", "lbl b")]
    b.append(_t(20, 58, "scan", "lbl b"))
    for i in range(20):
        x = 80 + i * 30
        cls = "box brk" if i == 19 else "box sunk"
        b.append(_box(x, 46, 26, 18, cls, rx=1))
    b.append(_t(80, 84, "read every record until the one you want turns up: a million reads", "lbl sm brk"))
    b.append(_t(20, 130, "search", "lbl b"))
    b.append(_labelled_box(300, 104, 120, 28, "index", "", "box learn"))
    b.append(_labelled_box(220, 152, 100, 26, "id < 500k", "", "box"))
    b.append(_labelled_box(400, 152, 100, 26, "id >= 500k", "", "box learn"))
    b.append(_line(340, 132, 270, 152, "flow mut"))
    b.append(_line(380, 132, 450, 152, "flow learn"))
    for i in range(20):
        x = 80 + i * 30
        cls = "box learn" if i == 19 else "box sunk"
        b.append(_box(x, 196, 26, 18, cls, rx=1))
    b.append(_line(450, 178, 663, 196, "flow learn"))
    b.append(_t(80, 234, "a second structure, kept sorted on every write, says where to look: "
                         "about twenty reads", "lbl sm learn"))
    return _svg(720, 246, "".join(b), 640)


# --------------------------------------------------------------------------
# chapter fifteen: the six components, all on one machine
# --------------------------------------------------------------------------

@diagram("deployment-topology")
def deployment_topology(_=None) -> str:
    b = [_t(20, 24, "one machine, six pressures answered: every box is a process", "lbl b")]
    b.append('<rect x="150" y="40" width="550" height="230" rx="4" class="box sunk"/>')
    b.append(_t(160, 56, "one machine", "lbl sm mut"))
    b.append(_labelled_box(20, 100, 100, 44, "browsers", "the internet", "box"))
    b.append(_labelled_box(180, 100, 130, 44, "reverse proxy", "holds port 443", "box learn"))
    b.append(_line(120, 122, 180, 122))
    b.append(_labelled_box(360, 72, 130, 40, "app, old", "finishing up", "box"))
    b.append(_labelled_box(360, 128, 130, 40, "app, new", "your code", "box learn"))
    b.append(_line(310, 115, 360, 92, "flow mut"))
    b.append(_line(310, 128, 360, 148, "flow learn"))
    b.append(_labelled_box(540, 72, 140, 40, "database", "its own port", "box"))
    b.append(_labelled_box(540, 128, 140, 40, "cache", "shared answers", "box"))
    b.append(_line(490, 148, 540, 148, "flow mut"))
    b.append(_line(490, 140, 540, 96, "flow mut"))
    b.append(_labelled_box(360, 200, 130, 40, "queue", "jobs written down", "box"))
    b.append(_labelled_box(540, 200, 140, 40, "worker", "does them later", "box"))
    b.append(_line(425, 168, 425, 200, "flow mut"))
    b.append(_line(490, 220, 540, 220, "flow mut"))
    b.append(_t(180, 216, "supervisor: restarts", "lbl sm mut"))
    b.append(_t(180, 230, "anything that dies", "lbl sm mut"))
    b.append(_t(180, 254, "logs and metrics: what happened", "lbl sm mut"))
    b.append(_t(20, 292, "the proxy is the only process with a public address; "
                         "everything behind it still binds 127.0.0.1", "lbl sm mut"))
    return _svg(720, 304, "".join(b), 640)


# --------------------------------------------------------------------------
# chapter sixteen: your code inside the framework
# --------------------------------------------------------------------------

@diagram("framework-shell")
def framework_shell(_=None) -> str:
    b = [_t(20, 24, "you do not call a framework; it calls you", "lbl b")]
    b.append('<rect x="40" y="44" width="640" height="200" rx="4" class="box sunk"/>')
    b.append(_t(52, 62, "uvicorn and FastAPI: the loop, the reader, the router, the parsers, the escaper", "lbl sm mut"))
    b.append(_labelled_box(60, 80, 150, 40, "accept loop", "a pool or an event loop", "box"))
    b.append(_labelled_box(60, 136, 150, 40, "read a request", "limits, timeouts, 400", "box"))
    b.append(_labelled_box(60, 192, 150, 40, "route and parse", "fields, cookies, types", "box"))
    b.append(_line(210, 212, 270, 212))
    b.append('<rect x="270" y="80" width="390" height="152" rx="4" class="box learn"/>')
    b.append(_t(280, 98, "app.py: the thirty lines that are about a guestbook", "lbl sm learn"))
    for i, name in enumerate(["guestbook()", "log_in()", "sign()", "one_message()"]):
        b.append(_box(284 + i * 94, 112, 86, 26, "box"))
        b.append(_t(327 + i * 94, 129, name, "lbl sm mid"))
    b.append(_labelled_box(284, 156, 180, 40, "templates", "escaped for you", "box"))
    b.append(_labelled_box(480, 156, 170, 40, "sqlite", "chapter fourteen's", "box"))
    b.append(_line(480, 176, 464, 176, "flow mut", arrow=False))
    b.append(_t(20, 268, "everything outside the indigo box is something you wrote by hand "
                         "between chapters ten and fifteen", "lbl sm mut"))
    return _svg(720, 280, "".join(b), 640)


# --------------------------------------------------------------------------
# chapter seventeen: why a system spreads, and what a partition forces
# --------------------------------------------------------------------------

@diagram("three-distributions")
def three_distributions(_=None) -> str:
    b = [_t(20, 24, "the same system, spread three ways", "lbl b")]
    b.append(_t(20, 80, "for load", "lbl b"))
    b.append(_labelled_box(120, 60, 90, 32, "proxy", "", "box"))
    for i in range(3):
        y = 40 + i * 36
        b.append(_labelled_box(300, y, 90, 28, f"app {i + 1}", "", "box learn"))
        b.append(_line(210, 76, 300, y + 14, "flow mut"))
    b.append(_t(410, 80, "horizontal scaling: the same program, three times", "lbl sm mut"))
    b.append(_t(20, 172, "for data", "lbl b"))
    b.append(_labelled_box(120, 152, 110, 32, "primary", "", "box learn"))
    b.append(_labelled_box(260, 152, 90, 32, "copy", "", "box"))
    b.append(_labelled_box(370, 152, 90, 32, "copy", "", "box"))
    b.append(_line(230, 168, 260, 168, "flow mut"))
    b.append(_line(350, 168, 370, 168, "flow mut"))
    b.append(_t(480, 172, "replication, or shards by key", "lbl sm mut"))
    b.append(_t(20, 244, "for capability", "lbl b"))
    for i, (name, sub) in enumerate([("database", "big disks"), ("cache", "big memory"), ("queue", "its own job")]):
        b.append(_labelled_box(140 + i * 150, 222, 130, 44, name, sub, "box"))
    b.append(_t(140, 284, "one job, one machine, with the hardware that job wants", "lbl sm mut"))
    b.append(_t(20, 312, "every line between boxes is now chapter two's network: out of order, lossy, "
                         "and silent about timing", "lbl sm mut"))
    return _svg(720, 324, "".join(b), 640)


@diagram("partition")
def partition(_=None) -> str:
    b = [_t(20, 24, "the network splits, and each side has to choose", "lbl b")]
    for i in range(3):
        b.append(_labelled_box(40 + i * 90, 60, 80, 36, f"copy {i + 1}", "", "box"))
    for i in range(2):
        b.append(_labelled_box(460 + i * 90, 60, 80, 36, f"copy {i + 4}", "", "box"))
    b.append('<path d="M310,78 L460,78" class="flow brk"/>')
    b.append(_t(385, 70, "no packets cross", "lbl sm mid brk"))
    b.append(_t(160, 130, "three copies, a majority", "lbl b mid"))
    b.append(_t(160, 148, "can keep deciding, and knows it", "lbl sm mut mid"))
    b.append(_t(545, 130, "two copies, a minority", "lbl b mid"))
    b.append(_t(545, 148, "refuse and stay right, or answer and risk being stale", "lbl sm mut mid"))
    b.append(_t(20, 190, "that choice is the whole of CAP: what you give up while the split lasts, "
                         "not a menu of three", "lbl sm mut"))
    return _svg(720, 202, "".join(b), 640)


# --------------------------------------------------------------------------
# chapter eighteen: the stack again, with the other names on it
# --------------------------------------------------------------------------

@diagram("stack-relabelled")
def stack_relabelled(_=None) -> str:
    b = [_t(20, 24, "the same stack, with the other set of names on it", "lbl b")]
    rows = [
        ("a process reading files and doing arithmetic", "a training run on GPUs", 1),
        ("a saved copy because memory dies with the process", "a checkpoint", 14),
        ("many machines agreeing at every step", "distributed training", 17),
        ("a server: socket, bind, listen, accept", "a model serving requests", 5),
        ("a request: text in lines, JSON in the body", "a prompt, in tokens", 6),
        ("a chunked response, a piece at a time", "streaming", 6),
        ("a queue, a cache, backpressure, a health check", "batching, KV cache, rate limits", 15),
        ("a client making HTTP requests and acting on them", "an agent", 7),
    ]
    b.append(_t(40, 52, "this course", "lbl b"))
    b.append(_t(420, 52, "the other vocabulary", "lbl b"))
    for i, (ours, theirs, ch) in enumerate(rows):
        y = 64 + i * 26
        b.append(_box(40, y, 360, 22, "box learn", rx=2))
        b.append(_t(50, y + 15, ours, "lbl sm"))
        b.append(_box(420, y, 250, 22, "box", rx=2))
        b.append(_t(430, y + 15, theirs, "lbl sm"))
        b.append(_t(690, y + 15, f"ch {ch}", "lbl sm mut"))
        b.append(_line(400, y + 11, 420, y + 11, "flow mut", arrow=False))
    b.append(_t(20, 292, "nothing on the left is missing from the right", "lbl sm mut"))
    return _svg(720, 304, "".join(b), 640)
