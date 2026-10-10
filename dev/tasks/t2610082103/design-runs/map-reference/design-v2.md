# Shared historical map reference

Status: revised v2 for independent review; G1 framing approved; G2 pending. Date: 2026-10-10.
Lifecycle: task-owned review; reviewed versions are immutable and acceptance lives in `status.md`.
Canonical home: `dev/tasks/t2610082103/design-runs/map-reference/`; scratch is the author workspace.
Reading guide: sections 1–3 and 8 carry the owner decisions; the remaining detail fixes implementer contracts.
The length exception keeps exact identity, scientific support and independent repair checks in one record.

## 1. Overview

Produce one historical map reference from the project's declared climate candidates. WF0 source maps and
WF1 forcing maps read its frame, coordinate ticks and color classes. Running WF1 alone produces the same
reference as running WF0 followed by WF1 under matched data and settings. Existing figure filenames remain.

The researcher still chooses candidates, selected forcing, historical window and reporting year in project
config. WF0 remains optional. WF1 now needs historical summaries of every candidate to establish pooled
scales, even though only the selected source supplies model forcing. Measure that extra cost; no acceptable
time or memory budget has been asserted. Retained WF0 map fields carry a preparation identity checked
against the reference before rendering, so fresh scales cannot certify stale source arrays.

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

G1 selected the common source frame, project-owned completeness with a 0–27 missing-day monthly bound,
and preservation of auxiliary CHIRPS arrays with honest source-role contributions. This revision specifies
those choices and the bounded field-provenance repair. Temporal science and simulation inputs stay intact.

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

Decision D1 changes display pooling: padded-basin support and its single-grid special case cannot
guarantee a scale covering every cell in a common selected-source viewport. Keeping them would preserve
some old limits but leave visible historical cells outside the scale. G1 approved this replacement;
section 8 retains the alternative and its tradeoff.

Scientific support remains source-specific. CHIRPS candidates contribute precipitation only, including
when selected CHIRPS stores contain borrowed forcing variables. Genuine temperature carriers contribute
temperature and derived source PET when available. A missing variable is a recorded exclusion, not zero.
Available full reporting years can differ by source and cell. Source maps retain those differences.
Decision D3 preserves selected CHIRPS's retained auxiliary temperature/PET arrays, if present, including
their values, masks and counts. Reference contribution filtering uses source role after preparation; it
does not delete or rewrite those arrays. Extra CHIRPS without companions remains precipitation-only.

### 2.3 Units, reporting years and completeness

Source preparation accepts ordered unique midnight daily Gregorian dates and reindexes from the first
through last extracted date to daily frequency; absent dates become missing. A full reporting year spans
every calendar day from month `m0` day 1 to the next year's same date, with `m0` an integer 1–12. Its label
is the start year, including non-January starts. Partial boundary years do not contribute. Record requested
window, actual extraction span and full reporting-year labels separately; per-cell eligible counts do not
assert that cells share the same eligible years.

For each cell and variable, eligibility requires missing original daily values to be within the monthly
tolerance in every calendar month AND within the annual tolerance across the reporting year. Tolerated
gaps are filled with that calendar month's observed mean. Precipitation/PET sum those daily amounts;
temperature takes the daily mean. The displayed climatology is the arithmetic mean of eligible annual
values; zero eligible years gives NaN, count zero and an unavailable mask. Preserve the current NaN-based
eligibility/counting and nonfinite display mask; do not silently unify source and forcing infinity handling.

Extracted precipitation and derived PET are daily amounts in mm; annual fields are `mm/year`, not daily
rates or a 365-day normalization. Temperature is Celsius and the field unit is `degC`. The existing
basin-mean temperature gate accepts case-insensitive `degc`, `celsius`, `degree_celsius`,
`degrees_celsius`, or `°c`. Legacy `k`/`kelvin` is accepted only with catalog `unit_add.temp: -273.15`
and a nonempty extraction `region_geojson_sha256`: values are already Celsius, with no second conversion.
Empty basin values, unresolved units, or basin-mean extrema outside [-100, 70] suppress genuine source
temperature and source PET. This gate does not validate every viewport cell. Source PET retains the
existing de Bruin path with source orography as both elevation arguments; it is derived, not observed.
It need not equal model PET. Missing required PET inputs fail preparation, not silently change its method.

