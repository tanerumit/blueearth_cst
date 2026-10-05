---
title: Make a copied project tree reusable in another worktree
type: todo-item
status: backlog
branch: fix/t2610042152-relocatable-project-tree
effort: 2
area: testing
queue:
created: 2026-10-04
updated: 2026-10-05
---

> [!note] Overview
> **What** — A test_local tree copied from one worktree into another can run WF3 and WF4 there without regenerating, as copy-seeding assumes.
> **Why** — Copy-seeding a worktree fails at WF3 and then at WF4, because both retain absolute paths that are checked on reuse. Every other worktree's tree can only be brought current by a full five-workflow rebuild of about an hour.
> **Effort** — WF3 fixed without moving any id; WF4 needs a ruling, because the natural fix is in `metric_plan.py` and moves the metric-set id once.

## Progress

- [x] Reproduce — measured 2026-10-04, re-measured 2026-10-05 on a fresh copy of the primary's tree in a scratch root (WF3+WF4 only).
- [x] WF3: reuse-only relaxation of the installed `out_dir` check (`125ba757`); all three code inventories unchanged, measured.
- [ ] WF4: rule on the metric-plan fix (failure 3), then implement it with a relocation test.
- [ ] Re-seed session-1 and session-2 from the primary once a copy works (user-run: replacing a seed tree needs the user's permission).

## Measured failures

1. **Reused collection, copied in place.** WF3 refused with `installed generator arguments differ from pinned plan`. `generation_publication._installed_generator` binds `generate_weather.out_dir` to the absolute `<data_root>/weathergenr`, so the installed `weather_generation_input.yml` copied from another worktree names that worktree's path, and `validate_installed_generator` compares it against the new root.
   Fixed in `125ba757`: the reuse path admits an `out_dir` whose trailing `<data_root>/weathergenr` matches; paths that run the generator stay strict.
2. **Copied tree with the scenario store moved aside.** WF3 refused with `archive terminal state is corrupt: committed`: the copied archive records refer to a publication whose files were no longer there. Inferred not a copy defect: transaction journals store project-relative paths, and a plain copy passed WF3 on 2026-10-05. The failure came from moving the store aside by hand.
3. **WF4 metric plan.** `MetricPlanStale`: `build_metric_plan` stores absolute `targets`, and `request_sha256` hashes them, so `verify_metric_plan` refuses the copied `_engine/metric_requests/<id>.json`. With the comparison bypassed (a reverted probe), WF4 reused the simulation and metric set `169fc1931781`, running only the gather rules. So this is the last failure.

The primary checkout is unaffected: WF3 there reuses its collection in place.

## Refs

- Found while finishing the test-suite trim, board item t2610041227 (assessment: `dev/tasks/t2610041227/assessment.md`).
- `blueearth_cst/experiment/generation_publication.py` — `_installed_generator`, `validate_installed_generator`.
