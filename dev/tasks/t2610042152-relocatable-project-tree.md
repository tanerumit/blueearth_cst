---
title: Make a copied project tree reusable in another worktree
type: todo-item
status: backlog
effort: 2
area: testing
queue:
created: 2026-10-04
updated: 2026-10-05
---

> [!note] Overview
> **What** — A test_local tree copied from one worktree into another can run WF3 and WF4 there without regenerating, as copy-seeding assumes.
> **Why** — Copy-seeding a worktree fails at WF3 and then at WF4, because both retain absolute paths that are checked on reuse. Every other worktree's tree can only be brought current by a full five-workflow rebuild of about an hour.
> **Effort** — Landed (`0bc65957`); only re-seeding the session worktrees remains.

## Progress

- [x] Reproduce — measured 2026-10-04, re-measured 2026-10-05 on a fresh copy of the primary's tree in a scratch root (WF3+WF4 only).
- [x] WF3: reuse-only relaxation of the installed `out_dir` check (`dd745f2e`); all three code inventories unchanged, measured.
- [x] WF4: owner ruled for the fix in `metric_plan.py` (2026-10-05); `verify_metric_plan` accepts a plan whose targets differ only by root (`1cb444a9`). The metric-set id moves once (`169fc1931781` -> `b7e1afe8dea5` on the baseline, identical tables).
- [x] Prove it: a copy of a copy ran WF3+WF4 with every target up to date.
- [x] Land (`0bc65957`, test-fast 3,888 passed; test-e2e passed before landing). Metrics-only run in the primary published `b7e1afe8dea5`; the superseded plan and set were moved out of the tree; `check_baseline check` passes all 6 targets, so no re-record was needed.
- [ ] Re-seed session-1 and session-2 from the primary (user-run: replacing a seed tree needs the user's permission), then close this item and t2610041227.

## Measured failures

1. **Reused collection, copied in place.** WF3 refused with `installed generator arguments differ from pinned plan`. `generation_publication._installed_generator` binds `generate_weather.out_dir` to the absolute `<data_root>/weathergenr`, so the installed `weather_generation_input.yml` copied from another worktree names that worktree's path, and `validate_installed_generator` compares it against the new root.
   Fixed in `dd745f2e`: the reuse path admits an `out_dir` whose trailing `<data_root>/weathergenr` matches; paths that run the generator stay strict.
2. **Copied tree with the scenario store moved aside.** WF3 refused with `archive terminal state is corrupt: committed`: the copied archive records refer to a publication whose files were no longer there. Inferred not a copy defect: transaction journals store project-relative paths, and a plain copy passed WF3 on 2026-10-05. The failure came from moving the store aside by hand.
3. **WF4 metric plan.** `MetricPlanStale`: `build_metric_plan` stores absolute `targets`, and `request_sha256` hashes them, so `verify_metric_plan` refuses the copied `_engine/metric_requests/<id>.json`. With the comparison bypassed (a reverted probe), WF4 reused the simulation and metric set `169fc1931781`, running only the gather rules. So this is the last failure.

The primary checkout is unaffected: WF3 there reuses its collection in place.

## Refs

- Found while finishing the test-suite trim, board item t2610041227 (assessment: `dev/tasks/t2610041227/assessment.md`).
- `blueearth_cst/experiment/generation_publication.py` — `_installed_generator`, `validate_installed_generator`.