## 3. Configuration and producer ownership

### 3.1 Project-owned historical reference settings

Propose one optional closed mapping, `climate.map_reference`, in the project config:

```yaml
climate:
  map_reference:
    max_missing_days_month: 3
    max_missing_days_year: 15
```

Decision D2: defaults remain 3/15. `max_missing_days_month` is an integer in [0, 27];
`max_missing_days_year` is any nonnegative integer; reject booleans, floats and unknown keys. There is no
finite maximum annual setting; 366 already saturates the possible missing days in a supported full year.
The monthly bound keeps at least one observation in every eligible month, including 28-day February.
Reject 28 or greater before scheduling a reference or WF0 map. This restricts accepted configuration;
it does not change `diagnostics.annual()` or other temporal calculations. Register the
mapping as project-owned in `shared/config_composition.py` and reject it in workflow files. The shared
resolver owns these defaults. Do not add a scale-policy menu: frame, support and classes have a versioned
policy in code. `climate.window` is the requested extraction window; `water_year_start` governs annual
labels. WF0 diagnostic `reference_period` and `comparison_period` do not select map years today and
must not silently acquire that meaning.

WF0's existing diagnostic completeness continues to govern all its scientific summaries. Its effective
values must equal the shared historical reference values whenever WF0 renders maps. Reject disagreement
at DAG construction with both key paths and values. For existing custom WF0 configurations, copy those
two values into the project mapping when the monthly value is at most 27. A larger old tolerance cannot
qualify for shared maps: the owner must select supported matching values, with any resulting temporal
change explicit. Do not clamp values or change the old aggregator. Retain WF0's keys. Never read a disabled
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
do not silently claim complete identity from a catalog filename or add a remote storage system. The same
resolved per-source data/catalog/orography dependency specification must feed WF0's existing compute rule,
the reference producer and adapter validation. Declare those files on both producers, with the same
preparation-code/environment digests in parameters; catalog-backed DEM replacement must rebuild both.

Parameters: selected-first candidate order and roles, selected frame authority, requested window, reporting
start month, completeness, source preparation/scale policy versions, and relevant code/environment digests.
No workflow name, WF0 enable flag, plot inventory or absolute project root enters the reference semantics.

WF0 rendering declares the JSON, its current validation inputs and retained fields as inputs in addition
to existing tables and overlays. It validates field identities as well as the reference. Preserve pooled
table dependencies used by non-map plots; remove only map-only dependencies after caller inspection.
WF1 `plot_model_forcing` declares the JSON and its validation inputs, replacing its direct frame selection.
Each renderer validates the expected record before saving any figure. Both terminal inventories reach the
producer through explicit inputs; no directory scan, existing PNG, WF0 diagnostic metadata or figure order
is a producer input. The producer does not schedule WF0 temporal diagnostics or comparison tables.

## 4. Small interfaces and persisted record

### 4.1 Preparation versus portable drawing

Extract existing source-map preparation into `climate_analysis/source_map_fields.py`. Its
`prepare_source_map_fields(source_spec, m0, completeness)` returns the existing annual-field dataset,
lineage and its preparation identity. `source_spec` carries climate/cell paths, source role, ordered
catalogs and resolved orography inputs from section 3.2. Reuse the current unit gate, raw precip/temp
selection, source-grid PET machinery and `annual_fields()` without changing their numerical method.
WF0 compute and the shared producer call it. Both seal the same dataset identity before use (section 5, D4).
Producer reduces one source at a time, retains its identities in JSON and discards arrays afterward.
Initial WF0 execution repeats source-map reductions; measure that duplication before proposing optimization.

