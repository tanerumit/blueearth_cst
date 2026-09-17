---
title: Move the experiment's frozen simulation documents into _engine
type: todo-item
status: backlog
effort: 2
area: project-tree
origin: owner review of test_rapid, 2026-09-17
queue:
created: 2026-09-17
updated: 2026-09-17
---

> [!note] Overview
> **What** — Move `experiments/<name>/config/` -- the five hash-referenced simulation documents -- into the experiment's `_engine/` bin, keeping the whole directory together so the intra-directory relative paths survive.
> **Why** — The repo's own `_engine/` criterion says these are files a workflow writes so it can refuse a stale run, not anything a reader opens. `simulation_environment.json` alone is 22 KB of package pins.
> **Effort** — large
> **Trigger** — A WF3+WF4 baseline re-run is being paid for another reason, AND a tree matching `dev/baseline/manifest.json` is available to re-record from.

## Where this came from

An owner review of `test_case/test_rapid` on 2026-09-17 asked three questions of
the generated tree. Two were answered by shipping
[migration_config-snapshots.md](../milestones/post-r12/migration_config-snapshots.md);
this is the third. The owner's reading was: *"these don't seem to be user-facing
files but more for machine-reading and records."* That reading is **correct by
the criterion this repo already wrote down** for the `_engine/` bins
([[t2609152104]]) -- "the files a workflow writes so it can refuse a stale run,
rather than anything you open". What blocks it is cost, not the reasoning.

## The shape that works, and the one that does not

**Move the WHOLE directory.** `simulation.json` references four of its siblings
by BARE FILENAME (`simulation_environment.json`, `response_request.json`,
`simulator_settings.json`, `simulator_adapter_code_inventory.json`), so moving
them together preserves every one of those strings.

**Do not split the bin by audience.** Relocating individual files breaks the
recorded relative paths, and `docs/migration-post-r12.md` establishes there is
no compatibility read path -- every existing experiment would need re-running.

## The two costs

1. **`model.reference_path` is the exception and must be rewritten.** It is
   `"config/model_reference.yml"` -- EXPERIMENT-ROOT-relative, unlike the four
   bare filenames. So the move rewrites a stored string in every existing tree,
   which is the post-r12 migration class and needs its own user-facing note.
   `_check_model_reference` and roughly ten `_simulation_path(root, "config/...")`
   literals in `simulation_record.py` move with it, plus the metrics-only leaf in
   `cross_workflow_leaves.py` and the `experiments/*/config/simulation.json` glob
   in `scenario_collection.collection_references`.

2. **`dev/baseline/manifest.json` pins `experiments/experiment/config/simulation.json`.**
   Unlike the `config/runs/` snapshots, this one cannot be re-recorded by running
   a single cheap rule: it needs a full WF3+WF4 run against
   `project_config_baseline.yml`. As of 2026-09-17 that target and the
   `q_indicators.csv` metric set are both MISSING from `session-1`'s
   `test_case/test_local`, and two `cmip6_change_factors_*.csv` data targets
   already diverge -- so the re-record also needs a tree that matches the
   manifest, which that one is not. See `dev/baseline/provenance.md`.

## What is NOT a cost

`simulation_id` hashes digests only -- never path strings
(`simulation_record.simulation_id`). A pure directory move therefore does not
move the identity, and no retained metric set is invalidated. The expense is
entirely the stored-path rewrite and the baseline, not identity churn.

## Open question to settle when it is done

**Where exactly, and what happens to `config/`.** `_engine/config/` keeps a
nested "config" word; `_engine/simulation/` reads better. Either frees the
`config/` name -- and `experiments/<name>/config/composed_config.yml`, the
user-facing snapshot added 2026-09-17, should stay behind under it so the bin's
name becomes true: `config/` for the config a reader opens, `_engine/` for
machinery. That was NOT decided on 2026-09-17; it was deliberately left here
because it is a third structural choice beyond the two the owner approved.

`simulator_settings.json` and `model_reference.yml` are the two documents with a
plausible claim to being reader-facing. `simulation_window` is already carried
verbatim in the new `composed_config.yml`, so moving `simulator_settings.json`
out of sight costs nothing a reader needs.

## Progress

- [ ] Settle the open question above (`_engine/simulation/` vs `_engine/config/`)
- [ ] Confirm the trigger is met -- a matching baseline tree AND a re-run already paid for
- [ ] Move the directory; rewrite `model.reference_path` and the `config/` literals
- [ ] User-facing migration note (post-r12 class: no compatibility read path)
- [ ] Re-record `--workflow simulate_system` from the matching tree
