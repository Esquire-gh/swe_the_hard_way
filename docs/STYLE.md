# How to write this tutorial

This file is the writing contract. Every chapter follows it. If a sentence in
this repository breaks one of these rules, the sentence is wrong, not the rule.

Before writing anything, read the sibling repository at
`../beyond_rag`. That repository is the reference for both layout and voice.
Where this file and `beyond_rag` disagree, `beyond_rag` wins, and this file
should be updated to match it.

## Voice

Write the way a person speaks when they are explaining something to a friend
who is smart but has not seen this before. Calm, direct, unhurried.

Use full sentences. A sentence should be able to stand on its own and be read
out loud without sounding like notes.

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

Keep the heading depth shallow. A chapter needs `#` for its title and `##` for
its sections. Reach for `###` only when a section genuinely has parts.

Wrap prose at eighty characters so the raw markdown reads well in a terminal
and diffs stay small.

## Things not to write

No filler openers. Do not begin a section with "In this chapter we will
explore". Begin with the thing itself.

No hype. Nothing is powerful, blazing fast, game changing, or a superpower.

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

## Code in the tutorial

Code should be short enough to type by hand. If a listing runs past about forty
lines, it is doing too much and the chapter needs splitting.

Prefer the standard library. A reader should not install anything until a
chapter has argued for why the thing they would install needs to exist.

Every listing lives as a real runnable file under `code/`, and the chapter
includes it by path. The chapter text and the file must not drift apart.

Show the output. If a command prints something, show what it prints. A reader
who gets different output needs to know immediately.

Comment sparingly and only to say why, never what. The prose around the listing
is where the what belongs.

## Language

Use one language for the whole tutorial where possible, and use Python. It is
the language with the smallest gap between what you write and what you mean,
which matters when the point is the idea rather than the syntax. Where a point
genuinely needs a lower level view, drop to C for that one listing and say why.
