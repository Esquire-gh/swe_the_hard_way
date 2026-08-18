#!/usr/bin/env python3
"""Check the tutorial against the writing contract in docs/STYLE.md.

Run it from the repository root with: python3 scripts/check.py
It prints every problem it finds and exits non zero if there was any.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAX_WIDTH = 80

BANNED_CHARS = {
    "—": "em dash, use a full stop or a comma instead",
    "–": "en dash, use plain words instead",
}

# Words that tell the reader a thing is easy. They do nothing for the reader
# who found it easy and make the stuck reader feel worse.
HEDGING = [
    "simply",
    "obviously",
    "of course",
    "clearly",
    "merely",
    "trivially",
    "just a matter of",
    "needless to say",
    "it goes without saying",
]

# Words that promise more than the sentence delivers.
HYPE = [
    "powerful",
    "blazing",
    "game changing",
    "superpower",
    "magical",
    "seamless",
    "effortless",
    "revolutionary",
]

# Capitalised because that is how they are spelled, not because a heading has
# slipped into title case. Grows as the tutorial introduces more names.
PROPER = {
    "ACID", "API", "APIs", "ARPA", "ARPANET", "ASCII", "AI", "BSD", "C",
    "CERN", "CGI", "CPU", "CPUs", "CRUD", "CSS", "DNS", "DSL", "Docker",
    "English", "Ethernet", "FastAPI", "GET", "GIL", "GPU", "GPUs", "HTML",
    "HTTP", "HTTPS", "I", "ID", "IP", "JSON", "JavaScript", "Linux", "Mosaic",
    "NCP", "Netscape", "Nginx", "OS", "POST", "PUT", "Postgres",
    "PostgreSQL", "Python", "RAM", "RFC", "Redis", "SQL", "SQLite", "TCP",
    "TLS", "UDP", "URL", "URLs", "UTF", "Unix", "W3C", "WHATWG", "Wi-Fi",
    "Berners-Lee", "Cerf", "Kahn", "Baran", "Davies", "Andreessen",
}

HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
CODE_PATH = re.compile(r"`((?:\.\./)*code/[^`\s]+)`")

# A list item or navigation line that is made entirely of markdown links.
LINK_LINE = re.compile(
    r"^(?:[-*]|\d+\.)?\s*\[[^\]]+\]\([^)]+\)"
    r"(?:\s*\|\s*\[[^\]]+\]\([^)]+\))*\s*(?:is [^.]*)?\.?\s*$"
)

# The file that names the banned words cannot avoid containing them.
WORD_CHECK_EXEMPT = {pathlib.Path("docs/STYLE.md")}


def heading_problems(heading):
    """Report words in a heading that look like title case."""
    found = []
    starts_sentence = True
    for word in heading.split():
        core = word.strip("*_`()[]{}<>,.:;?!\"'")
        core = re.sub(r"['’]s$", "", core)
        if core:
            if not starts_sentence and core[0].isupper() and core not in PROPER:
                found.append(f"heading is not sentence case: '{core}'")
        starts_sentence = word.endswith((".", ":", "?", "!"))
    return found


def phrase_problems(line, phrases, reason):
    """Report banned phrases, matched on whole words."""
    found = []
    lowered = line.lower()
    for phrase in phrases:
        if re.search(rf"(?<![\w-]){re.escape(phrase)}(?![\w-])", lowered):
            found.append(f"'{phrase}' {reason}")
    return found


problems = []
stubs = []

for path in sorted(ROOT.rglob("*.md")):
    if ".git" in path.parts or ".venv" in path.parts:
        continue
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    check_words = rel not in WORD_CHECK_EXEMPT

    if "Status: not written yet" in text:
        stubs.append(str(rel))

    in_fence = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()

        for char, reason in BANNED_CHARS.items():
            if char in line:
                problems.append(f"{rel}:{line_no}: {reason}")

        if stripped.startswith("```"):
            in_fence = not in_fence
            continue

        is_code = in_fence or line.startswith("    ")
        is_table = stripped.startswith("|")
        # A line whose whole job is to hold a link cannot be wrapped, so it is
        # allowed to run long.
        is_link_line = "http" in stripped or bool(LINK_LINE.match(stripped))
        if len(line) > MAX_WIDTH and not (is_code or is_table or is_link_line):
            problems.append(
                f"{rel}:{line_no}: line is {len(line)} characters, "
                f"wrap at {MAX_WIDTH}"
            )

        if is_code:
            continue

        if check_words:
            for found in phrase_problems(
                line, HEDGING, "tells the reader it is easy, cut it"
            ):
                problems.append(f"{rel}:{line_no}: {found}")
            for found in phrase_problems(
                line, HYPE, "is hype, say what it does instead"
            ):
                problems.append(f"{rel}:{line_no}: {found}")

        heading = HEADING.match(line)
        if heading:
            for found in heading_problems(heading.group(2)):
                problems.append(f"{rel}:{line_no}: {found}")

    for target in LINK.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = target.split("#")[0]
        if target and not (path.parent / target).exists():
            problems.append(f"{rel}: link points at nothing: {target}")

    for named in CODE_PATH.findall(text):
        if "<" in named:  # a placeholder in the instructions, not a real path
            continue
        cleaned = named.rstrip("/")
        # A path in prose is written either from the repository root or from
        # the file that mentions it. Both are fair, so accept either.
        if not ((ROOT / cleaned).exists() or (path.parent / cleaned).exists()):
            problems.append(f"{rel}: names a path under code/ that is not "
                            f"on disk: {named}")

if problems:
    for problem in sorted(set(problems)):
        print(problem)
    print(f"\n{len(set(problems))} problems found.")
    sys.exit(1)

if stubs:
    print(f"All checks passed. {len(stubs)} chapters are still stubs.")
else:
    print("All checks passed.")
