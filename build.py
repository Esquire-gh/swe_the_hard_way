#!/usr/bin/env python3
"""Assemble the site.

Authoring-time only. Readers never run this. The HTML committed under site/ is
complete: it opens from file:// with no server, and hosts on GitHub Pages
unchanged.

What it does:

  1. reads each chapter body from content/
  2. substitutes {{ }} tokens:
       {{ code:code/01-.../machine.py }}   inline the real runnable file
       {{ code:path#MARK }}                a BEGIN/END-marked slice of it
       {{ diagram:name }}                  a hand-rolled inline SVG
       {{ resources }}                     this chapter's curated links
  3. wraps each body in the shared shell (masthead, sidebar, prev/next)
  4. writes site/index.html, site/chapters/*.html, site/further-watching.html

The point of step 1: code shown on the site is code that exists and runs. If a
listing drifts from its file, the build shows the drift, because there is only
one copy.

    python3 build.py            # build everything
    python3 build.py --check    # report unresolved tokens, write nothing
"""
from __future__ import annotations

import argparse
import re
import sys
from html import escape
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

from chapters import CHAPTERS, FRONT, BY_NUM, PART_TITLES, part_chapters  # noqa: E402
import diagrams  # noqa: E402
import resources  # noqa: E402

CONTENT = REPO / "content"
SITE = REPO / "site"

TOKEN = re.compile(r"\{\{\s*(.+?)\s*\}\}", re.S)


# --------------------------------------------------------------------------
# python highlighting — enough to read by, not one colour more
# --------------------------------------------------------------------------

PY_KEYWORDS = {
    "and", "as", "assert", "break", "class", "continue", "def", "del", "elif",
    "else", "except", "False", "finally", "for", "from", "global", "if",
    "import", "in", "is", "lambda", "None", "nonlocal", "not", "or", "pass",
    "raise", "return", "True", "try", "while", "with", "yield",
}

PY_TOKEN = re.compile(r"""
      (?P<comment>\#[^\n]*)
    | (?P<string>'''.*?'''|\"\"\".*?\"\"\"|'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*")
    | (?P<def>(?<=\bdef\s)\w+)
    | (?P<name>[A-Za-z_]\w*)
    | (?P<number>\b\d[\w.]*)
    | (?P<other>.)
""", re.X | re.S)


def highlight_python(src: str) -> str:
    out = []
    for m in PY_TOKEN.finditer(src):
        kind = m.lastgroup
        text = escape(m.group())
        if kind == "comment":
            out.append(f'<span class="c-cm">{text}</span>')
        elif kind == "string":
            out.append(f'<span class="c-st">{text}</span>')
        elif kind == "def":
            out.append(f'<span class="c-fn">{text}</span>')
        elif kind == "name" and m.group() in PY_KEYWORDS:
            out.append(f'<span class="c-kw">{text}</span>')
        else:
            out.append(text)
    return "".join(out)


# --------------------------------------------------------------------------
# tokens
# --------------------------------------------------------------------------

class MissingToken(Exception):
    pass


def inline_code(spec: str) -> str:
    """{{ code:path }} or {{ code:path#MARK }} — put the real file on the page."""
    path_part, _, mark = spec.partition("#")
    path = REPO / path_part.strip()
    if not path.exists():
        raise MissingToken(f"no such file: {path_part}")
    src = path.read_text()
    if mark:
        lines = src.splitlines()
        try:
            a = next(i for i, l in enumerate(lines) if f"BEGIN {mark}" in l)
            b = next(i for i, l in enumerate(lines) if f"END {mark}" in l)
        except StopIteration:
            raise MissingToken(f"{path_part}: no BEGIN/END {mark} markers")
        src = "\n".join(lines[a + 1:b]).strip("\n")
    body = highlight_python(src) if path.suffix == ".py" else escape(src)
    return f'<div class="code"><pre>{body}</pre></div>'


def table_of_contents() -> str:
    """{{ toc }} — the five parts and eighteen chapters, from the spine."""
    out = ['<ul class="toc">']
    for part in (1, 2, 3, 4, 5):
        out.append(f'<li class="toc-part">{escape(PART_TITLES[part])}</li>')
        for c in part_chapters(part):
            out.append(
                f'<li><a href="chapters/{c.slug}.html" data-module="{c.slug}">'
                f'<span class="n">{c.nn}</span>'
                f'<span class="t">{escape(c.title)}</span>'
                f'<span class="d">{escape(c.desc)}</span></a></li>')
    out.append("</ul>")
    return "".join(out)


def resources_card(num: int) -> str:
    items = resources.for_chapter(num)
    if not items:
        return ""
    out = ['<div class="resources"><ul class="res-list">']
    for r, note, t in items:
        url = r.url
        if t:
            url = url + (f"&t={t}s" if "?" in url else f"?t={t}s")
        out.append(
            '<li><div class="res-head">'
            f'<span class="res-kind {r.kind}">{r.kind}</span>'
            f'<a class="res-title" href="{escape(url)}" target="_blank" '
            f'rel="noopener">{escape(r.title)}</a>'
            f'<span class="res-by">{escape(r.author)}</span></div>'
            f'<p class="res-note">{escape(note)}</p></li>')
    out.append("</ul></div>")
    return "".join(out)


