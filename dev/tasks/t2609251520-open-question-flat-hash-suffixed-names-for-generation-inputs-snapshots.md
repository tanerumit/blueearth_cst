---
title: "Decide naming of generation_inputs snapshots"
type: watch-item
area: wf3
origin: gabon-ntoum-v3 review (2026-09-25)
created: 2026-09-25
updated: 2026-09-28
---

> [!note] Overview
> **What** — Undecided: replace data/climate/generation_inputs/<hash12>/<name> with flat <stem>_<hash12><suffix> (e.g. basin_cells_25f6a9a9dc86.csv). Feasible: consumers resolve snapshots only via plan file references, and collection ids/seeds use content digests, not paths. Costs: old folders must stay (existing plans reference them, so both layouts coexist); keep the exclusive hard-link publish; guard names already ending in _<hex12>; prune tooling matches a name pattern instead of a folder. Readability-only; no result changes.
> **Why** — A later path cleanup could break plans that still reference the folder layout; keep the compatibility cost visible until the owner decides.
> **Trigger** — Owner decides whether folder readability is worth a mixed layout; then board implementation (snapshot_generation_input + tests) or drop.
