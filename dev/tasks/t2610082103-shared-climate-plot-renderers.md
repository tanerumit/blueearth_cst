---
title: Share plot renderers across climate workflows
type: todo-item
status: active
effort: 2
area: plotting
queue: 1
created: 2026-10-08
updated: 2026-10-10
doc: dev/tasks/t2610082103/landscape-and-plan.md
branch: refactor/t2610082103-shared-plotting
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
- [x] Consolidate style, sizing, export and caption placement; migrate WF2's common helper imports.
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
## Agreed direction (2026-10-10)

The user approved Python rendering first, an internal core with a portable dependency boundary,
then reusable chart interfaces, a separately scoped map-reference producer, and later external packaging.
The [landscape and development plan](t2610082103/landscape-and-plan.md) preserves the full assessment.
Start with a bounded foundations design and focused specialist handoffs. Implementation remains in
the pinned session branch; board and planning records stay on main.

The first foundations design passed internal and independent review with no findings, and the user
approved its exact revision. The extraction is implemented and verified on the pinned branch.
See [completion evidence](t2610082103/design-runs/rendering-foundations/completion.md) and
[review state](t2610082103/design-runs/rendering-foundations/status.md).


### Rendering foundations increment completed (2026-10-10)

The new internal plotting core owns the existing style tokens and ten drawing helpers. Active WF0–WF2
callers now import it directly; WF0 compatibility aliases remain. WF1 explicitly owns its batch backend.
Existing scientific preparation, appearance and product inventories are preserved. The broader progress
remaining items cover reusable chart interfaces, shared map references and their workflow acceptance.

Export mechanics are now separated from workflow logging in source commit `480f9be5`.
See [export completion and validation](t2610082103/export-mechanics/completion.md).
Six focused tests and the independent review passed; 49 PNG pairs showed no new visual regression.
Two PDF pairs passed structural checks; PDF rasterized visual parity remains unverified.

The caption/layout correction is complete in `4d19a377`: embedded captions preserve the ordinary
plot's physical geometry and wrap to the drawn axes. All 79 caption variants passed saved-geometry checks
and visual inspection; maximum drift was about 0.0042 mm. See
[caption completion and contract](t2610082103/caption-layout/completion.md).

The next chart-interface design is saved as
[design-v2](t2610082103/design-runs/prepared-charts/design-v2.md).
Scientific and risk reviews approved it with zero findings; v2 preserves the reviewed draft bytes.
It proposes one new prepared-chart module and migration of three WF0/WF1 callers, including
hydrological summaries. Existing scientific preparation, appearance and outputs remain constraints.
The independent headless review has not run: automatic approval review rejected sending private
design/repository context without payload-specific authorization. The next action is that explicit
authorization, then independent review and exact-version implementation approval. See
[review state](t2610082103/design-runs/prepared-charts/status.md). No source changes in this design packet.
Remaining visual issues: very long records crowd year labels; all-missing maps retain a default scale
with little interpretive value; the soil-clay colourbar title clips the upper canvas edge.
Map-reference production, R/WF3 and external packaging remain later work.


### Branch identity (2026-10-10)

At the user's request, renamed `chore/minor-fixes` to `refactor/t2610082103-shared-plotting`.
Session-1 remains occupied; HEAD and the recorded base are unchanged. The supported advisory
`task-adopt --confirm` command updated the session registration, and session-check found no mismatch.
Earlier reviewed artifacts retain the branch name used when they were produced. No merge or push.
