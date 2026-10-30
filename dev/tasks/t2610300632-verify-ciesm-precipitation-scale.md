---
title: Verify and correct WF2 CIESM precipitation scale
type: todo-item
status: backlog
effort: 1
area: wf2
queue:
created: 2026-10-30
updated: 2026-10-30
---

> [!note] Overview
> **What changes** — Verify THU/CIESM source precipitation units and correct WF2 ingestion or quarantine
> invalid data before absolute statistics are produced.
> **Why it matters** — Retained CIESM precipitation is about 1000 times smaller than peer models and depresses
> annual precipitation envelopes; dry filtering drops anomalies but retains absolute values.
> **What it takes** — Trace original source metadata and values through acquisition, reduction and analysis;
> handle historical and SSP stores, cache identity and regression coverage without plot-side corrections.

## Progress

Next: Define explicit WF2 invalid-precipitation handling; require producer evidence before any CIESM rescaling.

- [x] Verify original CIESM source units and sampled values - all four stores are already anomalously small.
- [ ] Implement an evidence-backed WF2 conversion or explicit invalid-source handling with cache invalidation.
- [ ] Verify annual totals, absolute changes, dry eligibility and percentage invariance on retained inputs.

## Findings

The tiny precipitation scale is already present in the published historical and three SSP stores.
All four declare kg m-2 s-1, so WF2's multiplication by 86400 is dimensionally correct.
Direct first-month global means are about 0.003 mm/day in every store. A missing upstream factor
of 1000 is plausible but unverified. Prefer explicit invalid-source handling before analysis.

See [source verification](t2610300632/source-verification.md) for measurements, source versions,
retained-run evidence, independent literature, limitations and acceptance criteria.
