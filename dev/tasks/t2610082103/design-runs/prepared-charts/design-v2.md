# Use prepared inputs for shared annual and monthly charts

Status: proposed; G1 scientific review and G2 exact-version acceptance pending.
Date: 2026-10-10. Decider: task owner. Supersedes: none.
Lifecycle: immutable reviewed revision in the task run; acceptance lives in run status.
Canonical destination: `dev/tasks/t2610082103/design-runs/prepared-charts/design-v1.md` on main.
Revisions: 2026-10-10 — initial decision record; no implementation or validation success claimed.

## 1. Overview

Add `plotting/prepared_charts.py` for prepared annual lines, retained trend segments and monthly cycles.
WF0 keeps its `View` adapter. WF1 supplies small records directly, removing its construction of a WF0
diagnostic bundle. Existing adapters retain scientific preparation, output ownership and exceptional styling.
Users receive the same figures, captions and metadata through the same workflow commands.

This is the prepared-chart increment of the approved shared-rendering plan. Its reading budget includes
the exact API and acceptance contract so implementers and reviewers can use one document.

Contents: [Context](#2-context-and-caller-map), [Decision](#3-decision-and-contract),
[Layout](#4-proposed-layout-and-compatibility), [Alternatives](#5-alternatives-and-consequences),
[Validation](#6-validation-and-handoff).

## 2. Context and caller map

WF1 currently constructs `diagnostic_figures.View` with unused agreement/reference fields to obtain a
few drawing operations. The reusable boundary is already visible: annual values and fitted estimates,
or monthly mean/p10/p90 tables, arrive before drawing begins. No statistical method needs extraction.

| Caller in `blueearth_cst/` | Proposed route |
|---|---|
| `climate_analysis/diagnostic_figures.py:series` | View adapter → `annual_series` |
| Same: `_climatology`, `seasonal`, `temperature` | View adapter → `monthly_cycle` |
| Same: `_annual_trends`; used by `extremes(metric)` | View adapter → `draw_annual_trends` |
| `model/forcing_figures.py:render_forcing_figures` | Prepared records → both complete charts |
| `shared/func_plot_signature.py:plot_basavg` | Annual primitives; complete monthly chart |

`extremes(metric)` currently makes one axis per metric. Preserve that composition and its existing
wrapper; the axes-level trend function also remains usable in composed figures. Do not redesign extremes.
Hydrological annual plots retain their preceding-five/ten-year tick anchor, annual minor ticks,
disabled y-axis offset, and inside `Annual total`/`Annual mean` legend. Monthly hydrological plots retain
`Mean`, the percentile legend and unrestricted y-limits, including physically valid negative recharge.

Evidence E1–E5 in intake is confirmed by these source paths, including retained fitted slopes/intercepts
and monthly tables. E6 identifies existing render roots, not complete parity evidence. E7, preservation
after extraction, remains an untested hypothesis. No indexed ADR already covers this extraction; this
record continues the existing task plan and caption/layout foundations.

## 3. Decision and contract

The workflow runner continues to load and prepare data using current code. The adapter supplies ordered
values and their meaning; shared functions draw them and return Matplotlib objects. The adapter exports
and closes figures and writes captions. No new run stage, configuration or persistent intermediate appears.

```text
Existing WF0/WF1 inputs → existing scientific preparation → workflow adapters
                                                             │ prepared records
                                                             ▼
                                                    plotting/prepared_charts
                                                             │
                                                    plotting/fundamentals
                                                             │ Figure / artists
                                                             ▼
                                        existing adapter exports + caption inventories
```

The core imports only the standard library, NumPy, Matplotlib and plotting foundations. It must not
import workflows, pandas, configuration, filesystem helpers or Snakemake. It neither selects a backend
nor installs global styling; callers retain their existing style contexts. No new dependencies.

### 3.1 Exact proposed Python surface

The following are frozen dataclasses; `Array` means a one-dimensional numeric NumPy array, consumed
without mutation. `Sequence` preserves caller order. Imports are directly from `prepared_charts`.

```python
AnnualLine(label: str, color: str, marker: str, values: Array)
MonthlyBand(label: str, color: str, marker: str,
            mean: Array, lower: Array, upper: Array)
TrendSegment(color: str, years: tuple[float, float],
             values: tuple[float, float], label: str)

def draw_annual_lines(
    ax: Axes, years: Array, lines: Sequence[AnnualLine],
) -> list[Line2D]: ...

def draw_annual_trends(
    ax: Axes, trends: Sequence[TrendSegment], *, label_x: float,
) -> tuple[list[Line2D], list[Annotation]]: ...

def annual_series(
    years: Array, lines: Sequence[AnnualLine], *, ylabel: str,
    trends: Sequence[TrendSegment] = (),
) -> Figure: ...

def monthly_cycle(
    bands: Sequence[MonthlyBand], *, month_labels: Sequence[str],
    ylabel: str, band_label: str, zero: bool,
) -> Figure: ...
```

`draw_annual_lines` creates and labels lines using the existing width/marker defaults; it changes no
ticks, legends or margins. `draw_annual_trends` retains dashed lines, alpha, the 8% margin, stable
end-value ordering, 7%-of-y-range annotation separation, offsets, fonts and label boxes. Empty trends
still apply the current margin behavior. It draws on the supplied axis without creating a figure.

`annual_series` composes those primitives in today's `series` order: lines, year ticks, margins,
trends, ylabel, multi-source identity legend, horizontal grid. Its trend-label x-coordinate remains
`years[-1] - 0.4`. Single-source identity legends remain absent. Figure size/layout remain `H_SINGLE`.

`monthly_cycle` preserves `H_SINGLE`, x positions 0–11, limits -0.5–11.5, band alpha, mean line/markers,
identity handles and occupancy-selected inside legend. `band_label` is supplied explicitly as
`10–90th percentile` by every current caller. With `zero=True`, retain the upper limit
`max(1, 1.08 * max(0, finite upper values))`; otherwise retain the 8% margin. No sorting, clipping of
input values, quantiles or distribution fitting occurs. The adapter supplies twelve displayed month
labels in the same order as all three arrays; the renderer never rotates values.

Validate nonempty one-dimensional years, annual length agreement, twelve monthly labels and values,
and two endpoints per trend before creating artists. Raise `ValueError` for structural mismatch.
Allow NaNs, all-missing values, constants, negatives and an empty source sequence. Preserve masks/gaps;
do not silently drop or repair entries. Renderers do not infer scientific availability.

### 3.2 Adapter obligations and developer migration

Annual adapters retain `.reindex(years)`. To prepare each trend, reproduce the existing predicate
exactly: finite retained slope and a nonempty `y.dropna().index`. Preserve its first/last eligible
years; evaluate the retained intercept plus slope/10 times those endpoints. Do not refit, change
eligibility, substitute finite-value filtering or change slope units. Formatting retains the signed
Unicode-minus label and current precision. Pass the final display year's annotation position to the
axes primitive. This translation belongs beside the workflow's current table selection.

Monthly adapters pass the existing mean/p10/p90 arrays in existing row order. WF0 selects available
sources as today; its missing-temperature notice stays in `temperature`. WF1 preparation retains
forcing masks, completeness, reporting years and sum/mean distinctions. Hydrological preparation
retains fixed cell weights, warm-up handling, calendar rules, amount infilling, mean aggregation and
Sen fitting. Bands describe interannual variability, not confidence intervals.

Before: `artists.series(View(...), ylabel=unit, trend_unit=..., digits=...)`.
After, once the same summaries and trend endpoints have been prepared:

```python
line = AnnualLine("Wflow forcing", color, "o", annual_values)
fig = annual_series(years, [line], ylabel=unit, trends=prepared_trends)
```

Hydrological annual composition uses `draw_annual_lines` and `draw_annual_trends` on its existing axis,
then applies its existing ticks, labels and inside legend. Its unavailable-period text stays adapter-owned.
No generic chart-options framework or hydrology preset is introduced.

## 4. Proposed layout and compatibility

The tree below is proposed, not evidence of implementation. Only four source files need change.

```text
blueearth_cst/
├── plotting/prepared_charts.py                 # ADD: records and five rendering functions
├── climate_analysis/diagnostic_figures.py       # CHANGE: compatible View wrappers
├── model/forcing_figures.py                    # CHANGE: direct prepared-chart calls
└── shared/func_plot_signature.py               # CHANGE: direct calls, retain composition
dev/reference/plot-style.md                     # CHANGE: root-owned API/ownership guidance
dev/tasks/t2610082103/design-runs/prepared-charts/ # RETAIN: reviewed design and gate evidence
```

Keep `series`, `_climatology`, `_annual_trends`, `seasonal`, `temperature`, `extremes` and `View`
signatures/return conventions compatible; keep unrelated artists and helpers. Remove replaced drawing
bodies and WF1 View construction atomically with caller migration. No source files move or disappear.
Other WF1 scientific/map imports need not disappear. No external package/API stability promise is added.
Managed-run slots, manifests, digests, stages and namespaces do not change; no schema migration is needed.

Unchanged generated inventory, relative to each existing adapter-owned plot root:

```text
WF0 plots/
├── <scope>_<variable>_<context>_<spatial>.png    # SAME: annual/monthly/extreme products
├── <existing captioned-copy paths>             # SAME: only when already requested
├── figure_captions.md                          # SAME: readable descriptions
└── _engine/figure_captions.json                # SAME: availability and methods
WF1 forcing plot root/
├── forcing_<precip|temp|pet>_<kind>.png         # SAME: map, annual, monthly; nine total
└── <existing caption inventories>              # SAME: existing owner and paths
WF1 hydrological plot root/
├── wflow_<stem>_<kind>_basin_avg.png            # SAME: two per selected variable
└── subbasins/wflow_<stem>_<kind>_subbasin_<id>.png # SAME: optional, two per variable/id
```

WF0 keeps its controlled naming vocabulary, including `annual_trend_ts`, `monthly_clim_band` and four
annual extreme contexts. Hydrological kinds remain `annual_ts` and `monthly_clim_band`; stems remain
`precip`, `overland_flow`, `snow`, `aet`, `gwr`. Both hydrological directories retain their existing
caption inventories. No new generated artifacts, filenames, formats, commands, config keys, defaults
or user steps. Exports retain DPI, padding, caption options and metadata. Map outputs are unchanged
neighbors in the forcing inventory. WF2, R/WF3, simulation results and interactive rendering are excluded.

## 5. Alternatives and consequences

**Keep View reuse:** lowest immediate change risk and preferable if WF1 had no further reuse needs.
It retains synthetic diagnostic bundles and cross-workflow drawing ownership, failing this increment's
approved objective.

**Axes-only primitives everywhere:** smaller complete-chart surface and preferable if every caller had
different composition. Here WF0 and forcing share complete annual/monthly layouts; that option retains
duplicate layout and legend code. Keep axes primitives only where real callers need composition.

**One configurable chart engine:** could serve many future chart families, but introduces unexercised
options and obscures statistical meanings. Reconsider only with concrete additional consumers.

Positive consequences: WF1 no longer constructs View; shared drawing has one owner and can be called
with arrays. Costs: adapters explicitly translate tables and trends, and wrappers remain for compatibility.
No performance improvement is claimed. A failed preservation check requires correcting the extraction;
changed scientific behavior or visual redesign requires a separate decision.

## 6. Validation and handoff

Use the live `AGENTS.md` ladder and `dev/reference/validation-ladder.md` § Planning and reusing
verification. Before source edits, capture current prepared values and artists from the same retained
inputs. Existing image roots alone cannot prove array parity. Read and adapt retained render recipes
into the new verification root; never run their fixed paths over frozen evidence.

Let V be `.tmp/scratchpad/shared-rendering/prepared-charts/verification/`, with separate `before/`
and `after/` roots. Reuse WF0 inputs/images from `caption-layout/candidate/` and WF1 material from
`candidate/wf1/`, both under `.tmp/scratchpad/shared-rendering/`. These are development evidence,
not a scientific baseline manifest.

| Claim | Check / falsifier | Case and output root |
|---|---|---|
| Preparation unchanged | Exact arrays/NaN positions, labels, endpoints differ | Matched WF0/WF1, V |
| Drawing unchanged | Line/band vertices, trend text or order differ | Same inputs, V |
| Layout preserved | Geometry drift >0.5 export pixel or rejected visual pair | Same PNGs, V |
| Outputs preserved | Missing/extra names or changed captions/metadata | Same adapter runs, V |
| Optional behavior preserved | Unavailable notice or product inventory differs | Edge/optional cases, V |
| Dependency boundary holds | Core imports workflow/pandas; WF1 constructs View | Source/import probe, V |

Extend the existing `caption-layout/capture.py` recorder in disposable probes: it currently misses
band path vertices, axis legends and axis annotation text/positions. Compare those plus ticks, limits,
styles, figure sizes and export settings. Use exact numeric equality with NaNs aligned; geometry
tolerance covers subpixel rendering only. Publish PNG pairs for visual review; PNG byte equality is
not an acceptance criterion.

Render all affected WF0 single/multi-source annual, seasonal, temperature and extreme charts; forcing
annual/monthly charts for all three variables; hydrological amount, rate and stock summaries. Include
optional individual subbasins, non-January order, missing temperature, gapped/all-missing/constant and
negative values, and available/unavailable trends. Synthetic cases add edge coverage, not domain
qualification.
Confirm untouched forcing maps and captioned copies through inventory and applicable render comparison.

Python-engineer implements the four-file packet after G2, with no algorithm changes. Model-validator
dispositions E1–E7 and scientific preservation before G1 and reviews prepared-value evidence after
implementation. Dataviz-designer judges affected rendered pairs; root reconciles evidence and updates
nearby documentation. No persistent tests solely for terminal figure appearance.

Record tested commit, commands/results, environment and lock identity, input/config hashes and output
roots in existing task evidence. Apply touched-file Ruff and any relevant existing focused checks;
root applies final/landing gates from the live ladder. Figure-only extraction does not require a new
hydrological simulation, baseline-manifest comparison, full suite or all-five execution. Broader runtime
changes reopen scope and gates. Unavailable inputs or uncaptured optional products remain blockers to
their acceptance claims. The immediate next decision is G1 scope/tree confirmation after scientific review,
followed by review and G2; this draft grants no implementation approval.
