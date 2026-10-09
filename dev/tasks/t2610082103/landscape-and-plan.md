# Shared scientific plotting: landscape and agreed development plan

Status: direction agreed on 2026-10-10; detailed implementation design pending.
Lifecycle: temporary task-owned planning record; preserve needed decisions before task closure.
Owner: t2610082103. Scope: WF0–WF3 inventory; Python rendering first.

## 1. Direction and intent

Develop a small Matplotlib library inside CST first, with a clean boundary that allows later extraction.
The eventual audience extends beyond BlueEarth CST to climate, hydrology and water-resources researchers.
The initial product is a shared rendering system with helper functions, style presets and explicit rules
for axes, legends, physical dimensions, aspect ratios and export. Grow through demonstrated use cases.

The user approved this direction and the plan below on 2026-10-10, asked to save the extensive assessment,
and authorized starting work with focused specialist/model handoffs balancing cost and effectiveness.
Python first was explicitly selected; R/WF3 integration is deferred. Direction approval is recorded here;
the detailed design and its review identity remain separate.

WF0 and WF1 already share several renderers. The immediate task is to stabilize those interfaces,
separate scientific preparation from drawing, and resolve remaining style/export differences.

## 2. Source-based landscape

Inspection baseline: session-1 HEAD `07288e94` (2026-10-10). Source inspection only: no tests or renders ran.
The cst-architect independently traced active producers and consumers. This is not visual validation.

| Workflow | Current landscape | Consequence |
|---|---|---|
| WF0 | Maps, coverage, annual/climatology, timing, SPI, droughts, extremes, trends | Main foundation |
| WF1 forcing | Reuses WF0 map, annual and monthly artists | Stabilize existing interfaces |
| WF1 model/evaluation | Separate cartography; mixed older/newer evaluation styles | Preserve compositions |
| WF2 | Ensemble artists consume prepared tables; import WF0 common helpers | Migrate common imports |
| WF3 | External R weathergenr generates diagnostics; CST relocates images | Later integration |

### 2.1 WF0

`analyze_climate.smk` separates diagnostic computation, rendering and comparison.
`blueearth_cst/climate_analysis/diagnostic_render.py` dispatches `diagnostic_figures.py` and
`diagnostic_maps.draw_map()`. The suite includes maps, coverage, annual/climatology, timing, anomalies,
SPI, drought events, extremes, spells, autocorrelation, trends and precipitation–temperature plots.

The newer reviewed typography and common functions live in `diagnostic_figures.py`: `STYLE`, `new_fig`,
`year_ticks`, `ygrid`, `inside_legend`, `colourbar` and `add_caption`. Their ownership is workflow-specific
although their consumers already span workflows. The module also selects Agg at import and imports
scientific diagnostics. Its `View` object carries WF0-specific results and settings.

### 2.2 WF1

Forcing: `build_model.smk` calls `model/plot_map_forcing.py`, which calls
`model/forcing_figures.render_forcing_figures()`. This already uses `diagnostic_maps.draw_map`,
`diagnostic_figures.series` and private `_climatology`. `prepare_forcing()` retains scientific preparation.
Nine precipitation/temperature/PET map, annual and monthly PNG products are produced.

Spatial products: `shared/plot_spatial_maps.py` uses `cartographic_map.plot_raster_map()`. This is a
substantial separate Cartopy/GeoPandas/Xarray system with `RasterStyle`, profiles and older style defaults.
It already shares cartographic drawing across spatial products; it is not the current climate-map artist.

Evaluation: `model/plot_results.py` calls `shared/func_plot_signature.plot_basavg()` and
`shared/plot_evaluation.plot_station_evaluation()`. Basin/subbasin annual and seasonal figures reuse WF0
private `_annual_trends` and `_climatology`; hydrograph/performance sheets use newer `STYLE`, while
extremes retain older `_rc()` settings. Specialist compositions should stay separate.

### 2.3 WF2

`analyze_projections.smk` prepares analysis tables before `projections/plot_proj_timeseries.render_suite()`
dispatches `projection_suite_figures.render_product()`. Its artists import common tokens/helpers from WF0.
Products cover ensemble coverage, annual overview/trajectories, changes, seasonal/monthly products,
variability ratios, change clouds and sign agreement. Preserve their ensemble meaning during migration.

### 2.4 WF3

`generate_scenarios.smk` reaches `weathergen/generate_weather.R` through scenario-provider generation.
The R wrapper calls `weathergenr::run_weather_generator()`, including its evaluation pass. CST relocates
dynamically named PNG/PDF outputs by extension. This path has no CST-owned Python artists. Upstream
styling hooks were not audited; common WF0–WF3 rendering must not be claimed for the first release.

## 3. Architectural findings

- Two style foundations coexist: older `shared/plot_style.py` defaults and newer reviewed WF0 tokens.
- Reusable drawing depends on WF0 structures and private helpers. Extracting the entire module would
  export scientific diagnostics, backend side effects and workflow assumptions too.
- `shared/snake_utils.save_figure()` combines export with CST logging and global directory bundles.
  WF0/forcing also have direct save paths. Export mechanics can be neutral; logging remains in CST.
- Caption content and placement have different owners. Domain generators describe support and methods;
  shared code places supplied text. The current character-count caption wrapping/figure-height expansion
  does not establish preservation of plotting-area proportions without a render check.
- Climate and full cartographic maps are separate compositions. Do not merge both engines in the first
  slice or pull heavy geospatial dependencies into ordinary line-chart imports.
- WF1 uses historical native-grid extent but independent finite-value color limits; WF0 pools candidate
  values. An input-identified common map reference changes preparation and workflow dependencies.
- No active runtime caller of legacy `climate_figures.plot_climate_figures()` was found in shipped code;
  its naming/source-variable helpers remain active. Check all callers before any retirement.
