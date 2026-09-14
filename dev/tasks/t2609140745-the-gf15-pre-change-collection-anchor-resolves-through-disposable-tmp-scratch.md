---
title: The GF15 pre-change collection anchor resolves through disposable .tmp scratch
type: watch-item
area: wf3
origin: R12
created: 2026-09-14
updated: 2026-09-14
---

> [!note] Overview
> **What** — The accepted GF15 snapshot's integrity verdict is conditional on preserving the ORIGINAL absolute collection anchor, and that anchor is .tmp/scratchpad/2026-09-11_0010/p3-final-direct/project/scenario_collections/71bf34ef.../collection.json - inside the scratch tree the repository treats as deletable. experiments/p3_final/config/simulation.json embeds it as its one absolute path, so a working copy made from the durable snapshot still reads the collection from scratch.
> **Why** — A routine scratch sweep would silently invalidate an already-accepted gate and block the Stage 3 metrics comparison, with the immutable simulation record unable to be rewritten to point elsewhere.
> **Trigger** — Resolved when Stage 3 either completes its comparison or re-materializes the anchor at the same absolute path from the frozen snapshot at blueearth_cst-artifacts/r12/gf15-production-integration/prechange/p3-final-direct.
