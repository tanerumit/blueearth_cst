---
title: "Open question: flat, hash-suffixed names for generation_inputs snapshots?"
type: watch-item
area: wf3 / generation inputs
origin: gabon-ntoum-v3 review (2026-09-25)
created: 2026-09-25
updated: 2026-09-25
---

> [!note] Overview
> **What** — Undecided: replace data/climate/generation_inputs/<hash12>/<name> with flat <stem>_<hash12><suffix> (e.g. basin_cells_25f6a9a9dc86.csv). Feasible: consumers resolve snapshots only via plan file references, and collection ids/seeds use content digests, not paths. Costs: old folders must stay (existing plans reference them, so both layouts coexist); keep the exclusive hard-link publish; guard names already ending in _<hex12>; prune tooling matches a name pattern instead of a folder. Readability-only; no result changes.
> **Why** — <why it needs to stay visible / what it costs to forget>
> **Trigger** — Owner decides whether folder readability is worth a mixed layout; then board implementation (snapshot_generation_input + tests) or drop.
