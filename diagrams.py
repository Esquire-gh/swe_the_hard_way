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
