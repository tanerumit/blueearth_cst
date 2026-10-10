# Shared historical map reference

Status: provisional v1; G1 and G2 pending; no implementation approval. Date: 2026-10-10.
Lifecycle: task-owned review; reviewed versions are immutable and acceptance lives in `status.md`.
Canonical home: `dev/tasks/t2610082103/design-runs/map-reference/`; scratch is the author workspace.
Reading guide: sections 1–3 and 8 carry the owner decisions; the remaining detail fixes implementer contracts.
The extra contract detail keeps identity, scientific support and verification in one record.

## 1. Overview

Produce one historical map reference from the project's declared climate candidates. WF0 source maps and
WF1 forcing maps read its frame, coordinate ticks and color classes. Running WF1 alone produces the same
reference as running WF0 followed by WF1 under matched data and settings. Existing figure filenames remain.

The researcher still chooses candidates, selected forcing, historical window and reporting year in project
config. WF0 remains optional. WF1 now needs historical summaries of every candidate to establish pooled
scales, even though only the selected source supplies model forcing. That extra cost is unmeasured.

Source preparation retains native cells, eligibility rules and source-grid PET. Model forcing retains its
basin mask, corrections, PET and existing summary policy. Shared colors compare displayed quantities;
they do not establish equal spatial support, periods, eligibility or PET methods.

```text
Project climate choices                                         + catalogs + region
                    |
        Existing candidate climate stores
                    |
        Shared historical reference producer ------> historical/_engine/map_reference.json
                    |                                             |
WF0 native source fields --------------------------> portable raster drawing
WF1 prepared model forcing ------------------------> portable raster drawing
                                                                  |
                                                    Existing maps and captions
```

Two consequential changes need G1: pooling over the common selected-source frame, and project ownership
of historical reference completeness. This document proposes them explicitly; the earlier pooled-scale
decision does not settle their details. Temporal charts and simulation inputs remain outside this change.

## Contents

