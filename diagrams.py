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
        ("Part five", "everything on top", "data, scale, many machines, and AI"),
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
