# Chapter 15. Where the data lives

## Where things go when the process stops

Chapters 13 and 14 both ended in the same place. Everything the guestbook knows
is in the memory of one process, and chapter 1 said what happens to that when
the process ends. Press control C and the messages are gone and everybody is
logged out.

Chapter 14 added a second reason to care. That same memory is now touched by
many threads at once, so keeping it correct depends on a lock being right at
every place it is used, in every piece of code anybody writes later.

So the data needs to be somewhere that outlives the process and that already
knows what to do when several people touch the same thing. This chapter is
about why that place is not a file, told by trying a file first.

## The obvious answer, and it works

Chapter 1 said a file is a named stretch of bytes on a disk and that nothing is
happening inside it while nobody is looking. That inertness is the property we
want. Write the messages into a file and they are still there tomorrow.

The file is
[`code/15-where-the-data-lives/to_a_file.py`](../code/15-where-the-data-lives/to_a_file.py).

```python
def load():
    """Every message written so far, or none if there is no file yet."""
    if not BOOK.exists():
        return []
    return json.loads(BOOK.read_text())


def add(who, text):
    messages = load()
    messages.append({"who": who, "text": text})
    BOOK.write_text(json.dumps(messages))
```

```
$ python3 to_a_file.py
the file is 69 bytes
  Ada: first
  Grace: second

$ python3 to_a_file.py
the file is 138 bytes
  Ada: first
  Grace: second
  Ada: first
  Grace: second
```

The second run found what the first run left. That is persistence, in eleven
lines, and for a program with one user it is a perfectly good answer. A great
deal of working software stores its data exactly like this and is right to.

Notice the shape of `add`, because everything that follows is about it. Read the
whole book. Change it. Write the whole book back.

## What it costs the moment anybody else is there

Chapter 14 ran four threads against a shared number. Run the same four threads
against this file. The file is
[`code/15-where-the-data-lives/lost_and_truncated.py`](../code/15-where-the-data-lives/lost_and_truncated.py).

```
$ python3 lost_and_truncated.py
messages the program tried to write: 200
times a reader found the file half written: 175
the finished file is not valid at all: Extra data: line 1 column 375 (char 374)

the file is 375 bytes
interrupted: the machine lost power here
the file is now 0 bytes
```

Your numbers will differ, and the three failures will not.

A reader can see a file that is neither the old contents nor the new one. A
hundred and seventy five attempts out of two hundred opened the file while
somebody else was partway through writing it, and got something that was not
valid at all. In this program those attempts gave up. In a web server they are
an error page for a visitor who did nothing wrong.

The file that survives is broken. Two writers wrote over each other and the
result is not a list of messages any more. It is not that some messages were
lost, which would be bad enough. The file cannot be read.

And a write can be interrupted. Opening a file for writing empties it first,
before a single byte of the new content is written, so there is a moment when
everything is gone and nothing has replaced it. A power cut at that instant does
not lose the last message. It loses the guestbook.

There is a third cost, and it is the one you meet on a good day rather than a
bad one. The file is
[`code/15-where-the-data-lives/scanning.py`](../code/15-where-the-data-lives/scanning.py),
and it looks for one record among many.

```
$ python3 scanning.py
    10000 records    file      6.4 ms    database   0.059 ms
   100000 records    file     65.6 ms    database   0.073 ms
  1000000 records    file    648.1 ms    database   0.089 ms
```

Ten times the records, ten times the time, because finding the last record
means reading every record before it. The right hand column barely moves.
Whatever the database is doing, it is not looking at a million things to find
one, and the difference between the columns is a hundred and one thousand and
then seven thousand.

## Everything you would build next already exists

The useful exercise here is not to be told the answer. It is to work out what
you would do about each of those, because the answers are not out of reach.

For readers seeing half written files, stop writing in place. Write the new
version to a second file, then rename it over the old one. A rename is one
operation that the filesystem either does or does not do, so a reader sees the
old file or the new one and never a mixture.

For two writers overwriting each other, take a lock. The writers may be
separate processes rather than threads, so it has to be a lock in the
filesystem that any process can see, and now you have to decide what happens
when the process holding it dies without releasing it.

For rewriting the whole file on every message, stop doing that too. Append only
what changed and work out the current state by replaying the changes. That is
faster to write and slower to read, so eventually you need something that folds
the accumulated changes back into a compact form, in the background, without
stopping the writers.

For the scanning, keep a second file mapping each id to a position in the first
one, arranged so it can be searched without being read end to end. Then keep it
correct on every single write, including the ones that fail halfway.

For the day you add a field, put a version number in every record and write
code that understands the old shapes.

Every one of those is reasonable and none of them is exotic. Together they are
a **database**. That is what the word means. It is a program that keeps records
on a disk in a layout designed around exactly these problems, and it has been
attacked by more people over more years than your version ever will be.

## A language for saying one kind of thing

Some languages are built to express anything at all. Python is one of those,
and so is every language you would call a programming language.

Others are built to say one narrow kind of thing extremely well, and nothing
else whatsoever. You have met three already in this tutorial. The HTML in
chapter 6 says what a document is made of and cannot add two numbers. The
template syntax in chapter 13 says how to fill values into a page. A language
shaped around one subject rather than around general computation is called a
**domain specific language**.

Databases are driven by one, and it is called **SQL**.

The property that matters about it is easy to miss. You say what you want, and
not how to get it.

```sql
SELECT who, text FROM messages WHERE id = 5
```

Nothing in that says whether to use an index or read every row. The database
decides, and it decides differently as the table grows, without the sentence
changing. Compare that with the file version, where the how is code you wrote
and it will be scanning the whole file until somebody rewrites it.

