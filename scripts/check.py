#!/usr/bin/env python3
"""Mechanical checks for the site.

These are the rules a program can enforce, run before every commit from the
repository root:

    python3 scripts/check.py

It reports, over the authored pages in content/ and the built pages in site/:

  * em dashes and en dashes, which this repository does not use
  * banned words: the ones that tell the reader a thing is easy, and the ones
    that promise more than the sentence delivers
  * prose wider than eighty columns (tags and code blocks do not count)
  * headings that have slipped into title case
  * internal links that point at a page that does not exist
  * {{ }} tokens the build could not resolve
  * code/ paths named in a page that are not on disk

Add rules here as the site grows rather than checking by eye.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
SITE = ROOT / "site"
MAX_WIDTH = 80

sys.path.insert(0, str(ROOT))
from chapters import CHAPTERS  # noqa: E402

# Pages the site is allowed to link to, whether or not they are built yet.
EXPECTED_PAGES = {"index.html", "further-watching.html"} | {
    f"{c.slug}.html" for c in CHAPTERS}

BANNED_CHARS = {
    "—": "em dash, use a full stop, a comma, or brackets",
    "–": "en dash, use a full stop, a comma, or brackets",
}

HEDGING = ["simply", "obviously", "of course", "clearly", "merely",
           "trivially", "just a matter of", "needless to say"]
HYPE = ["powerful", "blazing", "game changing", "superpower", "magical",
        "seamless", "effortless", "revolutionary"]

# Proper nouns and acronyms allowed to keep their capital mid-heading.
PROPER = {
    "python", "http", "https", "html", "css", "tcp", "ip", "dns", "url", "urls",
    "arpanet", "ucla", "wi-fi", "ethernet", "rand", "cs", "sql", "fastapi",
    "cern", "os", "cpu", "gil", "ai", "api", "json", "i", "openapi",
}

TAG = re.compile(r"<[^>]+>")
TOKEN = re.compile(r"\{\{.*?\}\}")
HEADING = re.compile(r"<h([1-3])[^>]*>(.*?)</h\1>", re.S)
HREF = re.compile(r'(?:href|src)="([^"]+)"')
CODE_TOKEN = re.compile(r"\{\{\s*code:([^#}\s]+)")
CODE_MENTION = re.compile(r"(?<![\w/])(code/[A-Za-z0-9._/-]+)")
BAD_TOKEN_MARK = "background:#f8e4ee"


def visible(line: str) -> str:
    """The line with tags and tokens removed, for width and word checks."""
    return TOKEN.sub("", TAG.sub("", line))


def word_hits(text: str, words: list) -> list:
    low = text.lower()
    return [w for w in words if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low)]


def heading_title_case(text: str) -> bool:
    """True if a heading looks like Title Case rather than sentence case."""
    text = TAG.sub("", text).strip()
    # a capital is allowed right after a sentence break
    words = re.findall(r"[A-Za-z][A-Za-z'\-]*", text)
    prev_break = True
    caps = 0
    for w in words:
        if prev_break:
            prev_break = False
            continue
        base = w.lower().split("'")[0]
        if w[0].isupper() and base not in PROPER and not w.isupper():
            caps += 1
        prev_break = False
    return caps >= 1


def check_content(problems: list) -> None:
    for path in sorted(CONTENT.glob("*.html")):
        rel = path.relative_to(ROOT)
        text = path.read_text()

        # banned punctuation, anywhere
        for i, line in enumerate(text.splitlines(), 1):
            for ch, why in BANNED_CHARS.items():
                if ch in line:
                    problems.append(f"{rel}:{i}: {why}")

        # width and banned words, on visible prose only
        in_pre = False
        for i, line in enumerate(text.splitlines(), 1):
            if "<pre" in line:
                in_pre = True
            vis = "" if in_pre else visible(line)
            if "</pre>" in line:
                in_pre = False
            if not vis.strip():
                continue
            # leading whitespace is HTML indentation, not prose; measure the prose
            if len(vis.strip()) > MAX_WIDTH:
                problems.append(f"{rel}:{i}: prose is {len(vis.strip())} columns wide")
            for w in word_hits(vis, HEDGING):
                problems.append(f"{rel}:{i}: hedging word '{w}'")
            for w in word_hits(vis, HYPE):
                problems.append(f"{rel}:{i}: hype word '{w}'")

        # headings in sentence case
        for _, htext in HEADING.findall(text):
            if heading_title_case(htext):
                clean = TAG.sub("", htext).strip()
                problems.append(f"{rel}: heading looks like title case: \"{clean}\"")

        # code/ paths named on the page must exist
        for m in set(CODE_TOKEN.findall(text)) | set(CODE_MENTION.findall(text)):
            target = ROOT / m
            if not target.exists():
                problems.append(f"{rel}: names code path that does not exist: {m}")


def check_built(problems: list) -> None:
    pages = list(SITE.glob("*.html")) + list(SITE.glob("chapters/*.html"))
    if not pages:
        problems.append("site/ has no built pages, run python3 build.py first")
        return
    for path in pages:
        rel = path.relative_to(ROOT)
        text = path.read_text()
        if "{{" in text or BAD_TOKEN_MARK in text:
            problems.append(f"{rel}: contains an unresolved token")
        for target in HREF.findall(text):
            if target.startswith(("http:", "https:", "mailto:", "#", "data:")):
                continue
            frag = target.split("#", 1)[0]
            if not frag:
                continue
            dest = (path.parent / frag).resolve()
            if dest.exists():
                continue
            if Path(frag).name in EXPECTED_PAGES:
                continue  # a planned page, not authored yet
            problems.append(f"{rel}: broken link to {target}")


def main() -> None:
    problems: list = []
    check_content(problems)
    check_built(problems)

    stubs = [c.name for c in CONTENT.glob("*.html")]
    if problems:
        print(f"{len(problems)} problem(s):\n")
        for p in problems:
            print("  " + p)
        sys.exit(1)
    written = sorted(p.stem for p in CONTENT.glob("*.html"))
    print(f"All checks passed. {len(written)} page(s) authored.")


if __name__ == "__main__":
    main()
