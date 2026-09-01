---
title: Build C-37, the declared-keys-reach-a-reader check, and make it fail closed
type: todo-item
status: backlog
effort: 2
area: config / gates
origin: R14 closure
queue: 2
created: 2026-09-01
updated: 2026-09-01
---

> [!note] Overview
> **What** — Build `C-37`: a mechanical "every declared config key reaches a
> reader" check, and make it **assert its ground truth is non-empty before it
> reports** (design D-14.5, `E5`). No such tool exists;
> `dev/scripts/sweep_stale_spellings.py` is its predecessor and answers a
> different question (retired SPELLINGS, not unread KEYS).
> **Why** — R14's design put `C-37` deliberately OUTSIDE the migration bundle
> (D-11.4, "everything except `C-37` and `C-83` lands in ONE bundle"), and no
> phase in the master brief's table picked it up afterwards, so it survived the
> milestone as residue. It is also the only remaining answer to design question
> P2 — R14 found the misplaced keys by hand and zero by machine, and a shape
> that does not make `C-37` feasible has not solved the problem with
> consequences.
> **Effort** — medium

## The fail-closed requirement is not decoration

R14's own re-measure demonstrated the failure mode once, live: its extraction
returned **zero** keys, and it then reported MORE flags while knowing LESS, with
nothing in the output saying so. `C-37` is the same shape of check and would
fail open the same way. Design `D-14.5` makes non-empty ground truth an
assertion, not a log line.

`dev/scripts/sweep_stale_spellings.py` already fails closed on an unknown
classification (D-14.4, external finding `ext1-2`) — that is the precedent to
copy, including its declared-reason allowance classes.

## Progress

- [ ] Decide where the check lives (`dev/scripts/`, or shipped if a run path
      ever calls it — AGENTS.md's rule on `dev/scripts/` acquiring a caller)
- [ ] Assert non-empty ground truth on BOTH sides before reporting
- [ ] Give it allowance classes with declared reasons, as the sweep has

## Links

- `dev/milestones/r14/config-shape-design.md` §14.4, `D-14.5`, `D-11.4`
- `dev/milestones/r14/config-shape-scoping.md` — the `C-37` register row, and
  the re-measure under Group G that exposed the fail-open shape
- `t2608290620` — the sibling: the stale-spelling sweep's missing allowance
  classes. Different question, same machinery