Do not use WF0's existing `tables/annual_climatology.nc` opportunistically: its presence alone establishes
neither compatible settings nor provenance. It remains WF0-owned, written for inspection and consumed by
WF0 maps only after identity checks; the reference never depends on its existence. Add identity attributes
to this existing NetCDF, including all retained auxiliary fields in its payload digest, without a new cache.
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

The closed schema-v1 record contains `schema_version`, `reference_id`, `identity`, `frame`, `variables`, and
`provenance`. `identity` contains the settings and input identities from section 5, with `source_preparations`
keyed by candidate source. Each entry has `preparation_id`, `preparation_identity` and `fields_digest`,
including sources contributing no finite values. `frame` contains selected source, extent, explicit ticks,
aspect and `crs: EPSG:4326`. `variables` has exactly
`precip`, `temp`, `pet`, each with units, status/reason, finite pool count, contributing source summaries,
excluded source reasons, extrema, boundaries, ticks and the resolved palette/under/over/missing colors.

Each source summary records source role, effective dates, present scientific variables, grid dimensions
and cell edges digest, intersecting/finite/unavailable cell counts, and minimum/maximum eligible-year
counts over finite contributing cells, full reporting-year labels, `preparation_id` and `fields_digest`.
These IDs must match the source's entry in `identity.source_preparations`. No finite values means null
extrema/count range and empty boundaries/ticks, with a reason. Boundary-touching counts need not represent
positive visible area.
Missing JSON numbers are `null`; NaN/Infinity are forbidden. Counts describe cells, not independent samples.

`provenance` records logical input roles, relative store paths, input digests, source/catalog identities,
preparation method, policy versions and environment identity. Do not place timestamps, invocation IDs,
absolute roots or workflow names in the record: exact bytes must be equal across the paired-root check.
Those execution facts remain in existing workflow logs/run records. Consumers reject unknown versions.

Readable explanations remain in existing `figure_captions.md`. Existing figure JSON gains, for maps only,
`reference_id`, reference path relative to project root, reference/frame support, reference and field periods,
both completeness policies, units, unavailable reason, and in-frame under/over cell counts. Source-map
metadata also carries verified `preparation_id` and `fields_digest`; borrowed arrays remain auxiliary,
never described as CHIRPS temperature/PET observations or contributions. Existing caption JSON paths
remain for compatibility; this increment does not migrate their older `plots/_engine/` placement.

## 5. Identity, invalidation and publication

### 5.1 Reference and per-source preparation identities (D4)

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

For each source, `preparation_identity` records schema/policy versions, source and variable roles, requested
and extracted dates, reporting month/full-year labels, completeness, ordered catalog byte digests, concrete
consumed climate/cell/orography input digests, shared preparation code closure and environment identities.
Its `preparation_id` hashes that object with the same canonical JSON recipe. Exclude frame/classes,
candidate membership/order, WF0-only diagnostic settings, workflow entry point and output location from
this per-source identity. These can alter the reference or other diagnostics without altering source fields.
Both producers build this identity from the same resolved specification and current bytes.

The shared preparation closure starts with `source_map_fields.py`, `diagnostic_maps.py`, `diagnostics.py`,
`diagnostic_tables.py`, `diagnostic_settings.py`, `plot_climate_source.py`, `shared/climate_parity.py` and
`shared/grid_cells.py`, plus shared identity/dependency logic in `shared/map_reference.py`. Qualify and
record its transitive local preparation dependencies at implementation.
Both producer rules declare this exact closure and its digest, plus `pixi.lock`, `Manifest.toml` and actual
loaded package versions; reject an environment inconsistent with its locks. Reference identity additionally
covers the reference producer/resolver and scale/frame modules. Record the explicit lists; changing a list
changes identity. Do not use a whole-checkout commit as a cache key or put absolute paths into identities.