- `test_climate_figures.py` and `test_shared_plot_scales.py` mostly cover older paths. No direct test
  references to `forcing_figures` or `prepare_forcing` were found. Existing tests are not evidence that
  the current forcing implementation or a new extraction has been exercised.

## 4. Proposed architecture

```text
Workflow preparation -> prepared values and explicit meaning -> shared rendering -> Figure
                                                                         |
                                                    CST export/output adapter -> report/publication
```

The renderer understands lines, bands, panels, labels and scales. Workflow code supplies their meaning.
A monthly renderer receives month order, central values, bounds, units and series identities. It does not
choose completeness thresholds, calculate percentiles or infer whether a band is spread or uncertainty.

| Component | Initial responsibility |
|---|---|
| Style presets | Typography, line weights, backgrounds and color defaults |
| Layout helpers | Physical dimensions, panels, spacing and panel labels |
| Axis/legend helpers | Year/month ticks, label conventions, grids and placement |
| Export helpers | Explicit figure, dimensions, resolution and output format |
| Chart functions | Annual series and monthly cycles with supplied bands/trends |
| Workflow adapters | Scientific preparation, captions, paths, manifests and logging |

Use ordinary functions and small settings objects. Return Matplotlib figures/axes so specialist figures
remain composable. No plugin system, universal chart schema or backend abstraction is needed initially.
Matplotlib's scoped styles and physical box-aspect support provide the needed mechanisms:

- https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.rc_context.html
- https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_box_aspect.html

### 4.1 Defaults versus scientific rules

Start with a CST preset reproducing `dev/reference/plot-style.md`: physical typography, restrained grids,
panel labels, caption separation and established legend treatments. Preserve figure-specific exceptions.
Units-only axes suit many CST figures; reference-relative axes and external standalone figures need
context. Square panels specify physical dimensions, not equal data scales. Dataset colors belong to the
CST preset; general palette/layout mechanisms belong to the core. Style changes do not authorize new
scientific methods, aggregation, weighting, masking or completeness rules.

## 5. Incremental development

1. Consolidate fundamentals in proposed `blueearth_cst/plotting/`: styling, sizing, ticks, legends and
   export mechanics. Migrate active WF0–WF2 consumers while preserving reviewed appearance. Separate
   caption content from placement. A bounded implementation design must identify the exact first slice.
2. Stabilize prepared-input annual-series and monthly-cycle interfaces, exercised by WF0 climate,
   WF1 forcing and WF1 hydrological summaries. Remove the dependency on the full WF0 `View` context.
3. Resolve maps separately. Retain both compositions initially; implement the task note's identified
   historical reference producer for extent, grids and color classes. Review its workflow dependencies
   and WF1-only pooled-candidate runtime cost separately.
4. Prove external reuse with a real example outside CST execution, then extract a distribution once a
   second use case establishes the public API. No Snakemake, HydroMT/Wflow, CST config/logging imports or
   backend selection at core import. Geospatial dependencies stay optional. R and interactive plotting
   follow demonstrated needs.

The existing task's 4–7 day estimate predates this broader aspiration. Treat it as historical planning
context, not a validated estimate for an independently distributed library.

## 6. Alternatives

| Approach | Benefit | Cost/tradeoff |
|---|---|---|
| Style-only package | Smallest effort | Leaves drawing/export duplication |
| Internal core, later extraction | Real callers establish interfaces | Needs enforced dependency boundary |
| Independent distribution now | Immediate packaging boundary | Premature API/release maintenance |

Selected direction: internal core with explicit dependency boundaries and later extraction.
No new chart backend, package name, publication format inventory or external release is approved here.
The offline report consumes figures/captions; report assembly does not own scientific rendering.

## 7. Acceptance and verification plan

Follow `dev/reference/validation-ladder.md`; match each claim to an input case and reusable output root.

| Claim | Check | Inputs / reusable output |
|---|---|---|
| Scientific values preserved | Pre/post prepared-value comparison | Matched retained rapid inputs |
| Visual consistency | Render and inspect every affected caller | One task-owned comparison root |
| Product compatibility | Inventory/caption/provenance comparison | Same render root |
| Edge-case behavior | Missing/constant data, long labels/records | Named temporary cases |
| Dense-ensemble readability | Inspect all members/scenarios retained | 4–5 scenarios, 10–20+ models |
| Map order independence | Compare reference and rendered frame/scales | Fresh WF0→WF1 and WF1-only roots |
| Portable core | Import/render outside CST execution | Minimal dependency environment |

Capture authoritative baseline images before edits. Inspect exported physical sizes, typography,
clipping, legend placement, missing-value handling, caption placement and vector/raster output where
applicable. Preserve filenames, availability reporting and scientific interpretation.

Use the existing figure-comparison viewer. Keep figure-specific probes temporary under task scratch;
preserve numerical/workflow checks separately. A shared figure-only helper requires all affected renders,
not automatically the full suite or baseline. Runtime/configuration/non-figure changes invoke broader
gates. Retain exact commands, commit, environment, input identity and output root in task evidence.

## 8. Next action and decision history

The first milestone is a shared Python rendering foundation used by WF0–WF2. Prepared-input chart APIs
follow as a bounded increment. The map-reference producer remains a separately scoped component.

- 2026-10-10: source landscape reviewed with cst-architect; no execution or visual validation claimed.
- 2026-10-10: user selected Python first.
- 2026-10-10: user approved the plan, requested this saved note and authorized delegated work.

Detailed design must preserve these decisions and identify concrete ownership, migration and acceptance
without reopening the agreed direction. Save design/review state with this task; do not implement a
public library or change scientific methods as an incidental part of helper extraction.
