---
title: Make a copied project tree reusable in another worktree
type: todo-item
status: backlog
effort: 2
area: testing
queue:
created: 2026-10-04
updated: 2026-10-04
---

> [!note] Overview
> **What** — A test_local tree copied from one worktree into another can run WF3 and WF4 there without regenerating, as copy-seeding assumes.
> **Why** — Copy-seeding a worktree now fails at WF3: the installed weather-generator input binds an absolute out_dir, and archive transaction records do not survive a copy. Every other worktree's tree can only be brought current by a full five-workflow rebuild of about an hour.
> **Effort** — Large; the main unknown is whether to relativize the installed generator binding or treat relocation as a fresh WF3 publication, without moving the WF3 collection identity.

## Progress

- [x] Reproduce — both failures measured 2026-10-04 by copying the primary's fresh `test_local` into session-2 and running WF3+WF4 there.
- [ ] Decide the fix: relativize the installed generator's `out_dir` binding, or re-publish on relocation; keep the WF3 collection id unchanged either way.
- [ ] Make archive transaction records survive a copy, or refuse a copied tree with a message that names the remedy.
- [ ] Add a relocation test: copy a built project to a new root and reuse its collection and experiment.
- [ ] Re-seed session-1 and session-2 from the primary once a copy works.

## Measured failures

1. **Reused collection, copied in place.** WF3 refused with `installed generator arguments differ from pinned plan`. `generation_publication._installed_generator` binds `generate_weather.out_dir` to the absolute `<data_root>/weathergenr`, so the installed `weather_generation_input.yml` copied from another worktree names that worktree's path, and `validate_installed_generator` compares it against the new root.
2. **Copied tree with the scenario store moved aside.** WF3 refused with `archive terminal state is corrupt: committed`: the copied archive records refer to a publication whose files were no longer there.

The primary checkout is unaffected: WF3 there reuses its collection in place.

## Refs

- Found while finishing the test-suite trim, board item t2610041227 (assessment: `dev/tasks/t2610041227/assessment.md`).
- `blueearth_cst/experiment/generation_publication.py` — `_installed_generator`, `validate_installed_generator`.