`fields_digest` binds the actual prepared payload, independently of its provenance tag. Hash a canonical
JSON inventory of sorted variable names, dimensions/shapes, per-array SHA-256 and scientific attributes:
units, native resolution, `reporting_year_label`, `period_start` and `period_end`. Extraction span and full
year labels live in preparation identity. Include coordinates and every retained precip/temp/pet value,
valid-year count and unavailable mask, including CHIRPS auxiliaries. Hash arrays in latitude/longitude
dimension order, C order: coordinates/values as little-endian float64, counts as int64, masks as uint8.
Normalize signed zero to positive zero and all NaNs to float64 quiet-NaN bits `0x7ff8000000000000`.
Preserve signed infinities in binary values; JSON contains only their digests. Exclude encoding/compression
and the identity attributes themselves. The producer and reopened NetCDF must yield exactly the same digest.

Persist four global attributes in WF0's existing `annual_climatology.nc`: `map_preparation_schema` (1),
`map_preparation_identity` (canonical JSON string), `map_preparation_id`, and `map_fields_digest`.
For example, `identity.source_preparations.era5` holds
`{preparation_id, preparation_identity, fields_digest}`; the NetCDF's latter three attributes hold those
same values, and source-map caption JSON repeats the two verified digests. Hash values are computed from
content, never placeholders. Existing scientific variables and period attributes remain. Old NetCDFs
without these attributes are unqualified and require WF0 compute
regeneration before map rendering; other retained diagnostics keep their existing ownership and formats.

### 5.2 Validation and repair

Hash actual input bytes, including resolved catalog-backed orography, code and locks; never accept size or
mtime as identity. Stream hashes and measure that cost separately. Both producers check identities before
preparation and again before publication; changed inputs abort publication. WF0 seals attributes with its
arrays, then verifies the reopened file's payload digest. Reference preparation independently obtains the
same pair of digests; it never trusts a retained field file to establish them.

Before saving any figures, each adapter validates reference schema, payload digest, settings/policies and
all current input/code/environment identities. WF0 additionally requires each consumed field's preparation
identity to equal both the current expected identity and the reference's per-source identity. Recompute its
actual payload digest and require equality with its stored digest and the reference's `fields_digest`.
Missing attributes, stale code, catalog/DEM changes or tampered arrays fail with the source, affected field
target and reason. Recheck consumed identities before publication. There is no local rescaling or metadata
retagging repair. WF1 still prepares its model field in the existing invocation; it does not consume WF0
fields or assert their preparation identity for model forcing.

Ordinary changes use matching declared climate/cell/catalog/orography/code/lock inputs on the reference
and affected WF0 compute rules, and matching preparation digests/settings in their parameters. Renderers
declare the same validation inputs. Source membership/selection/frame policies also reschedule the
reference. Verify actual scheduling; an identity described only in JSON is not a DAG dependency.

For preserved-mtime mutations, rebuild only the reference and force WF0 rendering: validation must reject
old fields even when their producer appears up to date. Supported repair explicitly forces each affected
source's existing WF0 compute rule AND `produce_historical_map_reference`, then rerenders affected maps
under an owned runner. The compute rule also rewrites its existing temporal products without changing
their method. If stores are stale, force their extraction rules first; catalog/region freshness alone does
not detect changed backing data. A same-mtime DEM replacement needs both preparations rebuilt but no
extraction when that DEM is consumed only at preparation. Never infer freshness from a successful no-op:
retained figures are not read or certified until an explicit renderer/producer invocation exercises checks.

