---
title: Share plot renderers across climate workflows
type: todo-item
status: active
effort: 2
area: plotting
queue: 1
created: 2026-10-08
updated: 2026-10-23
doc: dev/tasks/t2610082103/landscape-and-plan.md
branch: refactor/t2610082103
---

> [!note] Overview
> **What changes** — WF0 diagnostics and WF1 forcing use shared renderers for equivalent chart types.
> A shared map-reference producer makes extent, grid lines and colorbar classes independent of workflow order.
> WF2 adopts the common plotting fundamentals.
> **Why it matters** — Separate map, style and export paths let comparable figures drift and duplicate fixes.
> **What it takes** — Internal v1 is landed. Next, prove standalone use and scope external packaging;
> R/WF3 adoption and remaining spatial-layout corrections stay incremental.

## Progress

- [x] Review target appearance and renderer inputs — approved foundations, chart and map designs.
- [x] Consolidate style, sizing, export and captions — active WF0–WF2 helpers share the internal core.
- [x] Share native raster rendering and identified references — WF0/WF1 use one producer and policy.
- [x] Share annual/monthly chart rendering — scientific preparation remains workflow-owned.
- [x] Verify numerical/visual preservation — full suite, fresh all-five and independent review pass.
- [x] Retire replaced paths and land internal v1 — local main merge `761c8e54`; no push or release.
- [ ] Prove standalone reuse and scope external packaging — implemented and verified on
  `refactor/t2610082103`; batch gate and landing pending. R/WF3 remain later increments.

The owner approved the six standalone demo figures on 2026-10-23 and requested the landing checks.

Next: run the landing checks (fresh rapid WF0→WF1 in a new project directory), then await the go to land.

Current evidence: [internal v1 landing](t2610082103/landing-evidence.md).

## Scope and acceptance

Batch 1: plotting fundamentals and maps, 2–4 days. Batch 2: annual/monthly charts, 2–3 days.
Domain code retains masking, aggregation,
completeness, units, reporting years and PET handling. Keep specialist compositions separate.

Compare pre/post prepared values under matched inputs. Check missing cells, constant fields, units and
reporting-year boundaries. Inspect real WF0/WF1 figures and all affected WF2 products. Preserve inventories
and provenance. Follow dev/reference/dev-validation.md; reuse rapid outputs and record config, tested
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
this requirement; implementation was deferred at that checkpoint and is now complete.
## Agreed direction (2026-10-10)

The user approved Python rendering first, an internal core with a portable dependency boundary,
then reusable chart interfaces, a separately scoped map-reference producer, and later external packaging.
The [landscape and development plan](t2610082103/landscape-and-plan.md) preserves the full assessment.
The initial work used a bounded foundations design and focused specialist handoffs. Implementation
was isolated in the pinned session branch; board and planning records stayed on main.

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
The next packet at this checkpoint was the separately reviewed shared map-reference producer design.
At this chart checkpoint, long records crowded year labels and all-missing maps retained a default
scale. The later map-reference work replaces unavailable scales with explicit unscaled display.
Spatial soil-clay and LAI colorbar-title cropping remains; R/WF3 and external packaging stay open.


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
no performance acceptability or token-savings claim. At that implementation checkpoint, the source
worktree was clean and full-suite/fresh all-five gates were owed. The landing section below records
their completion. Broader library development, R/WF3 and external packaging remain open.


### Internal v1 landed (2026-10-10)

The owner-approved batch is merged to local main in `761c8e54`; session-1 is parked and its source
branch is deleted. The corrected software gate passes 4,120 tests, with 17 documented skips and one
upstream expected failure. Fresh all-five execution passes without skips, followed by exact WF0
preservation, classified WF1 preservation and independent WF0–WF2 visual/caption review.
See the [landing receipt](t2610082103/landing-evidence.md) for candidate/configuration/environment
identities, output roots, gate records, coverage limits and cleanup proofs. No push or release.

Internal v1 is complete. This broader item stays active for standalone reuse and external packaging;
R/WF3 migration and residual spatial title clipping remain later work.

