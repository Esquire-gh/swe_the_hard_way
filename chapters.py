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
    2: "Part two · the machines get connected",
    3: "Part three · the conversation",
    4: "Part four · building the server",
    5: "Part five · more users, more machines",
}


class Chapter:
    def __init__(self, num, slug, title, part, desc, *, builds="", breaks=""):
        self.num = num          # 0 is the front page
        self.slug = slug        # matches code/<slug>/ and site/chapters/<slug>.html
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


FRONT = Chapter(0, "index", "Introduction", 0,
                "What software engineering is underneath the tools, taught by "
                "building one web server all the way down.")

CHAPTERS = [
    # ---- Part one -------------------------------------------------------
    Chapter(1, "01-computers-programs-and-programming",
            "Computers, programs, and programming", 1,
            "The usual definition of programming taken apart on one computer: "
            "what a program is on disk, what changes when it runs, and who is "
            "in charge of the difference.",
            builds="a process on one machine",
            breaks="one machine cannot reach another"),

    # ---- Part two -------------------------------------------------------
    Chapter(2, "02-computer-networks",
            "Computer networks", 2,
            "Why moving bytes between machines needed packet switching and "
            "layered protocols, and why that design was inevitable.",
            builds="bytes moving between two machines",
            breaks="bytes arrive with no meaning attached"),
    Chapter(3, "03-the-web",
            "The web", 2,
            "The internet moves bytes; the web is one agreement about what "
            "they mean. Why it arrived late and won anyway.",
            builds="documents anyone can link to and read",
            breaks="you still cannot say where a document lives"),
    Chapter(4, "04-what-is-a-website",
            "What is a website?", 2,
            "Where a page physically lives, how machines are found by address, "
            "and how a name people remember becomes one.",
            builds="a way to find the machine that holds the file",
            breaks="knowing where it is does not say who hands it over"),

    # ---- Part three -----------------------------------------------------
    Chapter(5, "05-clients-and-servers",
            "Clients and servers", 3,
            "Who asks and who answers. Why it is a role and not a kind of "
            "machine, and why your laptop is both.",
            builds="the two roles in every exchange",
            breaks="the roles do not say what they send each other"),
    Chapter(6, "06-requests-and-responses",
            "Requests and responses", 3,
            "A real HTTP request and response read line by line, until the "
            "format holds no mystery.",
            builds="the exact bytes of a request and a response",
            breaks="something has to write, send, and draw that text"),
    Chapter(7, "07-web-browsers",
            "Web browsers", 3,
            "Sending the text by hand, and what a browser adds: writing it, "
            "drawing it, and agreeing with every other browser.",
            builds="the side that asks, understood fully",
            breaks="now look at the side that answers"),

    # ---- Part four ------------------------------------------------------
    Chapter(8, "08-web-servers",
            "Web servers", 4,
            "A server is a program that never stops: wait, read, answer, "
            "close, wait again. What the waiting actually is.",
            builds="the loop every server runs",
            breaks="waiting needs something only the OS can give"),
    Chapter(9, "09-socket-programming",
            "Socket programming and the Linux socket API", 4,
            "The operating system owns the network card, so it hands programs a "
            "handle that behaves like a file.",
            builds="the handle a program holds the network by",
            breaks="a handle is an idea until you use it"),
    Chapter(10, "10-building-a-static-web-server",
             "Building a static web server", 4,
             "Twenty lines a browser will talk to, then a folder of files: the "
             "request path maps to a file path, and 404 when it does not.",
             builds="a working static web server, by hand",
             breaks="every visitor gets the same bytes"),
    Chapter(11, "11-building-a-dynamic-web-server",
             "Building a dynamic web server", 4,
             "Static becomes dynamic: run code per request. Routing, forms, "
             "query strings, sessions, escaping, all by hand.",
             builds="pages generated per visitor, by hand",
             breaks="two programs, and one word for both"),
    Chapter(12, "12-servers-as-hardware-and-software",
             "Servers as hardware and software", 4,
             "A machine and a program share the word, and so do the file "
             "server and the application server you just wrote.",
             builds="a name for each thing called a server",
             breaks="it still answers one visitor at a time"),

    # ---- Part five ------------------------------------------------------
    Chapter(13, "13-handling-multiple-users-at-once",
             "Handling multiple users at once", 5,
             "The hand written server does one thing at a time. Threads, and "
             "everything that goes wrong when two touch the same data.",
             builds="a server that serves many at once",
             breaks="it forgets everything the moment it stops"),
    Chapter(14, "14-introducing-databases",
             "Introducing databases", 5,
             "Files on disk, why that stops working, and what a database "
             "actually is, down to the language it speaks.",
             builds="memory that survives the process",
             breaks="a working system is where the hard part begins"),
    Chapter(15, "15-scaling-web-applications",
             "Scaling web applications", 5,
             "Ten thousand users and a bigger application. Each pressure "
             "forces a component: cache, queue, supervisor, proxy, logs.",
             builds="a system that stays up under load",
             breaks="every piece of it was written by hand"),
    Chapter(16, "16-introducing-web-frameworks",
             "Introducing web frameworks", 5,
             "Everything you wrote by hand, standing behind one install "
             "command. Line by line against what it replaces.",
             builds="the same system, without the tedium",
             breaks="it all still runs on one machine"),
    Chapter(17, "17-introduction-to-distributed-systems",
             "Introduction to distributed systems", 5,
             "Spreading the system across machines for load, for data, and "
             "by capability, and what stops being true when you do.",
             builds="a system spread across machines",
             breaks="the newest, loudest part is still unexplained"),
    Chapter(18, "18-ai-systems-are-still-software",
             "AI systems are still software", 5,
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
