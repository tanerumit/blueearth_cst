---
title: Prune the pre-R12 orphans from the rapid tree so tree-check regains its signal
type: todo-item
status: backlog
effort: 1
area: dev tree hygiene
origin: t2609151643 follow-up (2026-09-15)
queue:
created: 2026-09-15
updated: 2026-09-15
---

> [!note] Overview
> **What** — Quarantine the 63 pre-R12 orphan files under test_case/test_rapid that make snapshot_project_tree.py exit 1 on every run.
> **Why** — A gate that always exits 1 stops being read, so a real inventory gap would land unnoticed.
> **Effort** — small

## Progress

- [ ] <first step>

## Outcome

Done 2026-09-15, in the same session as [[t2609151643]].

**Quarantined, not deleted**, per step 1 of
`dev/milestones/r09/observed-tier-runbook.md`: the 63 files moved to
`test_case/_pruned_20260915/`, which sits BESIDE the tree and so cannot enter a
snapshot. That directory's `README.md` is the durable record -- it groups every
path, says why each is an orphan, and carries the reverse-move restore command.
`test_case/` is git-ignored, so none of this is visible to `git status`, which
is exactly why the board entry exists: it is the only tracked pointer to
`_pruned_20260915/`.

`snapshot_project_tree.py --config test_case/project_config_rapid.yml` went from
`320 paths, 63 unmapped` (exit 1) to `MAP CLEAN: 257 paths, 0 unmapped`
(exit 0). 320 - 63 = 257 exactly, which is the check that nothing moved that
should not have. `test_snake_utils.py`, `test_cli.py` and
`test_project_tree_inventory.py` re-run green afterwards (465 passed) -- those
are the only tests that name `test_rapid`.

Two things deliberately NOT done, both recorded in the quarantine README:

- `prune_climate_store.py` reports 8.0 MB reclaimable
  (`chirps_20000101_20161231/`, `comparison/`). The inventory DECLARES both, so
  they are no part of the exit-1 this item was about, and they are WF0
  forcing-comparison inputs a re-run would have to re-extract.
- `benchmarks/wf3_benchmarks_experiment_{rapid,verify_a2}.md` are pre-R12
  leftovers exactly like the two `wf3_run_stress_test_*.log` files that WERE
  removed -- but they resolve IDENTITY, because the inventory row
  `benchmarks/wf[34]_benchmarks_[a-z0-9_]+\.md` cannot tell WF3's plan key from
  WF4's experiment name. Step 0 did not name them, and the runbook's rule is to
  delete nothing step 0 did not name. So the tree now reads MAP CLEAN while
  still holding two stale benchmark tables.

## Found while pruning

`blueearth_cst/experiment/write_experiment_config.py` has NO caller -- no rule,
no script, nothing under `experiment/rules/` invokes it. It documents itself as
writing and freezing `experiments/<id>/config/experiment.yml`, which is why that
file looked like an inventory gap rather than the pre-R12 orphan it is. Dead
module code in the SHIPPED package, boarded separately as [[t2609151800a]].
