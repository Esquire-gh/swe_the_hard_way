"""The site's spine: the eighteen chapters, in order, grouped into five parts.

Everything structural is computed from this one list: the sidebar, the table of
contents, the previous and next links, the breadcrumb. If the navigation ever
disagrees with itself, the bug is here and nowhere else.

A chapter carries the limit it closes on, because in this course the limit is
the next chapter's opening question. `builds` and `breaks` drive the two colours
the site uses: indigo for the thing a chapter builds, magenta for the thing it
then breaks.
"""
from __future__ import annotations

PART_TITLES = {
    1: "Part one · one computer",
    2: "Part two · how the machines got connected",
    3: "Part three · the conversation",
    4: "Part four · building the server",
    5: "Part five · everything on top",
}


class Chapter:
    def __init__(self, num, slug, title, part, desc, *, builds="", breaks=""):
        self.num = num          # 0 is the front page
        self.slug = slug        # matches chapters/<slug>.md and code/<slug>/
        self.title = title
        self.part = part
        self.desc = desc        # one line, for the table of contents
        self.builds = builds    # the thing this chapter builds (indigo)
        self.breaks = breaks    # the limit it hits (magenta), opens the next one

    @property
    def nn(self) -> str:
        return f"{self.num:02d}"

    @property
    def code_dir(self) -> str:
        return f"code/{self.slug}"


FRONT = Chapter(0, "index", "What happens between pressing enter and a page", 0,
                "The whole stack, from the processor to the page, with nothing "
                "left as magic.")

CHAPTERS = [
    # ---- Part one -------------------------------------------------------
    Chapter(1, "01-what-it-means-to-tell-a-computer-what-to-do",
            "What it means to tell a computer what to do", 1,
            "What a program is on disk, what changes when it runs, and who is "
            "in charge of the difference.",
            builds="a process on one machine",
            breaks="one machine cannot reach another"),

    # ---- Part two -------------------------------------------------------
    Chapter(2, "02-how-networks-came-about",
            "How networks came about", 2,
            "Why moving bytes between machines needed packet switching and "
            "layered protocols, and why that design was inevitable.",
            builds="bytes moving between two machines",
            breaks="bytes arrive with no meaning attached"),
    Chapter(3, "03-how-networks-made-the-web-possible",
            "How networks made the web possible", 2,
            "The web as one application the network allowed, and what was new "
            "about documents that link to each other.",
            builds="documents anyone can link to and read",
            breaks="you still cannot say where a document lives"),
    Chapter(4, "04-a-website-is-a-file-on-someone-elses-computer",
            "A website is a file on someone else's computer", 2,
            "Where a page physically lives, how machines are found by address, "
            "and how a name people remember becomes one.",
            builds="a way to find the machine that holds the file",
            breaks="knowing where it is does not say who hands it over"),

    # ---- Part three -----------------------------------------------------
    Chapter(5, "05-the-client-server-model",
            "The client server model", 3,
            "Who asks and who answers, why it is a role and not a kind of "
            "machine, and why one computer can be both.",
            builds="the two roles in every exchange",
            breaks="the roles do not say what they send each other"),
    Chapter(6, "06-requests-and-responses-are-just-text",
            "Requests and responses are just text", 3,
            "A real HTTP request and response read byte by byte, until the "
            "format holds no mystery.",
            builds="the exact bytes of a request and a response",
            breaks="something has to write, send, and draw that text"),
    Chapter(7, "07-why-we-need-browsers",
            "Why we need browsers", 3,
            "Sending the text by hand, and what a browser adds: writing it, "
            "drawing it, and agreeing with every other browser.",
            builds="the side that asks, understood fully",
            breaks="now look at the side that answers"),

    # ---- Part four ------------------------------------------------------
    Chapter(8, "08-how-a-server-receives-a-request",
            "How a server receives a request", 4,
            "A web server is a program that waits. The mechanism that lets a "
            "program wait for the network.",
            builds="a program that waits for a connection",
            breaks="waiting needs something only the OS can give"),
    Chapter(9, "09-what-a-socket-is",
            "What a socket is", 4,
            "The operating system owns the network card, so it hands programs a "
            "handle that behaves like a file.",
            builds="the handle a program holds the network by",
            breaks="a handle is an idea until you use it"),
    Chapter(10, "10-a-web-server-in-one-file",
             "A web server in one file", 4,
             "Open a socket, accept a connection, read the request, serve a "
             "real file. Then watch it fall apart.",
             builds="a working web server, by hand",
             breaks="it serves one visitor, one fixed file, and forgets"),
    Chapter(11, "11-server-as-hardware-server-as-software",
             "Server as hardware, server as software", 4,
             "The box in a rack and the program running on it are both called "
             "the server. Separating them clears up a lot.",
             builds="a name for each of the two servers",
             breaks="naming things does not make the program do more"),
    Chapter(12, "12-from-reading-files-to-running-code",
             "From reading files to running code", 4,
             "Making the page different for each visitor: forms, methods, "
             "query strings, sessions, state, all by hand.",
             builds="pages generated per visitor, by hand",
             breaks="the same tedious code, written slightly wrong"),
    Chapter(13, "13-what-a-framework-is-for",
             "What a framework is for", 4,
             "Rebuild chapter 12 in a framework, line for line, so every "
             "feature maps to a problem you already felt.",
             builds="the same server, without the tedium",
             breaks="the framework hides the hardest part, still there"),
    Chapter(14, "14-two-people-at-once",
             "Two people at once", 4,
             "The hand written server does one thing at a time. Threads, and "
             "everything that goes wrong when two touch the same data.",
             builds="a server that serves many at once",
             breaks="it forgets everything the moment it stops"),

    # ---- Part five ------------------------------------------------------
    Chapter(15, "15-where-the-data-lives",
             "Where the data lives", 5,
             "Files on disk, why that stops working, and what a database "
             "actually is, down to the language it speaks.",
             builds="memory that survives the process",
             breaks="a working system is where the hard part begins"),
    Chapter(16, "16-what-makes-real-systems-hard",
             "What makes real systems hard", 5,
             "Take the working system and apply pressure. Each fix names "
             "itself: caching, queues, workers, containers, deployment.",
             builds="a system that stays up under load",
             breaks="every fix here still assumes one machine"),
    Chapter(17, "17-more-than-one-machine",
             "More than one machine", 5,
             "What becomes impossible with more than one computer: unreliable "
             "networks, clocks that disagree, the cost of agreement.",
             builds="a system spread across machines",
             breaks="the newest, loudest part is still unexplained"),
    Chapter(18, "18-ai-systems-are-the-same-systems",
             "AI systems are the same systems", 5,
             "Training is a process, inference is a server. Walk the whole "
             "stack again with the AI names attached.",
             builds="the AI stack, recognised",
             breaks=""),
]

BY_NUM = {c.num: c for c in CHAPTERS}
BY_NUM[0] = FRONT
BY_SLUG = {c.slug: c for c in CHAPTERS}


def part_chapters(part: int) -> list:
    return [c for c in CHAPTERS if c.part == part]