Publish reference JSON and the retained map NetCDF each through a private sibling and atomic replacement
after validation; no cross-file atomicity is claimed. Any mixed pair must fail the consumer checks. Retain
no claim of new figure success after failure. Snakemake failed-output cleanup can remove prior outputs;
do not promise their survival. Reuse requires full identity and payload validation, not file existence.

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
  climate_analysis/compute_climate_diagnostics.py               ~ Prepare fields and seal existing NetCDF
  climate_analysis/diagnostic_render.py                         ~ Validate reference and field identities
  climate_analysis/plot_climate_diagnostics.py                  ~ Forward declared reference inputs
  model/plot_map_forcing.py                                     ~ Load reference instead of selecting frame
  model/forcing_figures.py                                      ~ Reference maps; retain temporal preparation
  shared/map_reference.py                                       + Resolver, producer spec, identity, validation
  shared/produce_map_reference.py                               + Snakemake script entry and JSON publication
  shared/config_composition.py                                  ~ Register project-owned mapping
analyze_climate.smk                                             ~ Shared rule; match field input/code dependencies
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
    <source>_<window>/tables/annual_climatology.nc              ~ WF0-owned fields; add identity attributes
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

No user command, PNG filename, NetCDF format or existing table/caption path is renamed. Users receive the
new JSON record and optional project config mapping. Existing map NetCDFs gain provenance attributes;
old files must be regenerated, preserving arrays under supported matching settings. Existing caption JSON
gains map methods and verified IDs; readable captions explain source support, periods and scale limits.
The config parser now rejects missing-month values above 27 and WF0/reference disagreement; custom users
migrate explicitly as in section 3.1. Maintainers repair stale fields and reference together (section 5.2).
Retire WF0 render-time limit pooling, WF1 forcing-derived limits, and adapter-local frame selection.
Retire `visible_values()` only after confirming no callers remain; replace its use with frame intersection.
Remove migrated drawing implementation, retaining a compatibility wrapper only if caller search proves need.
Do not delete old generated outputs. WF0 optional captioned maps adopt the same reference and layout.

## 8. Alternatives and G1 choices

1. **Selected: selected-frame pooling (D1).** Scales cover historical cells in the shared viewport and
   remain pooled. G1 approved changes to WF0 display extrema and clipping relative to current output.
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

G1 approved D1, project policy and its equality guard, JSON ownership, empty-scale display, ticks/extensions,
and added WF1 candidate work. D2 selects the 0–27 monthly bound rather than changing the annual algorithm;
the latter would admit more policies but require scientific approval for changed eligibility. D3 retains
CHIRPS auxiliary arrays and corrects their pooled contribution. D4 repairs field identity within existing
ownership; a separate map cache or mandatory WF0 would require a G1 return and is not selected.

Decision D5 makes E9 a measurement objective: time extraction, hashing, reductions, consumer validation
and repeated WF0 reductions separately, with peak memory, candidate count, grid sizes and window. No
time/memory acceptability threshold exists, and no performance claim follows from measuring them. A future
optimization or budget decision needs the measured scaling evidence. G2 remains pending exact-version
independent review and owner approval; this document authorizes no implementation.

## 9. Verification, handoff and limits

### 9.1 Claims, inputs and evidence

Before implementation capture every affected WF0/WF1 map, optional captioned variant, map-field arrays,
valid-year counts, metadata and nine-file forcing inventory from `22fbe441` under matched rapid inputs.
Retain temporal-chart captures to establish untouched preparation and rendering. Existing chart-only
captures do not cover maps. Keep the reference capture read-only and render candidates to another root.

| Claim | Check | Input/output case | Distinct coverage |
|---|---|---|---|
| Native science retained | Exact arrays/counts/masks | Matched pre/post | D3 auxiliaries included |
| Order independence E8 | Equal JSON and artist settings | Fresh A: WF0→WF1; B: WF1 only | Disabled WF0 |
| Pooled support correct | Independent intersection/extrema oracle | Unequal grids | Frame vs basin |
| Classes coherent | Boundaries and under/over counts | Constant/missing/exceeding | Edge conventions |
| Identity safe D4 | Stale reference/fields refused | Incremental scratch root | Same-mtime repair |
| Publication safe | Interrupt and serialize two owned runs | One scratch project | No partial reuse |
| Visual acceptance | Inspect all affected maps and captions | Fresh rapid root | Clipping/grid/labels |
| Products compatible | Compare inventories and temporal metadata | Same rapid root | No extra simulation |
| Portable core | Import/render with NumPy/Matplotlib only | Scratch standalone probe | No CST IO/backend |
| Cost E9/D5 | Separate timings; peak memory | WF1/WF0 and larger input | Measurement only |

