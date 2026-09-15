---
title: Shorten the WF3 fingerprint suffix in run-scoped filenames to 12 characters
type: todo-item
status: backlog
effort: 1
area: wf3 / outputs
origin: R12 rapid review (2026-09-15)
queue:
created: 2026-09-15
updated: 2026-09-15
---

> [!note] Overview
> **What** — Key the WF3 run-scoped log and benchmark filenames, and their `_parts/` directories, on the first 12 hex characters of the scenario-plan fingerprint instead of all 64. The `scenario_plans/<fp>/` directory itself keeps its full-length name.
> **Why** — The 64-hex suffix is roughly three times the length of the rest of the filename, is unreadable at a glance, and lengthens already-nested `_parts/` paths on Windows. The repo already shortens digests to 12 for human display in `write_model_reference.py`; this extends that convention to the one place a user actually reads a filename.
> **Effort** — small

## Context

Observed on a post-R12 rapid run under `.tmp/test_run/`: `benchmarks/` holds
`wf0_benchmarks.md`, `wf1_benchmarks.md`, `wf2_benchmarks.md`,
`wf4_benchmarks_experiment_rapid.md` -- and
`wf3_benchmarks_c78c42d77345885818d7844efac9f2323a7634ded1c9806be99bdaba790973c7.md`.

The keying itself is correct and must not be removed. WF0-WF2 are project
singletons, so an unkeyed constant name is safe for them. WF3 and WF4 are not:
a project can hold several scenario plans and several experiments at once, so
an unkeyed name would have each run overwrite the previous one.
`tests/test_project_tree_inventory.py:264` pins this deliberately -- bare
`benchmarks/wf3_benchmarks.md` must report as UNDECLARED, with the comment
"unkeyed: no experiment can produce it". WF4 keys on the experiment name
because it has one; WF3 has no user-facing plan name, only content identity.

Note the suffix is the **scenario-plan** fingerprint, not the collection
fingerprint -- the same run carried plan `c78c42d7...` and collection
`a340c934...`.

## Decision

Owner ruling 2026-09-15: **truncate to 12** (option 1 of three offered).
Rejected: leaving it as is; adding a user-facing plan alias, which would mean
introducing a naming surface WF3 does not currently have.

Accepted trade: the filename stops being a literal `ls | grep` match for its
`scenario_plans/<fp>/` directory, and collision probability becomes non-zero
rather than nil. At 12 hex characters over the number of plans a project
realistically accumulates, that risk is negligible.

## Scope

Name construction is four adjacent lines in one file,
`generate_scenarios.smk:27-30` -- `LOG_PARTS_DIR`, `BENCH_PARTS_DIR`,
`WORKFLOW_LOG_NAME`, `BENCHMARKS_NAME`, all built from
`Path(_scenario_plan_path).parent.name`. Derive the short form once and use it
in all four, so the log, the benchmark table and both `_parts/` trees stay
consistent with each other.

Then sweep the references: `docs/guide/outputs.qmd:49-53` documents the scheme
as `<request_id>`, and `dev/reference/workflows/climate_experiment.md` carries
the older spelling. Grep before assuming that is the whole list.

The tree inventory needs no change: `dev/scripts/semantic_tree_diff.py:331,335`
matches `[a-z0-9_]+`, which already accepts both a 64- and a 12-character hex
suffix. Confirm that by running `snapshot_project_tree.py` after the change
rather than by reading the regex.

## Also found while scoping

`dev/scripts/semantic_tree_diff.py:325-329` states that "WF3's are
experiment-keyed in the FILENAME" and that "the experiment fragment is what
distinguishes them". That has been false since R12 -- WF3 is keyed by the
scenario-plan fingerprint, and only WF4 is experiment-keyed. The regex is
still correct; only the comment explaining it is wrong. Fix it in the same
commit, since this task edits the behaviour the comment describes.

## Progress

- [ ] Derive the short fingerprint once in `generate_scenarios.smk` and use it for all four names
- [ ] Correct the stale experiment-keyed comment in `semantic_tree_diff.py`
- [ ] Sweep `docs/guide/outputs.qmd` and `dev/reference/workflows/climate_experiment.md`
- [ ] Run WF3 on the rapid config and confirm `snapshot_project_tree.py` still reports MAP CLEAN
