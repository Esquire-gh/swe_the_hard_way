"""Curated outside resources, one pool and a per-chapter mapping.

Every entry here was checked: the id resolves to the named video, and the video
is on the chapter's topic. The pool is drawn from CS 361 Systems Programming
(Chris Kanich), Crash Course Computer Science, a handful of standalone videos,
two Udacity courses, and, for the last chapter, Karpathy. Only what earns its
place is listed against a chapter; the rest of a source is not padding.

A resource is a small record. The per-chapter list adds the one thing the pool
cannot know: why this chapter sends you here, and where in the video to start.
"""
from __future__ import annotations


def yt(vid: str, t: int = 0) -> str:
    base = f"https://www.youtube.com/watch?v={vid}"
    return f"{base}&t={t}s" if t else base


class Resource:
    def __init__(self, key, kind, title, author, url):
        self.key = key
        self.kind = kind        # "video" | "series" | "course"
        self.title = title
        self.author = author
        self.url = url


def _v(key, vid, title, author):
    return Resource(key, "video", title, author, yt(vid))


# --------------------------------------------------------------------------
# the pool
# --------------------------------------------------------------------------

RESOURCES = {r.key: r for r in [
    # CS 361 Systems Programming — Chris Kanich
    _v("k-processes", "WkuKhLYtUHw", "Introduction to processes in Linux", "Chris Kanich · CS 361"),
    _v("k-file", "UJBr211etS4", "The file abstraction in Linux", "Chris Kanich · CS 361"),
    _v("k-fd", "rW_NV6rf0rM", "What's behind a file descriptor (and dup2)", "Chris Kanich · CS 361"),
    _v("k-net1", "rdvfHWA9efU", "A system-design approach to the Internet", "Chris Kanich · CS 361"),
    _v("k-net2", "Fzdx222mBng", "Making the Internet work by breaking it into smaller problems", "Chris Kanich · CS 361"),
    _v("k-net3", "LfiRKZze0HM", "The one trick that keeps the whole Internet from exploding", "Chris Kanich · CS 361"),
    _v("k-net4", "RJ_JV3Y-rhc", "Why the Internet beats the phone network", "Chris Kanich · CS 361"),
    _v("k-socket", "XXfdzwEsxFk", "The Linux socket API explained", "Chris Kanich · CS 361"),
    _v("k-www", "zXqblbDLGf0", "A systems programmer's introduction to the world wide web", "Chris Kanich · CS 361"),
    _v("k-conc1", "YKGa8NCJhZs", "Concurrency: what's good about it, what's hard about it", "Chris Kanich · CS 361"),
    _v("k-conc-ptio", "85T_ZaT8EUI", "Processes, threads, and I/O multiplexing", "Chris Kanich · CS 361"),
    _v("k-conc2", "LDPUWGLjHIg", "Concurrency: the cause of, and solution to, lots of problems", "Chris Kanich · CS 361"),
    _v("k-tool", "syecJXuC80I", "The right tool: when to use processes, when to use threads", "Chris Kanich · CS 361"),
    _v("k-mux", "oD94jnuOHLM", "Why I/O multiplexing works well for web servers", "Chris Kanich · CS 361"),
    _v("k-rwlock", "7zI_4CKk-3Y", "Read-write locks and bounded buffers", "Chris Kanich · CS 361"),
    _v("k-safety", "6Y0NF85cUvk", "Thread safety in two minutes", "Chris Kanich · CS 361"),
    _v("k-race", "K-XlKZ9g0zo", "Race conditions in two minutes", "Chris Kanich · CS 361"),
    _v("k-deadlock", "oEbXlSH8hyE", "Deadlock in three minutes", "Chris Kanich · CS 361"),

    # Crash Course Computer Science
    _v("cc-early", "O5nskjZ_GoI", "Early computing (Crash Course #1)", "Crash Course CS"),
    _v("cc-binary", "1GSjbWt0c9M", "Representing numbers and letters with binary (Crash Course #4)", "Crash Course CS"),
    _v("cc-cpu", "FZGugFqdr60", "The central processing unit (Crash Course #7)", "Crash Course CS"),
    _v("cc-instr", "zltgXvg6r3k", "Instructions and programs (Crash Course #8)", "Crash Course CS"),
    _v("cc-os", "26QPDBe-NB8", "Operating systems (Crash Course #18)", "Crash Course CS"),
    _v("cc-mem", "TQCr9RV7twk", "Memory and storage (Crash Course #19)", "Crash Course CS"),
    _v("cc-files", "KN8YgJnShPM", "Files and file systems (Crash Course #20)", "Crash Course CS"),
    _v("cc-net", "3QhU9jd03a0", "Computer networks (Crash Course #28)", "Crash Course CS"),
    _v("cc-internet", "AEaKrq3SpW8", "The Internet (Crash Course #29)", "Crash Course CS"),
    _v("cc-web", "guvsH5OFizE", "The world wide web (Crash Course #30)", "Crash Course CS"),
    _v("cc-security", "bPVaOlJ6ln0", "Cybersecurity (Crash Course #31)", "Crash Course CS"),
    _v("cc-ml", "z-EtmaFJieY", "Machine learning and AI (Crash Course #34)", "Crash Course CS"),

    # Standalone videos the author uses
    _v("f-readcode", "QXjU9qTsYCc", "How do computers read code?", "Frame of Essence"),
    _v("b-1s0s", "Xpk67YzOn5w", "Why do computers use 1s and 0s? Binary and transistors", "Basics Explained"),
    _v("m-binary", "c8bIpDjkN0s", "How computers turn binary into video, audio and text", "Marco A"),
    _v("cp-unicode", "MijmeoH9LT4", "Characters, symbols and the Unicode miracle", "Computerphile"),
    _v("ac-web", "hJHvdBlSxug", "How the web works, the big picture", "Academind"),
    _v("lc-web1", "e4S8zfLdLgQ", "How the Internet works for developers, part 1", "LearnCode.academy"),
    _v("lc-web2", "FTAPjr7vgxE", "How the Internet works for developers, part 2: servers and scaling", "LearnCode.academy"),
    _v("az-browser", "DuSURHrZG6I", "How a web browser builds and displays a page", "Al Zimmerman"),
    _v("js-browser", "0IsQqJ7pwhw", "How browsers work", "Kruno, JSUnconf"),
    _v("cs50-internet", "n_KghQP86Sw", "The Internet (CS50 Understanding Technology)", "CS50"),
    _v("cs50-web", "U6hkOAnFJxM", "Web development (CS50 Understanding Technology)", "CS50"),

    # Courses
    Resource("ud-clientserver", "course", "Client-server communication",
             "Udacity (free)", "https://www.udacity.com/course/client-server-communication--ud897"),
    Resource("ud-networking", "course", "Networking for web developers",
             "Udacity (free)", "https://www.udacity.com/course/networking-for-web-developers--ud256"),
]}


