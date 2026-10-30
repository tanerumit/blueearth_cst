---
title: Exclude CIESM from WF2 analysis (54736a2b; landing held)
type: todo-item
status: active
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

Next: Close at user request; implementation is verified on refactor/t2610241523c, with landing/push held.

- [x] Verify original CIESM source units and sampled values - all four stores are already anomalously small.
- [x] Exclude CIESM before acquisition; preserve coverage, provenance and report reasons - commit 54736a2b.
- [x] Verify script-produced factors, analysis tables, both variables, cache invalidation and four DAG cases.

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

## Completion evidence

Implementation: session-2 commit 54736a2b on refactor/t2610241523c; no landing or push.
Focused evidence: 47 resolution/analysis tests, five coverage tests, 60 Stage-B/provenance/report tests,
four DAG checks, scoped Ruff and compilation passed. Valid-model scientific tables remain unchanged.
Independent retained Egypt check: 38 to 37 models; SSP245 2050 precipitation minimum 0.1377 to
14.4578 mm/year. Production outputs and figures were preserved and need WF2 rerun after integration.
Unique source evidence is retained in commit 54736a2b at
dev/records/validation/ciesm-source-quality-2026-10-30.md. Close only this item at explicit user request.