def substitute(text: str, *, num: int, where: str) -> tuple[str, list[str]]:
    problems: list[str] = []

    def one(match: re.Match) -> str:
        expr = match.group(1).strip()
        try:
            if expr.startswith("code:"):
                return inline_code(expr[len("code:"):])
            if expr.startswith("diagram:"):
                name = expr[len("diagram:"):].strip()
                fn = diagrams.REGISTRY.get(name)
                if fn is None:
                    raise MissingToken(f"no diagram named '{name}'")
                return fn()
            if expr == "resources":
                return resources_card(num)
            if expr == "toc":
                return table_of_contents()
            raise MissingToken(f"unknown token '{expr}'")
        except MissingToken as e:
            problems.append(f"{where}: {{{{{expr}}}}} — {e}")
            return ('<span style="background:#f8e4ee;color:#a51f5c;'
                    'font-family:monospace;padding:0 .2em">?</span>')

    return TOKEN.sub(one, text), problems


# --------------------------------------------------------------------------
# the shared shell
# --------------------------------------------------------------------------

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{assets}style.css">
</head>
<body>
"""

FOOT = """<script src="{assets}site.js"></script>
</body>
</html>
"""

TOTAL = len(CHAPTERS)


def sitenav(chap, *, depth: int, page: str = "") -> str:
    base = "" if depth else "chapters/"
    home = "index.html" if depth == 0 else "../index.html"
    fw = "further-watching.html" if depth == 0 else "../further-watching.html"

    out = ['<nav class="sitenav" aria-label="the chapters">']
    cur_home = " current" if page == "index" else ""
    out.append(
        f'<a class="nav-home{cur_home}" href="{home}"><span class="n">00</span>'
        '<span class="t">Introduction</span></a>')
    for part in (1, 2, 3, 4, 5):
        out.append(f'<p class="nav-part">{escape(PART_TITLES[part])}</p>')
        out.append('<ul class="nav-list">')
        for c in part_chapters(part):
            cur = " current" if (c.num == chap.num and not page) else ""
            aria = ' aria-current="page"' if cur else ""
            out.append(
                f'<li><a class="nav-item{cur}" href="{base}{c.slug}.html" '
                f'data-module="{c.slug}"{aria}>'
                f'<span class="n">{c.nn}</span>'
                f'<span class="t">{escape(c.title)}</span></a></li>')
        out.append("</ul>")
    cur_fw = " current" if page == "further-watching" else ""
    out.append(
        f'<a class="nav-appendix{cur_fw}" href="{fw}"><span class="n">··</span>'
        '<span class="t">Further watching</span></a>')
    out.append("</nav>")
    return "".join(out)


def masthead(chap, *, depth: int, page: str = "") -> str:
    home = "index.html" if depth == 0 else "../index.html"
    if page == "further-watching":
        num, here, part = "", "Further watching", "appendix"
    elif chap.num == 0:
        num, here, part = "00", "Introduction", "the whole stack"
    else:
        num, here, part = chap.nn, chap.title, PART_TITLES[chap.part]
    numbered = " numbered" if num else ""
    hn = f'<span class="hn">{num}</span>' if num else ""
    counter = (f'<span class="progress-label">{chap.nn} / {TOTAL:02d}</span>'
               if chap.num and not page else
               f'<span class="progress-label" data-progress-count>'
               f'0 / {TOTAL} complete</span>')
    return (
        '<header class="masthead"><div class="masthead-inner">'
        f'<a class="brand" href="{home}"><b>swe the hard way</b></a>'
        f'<span class="crumb{numbered}"><span class="part">{escape(part.lower())}</span>'
        f'<span class="here">{hn}<span class="ht">{escape(here)}</span></span></span>'
        f'{counter}'
        '<button class="nav-toggle" type="button" aria-expanded="false" '
        'aria-controls="sitenav-panel">menu</button>'
        '</div></header>'
    )


def chapnav(chap, *, depth: int = 1) -> str:
    base = "" if depth else "chapters/"
    prev_c = BY_NUM.get(chap.num - 1)
    next_c = BY_NUM.get(chap.num + 1)
    out = ['<nav class="modnav">']
    if prev_c is not None:
        href = "../index.html" if prev_c.num == 0 else f"{prev_c.slug}.html"
        label = "Introduction" if prev_c.num == 0 else f"{prev_c.nn} · {prev_c.title}"
        out.append(f'<a class="prev" href="{href}"><span class="dir">previous</span>'
                   f'<span class="name">{escape(label)}</span></a>')
    if next_c is not None:
        href = f"{base}{next_c.slug}.html"
        out.append(f'<a class="next" href="{href}">'
                   f'<span class="dir">{"begin" if chap.num == 0 else "next"}</span>'
                   f'<span class="name">{next_c.nn} · {escape(next_c.title)}</span></a>')
    else:
        fw = "further-watching.html" if depth == 0 else "../further-watching.html"
        out.append(f'<a class="next" href="{fw}"><span class="dir">appendix</span>'
                   '<span class="name">Further watching</span></a>')
    out.append("</nav>")
    return "".join(out)


def done_toggle(chap) -> str:
    return (f'<button class="done-toggle" type="button" aria-pressed="false" '
            f'data-module="{chap.slug}"><span class="box"></span>'
            f'<span class="label">mark this chapter complete</span></button>')


def render_page(chap, body: str, *, depth: int, page: str = "",
                show_nav=True, show_toggle=True) -> str:
    assets = "assets/" if depth == 0 else "../assets/"
    if page == "further-watching":
        title = "Further watching — swe the hard way"
        desc = "Every outside video and course, mapped to its chapter."
    elif chap.num == 0:
        title = "Software Engineering the Hard Way"
        desc = escape(chap.desc)
    else:
        title = f"{chap.nn} · {chap.title} — swe the hard way"
        desc = escape(chap.desc)
    parts = [
        HEAD.format(title=escape(title), desc=desc, assets=assets),
        masthead(chap, depth=depth, page=page),
        '<div class="wrap"><div class="layout">',
        f'<div class="rail" id="sitenav-panel">{sitenav(chap, depth=depth, page=page)}</div>',
        '<main class="col">',
        body,
    ]
    if show_toggle and chap.num:
        parts.append(done_toggle(chap))
    if show_nav:
        parts.append(chapnav(chap, depth=depth))
    parts += ['</main></div></div>', FOOT.format(assets=assets)]
    return "".join(parts)


# --------------------------------------------------------------------------
# the further-watching appendix, built from resources.py
# --------------------------------------------------------------------------

def further_watching_body() -> str:
    out = ['<div class="hero"><p class="kicker learn">appendix</p>'
           '<h1>Further watching</h1>'
           '<p class="sub">Every outside resource this course points at, gathered '
           'in one place and mapped to the chapter it belongs to. Each was watched '
           'and kept only where it earns its place.</p></div>']
    last_part = None
    for num, items in resources.all_by_chapter():
        if not items:
            continue
        chap = BY_NUM[num]
        if chap.part != last_part:
            out.append(f'<p class="watch-part">{escape(PART_TITLES[chap.part])}</p>')
            last_part = chap.part
        out.append(f'<p class="watch-ch"><span class="n">{chap.nn}</span> '
                   f'<a href="chapters/{chap.slug}.html">{escape(chap.title)}</a></p>')
        out.append('<div class="resources"><ul class="res-list">')
        for r, note, t in items:
            url = r.url + ((f"&t={t}s" if "?" in r.url else f"?t={t}s") if t else "")
            out.append(
                '<li><div class="res-head">'
                f'<span class="res-kind {r.kind}">{r.kind}</span>'
                f'<a class="res-title" href="{escape(url)}" target="_blank" '
                f'rel="noopener">{escape(r.title)}</a>'
                f'<span class="res-by">{escape(r.author)}</span></div>'
                f'<p class="res-note">{escape(note)}</p></li>')
        out.append("</ul></div>")
    return "".join(out)


# --------------------------------------------------------------------------

def build(check_only: bool = False) -> int:
    problems: list[str] = []
    written = 0
    missing = []

    # front page
    src = CONTENT / "index.html"
    if src.exists():
        body, probs = substitute(src.read_text(), num=0, where="index.html")
        problems += probs
        html = render_page(FRONT, body, depth=0, page="index", show_toggle=False)
        if not check_only:
            (SITE / "index.html").write_text(html)
            written += 1
    else:
        missing.append("index")

    # chapters
    for chap in CHAPTERS:
        src = CONTENT / f"{chap.slug}.html"
        if not src.exists():
            missing.append(chap.slug)
            continue
        body, probs = substitute(src.read_text(), num=chap.num,
                                 where=f"{chap.slug}.html")
        problems += probs
        html = render_page(chap, body, depth=1)
        dest = SITE / "chapters" / f"{chap.slug}.html"
        if not check_only:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(html)
            written += 1

    # further-watching appendix
    if not check_only:
        html = render_page(FRONT, further_watching_body(), depth=0,
                           page="further-watching", show_nav=False, show_toggle=False)
        (SITE / "further-watching.html").write_text(html)
        written += 1

    if missing:
        print(f"content not written yet: {', '.join(missing)}")
    if problems:
        print(f"\n{len(problems)} unresolved token(s):")
        for p in problems[:40]:
            print("  " + p)
    print(f"\n{written} page(s) written to {SITE}"
          f"{' (check only)' if check_only else ''}")
    return 1 if problems else 0


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="report unresolved tokens without writing files")
    args = ap.parse_args()
    sys.exit(build(check_only=args.check))


if __name__ == "__main__":
    main()