# --------------------------------------------------------------------------
# per-chapter mapping: (resource key, why this chapter sends you here, start s)
# --------------------------------------------------------------------------

BY_CHAPTER = {
    1: [
        ("k-processes", "Kanich builds the exact picture this chapter does, a "
                        "process as the operating system's bookkeeping around a "
                        "running program, from the systems side.", 0),
        ("cc-instr", "The fetch, decode, execute loop this chapter's little "
                     "machine acts out, drawn on real hardware.", 0),
        ("f-readcode", "A calm animation of the same gap: how the text you wrote "
                       "turns into instructions a processor runs.", 0),
        ("cc-os", "The turn-taking that let one machine feel like it runs "
                  "everything at once, which the timing check measures.", 0),
    ],
    2: [
        ("k-net1", "Kanich derives the network the way this chapter does, as a "
                   "design that had to come out the way it did, not a list of "
                   "acronyms.", 0),
        ("k-net4", "Why packet switching beat the circuit-switched phone "
                   "network, the argument this chapter's history rests on.", 0),
        ("cc-net", "The same packet-switching idea in ten minutes, with "
                   "pictures.", 0),
        ("cs50-internet", "A gentler tour of the same ground if the history "
                          "moved fast.", 0),
    ],
    10: [
        ("k-socket", "The socket calls this chapter uses, explained from the "
                     "operating system's side by someone who teaches them for a "
                     "living.", 0),
        ("k-www", "A systems programmer wiring up the web by hand, which is "
                  "exactly what this chapter has you do.", 0),
        ("cc-security", "Path traversal is one of the oldest of the mistakes "
                        "this chapter has you make and then fix.", 0),
    ],
}


def for_chapter(num: int) -> list:
    """(Resource, note, t) triples for a chapter, in display order."""
    out = []
    for key, note, t in BY_CHAPTER.get(num, []):
        r = RESOURCES[key]
        out.append((r, note, t))
    return out


def all_by_chapter() -> list:
    """(chapter_num, [(Resource, note, t), ...]) for the further-watching page."""
    return [(n, for_chapter(n)) for n in sorted(BY_CHAPTER)]
