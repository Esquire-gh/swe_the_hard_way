# How to write this course

This file is the writing contract. Every page follows it. If a sentence in
this repository breaks one of these rules, the sentence is wrong, not the
rule.

The course is a built static site. The prose lives as HTML bodies under
`content/`, the build wraps each one in the shared shell, and the output under
`site/` is committed and published. The mechanical rules below are enforced by
`scripts/check.py` against both the sources and the built pages, and a rule a
machine can check is worth more than a rule that needs a judgement call every
time.

## Who it is written for

Somebody who has followed tutorials, built the todo app or the Netflix clone,
and cannot build their own thing, because the fundamentals underneath every
tutorial were never explained. Write from that reader's side. The hard way
means doing the things tutorials let you skip, and the point of every page is
that the reader ends with an intuition they can build the next idea on.

Say "course", not "tutorial". Say "from the ground up", never "from the floor
up".

## Voice

Write the way a person speaks when they are explaining something to a friend
who is smart but has not seen this before. Calm, direct, unhurried.

Use full sentences that connect to each other and carry the reader forward. A
sentence should be able to stand on its own and be read out loud without
sounding like notes. Do not write in fragments for effect. "Same bytes. Same
disk. Different answer." reads as clever to the writer and as confusion to the
person trying to learn.

Prefer short words. Prefer short sentences. If a sentence has more than about
twenty five words, it is usually two sentences pretending to be one.

Say what a thing is before you say what it does. Say what it does before you
say how to use it.

Prose must flow. A page that reads as a list of facts joined by chapter
numbers is a port, not a chapter. Rewrite it.

## Terms

Never use a technical term before you have explained it, unless it is a term
any working programmer already knows. Explain the idea in plain words first,
then name it, and mark the name with `<span class="term">`. The name comes
last because the name is the least useful part, and it must always come,
because the reader has to be able to map what they learned here onto what
everybody else calls it. A chapter about who asks and who answers must say
"client server model" on the page.

A chapter title names its topic plainly, the way a table of contents would,
so that reading the titles alone gives a fair idea of what each chapter
covers. The story is told in the content, not in the title.

## Punctuation and formatting

Do not use em dashes or en dashes. Not once. Use a full stop, a comma, or a
pair of brackets instead.

Do not use semicolons in prose. Split the sentence.

Do not use exclamation marks. Do not use emoji.

Bold is for the lead of a paragraph in a line by line comparison, and nothing
else. Terms are marked with `.term`, not bold.

Headings are sentence case. Write `How a socket works`, not `How A Socket
Works`. A heading says what the reader is about to learn, in the words the
reader would use.

Keep the heading depth shallow. A chapter has its `h1` and `h2` sections, and
nothing deeper.

Wrap prose at eighty visible characters in `content/*.html`. Tags and build
tokens do not count, and `<pre>` blocks are exempt. `scripts/reflow.py` does
the wrapping without touching tokens or preformatted text.

## Words that are banned

Two groups of words are banned outright, and the checker looks for both.

The first group tells the reader that something is easy: `simply`,
`obviously`, `of course`, `clearly`, `merely`, `trivially`, `just a matter
of`, `needless to say`. A word that says a thing is easy does nothing for the
reader who found it easy, and makes the reader who is stuck feel worse.

The second group promises more than the sentence delivers: `powerful`,
`blazing`, `game changing`, `superpower`, `magical`, `seamless`, `effortless`,
`revolutionary`. If a thing is worth using, say what it does and let the
reader decide how impressed to be.

## Things not to write

No filler openers. Begin with the thing itself.

No apologising for the topic. If the explanation is good, the reassurance is
not needed.

No forward references that go unpaid. If a page says something will be
explained later, it must be explained later, in a named chapter.

No lists where prose would do. A list is for things that are genuinely a set.
An argument is prose.

## Structure of a chapter

Every chapter has the same five movements, and the components of the site
exist to carry them.

First, the question, in the `.hook` paragraph. State the thing the previous
chapter left unresolved. The reader should recognise it as a question they
were already holding.

Second, the story. Explain the idea in plain language with no code. If the
idea exists because of a historical problem, say what the problem was and who
had it.

Third, the thing itself. Code, included from the real file with a
`{{ code: }}` token so the prose and the listing cannot drift. Terminal
output in a `.term-block`. A diagram with `{{ diagram: }}` where a picture
beats a paragraph, and nowhere else.

Fourth, the check, in a `.check` box. Something the reader runs or inspects
where the result would be surprising if they had misunderstood. Not a quiz.

Fifth, the next question, in the `.limit` block. End by breaking what was
just built. The `.to` paragraph names the next chapter.

A `.puzzle` box is for the moment two facts genuinely collide, and it asks the
question in bold before the page answers it. Use one only where the collision
is real. History and narrative chapters do not get one.

Two colours carry meaning. Indigo is the thing you built and it works. Magenta
is the limit, the break, the bug. Do not use them for anything else.

The order of the first three movements is the rule that matters most. A reader
should never meet a command before they know what it is a command about.

Tools confirm understanding, they do not supply it. A hex dump or a process
listing checks that what the reader was told is true. It is not where the
understanding comes from.

## Code in the course

Code should be short enough to type by hand. If a listing runs past about
forty lines, include a slice of it with `{{ code:path#MARK }}` between
`# BEGIN MARK` and `# END MARK` comments, and say which file it came from.

Prefer the standard library. Nothing is installed until a chapter has argued
for why the thing being installed needs to exist.

Every listing lives as a real runnable file under `code/`. Show the output,
and only output that was produced by running the file. Where a number depends
on the reader's machine, say so on the spot.

Comment sparingly and only to say why, never what.

## Resources

Each chapter ends with a short curated list of videos and courses from
`resources.py`, with one sentence per entry saying why this chapter sends the
reader there. Every link was checked to resolve to the named thing and to be
on the chapter's topic. A resource that is merely related is not listed.

## The test to apply to a finished chapter

Does it build a picture of what the thing is, in the reader's head, before any
code appears. Does it show what a real implementation looks like. Does the
question it opens with match the limit the previous chapter closed on. Does
it name the technical term for every idea it teaches. Does it meet the rules
above. If any answer is no, the chapter gets rewritten.

## The mechanical checks

Run from the repository root before every commit, and expect both to pass.

    python3 build.py
    python3 scripts/check.py

The checker reports em and en dashes, the banned words, visible prose lines
over eighty characters, headings that have slipped into title case, links
that point at nothing, build tokens that did not resolve, and paths under
`code/` that are named but do not exist on disk.