Use independent known-answer cases, not only pre/post parity:

- **D2 missingness:** a full all-NaN leap year and a full otherwise-1-mm/day nonleap year with wholly
  missing February, at 27/366 and 27/1000, give unavailable annual amounts, zero eligible counts and no
  finite pool contribution. 366 saturates the unbounded annual setting; 1000 checks that larger values
  cannot bypass the monthly limit. Probe the pinned old aggregator at 31/366: its erroneous 0 and 337
  totals must fail this oracle. Intake E11/E12 measured these cases at 31/366 and 27/366; proposed parser,
  map fields and counts are not yet tested. Reject month 28, negative values, booleans and fractional
  values. At 27 missing February days, the remaining 1-mm observation fills to 28 mm in a valid month;
  include an annual-total missingness failure with individually valid months and accepted 0/0 and 3/15.
- **D3 real preparation:** selected enriched CHIRPS and extra unenriched CHIRPS both contribute only
  precipitation. Preserve selected auxiliary arrays/counts/masks, native precipitation and genuine ERA5
  temperature/source-PET arrays exactly under matched settings. Exercise Celsius, catalog-normalized
  legacy K and unresolved units through the real gate; missing PET inputs must not masquerade as a
  supported derived field. Pin concrete orography dependencies before claiming these cases qualified.
- **Years and support:** independently enumerate leap/non-January years and exclude truncated ends;
  include missing dates, unequal grids, a boundary-only extreme, descending axes and one-cell dimensions.
  Verify reported full years, cell-specific counts, intersection populations and extrema; reject invalid
  resolution and unsupported geometry. Preserve the observed source/forcing infinity-handling difference.
- **Classes and meaning:** probe every boundary and adjacent floating values, especially exact final
  upper endpoint, constant fields, all-missing variables and strict under/over counts. Check gray missing,
  white outside/uncovered and finite-but-unscaled hatching independently. Use different forcing/reference
  periods, unavailable historical PET and custom supported WF0 completeness for captions and equality guards.
- **D4 incremental repair:** begin with complete WF0 outputs. Mutate extraction bytes preserving mtime,
  rebuild only the reference, then force rendering while retaining old fields: it must reject before any
  figure success. Force affected compute plus reference and rendering; compare arrays, IDs and payload
  digest against fresh preparation with the modified inputs. Repeat for catalog-backed orography, both
  ordinary replacement (dry-run schedules both producers) and preserved mtime (stale fields rejected).
  Also vary catalog text, preparation code, locks and settings; verify matching ordinary dependencies and
  stale-identity refusal. Corrupt retained arrays alone, omit identity attributes, and alter stored tags:
  each must fail. This explicitly detects the old fresh-reference/stale-field sequence, not just JSON age.

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
E9 is measurement only (D5). Actual PET dependency resolution, complete local code closure, package/lock
consistency, incremental repair, route equivalence and visual readability remain implementation gates.
Failure to expose consumed source-PET files returns that interface gap to G1; do not broaden ownership.

## 10. Revision log

- 2026-10-10, v1: first provisional producer/rendering design from intake and source inspection. Explicit
  G1 decisions cover pooling support, project policy and record/output contracts. No review or acceptance
  is claimed; later reviewed revisions are retained by the driver under the task-owned lifecycle.
- 2026-10-10, v2: apply G1's bound and auxiliary-array rulings (D2/D3), make E9 measurement-only (D5),
  and bind current inputs, retained fields and reference through preparation/payload identities (D4).
  Add independent falsifiers and bounded migration/repair. Original finding dispositions are in the
  append-only ledger; independent review and G2 remain pending. No implementation evidence is claimed.