### Step 7 framing decisions (2026-10-23)

A read-only boundary audit of `blueearth_cst/plotting/` found no Snakemake, HydroMT, xarray, geopandas or
Cartopy import and no backend selection at import. Blockers: `fundamentals.py` reaches the
checkout-relative `config/plotting/*.yml` through `shared/plot_style`, `plot_colors` and `plot_setup`
(PyYAML), and `location_labels.py` imports pandas for one missing-value check. `blueearth_cst` is not
installed; it imports only from a checkout.

The owner decided:

- Proof of reuse: a standalone script outside Snakemake, importing only the core, drawing annual/monthly
  charts and a map from retained WF0 tables. A second, non-CST use case still gates extraction.
- Style: the core ships neutral defaults and accepts an explicit style mapping; the CST preset stays in
  `blueearth_cst.shared` and injects it. PyYAML leaves the core.
- Core dependencies: numpy and matplotlib only; geospatial stays optional.
- Packaging: a scoping record only (candidate API, name options, dependency set, extraction trigger);
  no distribution, build metadata or release.

Next: a bounded step 7 design under `t2610082103/design-runs/standalone-core/`, including the identity-hash
impact of moving style ownership, before implementation.

The [step 7 design draft](t2610082103/design-runs/standalone-core/design-v1.md) proposes a scoped `Preset`
(`use_preset` replaces the nine `rc_context(STYLE)` entries) with the CST preset kept in
`blueearth_cst.shared`. A probe found no plotting/style path in the WF3, WF4 or indicator code-identity
inventories. The internal-v1 comparison harness no longer exists, so the design rebuilds one covering
every migrated caller. The independent review requested revision;
[design-v2](t2610082103/design-runs/standalone-core/design-v2.md) resolves all findings, including a
declared one-time map-reference rebuild. The owner approved exact v2 (git blob `61afa94a`, committed
in `eff4bb2b`) on 2026-10-23; implementation follows its §5 commit plan in session-1.

### Step 7 implemented (2026-10-23)

Commits `26fd59d7` (presets and caller migration), `93ed89ef` (standalone demo) and `f4c06321` (docs)
are on `refactor/t2610082103`; not landed or pushed. Matched WF0–WF2 renders under annotation none,
caption and title keep all 336 PNGs pixel-identical; only map-reference identity fields change, as
declared. A raising probe found no unscoped call on the exercised paths. WF0 subbasin charts were
checked by a test pair, and the dev-only `plot_basin_map_from_model` was not exercised. The core
imports and renders under `python -I` with numpy and matplotlib only. Five `test_simulation_reuse.py`
failures come from main commit `094bab3a` and need their own fix. See the
[implementation evidence](t2610082103/design-runs/standalone-core/implementation-evidence.md) and the
[packaging scope](t2610082103/design-runs/standalone-core/packaging-scope.md).

## Work location

- Owner: session-1; branch: refactor/t2610082103; implementation commits: `26fd59d7`, `93ed89ef`, `f4c06321`.
- Implementation: session-1 :: `blueearth_cst/plotting/`, `blueearth_cst/shared/plot_preset.py`, migrated
  callers listed in the design §2.4.
- Coordination: main :: dev/tasks/t2610082103/design-runs/standalone-core/.
- Scratch: session-1 :: .tmp/scratchpad/t2610082103-step7/ (harness, probes, logs, renders, venv-min).
- Outputs: session-1 :: .tmp/scratchpad/t2610082103-step7/verification/{base,before,control,after}-*;
  input root session-1 :: .tmp/pytest/run-4bf42bbc57744ddb8ec629e34230630c/test_all_five_workflows_run_en0.
- Verification: see implementation evidence; tested commit `26fd59d7` (render harness, affected tests,
  lint, format), `93ed89ef` (demo in Pixi and venv-min).
- Retention: the step 7 scratch and the input root until landing; then clean them.
- Next action: owner review of the demo figures, then the batch gate (fresh rapid WF0→WF1 run,
  validation-reference landing checks) when landing is requested; blockers: owner decision to land.
