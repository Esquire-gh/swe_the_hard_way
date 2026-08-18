# How to write this tutorial

This file is the writing contract. Every chapter follows it. If a sentence in
this repository breaks one of these rules, the sentence is wrong, not the rule.

The sibling repository at `../beyond_rag` is an earlier tutorial by the same
author and it is the reference for voice. It has been read, and the rules it
holds itself to have been folded into this file. Its layout was not copied,
because it builds a static HTML site and this tutorial is meant to be read on
GitHub with no build step. So `beyond_rag` wins on voice, and this file wins on
layout.

One rule here is stricter than `beyond_rag`. That repository allows the rare em
dash where a comma genuinely cannot do the job. This one allows none at all,
because `scripts/check.py` enforces it, and a rule a machine can check is worth
more than a rule that needs a judgement call every time.

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

Never use a technical term before you have explained it, unless it is a term
that any working programmer would already know. When you do introduce a term,
explain it in plain language first and then name it. The name comes last,
because the name is the least useful part.

## Punctuation and formatting

Do not use em dashes. Not once. Use a full stop, a comma, or a pair of
brackets instead.

Do not use semicolons in prose. Split the sentence.

Do not use exclamation marks.

Do not use emoji.

Do not use bold to shout. Bold is for a term being defined, and nothing else.

Headings are sentence case, not title case. Write `## How a socket works`, not
`## How A Socket Works`.

A heading says what the reader is about to learn, in the words the reader would
use. It is not a hint, and it is not a joke. If a reader cannot tell from the
heading alone what the section teaches, rewrite the heading.

Keep the heading depth shallow. A chapter needs `#` for its title and `##` for
its sections. Reach for `###` only when a section genuinely has parts.

Wrap prose at eighty characters so the raw markdown reads well in a terminal
and diffs stay small.

## Words that are banned

Two groups of words are banned outright, and the checker looks for both.

The first group tells the reader that something is easy: `simply`, `obviously`,
`of course`, `clearly`, `merely`, `trivially`, `just a matter of`, `needless to
say`. A word that says a thing is easy does nothing for the reader who found it
easy, and makes the reader who is stuck feel worse. Delete it and the sentence
is always better.

The second group promises more than the sentence delivers: `powerful`,
`blazing`, `game changing`, `superpower`, `magical`, `seamless`, `effortless`,
`revolutionary`. If a thing is worth using, say what it does and let the reader
decide how impressed to be.

## Things not to write

No filler openers. Do not begin a section with "In this chapter we will
explore". Begin with the thing itself.

No apologising for the topic. Do not write that something is scary, hard, or
that the reader should not worry. If the explanation is good, the reassurance
is not needed.

No forward references that go unpaid. If you write that something will be
explained later, it must be explained later, in a named chapter.

No lists where prose would do. A list is for things that are genuinely a set,
like the five parts of an HTTP request. An argument is not a set, so an
argument is prose.

## Structure of a chapter

Every chapter has the same five movements.

First, the question. Open by stating the thing the previous chapter left
unresolved. One or two paragraphs. The reader should recognise the question as
one they were already holding.

Second, the story. Explain the idea in plain language with no code. If the idea
exists because of a historical problem, say what the problem was and who had
it. People remember reasons more easily than facts.

Third, the thing itself. Now show it. Code, a protocol dump, a diagram in text.
The reader should be able to type it themselves in a few minutes.

Fourth, the check. A small exercise or observation that proves the reader
understood. Not a quiz. Something they run or inspect, where the result would
be surprising if they had misunderstood.

Fifth, the next question. End by breaking what you just built. Show the limit
of the thing. That limit is the opening line of the next chapter.

The order of the first three movements is the rule that matters most. A reader
should never meet a command before they know what it is a command about. Name
the idea, say why it exists, and only then put something on the screen.

Tools confirm understanding, they do not supply it. A hex dump, a packet
capture, or a process listing is a way to check that what the reader was told
is true. It is not where the understanding comes from, and a reader who has
never opened one should not be sent to it for their first explanation.

## Code in the tutorial

Code should be short enough to type by hand. If a listing runs past about forty
lines, it is doing too much and the chapter needs splitting.

Prefer the standard library. A reader should not install anything until a
chapter has argued for why the thing they would install needs to exist.

Every listing lives as a real runnable file under `code/`, and the chapter
includes it by path. The chapter text and the file must not drift apart.

Show the output. If a command prints something, show what it prints. A reader
who gets different output needs to know immediately.

Where a number depends on the reader's machine, say so on the spot. What the
chapter claims is the shape of the result, not the digits.

Comment sparingly and only to say why, never what. The prose around the listing
is where the what belongs.

## Language

Use one language for the whole tutorial where possible, and use Python. It is
the language with the smallest gap between what you write and what you mean,
which matters when the point is the idea rather than the syntax. Where a point
genuinely needs a lower level view, drop to C for that one listing and say why.

## The test to apply to a finished chapter

Before a chapter is done, ask four questions of it.

Does it build a picture of what the thing is, in the reader's head, before any
code appears. Does it show what a real implementation of that thing looks like.
Does the question it opens with match the limit the previous chapter closed on.
Does it meet the rules above.

If the answer to any of them is no, the chapter gets rewritten.

## The mechanical checks

These are the rules a program enforces, not judgements of taste. Run them from
the repository root before every commit.

    python3 scripts/check.py

It reports em dashes and en dashes, prose lines over eighty characters,
headings that have slipped into title case, the banned words above, links that
point at nothing, and paths under `code/` that are named in prose but do not
exist on disk. Add rules to it as the repository grows rather than checking by
eye.
