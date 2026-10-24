---
title: Rebuild deleted WF1 outputs that targets do not request
type: todo-item
status: backlog
effort: 1
area: wf1
queue:
created: 2026-10-24
updated: 2026-10-24
---

> [!note] Overview
> **What changes** — Deleting any declared WF1 output, such as `evaluation/plots/` or a forcing figure,
> makes the next run rebuild it.
> **Why it matters** — Snakemake reruns a non-target job only for missing outputs that something
> requests. WF1 targets one representative output per rule, so deleted plots and tables stay missing.
> **What it takes** — Request every declared output of the representative-target rules in
> `WF1_TERMINALS`, then check WF0 and WF2 for the same pattern.

## Progress

- [ ] Request all declared outputs of 1.11 `plot_basin_map`, 1.12 `plot_model_forcing`,
  1.14 `export_simulation_tables` and 1.15 `plot_model_evaluation` from the WF1 targets.
- [ ] Check WF0 and WF2 targets for representative-only requests.
- [ ] Confirm with a rapid run: delete each family, dry-run, and see the producing rule scheduled.

## Evidence (2026-10-24)

`build_model.smk` `WF1_TERMINALS` requests only `evaluation/performance_indicators.csv` from 1.15;
its `plots/` and `stations/` directory outputs are unrequested. A minimal Snakefile under
Snakemake 9.6.2 reproduced it: after deleting the unrequested `directory("plots")` and `b.png`
outputs, the dry-run reported "Nothing to be done"; requesting `plots` explicitly scheduled the job
with "Missing output files". Observed first in t2610082103 step 7, where deleting `plots/` left
1.15 up to date until `performance_indicators.csv` was also deleted.

Next: list every declared output of the four rules and add the missing ones to the targets.
