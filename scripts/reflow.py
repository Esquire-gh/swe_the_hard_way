#!/usr/bin/env python3
"""Reflow authored HTML so visible prose is at most 80 columns per line.

Tags are atoms (spaces inside <...> are never split), <pre> blocks are left
alone, and width is measured on visible text (tags stripped), which is what
scripts/check.py measures. Continuation lines start at column 0, matching the
existing pages.
"""
import re, sys
from pathlib import Path
TAG = re.compile(r"<[^>]+>")
MAX = 80

def atoms(line):
    out, cur, i = [], "", 0
    while i < len(line):
        c = line[i]
        if c == "<":
            j = line.find(">", i)
            if j == -1: j = len(line) - 1
            cur += line[i:j+1]; i = j + 1; continue
        if line.startswith("{{", i):
            j = line.find("}}", i)
            if j == -1: j = len(line) - 2
            cur += line[i:j+2]; i = j + 2; continue
        if c.isspace():
            if cur: out.append(cur); cur = ""
            i += 1; continue
        cur += c; i += 1
    if cur: out.append(cur)
    return out

def vis(s): return len(TAG.sub("", s))

def wrap(line):
    indent = line[:len(line) - len(line.lstrip())]
    words = atoms(line)
    lines, cur = [], indent
    for w in words:
        cand = w if cur.strip() == "" else cur + " " + w
        if cur.strip() == "": cand = cur + w
        if vis(cand.strip()) > MAX and cur.strip():
            lines.append(cur); cur = w
        else:
            cur = cand
    if cur.strip(): lines.append(cur)
    return lines

def reflow(text):
    out, in_pre = [], False
    for line in text.split("\n"):
        if "<pre" in line: in_pre = True
        if in_pre:
            out.append(line)
            if "</pre>" in line: in_pre = False
            continue
        if re.fullmatch(r"\{\{.*\}\}", line.strip()):
            out.append(line)          # a token-only line is never prose
        elif vis(line.strip()) > MAX:
            out.extend(wrap(line))
        else:
            out.append(line)
    return "\n".join(out)

for f in sys.argv[1:]:
    p = Path(f); before = p.read_text(); after = reflow(before)
    if after != before:
        assert TAG.sub("", re.sub(r"\s+", " ", before)).strip() == TAG.sub("", re.sub(r"\s+", " ", after)).strip(), "visible text changed"
        p.write_text(after); print(f"reflowed {f}")
