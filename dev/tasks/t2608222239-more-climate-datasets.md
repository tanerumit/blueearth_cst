---
title: Support additional historical climate datasets in the raw-climate path
type: todo-item
status: backlog
effort: 2
area: wf0 / wf1 climate store
origin: R14
queue:
created: 2026-08-22
updated: 2026-08-22
---

> [!note] Overview
> **What** — Extend the wf0/wf1 raw-climate path beyond the currently supported set. `_SUPPORTED_SOURCES` (`analyze_climate.smk:120`) is era5, chirps and chirps_global; anything else is refused at parse time, and `build_model.smk:148` refuses eobs on the wf1 path specifically. WHICH datasets to add is undecided — eobs and cru have been named only as illustrations of the gap, never as chosen targets.
> **Why** — R14's `climate.sources` makes a multi-dataset candidate set expressible in config, but the SHAPE is general while the supported SET is bounded and smaller, so the new config can name a dataset the pipeline cannot extract. Deliberately kept OUT of the R14 register (owner, 2026-08-22) so the config milestone does not imply it ships datasets.
> **Effort** — large

## Progress

- [ ] <first step>
