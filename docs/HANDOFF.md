# Instructions for writing this tutorial

This file is written for a coding agent picking up this repository with a fresh
context. Read it fully before touching anything.

## Where the work stands

All eighteen chapters are written, and every listing named in a chapter exists
under `code/` and was run to produce the output that is printed. So this file
is now a record of the rules the tutorial was written against rather than a
plan for writing it.

Two things follow from that. Anything added later has to hold to the same
rules, because a chapter written to a different standard is worse than no
chapter. And anything edited has to keep the handoffs intact, since every
chapter opens on the limit the previous one closed with, and changing one
ending silently breaks the next opening.

## What is already decided

The structure is fixed. Eighteen chapters, five parts, mapped one to one
against the eighteen points in `BRIEF.md`. Do not renumber, merge, or drop
chapters without being asked. The chapter files already exist as stubs with a
brief inside each one.

The voice is fixed. `STYLE.md` is the contract. The single most important rule
is that no chapter may use a term the reader has not met, and no chapter may
introduce a tool before the reader has felt the problem the tool solves.

## Step zero, which is already done

The sibling repository at `../beyond_rag` has been read and `STYLE.md` has
been reconciled with it. You do not need to repeat this. What follows is the
record of what was decided, so nobody has to guess later.

Its voice rules were taken: full flowing sentences rather than fragments, no
words that tell the reader a thing is easy, no words that promise more than
the sentence delivers, headings that say what the reader is about to learn,
the concept explained before any command is typed, and tools used to confirm
understanding rather than to supply it. All of these now live in `STYLE.md`
and most of them are enforced by `scripts/check.py`.

Its layout was not taken. `beyond_rag` builds a static HTML site from source
content, and `BRIEF.md` requires this tutorial to be readable on GitHub with
no build step. So the chapters stay as markdown under `chapters/` with their
code under `code/`. On voice `beyond_rag` wins, on layout this repository
wins.

One rule here is deliberately stricter. `beyond_rag` allows the rare em dash.
This repository allows none, because the checker can enforce that and cannot
enforce a judgement call.

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
