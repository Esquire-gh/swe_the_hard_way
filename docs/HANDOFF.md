# Instructions for writing this tutorial

This file is written for a coding agent picking up this repository with a fresh
context. Read it fully before touching anything.

## What is already decided

The structure is fixed. Eighteen chapters, five parts, mapped one to one
against the eighteen points in `BRIEF.md`. Do not renumber, merge, or drop
chapters without being asked. The chapter files already exist as stubs with a
brief inside each one.

The voice is fixed. `STYLE.md` is the contract. The single most important rule
is that no chapter may use a term the reader has not met, and no chapter may
introduce a tool before the reader has felt the problem the tool solves.

## Step zero, before writing a single word

Read the sibling repository at `../beyond_rag`.

That repository is an earlier tutorial by the same author and it is the
reference for both layout and voice. Look at how it organises files, how its
front page reads, how a chapter opens and closes, how code listings are
presented, and how long a typical paragraph is.

Then update `STYLE.md` in this repository so it matches what `beyond_rag`
actually does. Where `STYLE.md` and `beyond_rag` disagree, `beyond_rag` wins.
`STYLE.md` was written without access to it and is a best guess.

Also mirror the repository layout of `beyond_rag` where it makes sense. If it
puts chapters somewhere else, or names things differently, follow it rather
than the layout here.

## How to write a chapter

Work in order, chapter one first. Do not jump ahead. The whole design depends
on each chapter inheriting the exact question the previous one left open, and
you cannot know what that question sounds like until the previous chapter is
written.

For each chapter:

1. Read the stub's brief, and read the finished chapter before it.
2. Write the five movements in order. The question, the story, the thing
   itself, the check, the next question.
3. Write any code as a real file under `code/<chapter-slug>/`, run it, and
   confirm the output matches what the chapter claims.
4. Delete the stub brief and the horizontal rule above it.
5. Check the chapter against `STYLE.md`, particularly the punctuation rules.
6. Commit that one chapter on its own.

## Hard rules

No em dashes anywhere in the repository. Run the checker before every commit
and expect it to pass:

    python3 scripts/check.py

It checks for banned punctuation, over long lines, and links that point at
nothing. Add rules to it as the repository grows rather than checking by eye.

Every code listing shown in prose must exist on disk under `code/` and must
run. If you cannot run it, do not claim its output.

Prose wraps at eighty characters.

Headings are sentence case.

Nothing gets installed in the tutorial until a chapter has argued for it.
Python's standard library carries the reader through chapter twelve. FastAPI
arrives in chapter thirteen and not before. A database client arrives in
chapter fifteen and not before.

## Chapters that need extra care

Chapter 12 is deliberately uncomfortable. The reader is meant to find it
tedious, because chapter 13 only lands if the tedium was real. Do not make
chapter 12 easier out of kindness.

Chapter 13 must map every FastAPI feature back to a specific block of hand
written code from chapter 12. Side by side. If a framework feature cannot be
tied to something the reader already suffered through, cut it.

Chapter 16 must introduce every concept from a symptom, never from a
definition. Do not write a list of system design patterns. Apply pressure to
the working system and let each fix name itself.

Chapter 18 must not teach machine learning. It walks the existing stack again
with the AI names attached, and its whole job is to make the reader realise
they already understood it.

## Definition of done for the repository

A reader with no computer science background can start at the front page, read
straight through, type every listing, and finish able to explain what happens
between pressing enter in a browser and seeing a page, at every layer, without
hand waving.
