---
title: Point dev/working/parameter-placement.md at the R14 design, or drain it
type: todo-item
status: backlog
effort: 1
area: dev records / config
origin: R14 closure
queue:
created: 2026-09-01
updated: 2026-09-01
---

> [!note] Overview
> **What** — `dev/working/parameter-placement.md` is a DRAFT problem statement
> whose §4 question R14 has now answered. Either point it at
> `dev/milestones/r14/config-shape-design.md` and mark the answered part, or
> promote/drain it. It cannot simply be deleted: `run_stress_test.smk` cites its
> **M1** for why `project.static_dir` was not removed outright, and
> `dev/README.md`'s promotion rule forbids draining a cited working document.
> **Why** — Carried as an unchecked row on `t2608222016` and explicitly flagged
> there as "outside this lane's declared scope; needs its own task". The
> document's own banner says it moves to `dev/reference/` and gains an AGENTS.md
> pointer *once the problem statement is accepted and a direction is chosen* —
> R14 chose one, so the precondition it names has been met and nobody went back
> to it.
> **Effort** — small

## What is actually stale in it

Measured 2026-09-01. It contains **no** `shared:` spellings, so R14's section
rename did not leave it wrong in the way most documents would be. What is stale:

- Its **§6 cost columns**, written 2026-08-12, before R13 landed
  (`config-shape-scoping.md` says so explicitly and says "re-measure").
- Its M-numbers now have register equivalents: **M1** = `C-07`, **M2** = `C-35`
  (withdrawn — already done 2026-08-13), **M3** = `C-36`, **M4** ≈
  `C-10`..`C-15`. A reader following M2 finds a proposal for work that shipped.

So the defect is a live draft that reads as open when its question is closed —
not a broken path.

## Progress

- [ ] Decide: annotate-and-keep, promote to `dev/reference/`, or drain
- [ ] Whichever way, resolve `run_stress_test.smk`'s M1 citation first

## Links

- `dev/working/parameter-placement.md` — the document
- `dev/milestones/r14/config-shape-scoping.md` — the derived-artifact register
  row that maps M1..M4 onto `C-*`
- `dev/README.md` — the promotion rule that blocks a bare delete
