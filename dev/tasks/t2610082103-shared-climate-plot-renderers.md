---
title: Share plot renderers across climate workflows
type: todo-item
status: backlog
effort: 2
area: plotting
queue: 9
created: 2026-10-08
updated: 2026-10-09
---

> [!note] Overview
> **What changes** — WF0 diagnostics and WF1 forcing use shared renderers for equivalent chart types.
> WF2 adopts the common plotting fundamentals.
> **Why it matters** — Separate map, style and export paths let comparable figures drift and duplicate fixes.
> **What it takes** — Roughly 4–7 focused developer days in two batches. Agree the target appearance and
> scientific preparation boundary first; the estimate comes from source inspection, not a prototype.

## Progress

- [ ] Agree the target appearance and shared renderer inputs through a reviewed design.
- [ ] Consolidate style, sizing, export and caption placement; migrate WF2's common helper imports.
- [ ] Share raster-map drawing and migrate WF0/WF1 through thin workflow adapters.
- [ ] Share equivalent annual-series and monthly-distribution renderers with workflow-specific preparation.
- [ ] Verify unchanged prepared values with synthetic edge cases and inspect affected rapid-input renders.
- [ ] Remove replaced drawing paths, correct stale claims and document the resulting ownership.

## Scope and acceptance

Batch 1: plotting fundamentals and maps, 2–4 days. Batch 2: annual/monthly charts, 2–3 days.
Domain code retains masking, aggregation,
completeness, units, reporting years and PET handling. Keep specialist compositions separate.

Compare pre/post prepared values under matched inputs. Check missing cells, constant fields, units and
reporting-year boundaries. Inspect real WF0/WF1 figures and all affected WF2 products. Preserve inventories
and provenance. Follow dev/reference/validation-ladder.md; reuse rapid outputs and record config, tested
commit, output root and numerical/visual findings. Escalate gates if runtime or non-figure consumers change.

