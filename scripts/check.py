#!/usr/bin/env python3
"""Check the tutorial against the writing contract in docs/STYLE.md.

Run it from the repository root with: python3 scripts/check.py
It prints every problem it finds and exits non zero if there was any.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BANNED = {
    "—": "em dash, use a full stop or a comma instead",
    "–": "en dash, use plain words instead",
}
MAX_WIDTH = 80

# A list item or navigation line that is made entirely of markdown links.
LINK_LINE = re.compile(r"^(?:[-*]|\d+\.)?\s*\[[^\]]+\]\([^)]+\)(?:\s*\|\s*\[[^\]]+\]\([^)]+\))*\s*(?:is [^.]*\.)?$")

problems = []

for path in sorted(ROOT.rglob("*.md")):
    if ".git" in path.parts:
        continue
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")

    for line_no, line in enumerate(text.splitlines(), start=1):
        for char, reason in BANNED.items():
            if char in line:
                problems.append(f"{rel}:{line_no}: {reason}")

        stripped = line.strip()
        is_code = line.startswith("    ") or stripped.startswith("```")
        is_table = stripped.startswith("|")
        # A line whose whole job is to hold a link cannot be wrapped, so it is
        # allowed to run long.
        is_link_line = "http" in stripped or bool(LINK_LINE.match(stripped))
        if len(line) > MAX_WIDTH and not (is_code or is_table or is_link_line):
            problems.append(f"{rel}:{line_no}: line is {len(line)} characters, wrap at {MAX_WIDTH}")

    for link in re.findall(r"\]\((\./[^)]+)\)", text):
        target = (path.parent / link).resolve()
        if not target.exists():
            problems.append(f"{rel}: link points at nothing: {link}")

if problems:
    for problem in problems:
        print(problem)
    print(f"\n{len(problems)} problems found.")
    sys.exit(1)

print("All checks passed.")
