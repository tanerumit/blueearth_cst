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
> **What changes** — Exclude THU/CIESM completely from WF2 analysis across all variables and summaries.
> **Why it matters** — Retained CIESM precipitation is about 1000 times smaller than peer models and depresses
> annual precipitation envelopes; dry filtering drops anomalies but retains absolute values.
> **What it takes** — Apply the exclusion before analysis, invalidate derived caches, and report coverage.

## Progress

Next: Implement full THU/CIESM exclusion in WF2 processing with explicit provenance and coverage counts.

- [x] Verify original CIESM source units and sampled values - all four stores are already anomalously small.
- [ ] Exclude THU/CIESM across all variables in WF2 processing and invalidate affected derived caches.
- [ ] Regenerate affected analysis; verify all summaries omit CIESM and report its exclusion consistently.

## Findings

The tiny precipitation scale is already present in the published historical and three SSP stores.
All four declare kg m-2 s-1, so WF2's multiplication by 86400 is dimensionally correct.
Direct first-month global means are about 0.003 mm/day in every store. A missing upstream factor
of 1000 is plausible but unverified. Prefer explicit invalid-source handling before analysis.

See [source verification](t2610300632/source-verification.md) for measurements, source versions,
retained-run evidence, independent literature, limitations and acceptance criteria.

## Agreed exclusion policy (2026-10-30)

Exclude THU/CIESM from all WF2 variables, experiments, members and analysis products, including
absolute values, anomalies, changes, climatologies, variability, envelopes and joint summaries.
Report the reason and coverage counts; preserve source data and provenance.

The verified defect concerns precipitation; full-model exclusion is the user's ensemble-consistency
choice. This supersedes precipitation-only handling and speculative rescaling. Reconsider inclusion
only after review of a verified source correction. Implementation stays separate from plotting work.