- [2. Current behavior and scientific support](#2-current-behavior-and-scientific-support)
- [3. Configuration and producer ownership](#3-configuration-and-producer-ownership)
- [4. Small interfaces and persisted record](#4-small-interfaces-and-persisted-record)
- [5. Identity, invalidation and publication](#5-identity-invalidation-and-publication)
- [6. Drawing contract](#6-drawing-contract)
- [7. Files, products and compatibility](#7-files-products-and-compatibility)
- [8. Alternatives and G1 choices](#8-alternatives-and-g1-choices)
- [9. Verification, handoff and limits](#9-verification-handoff-and-limits)
- [10. Revision log](#10-revision-log)

## 2. Current behavior and scientific support

Static evidence is session-1 `22fbe441cef67db45130834eab87a31f8e3b6fc7`, in intake E1–E7 and E10.
These observations are not numerical validation. The approved parent plan is
`dev/tasks/t2610082103/landscape-and-plan.md`; the task note fixes pooled historical authority.

### 2.1 What currently differs

- WF0 orders `climate.sources` selected-first, deduplicating in declaration order. Its source-store
  factory relaxes minimum length for extra candidates and omits forcing enrichment for extra CHIRPS.
- `annual_fields()` in `climate_analysis/diagnostic_maps.py` computes cellwise means of eligible annual
  totals for precipitation/PET and annual means for temperature, using `diagnostics.annual()`.
- `compute_climate_diagnostics.py` retains raw precipitation/temperature; only source PET comes from
  `source_grid_climate()`. Its temperature validity gate comes from `diagnostic_tables.daily_series()`.
  Unsupported or unresolved temperature also suppresses source PET. These details must survive extraction.
- WF0 `diagnostic_render.py` pools finite values from candidate annual fields intersecting padded basin
  bounds: padding is 8% per axis, minimum 0.005 degrees. With at most one contributing grid it instead
  uses every cell of the plotted field. Each map nevertheless displays its own full extraction extent.
- WF1 `plot_map_forcing.py` gets the frame from selected historical precipitation cell edges.
  `forcing_figures.py` computes independent limits from all finite model-basin annual fields.
  Its `prepare_forcing()` always uses default completeness, three days/month and fifteen days/year.
- `draw_map()` derives classes on each call, derives aspect from that field's mean latitude, and lets
  Matplotlib locate coordinate ticks. Geographic grid lines are not explicitly standardized.

### 2.2 Proposed support: native science, common viewport

The selected historical extraction's full native cell edges define `[west, east, south, north]`, without
padding. This is a viewport, not a basin mask. Every source and model field keeps its existing native
coordinates and values; drawing clips cells at that viewport. A source may cover less than the frame.

Pool finite annual values from every eligible candidate cell whose closed cell rectangle intersects the
frame. Retain the existing inclusive edge-intersection convention, including boundary-touching cells;
report their counts. Apply the same support rule with one or many contributing sources. There is no
area weighting, interpolation, basin-cell restriction or common-year intersection in this min/max pool.
The pool controls display extrema, not a pooled climate estimate. Report each source's effective period.

This changes current display pooling: padded-basin support and its single-grid special case cannot
guarantee a scale covering every cell in a common selected-source viewport. Keeping them would preserve
some old limits but leave visible historical cells outside the scale. G1 must approve the proposed
replacement or choose the explicit alternative in section 8; it must not be hidden in refactoring.

Scientific support remains source-specific. CHIRPS candidates contribute precipitation only, including
when selected CHIRPS stores contain borrowed forcing variables. Genuine temperature carriers contribute
temperature and derived source PET when available. A missing variable is a recorded exclusion, not zero.
Available full reporting years can differ by source and cell. Source maps retain those differences.

## 3. Configuration and producer ownership

### 3.1 Project-owned historical reference settings

Propose one optional closed mapping, `climate.map_reference`, in the project config:

```yaml
climate:
  map_reference:
    max_missing_days_month: 3
    max_missing_days_year: 15
```

Both values default to today's 3/15 and require nonnegative integers, excluding booleans. Register the
mapping as project-owned in `shared/config_composition.py` and reject it in workflow files. The shared
resolver owns these defaults. Do not add a scale-policy menu: frame, support and classes have a versioned
policy in code. `climate.window` is the requested extraction window; `water_year_start` governs annual
labels. WF0 diagnostic `reference_period` and `comparison_period` do not select map years today and
must not silently acquire that meaning.

WF0's existing diagnostic completeness continues to govern all its scientific summaries. Its effective
values must equal the shared historical reference values whenever WF0 renders maps. Reject disagreement
at DAG construction with both key paths and values. For existing custom WF0 configurations, copy those
two values into the project mapping; retain the old values for temporal diagnostics. Never read a disabled
WF0 file to configure WF1. Default configurations need no edit. This explicit duplication is a narrow
compatibility guard, not a migration of all diagnostic settings.

WF1 forcing preparation keeps 3/15 regardless of reference policy. A nondefault reference may therefore
describe a different eligibility policy; captions/methods must state both. Changing forcing completeness
or unifying temporal settings would require separate scientific approval. Existing model simulation
windows can be shorter than the historical reference window; captions must distinguish the two periods.

### 3.2 One shared producer specification in two DAGs

Introduce `historical_map_reference_rule(...)` alongside ordinary shared helpers. Both Snakefiles use its
identical script, inputs, outputs and parameters; only rule label, log and benchmark differ. Name its
concrete rule `produce_historical_map_reference` in each DAG. It produces one explicit JSON file.

WF1 retains its selected `CLIMATE_STORE` and existing selected extraction rule for downstream consumers.
Add the same extra-candidate specs and concrete extraction rules as WF0, excluding the selected source
to avoid duplicate output ownership. Keep selected-store contracts identical to WF3. Extra candidates
use exactly WF0's `enforce_min_years` and `forcing_required` flags. Do not build extra hydrological models.

Declared reference inputs: every candidate's `extract_historical.nc`, `basin_cells.csv`, optional declared
orography, shared region, basin geometry, and ordered catalog files. Also declare the actual catalog-backed
orography files read for source PET; catalog text alone cannot detect replacement of their bytes. Resolve
these through HydroMT's existing source descriptors, without changing its loading or regridding methods.
If a source cannot expose concrete local inputs, fail qualification and return that interface gap to G1;
do not silently claim complete identity from a catalog filename or add a remote storage system.

Parameters: selected-first candidate order and roles, selected frame authority, requested window, reporting
start month, completeness, source preparation/scale policy versions, and relevant code/environment digests.
No workflow name, WF0 enable flag, plot inventory or absolute project root enters the reference semantics.

WF0 rendering declares the JSON as input in addition to its existing tables and overlays. Preserve pooled
table dependencies used by non-map plots; remove only map-only dependencies after caller inspection.
WF1 `plot_model_forcing` declares the JSON and its validation inputs, replacing its direct frame selection.
Each renderer validates the expected record before saving any figure. Both terminal inventories reach the
producer through explicit inputs; no directory scan, existing PNG, WF0 diagnostic metadata or figure order
is a producer input. The producer does not schedule WF0 temporal diagnostics or comparison tables.

## 4. Small interfaces and persisted record

### 4.1 Preparation versus portable drawing

Extract existing source-map preparation into `climate_analysis/source_map_fields.py`. Its
`prepare_source_map_fields(climate_nc, basin_cells, source, catalogs, oro_nc, m0, completeness)` returns
the existing annual-field dataset and lineage. Reuse the current unit gate, raw precip/temp selection,
source-grid PET machinery and `annual_fields()` without changing their numerical method. WF0 compute
and the shared producer call it. Producer reduces one source at a time and discards its arrays afterward.
Initial WF0 execution may repeat source-map reductions; optimizing that is deferred until cost is measured.

Do not use WF0's existing `tables/annual_climatology.nc` opportunistically: its presence alone establishes
neither compatible settings nor provenance. It remains WF0-owned and is still written for inspection.
WF1 `prepare_forcing()` and every temporal chart preparation path remain unchanged.

The portable module `plotting/prepared_maps.py` receives only prepared arrays and small records:

```python
MapFrame(extent, longitude_ticks, latitude_ticks, aspect)
MapScale(units, boundaries, ticks, colors, under_color, over_color, missing_color, status)
RasterMap(values, longitude_edges, latitude_edges, inside=None, cell_edges=True)
draw_raster_map(raster, frame, scale, overlays) -> Figure
```

Shapes are `(latitude, longitude)`; edge arrays have one more element than their corresponding dimension.
`inside` is an optional exactly aligned boolean array. `overlays` contains already loaded geometry and
labels; loading GeoJSON, interpreting source identity and generating captions stay in workflow adapters.
The core imports NumPy/Matplotlib only, selects no backend, reads no files and imports no CST workflow,
HydroMT, GeoPandas or Xarray modules. Existing overlay drawing and label placement move with the artist.

### 4.2 Record v1 and audiences

`data/climate/historical/_engine/map_reference.json` is the machine record for maintainers, renderers and
provenance audits. The historical climate collection owns it because it spans source stores and can exist
without a model. It is not a forcing artifact or a WF0 comparison result. No standalone report is added.

The closed v1 record contains `schema_version`, `reference_id`, `identity`, `frame`, `variables`, and
`provenance`. `identity` contains all resolved settings and input identities from section 5. `frame`
contains selected source, extent, explicit ticks, aspect and `crs: EPSG:4326`. `variables` has exactly
`precip`, `temp`, `pet`, each with units, status/reason, finite pool count, contributing source summaries,
excluded source reasons, extrema, boundaries, ticks and the resolved palette/under/over/missing colors.

Each source summary records source role, effective dates, present scientific variables, grid dimensions
and cell edges digest, intersecting/finite/unavailable cell counts, and minimum/maximum positive eligible
year counts. No finite values means null extrema/count range and empty boundaries/ticks, with a reason.
Missing JSON numbers are `null`; NaN/Infinity are forbidden. Counts describe cells, not independent samples.

`provenance` records logical input roles, relative store paths, input digests, source/catalog identities,
preparation method, policy versions and environment identity. Do not place timestamps, invocation IDs,
absolute roots or workflow names in the record: exact bytes must be equal across the paired-root check.
Those execution facts remain in existing workflow logs/run records. Consumers reject unknown versions.

Readable explanations remain in existing `figure_captions.md`. Existing figure JSON gains, for maps only,
`reference_id`, reference path relative to project root, reference/frame support, reference and field periods,
both completeness policies, units, unavailable reason, and in-frame under/over cell counts. Existing caption
JSON paths remain for compatibility; this increment does not migrate their older `plots/_engine/` placement.

## 5. Identity, invalidation and publication

`reference_id` is SHA-256 over the complete record except `reference_id`, using UTF-8 strict JSON with
sorted object keys, compact separators and no trailing newline. This also protects frame/scale payload
integrity. Lists preserve semantic order; integers remain integers; normalize negative zero and reject
nonfinite numbers. Serialize the enclosing record identically plus one newline. This is a local artifact
digest, not a new managed-run canonicalization scheme.

Identity includes selected-first deduplicated sources and roles; selected frame source; requested window;
actual extracted dates; reporting month; completeness; unit/availability and source-PET policy versions;
frame-support, tick, palette and class-policy versions; SHA-256 of every consumed input; and SHA-256 of
the preparation/producer source files and environment lock files. Use logical roles and store-
relative paths, never checkout/project absolute paths. Preserve catalog order and hash catalog bytes.
Changing only an unrelated workflow enable flag must not change identity.

The initial source digest closure includes both new shared modules, `source_map_fields.py`,
`diagnostic_maps.py`, `diagnostics.py`, `diagnostic_tables.py`, `diagnostic_settings.py`,
`plot_climate_source.py`, `shared/climate_parity.py`, `shared/grid_cells.py` and their local preparation
dependencies found at implementation. Record the explicit resolved list, plus `pixi.lock` and
`Manifest.toml`; changing that list changes identity. Do not use the whole checkout commit as a cache key.

Hash actual extracted stores and basin-cell tables, not their sizes/mtimes; include consumed orography
and geometry bytes. Hashes are streamed, with time accounted separately from science. Read input hashes
before preparation and again before publication; refuse publication if any input changed. Renderers check
the payload digest, expected settings, versions and current input digests against the record before use.
Keep this validation in the CST adapter. A mismatch fails with the reference target and reason; no automatic
local rescaling. A no-op invocation does not read or certify retained figures; a same-mtime mutation probe
must explicitly target the producer or force a map renderer to exercise this check.

Snakemake parameters include relevant code/environment digests, while plain file inputs carry dependency
freshness. Source membership, selection, window or policy changes reschedule the producer. A changed
in-place input with preserved timestamps must still fail consumer validation; the prescribed repair is an
explicit rerun of `produce_historical_map_reference`, not reuse of a stale record. If extraction itself is
stale, rerun its source rule first. Existing climate-store freshness ends at its catalog/region contract;
changes behind unchanged catalogs require explicit extraction, as documented by `climate_store_rule()`.

Reuse is allowed only after full identity and record validation. Never infer it from file existence.
Publish the one JSON through an attempt-private sibling file and atomic replacement after validation.
Do not promise previous-record survival through Snakemake failed-output cleanup; failure must leave no
record that passes validation as the new result. Consumer figures similarly retain no claim of new success.

Owned runners already use `archive_lock(project_root, "project-execution")` in
`shared/workflow_archive_launch.py` and `scripts/run_workflows.py`. Retain that serialization across
extraction, publication and rendering. The producer does not reacquire its parent's lock. Simultaneous
owned runs for the same root serialize or fail lock acquisition; different roots are independent.
Windows network project roots are already refused by this lock implementation. Direct concurrent
Snakefile invocations are outside this guarantee and must not be advertised as supported. Do not add a
second lock service or claim managed-run conformance.

## 6. Drawing contract

Accept regular, monotonic, rectilinear geographic grids; retain ascending or descending coordinates and
one-cell dimensions with explicit native resolution. Reject missing resolution, invalid extents, incompatible
units/CRS, curvilinear grids, or a frame crossing the antimeridian. Preserve the existing source units:
`degC` for temperature and `mm/year` for precipitation/PET. Do not introduce a second unit conversion.

Use the selected frame's midpoint latitude for the fixed degree aspect, `1/cos(latitude)`. Both routes
receive that same aspect; do not recompute it from model/source field latitude. Reject singular polar
frames. Longitude/latitude ticks use a deterministic nice step: choose the smallest of
`{1, 2, 2.5, 5, 10} * 10**k` at least axis-span/4, retain multiples inside the closed frame, round to
12 decimal places and normalize zero. Store these positions; draw subtle geographic grid lines there.
Preserve coordinate axis labels, minus formatting, cell-edge treatment and overlay/label styles.

Class policy retains today's increments: 100 mm/year for amounts; temperature 0.2 degrees for spans up
to 1.6 degrees, 0.5 through 4 degrees, otherwise 1 degree. For a constant field extend the working high
value by 1 mm/year or 0.2 degrees before selecting the step. Round lower/upper bounds outward to step
multiples, using integer step indices to avoid duplicate floating boundaries. Preserve raw extrema too.
Use all boundaries as colorbar ticks; no silent bin/tick cap. Dense scales that fail readability return
to G1 for a revised policy rather than quietly dropping values or classes.

Intervals are left-closed/right-open except the final class, which includes its upper boundary. Strictly
below/above the outer boundaries uses explicit under/over colors; clipping to endpoint colors is forbidden.
Retain the current sequential ramps and darkest single-class treatment. Proposed extensions are pale
`#f7fbff`/dark `#041f4a` for precipitation/PET and `#fffbe6`/`#a50f15` for temperature. Every available
reference colorbar shows both rectangular extensions, with identical geometry across WF0/WF1 even if
a particular field has no exceedance. Captions give strict under/over counts within displayed support.

Missing source cells and unavailable inside-basin forcing cells stay gray; outside-model cells stay white.
Uncovered frame area is white and identified separately in captions. If a variable has no finite historical
pool, draw an unavailable-reference map without numerical colorbar; do not invent a 0–1 scale or fall
back to forcing limits. Render finite inside cells with a light neutral hatch, retaining gray for missing
cells and white outside the basin. A finite forcing field remains scientifically available but unscaled;
state that distinction in metadata and caption. A missing field can use an available common colorbar.
No new PNGs are emitted for source-variable combinations absent from today's inventory.

## 7. Files, products and compatibility

These are proposed changes, not generated results. Trees show only affected branches; `+` adds,
`~` changes, and `=` retains a contract.

```text
blueearth_cst/
  plotting/prepared_maps.py                                     + Portable arrays/records and raster artist
  climate_analysis/source_map_fields.py                         + Shared source preparation, existing science
  climate_analysis/diagnostic_maps.py                           ~ Retain annual_fields; retire migrated artist
  climate_analysis/compute_climate_diagnostics.py               ~ Call source preparation helper
  climate_analysis/diagnostic_render.py                         ~ Consume reference for maps only
  climate_analysis/plot_climate_diagnostics.py                  ~ Forward declared reference inputs
  model/plot_map_forcing.py                                     ~ Load reference instead of selecting frame
  model/forcing_figures.py                                      ~ Reference maps; retain temporal preparation
  shared/map_reference.py                                       + Resolver, producer spec, identity, validation
  shared/produce_map_reference.py                               + Snakemake script entry and JSON publication
  shared/config_composition.py                                  ~ Register project-owned mapping
analyze_climate.smk                                             ~ Shared reference rule and map dependency
build_model.smk                                                 ~ Candidate extraction and reference rule
config/templates/project_config.template.yml                    ~ Document optional project map policy
config/templates/project_config.analyze_climate.template.yml    ~ Explain completeness compatibility
dev/reference/plot-style.md                                     ~ Approved common frame/scale conventions
docs/site/guide/configuration.qmd                               ~ Explain project policy and custom migration
docs/site/toolbox-reference/workflow-analyze-climate.qmd        ~ Explain map reference support
docs/site/toolbox-reference/workflow-build-model.qmd            ~ Explain extra candidate work and shared scale
```

```text
<project_dir>/
  data/climate/historical/
    _engine/map_reference.json                                  + Shared deterministic machine reference
    <source>_<window>/extract_historical.nc                     = Existing store; WF1 may now create candidates
    <source>_<window>/basin_cells.csv                           = Existing native basin-cell inventory
    <source>_<window>/orography.nc                              = Existing conditional forcing-store sidecar
    <source>_<window>/tables/annual_climatology.nc              = WF0-only retained scientific map fields
    <source>_<window>/plots/*.png                               ~ Existing source maps adopt reference
    <source>_<window>/plots/figure_captions.md                  ~ Explain frame and pooled support
    <source>_<window>/plots/_engine/figure_captions.json        ~ Existing path; add map methods
  models/hydrology/wflow/forcing/plots/
    forcing_<variable>_map.png                                  ~ Three maps adopt shared classes/frame
    forcing_<variable>_annual.png                               = Three annual charts
    forcing_<variable>_monthly.png                              = Three monthly charts
    figure_captions.md                                          ~ Map captions only
    _engine/figure_captions.json                                ~ Existing path; add map methods
```

No user command, PNG filename, NetCDF format or existing table/caption path is renamed. The JSON record
and config mapping are additions; scientific methods are retained subject to the explicit completeness
guard. Retire WF0 render-time limit pooling, WF1 forcing-derived limits, and adapter-local frame selection.
Retire `visible_values()` only after confirming no callers remain; replace its use with frame intersection.
Remove migrated drawing implementation, retaining a compatibility wrapper only if caller search proves need.
Do not delete old generated outputs. WF0 optional captioned maps adopt the same reference and layout.

## 8. Alternatives and G1 choices

1. **Proposed: selected-frame pooling.** Scales cover historical cells in the shared viewport and remain
   pooled. Changes WF0 display extrema and clipping relative to current output; requires explicit review.
2. **Keep padded-basin pooling.** Smaller visual change for multisource limits and scientifically defensible
   as a basin-context scale. Prefer if the owner values that comparison population; then acknowledge
   visible historical cells outside the pooling area and use extensions for them. It cannot claim that
   every visible historical value defines the shared scale. The single-grid exception still needs resolution.
3. **Selected-source-only scale.** Lowest WF1-only cost and useful when model-input fidelity is the sole
   question. It violates the settled pooled-candidate requirement and is not proposed for this increment.
4. **Depend on all WF0 diagnostics.** Reuses existing map tables and configuration, but WF1 alone would
   require a disabled workflow's settings and unrelated temporal computations. Prefer only if a future
   owner intentionally makes WF0 mandatory. A persisted per-source map cache is another optimization,
   justified only if measured duplication outweighs its additional outputs and identity contract.

G1 decides the frame-intersection pooling replacement; shared config/compatibility guard; JSON ownership
and fields; explicit empty-scale behavior; tick and extension appearance; and extra candidate work in WF1.
Scientific review must judge cell/year support, source identity, units and PET interpretation before G1.
G2 concerns the exact externally reviewed revision. Neither gate has passed in this draft.

## 9. Verification, handoff and limits

### 9.1 Claims, inputs and evidence

Before implementation capture every affected WF0/WF1 map, optional captioned variant, map-field arrays,
valid-year counts, metadata and nine-file forcing inventory from `22fbe441` under matched rapid inputs.
Retain temporal-chart captures to establish untouched preparation and rendering. Existing chart-only
captures do not cover maps. Keep the reference capture read-only and render candidates to another root.

| Claim | Check | Input/output case | Distinct coverage |
|---|---|---|---|
| Native science retained | Exact arrays/counts/NaN masks | Matched pre/post capture | No display oracle |
| Order independence E8 | Equal JSON and artist settings | Fresh A: WF0→WF1; B: WF1 only | Disabled WF0 |
| Pooled support correct | Independent intersection/extrema oracle | Unequal grids | Frame vs basin |
| Classes coherent | Boundaries and under/over counts | Constant/missing/exceeding | Edge conventions |
| Identity safe | Mutate each identity input; stale read refused | Named scratch copies | Same-mtime edits |
| Publication safe | Interrupt and serialize two owned runs | One scratch project | No partial reuse |
| Visual acceptance | Inspect all affected maps and captions | Fresh rapid root | Clipping/grid/labels |
| Products compatible | Compare inventories and temporal metadata | Same rapid root | No extra simulation |
| Portable core | Import/render with NumPy/Matplotlib only | Scratch standalone probe | No CST IO/backend |
| Cost E9 | Time IO/hash/prep; peak memory | Fresh WF1 and larger input | Unmeasured now |

Include descending and one-cell grids, invalid resolution, all-missing source/variable, precipitation-only
candidates, non-January years, truncated candidate records, custom WF0 settings, unavailable historical PET,
and forcing/reference periods that differ. Unsupported geometry/unit cases must fail clearly. Verify
temperature eligibility, PET and optional orography through the real preparation path, not invented metadata.

Use one-time scratch probes and the existing figure comparison viewer; add no permanent figure tests.
Producer/configuration changes trigger the live cross-workflow ladder: focused contract tests while editing,
then full software and fresh all-five execution gates at batch landing. A passing full gate replaces fast.
Reuse the fresh all-five root for map/inventory/caption checks; the WF1-only root adds the distinct route.
The stale numerical baseline is not a display acceptance oracle. No checks have executed for this proposal.

Runnable workflow probes use existing wrappers; `$cfg`, `$rootA`, `$rootB` are recorded absolute paths:

```powershell
pixi run python scripts/run_workflow.py analyze_climate --config $cfg --project-dir $rootA --dry-run
pixi run python scripts/run_workflow.py build_model --config $cfg --project-dir $rootB --dry-run
pixi run python scripts/run_workflow.py analyze_climate --config $cfg --project-dir $rootA --cores 3
pixi run python scripts/run_workflow.py build_model --config $cfg --project-dir $rootA --cores 3
pixi run python scripts/run_workflow.py build_model --config $cfg --project-dir $rootB --cores 3
```

The fresh all-five gate can supply A instead of repeating these executions. For B, use a captured config
variant disabling WF0 while retaining identical project climate choices and WF1 settings. Run targeted
reference-only DAGs with `--target produce_historical_map_reference`; prove no model/temporal jobs enter
that subgraph. Redirect logs to files. Evidence records exact candidate, command, config/input hashes,
environment, output root, numerical findings, visual verdict and any required skips under the task home.

### 9.2 Specialist ownership and capability mapping

After G2, a scoped `python-engineer` brief owns preparation extraction, core renderer, shared producer,
configuration and DAG wiring. `model-validator` owns scientific support/unit/eligibility verdicts and
pre/post numerical acceptance; the requesting owner accepts appearance. `model-builder` exercises the
WF1-only producer route if the implementation coordinator needs specialist execution support.

The affected stable slots are `data_adapter` and `orchestrator`: current bindings are the pinned existing
HydroMT/source-preparation code and Snakemake workflow code; proposed bindings add reference preparation
and declared dependencies at a new implementation commit. Python engineering implements both;
model validation authorizes science, and CST architecture authorizes interface/invalidation checks.
No engine package binding, managed manifest schema or stage-graph version changes. Historical QA remains
upstream of simulation; projections do not enter this producer. The other eight capability slots retain
their existing bindings or applicability. Do not present this auxiliary JSON as a managed-run manifest.

This proposal serves WF0 historical candidate comparison and WF1 forcing QA across basins. It does not
change WF2 maps, geographic model-property maps, R/WF3 artists, simulation physics, source catalogs or
HydroMT internals. Exact source preparation, declared orography identity and both workflow routes still
need execution evidence. E8 is falsified by any record/frame/class difference under matched inputs;
E9 has no acceptance threshold yet and needs measured cost before any performance claim or optimization.

## 10. Revision log

- 2026-10-10, v1: first provisional producer/rendering design from intake and source inspection. Explicit
  G1 decisions cover pooling support, project policy and record/output contracts. No review or acceptance
  is claimed; later reviewed revisions are retained by the driver under the task-owned lifecycle.
