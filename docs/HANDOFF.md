# Instructions for working on this course

This file is written for somebody, or some agent, picking up this repository
with a fresh context. Read it fully before touching anything.

## Where the work stands

The course is complete and published. An introduction and eighteen chapters
are authored as HTML bodies under `content/`, built into `site/` by
`build.py`, committed, and deployed to GitHub Pages on every push to `main`
by `.github/workflows/pages.yml`. Every listing named in a chapter exists
under `code/` and was run to produce the output printed beside it.

Anything added later has to hold to the same rules, because a chapter written
to a different standard is worse than no chapter. Anything edited has to keep
the handoffs intact, since every chapter opens on the limit the previous one
closed with, and changing one ending silently breaks the next opening.

## How the pieces fit

`chapters.py` is the spine. It lists the chapters in order with their slug,
title, part, one line description, and what each builds and breaks. All
navigation, the table of contents, and the part groupings are computed from
it, so nothing can drift.

`content/<slug>.html` is a chapter body. It uses the component vocabulary
described in `STYLE.md` and four tokens that the build replaces:

    {{ code:code/<slug>/f.py }}        the whole file, highlighted
    {{ code:code/<slug>/f.py#MARK }}   the slice between BEGIN and END MARK
    {{ diagram:name }}                     an inline SVG from diagrams.py
    {{ resources }}                        this chapter's cards from resources.py

`build.py` wraps each body in the shared shell (masthead, sidebar, previous
and next, progress toggle, copy buttons), resolves the tokens, and writes
`site/index.html`, `site/chapters/*.html` and `site/further-watching.html`.
Braces inside inlined non-Python code are entity encoded so a template's own
`{{ }}` is never mistaken for a token.

`diagrams.py` holds every diagram as a function registered with
`@diagram("name")`, drawn with the small helpers at the top of the file. Keep
a diagram under about 700 units wide, and keep caption text short, since the
page column is narrower than the drawing surface.

`resources.py` is the pool of checked videos and courses and the per chapter
mapping with a one sentence reason for each.

`code/<slug>/` holds the runnable files. Slices are marked with `# BEGIN x`
and `# END x` comments.

`site/` is committed output. Never edit it by hand. Rebuild it.

`site/assets/style.css` and `site/assets/site.js` are the design, copied
from the author's `beneath-the-pipeline` and relabelled. Change them only for
a reason that applies to the whole site.

## How to edit a chapter

1. Read the chapter before it and the chapter after it, so the handoffs stay
   true.
2. Edit `content/<slug>.html`, then run
   `python3 scripts/reflow.py content/<slug>.html` to wrap prose at eighty
   visible characters without touching tokens or preformatted blocks.
3. If code changes, change the file under `code/`, run it, and paste the real
   output into the chapter. Never claim output you did not see.
4. `python3 build.py && python3 scripts/check.py` and expect no problems.
5. Preview with `python3 -m http.server 8765 -d site` and open a browser.
6. Commit the content, the code, and the rebuilt `site/` together.

## How to add a diagram

Write a function in `diagrams.py`, register it with `@diagram("name")`, and
place `{{ diagram:name }}` inside a `<figure><div class="dgm">` with a
`<figcaption>`. Check it rendered without overflow or collisions before
committing. A throwaway page under `site/` that renders only the new
diagrams is the quickest way to look at several at once. Delete it before
committing.

## How to add a resource

Add the entry to the pool in `resources.py`, verify the link resolves to the
named thing, then add it to the chapter's list with the sentence that says
why this chapter sends the reader there. The further watching page is built
from the same data.

## Hard rules

No em dashes or en dashes anywhere. Run the build and the checker before
every commit and expect both to pass.

Every code listing shown in prose exists on disk under `code/` and runs.

Prose wraps at eighty visible characters. Headings are sentence case.

Every technical term is explained in plain words first, then named on the
page with `.term`. Say "course", not "tutorial". Say "from the ground up".

Nothing gets installed until a chapter has argued for it. The standard
library carries the reader through chapter fifteen. FastAPI arrives in
chapter sixteen and not before. The database in chapter fourteen is
`sqlite3` from the standard library, and the chapter says why a real
deployment has a server in front.

## Chapters that need extra care

Chapter 10 must say that a static server maps the request path to a file
path under a folder and answers 404 when the file is missing.

Chapter 11 is deliberately uncomfortable. The reader is meant to find it
tedious, because chapter sixteen only lands if the tedium was real.

Chapter 13 opens from chapter ten's one at a time limit, not from the
framework. The framework is not mentioned until chapter sixteen.

Chapter 15 introduces every component from a symptom, never from a
definition, and ends by counting what was written by hand.

Chapter 16 maps every framework feature to a specific block of hand written
code from chapter eleven. If a feature cannot be tied to something the reader
already suffered through, cut it. It also names what the framework quietly
handles and what it does not.

Chapter 17 opens with the three reasons a system spreads: load, data, and
capability, tied to chapter fifteen's components.

Chapter 18 must not teach machine learning. It walks the existing stack with
the AI names attached, and closes on the introduction's promise.

## Definition of done

A reader who has followed tutorials and cannot build their own thing can start
at the introduction, read straight through, type every listing, and finish
able to explain what happens between pressing enter in a browser and seeing a
page, at every layer, without hand waving, with the technical name for every
part.
