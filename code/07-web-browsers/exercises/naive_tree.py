"""Build a tree from HTML the obvious way, and see where it disagrees.

Open a tag, go one level deeper. Close a tag, come back up. Text goes
wherever you are. That is what anybody would write, and it is not what a
browser does, which is the point.

Run it with: python3 naive_tree.py page/broken.html
"""

import pathlib
import sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "source", "track", "wbr"}


class Naive(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.open = []

    def say(self, text):
        print("  " * self.depth + text)

    def handle_starttag(self, tag, attrs):
        self.say(f"<{tag}>")
        if tag not in VOID:
            self.open.append(tag)
            self.depth += 1

    def handle_endtag(self, tag):
        if tag not in self.open:
            self.say(f"</{tag}>   (closed but never opened)")
            return
        while self.open and self.open[-1] != tag:
            self.depth -= 1
            self.say(f"</{self.open.pop()}>   (closed for you, out of order)")
        self.open.pop()
        self.depth -= 1

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.say(f'"{text}"')


path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "page/broken.html")
parser = Naive()
parser.feed(path.read_text())
for still_open in reversed(parser.open):
    parser.depth -= 1
    parser.say(f"</{still_open}>   (never closed at all)")
