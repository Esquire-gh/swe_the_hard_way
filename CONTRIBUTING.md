# Contributing

The most useful contribution is telling us where you got lost.

If a chapter introduced something without explaining it, if a listing did not
run, or if you had to look something up elsewhere to keep going, open an issue
and say exactly where. That is a bug in the tutorial, and it is the kind we
most want to hear about.

If you want to send a change, read `docs/STYLE.md` first. The writing rules are
strict on purpose, and a pull request that reads differently from the rest of
the book will be sent back even if the content is correct.

Before opening a pull request, run the checker and make sure it passes:

    python3 scripts/check.py

Any code you add must live under `code/` as a runnable file and must actually
run.
