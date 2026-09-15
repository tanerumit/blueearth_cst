---
title: write_experiment_config.py is dead code in the shipped package
type: watch-item
area: experiment / dead code
origin: t2609151800 prune (2026-09-15)
created: 2026-09-15
updated: 2026-09-15
---

> [!note] Overview
> **What** — blueearth_cst/experiment/write_experiment_config.py has no caller: no .smk rule, no script, nothing under experiment/rules/ invokes it. It is R9-P4 module code that R12 routed around.
> **Why** — It documents itself as writing and freezing experiments/<id>/config/experiment.yml, so a reader chasing that artifact concludes the tree inventory has a gap rather than that the writer is dead. It cost exactly that detour during the t2609151800 prune.
> **Trigger** — Someone proposes to restore experiment.yml, or a WF4 change needs a per-experiment frozen config -- at which point decide between reviving the module and deleting it.
