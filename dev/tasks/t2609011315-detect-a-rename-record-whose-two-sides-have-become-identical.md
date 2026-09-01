---
title: Detect a rename record whose two sides have become identical
type: todo-item
status: backlog
effort: 2
area: config / gates
origin: R14 P6
queue: 2
created: 2026-09-01
updated: 2026-09-01
---

> [!note] Overview
> **What** — A check for a line that RECORDS a rename and whose two sides have
> become identical: `X -> X`. Split out of `t2608290620`, which gave the
> stale-spelling sweep its allowance classes; that note judged this "probably
> worth more than the allowance classes", and it is, but it is a different
> check with its own design rather than another class.
> **Why** — R14 produced this defect **six times**, which makes it the most
> reliable defect of the milestone: a blanket token rename rewriting the OLD
> side of a rename record. It hit `C-85`'s own mapping row, two board notes,
> `naming.md`'s ad-hoc-contraction sentence, and two columns of
> `rule-index.md`'s former-name table. Every one was caught by a test or by
> reading the diff — never by the sweep, which is the tool nominally
> responsible for exactly this.
> **Effort** — medium

## Why it is not another allowance class

The stale-spelling sweep asks "is this spelling dead". This asks "does this line
still say what it was written to say", and it fires on lines where BOTH sides
are live v2 spellings — invisible to a retired-key sweep by construction. It
also has the opposite polarity: the sweep's hits are mostly legitimate and need
excusing, while every `X -> X` is a defect.

`t2608290620` also surfaced the shape this has to avoid. The sweep matches a
key POSITION (`key:` in YAML, `"key"` in Python) because matching the bare token
produced 1371 hits. A rename-record detector has the same trap: it needs to
recognise the record FORMS the repo actually uses rather than any line with an
arrow in it.

## Known instances of the form

- `config/migrations/v1_to_v2.yml` — `old_path` / `new_path` pairs
- `dev/reference/naming.md` — prose "`X` is now `Y`" sentences
- `dev/reference/workflows/rule-index.md` — a former-name table with two columns
- `dev/scripts/semantic_tree_diff.py` — `COPIED_CONFIG_PATH_MAP`, keyed old -> new
- `--map old=new` arguments recorded in milestone records

## Progress

- [ ] Enumerate the record forms; decide which are mechanically recognisable
- [ ] Decide where it lives — a class inside the sweep, or its own script
- [ ] Falsify it against R14's six real instances, recovered from git history

## Links

- `dev/scripts/sweep_stale_spellings.py` — the sibling gate, and the model for
  position-sensitive matching with declared allowance classes
- `dev/milestones/r14/config-shape-gate5.md` — the milestone whose six
  instances motivate this
