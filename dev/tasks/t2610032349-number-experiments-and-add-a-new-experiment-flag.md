---
title: Number experiments and add a new-experiment flag
type: todo-item
status: backlog
effort: 1
area: wf4
queue:
created: 2026-10-03
updated: 2026-10-03
---

> [!note] Overview
> **What changes** — Default experiment_name to stress_test; allocate <name>_NN (01, 02, ...) for unset and set names; plain runs continue the highest number; run_workflows.py --new-experiment [--note] starts the next one; a name already ending in _NN pins that experiment.
> **Why it matters** — The <project_dir basename>_<date> default yields active_<date> for every create_case case and carries no meaning; numbered experiments with a recorded note are simpler and keep incremental reruns.
> **What it takes** — Two commits: allocation/numbering + tests, then the runner flag, experiment.yml note, console line and docs; main unknown is the >99 policy.

## Progress

- [ ] Allocation in `blueearth_cst/experiment/allocate.py` and `snake_utils`: base `stress_test` when unset, `<base>_NN` numbering, continue the highest existing number (first run creates `_01`), literal pin for a name already ending in `_NN`; tests.
- [ ] `scripts/run_workflows.py --new-experiment [--note "..."]` reserves the next number before the run; write `experiment.yml` (note, creation date, `git describe` toolbox version) in the experiment folder; console row `experiment: <name> (new|continuing)`.
- [ ] Docs: `config/templates/README.md` experiment_name section, simulate_system template comment, `suggest_experiment_name.py` role (retire or align).

## Decisions

- Agreed 2026-10-03: a plain run always continues the latest experiment; only the runner flag starts a new one (chosen over a separate `suggest_experiment_name.py --new` step).
- Existing `<slug>_<date>` folders are left alone and not continued; the first new-scheme run creates `<base>_01` beside them.
- Open: behaviour past `_99` (error vs three digits) — must be reported, never silent.
