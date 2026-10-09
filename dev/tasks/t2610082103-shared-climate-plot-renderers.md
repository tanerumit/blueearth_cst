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
> A shared map-reference producer makes extent, grid lines and colorbar classes independent of workflow order.
> WF2 adopts the common plotting fundamentals.
> **Why it matters** — Separate map, style and export paths let comparable figures drift and duplicate fixes.
> **What it takes** — Roughly 4–7 focused developer days in two batches. Agree the target appearance and
> scientific preparation boundary first; the estimate comes from source inspection, not a prototype.

## Progress

- [ ] Agree the target appearance and shared renderer inputs through a reviewed design.
- [ ] Consolidate style, sizing, export and caption placement; migrate WF2's common helper imports.
- [ ] Share raster-map drawing and an input-identified reference producer; migrate WF0/WF1 adapters.
- [ ] Share equivalent annual-series and monthly-distribution renderers with workflow-specific preparation.
- [ ] Verify prepared values and WF0-to-WF1 versus WF1-only equivalence; inspect affected rapid renders.
- [ ] Remove replaced drawing paths, correct stale claims and document the resulting ownership.

## Scope and acceptance

Batch 1: plotting fundamentals and maps, 2–4 days. Batch 2: annual/monthly charts, 2–3 days.
Domain code retains masking, aggregation,
completeness, units, reporting years and PET handling. Keep specialist compositions separate.

Compare pre/post prepared values under matched inputs. Check missing cells, constant fields, units and
reporting-year boundaries. Inspect real WF0/WF1 figures and all affected WF2 products. Preserve inventories
and provenance. Follow dev/reference/validation-ladder.md; reuse rapid outputs and record config, tested
commit, output root and numerical/visual findings. Escalate gates if runtime or non-figure consumers change.


### Shared map-reference producer (2026-10-09)

Either WF0 or WF1 must produce the same historical-authority map reference from declared inputs,
without depending on existing WF0 figures. Define extent, grid lines, colorbar range, class boundaries
and ticks once. Preserve pooled historical-candidate scales; show under/over-range forcing values.
Identify references by source set, period, reporting year and completeness/scale policy so stale
references are not reused. Store machine records in the cohesive output unit's root `_engine/`.

Estimate: 2–3 focused developer days for this component, including workflow wiring and one-time
validation. This overlaps the map batch above; re-estimate the combined batch during design rather
than adding the estimates mechanically. A selected-source-only reference may take about one day,
but changes WF0's cross-source scale policy and needs an explicit decision. WF1-only pooled scales
also require candidate summaries; measure that runtime cost separately.

Acceptance: fresh WF0 then WF1 and fresh WF1 alone produce identical references and matching map
frames, grids and colorbars under matched inputs. Changing source set or policy rebuilds the
reference. Use one-time checks and visual inspection; do not add these checks to the testing suite.
Keep workflow-specific scientific preparation unchanged. The Liberia output corrections prompted
this requirement; shared-producer implementation remains deferred.