## The guestbook, kept properly

The file is
[`code/15-where-the-data-lives/guestbook_db.py`](../code/15-where-the-data-lives/guestbook_db.py).
It uses `sqlite3`, which is in Python's standard library, so this chapter
installs nothing.

```python
setup.execute("""
    CREATE TABLE messages (
        id    INTEGER PRIMARY KEY,
        who   TEXT NOT NULL,
        text  TEXT NOT NULL
    )
""")
setup.execute("CREATE INDEX messages_by_who ON messages (who)")
setup.commit()


def writer(number):
    database = connect()
    for line in range(EACH):
        database.execute("INSERT INTO messages (who, text) VALUES (?, ?)",
                         (f"writer {number}", str(line)))
        database.commit()
    database.close()
```

That is the same test as before. Four threads, fifty messages each.

```
$ python3 guestbook_db.py
messages the program tried to write: 200
messages actually stored: 200

two of them, newest first:
  writer 2: 49
  writer 2: 48
```

Two hundred out of two hundred, and you did not write a lock. Making concurrent
writers correct is the database's job, and it is the same job chapter 14 handed
to you, done once by people who spent years on nothing else.

Three things in that listing are carrying more weight than they look.

The `CREATE TABLE` writes the shape down and then enforces it. `NOT NULL` means
a message with no author cannot be stored. In the JSON file, nothing stopped
one, and you would discover it when a page failed to render for one visitor.

The `CREATE INDEX` is the second structure from the previous section, kept
correct on every write by somebody else. It is not free: it takes space, and it
makes writes slower, because each write has to update it too. An index on every
column is a common and expensive mistake.

The `commit` marks the end of a **transaction**, which is a group of changes
that either all happen or none of them do. That is the answer to the truncated
file, applied at every level. The properties usually quoted are that a
transaction is all or nothing, that it leaves the data valid, that concurrent
transactions never see each other half finished, and that once it says yes a
power cut cannot undo it. Their initials spell **ACID**, which is why you see
the word.

## The third time this bug has appeared

The end of that program does one more thing. It takes a name that a stranger
might have typed and uses it two different ways.

```python
pretend_name = "writer 1' OR '1'='1"
unsafe = setup.execute(
    f"SELECT count(*) FROM messages WHERE who = '{pretend_name}'").fetchone()[0]
safe = setup.execute(
    "SELECT count(*) FROM messages WHERE who = ?", (pretend_name,)).fetchone()[0]
```

```
pasted into the query: 200 rows
passed as a value:     0 rows
```

The first one returned every message in the table. The quote in the middle of
that name closed the string the query was building, and the rest of it became
part of the question. There is no such author, and there did not need to be.

This is **SQL injection**, and it is the third appearance of one mistake. In
chapter 10, a path from a stranger was joined onto a directory and read a file
outside the site. In chapter 12, a name from a stranger was put into a page and
became a script. Here, a name from a stranger is pasted into a query and becomes
part of the query.

Every one is the same sentence: text that came from outside was placed
somewhere the program keeps its own instructions. Every fix is the same shape
too. Do not build the instruction out of the text. Leave a slot in the
instruction and hand the text over as a value, which is what the `?` is doing.

## The server in front, and why it is there

One thing here is not like a real deployment, and it is worth being straight
about it.

`sqlite3` is a library. Your process opens the file and reads it directly, and
there is no other program involved, which is why this chapter installed
nothing. That is a genuine database by every part of the definition above
except one.

The usual arrangement is a separate program that owns the files and lets nobody
else near them. Your program connects to it over a socket, exactly as chapter 9
described, on its own port, speaking its own protocol which is not HTTP.
Postgres does this on port 5432, MySQL on 3306. Everything from chapter 5
applies unchanged: the database server was started first, it waits, and your
application is the client.

The reason for the extra program is chapter 17 arriving early. When your
application runs on eight machines, they cannot all open the same file on the
same disk. They can all connect to one program.

So the sentence is now complete. A database is a program that stores data on a
disk, usually with a server in front of it speaking its own protocol, driven by
a language built for one purpose. SQLite is the same thing with the server left
out.

## Check it yourself: ask the database what it plans to do

The claim that SQL says what rather than how is checkable, because you can ask
what it decided. The file is
[`code/15-where-the-data-lives/plan.py`](../code/15-where-the-data-lives/plan.py).

```
$ python3 plan.py
with no index on who:
    SCAN messages

after adding one:
    SEARCH messages USING INDEX messages_by_who (who=?)
```

The question was identical in both cases. The only thing that changed was that
a second structure appeared on the disk, and the database noticed and changed
its mind. `SCAN` is the file version from earlier in this chapter, reading
everything. `SEARCH` is the fast column in that table.

That is the payoff for saying what rather than how. Nobody edited a query, and
the program got faster.

## Now make it popular

Here is what exists now. A server that answers many people at once, running
your code for each of them, with data that survives the process being stopped,
kept correct while several visitors write at the same moment.

That is a working system, and everything before this point has been about
making it work at all. Everything after it is about a different problem, which
is that it works and then a lot of people arrive.

That problem is not one thing. The machine runs out of room for visitors. Some
piece of work takes longer than anybody is willing to wait in front of a blank
page. The same expensive answer gets computed thousands of times a second for
thousands of people who would all accept the same one. Putting a new version of
the code on the machine means stopping the old one, and stopping it means the
site is down.

Each of those has an answer, each answer is a word you have heard, and the
words are much easier to remember when you have first felt the thing they fix.

---

[Previous chapter](./14-two-people-at-once.md) | [Next chapter](./16-what-makes-real-systems-hard.md)
