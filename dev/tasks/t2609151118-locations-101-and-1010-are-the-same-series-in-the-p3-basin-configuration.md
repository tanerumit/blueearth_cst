---
title: Locations 101 and 1010 are the same series in the P3 basin configuration
type: todo-item
status: backlog
effort: 1
area: wf3
queue:
created: 2026-09-15
updated: 2026-09-15
---

> [!note] Overview
> **What** — In the retained P3 experiment, output locations `101` and `1010`
> carry the *same* discharge series. Established from the published metric set,
> not inferred: they share an identical `fit.input.sample_sha256` in all 14
> bundle/unit groups, and all 140 of their `(metric, unit)` combinations publish
> identical values — 140 of the 700 rows in `q_indicators.csv` are exact copies.
> Decide whether this is a delineation artifact (two IDs for one outlet), a
> config duplication in `output_locations.csv`, or intended.
> **Why** — It silently inflates every per-key count computed from a metric set.
> GF15's own evidence was affected: what reads as 70 return-level fits is 56
> distinct samples, and "35 fits inside the tested shape domain" is 28. No
> conclusion in the GF15 workstream reversed, but several counts were overstated
> until re-review caught it, and any future analysis that treats locations as
> independent will be wrong in the same way.
> **Effort** — small to diagnose; unknown to fix

## Context

Found during the second independent review of the GF15 Stage 3 comparison,
2026-09-15. Disclosed in
`dev/milestones/r12/implementation/evidence/gf15-production-integration/stage-3-record.md`.

This is a property of the basin configuration rather than of GF15, which is why
it was boarded rather than fixed inside a GF15 stage.

## Progress

- [ ] Check `test_case/test_data/output_locations.csv` for a duplicated point
- [ ] Check whether the delineation emits two IDs for one subbasin outlet
- [ ] Decide: deduplicate, or document that some locations alias by design
- [ ] If locations can alias, consider whether metric sets should say so
