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
- [x] Share equivalent annual-series and monthly-distribution renderers with workflow-specific preparation.
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
After explicit payload authorization, the independent headless review also approved v2 with no
findings. The owner approved its exact bytes, and implementation is complete in `22fbe441`.
WF0 wrappers and WF1 forcing/hydrological summaries now share prepared annual/monthly charts.
All 109 matched render pairs preserved values, artists and saved geometry; 18 caption/metadata
files also matched. API probes, visual inspection, repository lint and formatting passed.
Post-implementation verification was root-owned after the worker service hit its usage limit.
See [completion evidence](t2610082103/design-runs/prepared-charts/completion.md) and
[review state](t2610082103/design-runs/prepared-charts/status.md).
The next packet is the separately reviewed shared map-reference producer design.
Remaining visual issues: very long records crowd year labels; all-missing maps retain a default scale
with little interpretive value; the soil-clay colourbar title clips the upper canvas edge.
Map-reference production, R/WF3 and external packaging remain later work.


### Branch identity (2026-10-10)

At the user's request, renamed `chore/minor-fixes` to `refactor/t2610082103-shared-plotting`.
Session-1 remains occupied; HEAD and the recorded base are unchanged. The supported advisory
`task-adopt --confirm` command updated the session registration, and session-check found no mismatch.
Earlier reviewed artifacts retain the branch name used when they were produced. No merge or push.

### Map-reference framing draft (2026-10-10)

The [map-reference draft](t2610082103/design-runs/map-reference/design-v1.md) is saved with its
annotated repository/output trees and configuration/compatibility inventory. It proposes one shared
historical machine record, selected-source frame authority, pooled frame-intersecting source scales,
project-owned completeness and explicit unscaled/extension display. WF1-only candidate cost is unmeasured.

The [scientific review](t2610082103/design-runs/map-reference/internal-review-domain.md) requests revision:
one blocking finding and two minor findings. A one-time probe confirms that permissive missing-data
settings can turn an entirely missing amount year into zero. Proposed G1 remedy is to narrow the new
map policy to at most 27 missing days per month. Retained CHIRPS auxiliary arrays need an explicit
preservation oracle; runtime cost becomes a measurement objective rather than an acceptability claim.

The owner approved G1 framing, including the 0–27 monthly bound, CHIRPS preservation and cost
measurement. Risk review found one major retained-field provenance gap. The fresh architect's
[design-v2](t2610082103/design-runs/map-reference/design-v2.md) resolves all four findings in the design,
with matching preparation/payload identities, rejection and repair; execution remains unverified.
After the owner's explicit payload approval, the independent read-only review approved exact v2
with no findings. All four internal findings have part-by-part design resolutions; the design converged
unchanged. The owner approved exact v2 for implementation; the reviewed bytes/header remain unchanged.
The approved implementation is complete in session-1 commit `99939abf` on the pinned branch.
WF0/WF1 now share historical frames/classes, a portable prepared-map renderer and validated preparation
and payload identities. Exact scientific preservation passes rapid and Liberia cases. Final fresh WF0
preserves 12 native arrays, 54 CSV tables and 51 temporal PNGs; four source maps and all four captioned
variants pass visual review. All nine retained WF1 products preserve their scientific/temporal values.
Independent producer/core checks pass 74 cases plus eight correct refusals; final CLI passes 20 tests.
Same-mtime source/DEM repairs and a newly valid pair swap refuse stale publication; complete repairs
match fresh payloads, and matched-input shared-factory roots produce identical reference bytes.

See [implementation evidence](t2610082103/design-runs/map-reference/implementation-evidence.md),
[scientific/visual verdict](t2610082103/design-runs/map-reference/scientific-consumer-report.md),
[repair/cost evidence](t2610082103/design-runs/map-reference/repair-and-cost-evidence.md) and
[run state](t2610082103/design-runs/map-reference/status.md). Costs are measured with explicit scope;
no performance acceptability or token-savings claim. The source worktree is clean. Full-suite and fresh
all-five gates remain owed at approved batch landing; no merge or push. Broader library development,
R/WF3 and external packaging remain open parts of this task.
