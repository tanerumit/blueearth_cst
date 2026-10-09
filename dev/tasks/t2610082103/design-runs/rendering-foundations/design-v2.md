# Shared rendering foundations — first extraction

Status: PROPOSED. Date: 2026-10-10. Owner: t2610082103.
Lifecycle: task-owned reviewed specification; immutable captured revisions and acceptance live in
`dev/tasks/t2610082103/design-runs/rendering-foundations/`. The driver promotes needed guidance at closure.

## 1. Overview

Extract existing Matplotlib fundamentals into `blueearth_cst/plotting/fundamentals.py` and migrate their
active WF0–WF2 callers. This establishes reusable ownership without changing scientific preparation,
reviewed appearance, filenames, caption meaning or availability. Analysts receive the same products
through the same workflow commands and report pages.

The first packet moves functions and tokens, with small import substitutions. Export decoupling follows
as a separately reviewed packet: present export paths already preserve explicit figures, whereas
`snake_utils.save_figure` additionally owns CST logging. No general chart framework is needed.

```text
Existing preparation -> workflow composition -> shared fundamentals -> Figure
                                                                    |
                              existing CST exporter/captions/logging -> report
```

Contents: [Scope](#2-scope-and-journey), [Contracts](#3-contracts), [Tree](#4-tree-and-compatibility),
[Validation](#5-acceptance-and-evidence), [Decisions](#6-alternatives-consequences-and-decisions).

## 2. Scope and journey

The reusable problem is that maps, station evaluation and projection plots import WF0 merely for
typography and drawing helpers. WF1 also imports real WF0 compositions; that separate dependency remains.
This change serves existing source diagnostics, model forcing, hydrological summaries and projections.
It introduces no calculation, statistical convention, managed-run schema, capability binding, stage,
workflow rule or configuration change. Scientific ordering and all existing provenance schemas remain.

An analyst runs the usual workflow. Preparation creates the same tables, fields and caption content.
The existing composition draws those values using shared fundamentals. Existing exporters write their
ordinary images, optional captioned copies and caption inventories. The report consumes the same paths.
The current comparison viewer is the review surface; no new UI or user-selectable layout is introduced.

Retain both active map families: `diagnostic_maps.draw_map` for WF0/WF1 forcing, and
`shared/cartographic_map.plot_raster_map` for spatial products. Preserve pooled WF0 versus independent
WF1 limits, native extents, masks and overlays. Shared map-reference production is deferred. R/WF3,
prepared-series public APIs, external packaging and broad style alignment remain later work.

## 3. Contracts

### 3.1 Exact extraction

Move these implementations without changing signatures, defaults or algorithms:

```python
new_fig(height_mm, nrows=1, ncols=1, width_mm=W_MID, **kw)
ygrid(ax)
year_ticks(ax, years, continuous=False)
five_year_ticks(ax, years, rotation=0)
heatmap_frame(ax)
blank()
top_legend(fig, *rows, handler_map=None)
colourbar(fig, mesh, axes, label, ticks, stack_mm, shrink=0.68)
inside_legend(fig, ax, handles, bands=(), lines=())
add_caption(fig, text)
```

`new_fig` returns `(Figure, axes)` with a two-dimensional axes array, constrained layout and the existing
millimetre padding. Other functions mutate supplied artists and retain their existing return values;
`blank` returns a legend handle. Preserve legend overlap scoring, draw timing, empty-handle behavior,
tick thinning and colorbar extension geometry. Do not add validation that changes existing errors.

Move these exact tokens with their present values:

```text
W_COL1 W_PANEL W_MID W_FULL MM
H_SINGLE H_STACK2 H_SIDE2 H_ROW3 H_GRID4
OUTER_PAD_X_MM OUTER_PAD_Y_MM FS_LABEL FS_TICK FS_NOTE
INK MUTED AXIS GRID BOUNDARY LW_BOUNDARY
LW_LINE LW_MEAN LW_REF LW_EDGE LW_RANGE LW_IQR LW_STEM
MS_LINE MS_POINT S_SCATTER BAND_ALPHA LABEL_BOX MONTH_ABBR STYLE
```

`STYLE` is the existing reviewed CST preset, explicitly documented as such; neutrality means dependency
independence, not new visual defaults. No new preset selector or theme object is introduced. Core imports
are standard library, NumPy and Matplotlib only: no diagnostics, pandas, geospatial stack, config,
Snakemake or logging. The package initializer is inert. New dependencies and import-time backend selection
are prohibited.

Keep `View`, `month_axis`, `heatmap_months`, `month_order`, source colors, source identity helpers,
`UNITS`, statistical formatting, anomaly bounds and all chart compositions in WF0. In particular,
`series`, `_climatology` and `_annual_trends` remain there. Moving calendar/scientific interpretation
would broaden the contract. WF2's caption dependency on `plural` is also outside this extraction.

### 3.2 State and backend ownership

Callers continue using scoped `rc_context(STYLE)`. Keep one mutable `STYLE` dictionary: WF0 compatibility
imports and direct consumers reference the same object, so in-place preview edits still propagate.
Do not introduce copies, frozen mappings or process-global `rcParams.update`. Likewise retain shared
`LABEL_BOX` identity. Rebinding an importing module's name is distinct from dictionary mutation; any
active preview that rebinds extracted names must be identified and migrated before acceptance.

The older `shared/plot_style.py` remains unchanged: its 8/7-point defaults, `rcparams` arguments and
runtime lookup behavior continue serving cartography and evaluation extremes. The tracked basin-map
preview uses `setattr` on cartographic globals; leave that mechanism intact. Do not replace its defaults
with the reviewed 7/6-point preset or cache derived values.

Existing WF0 and WF2 Agg selection stays in those workflow modules. Migrating station evaluation removes
an incidental Agg selection through its WF0 import. Proposed resolution: select Agg explicitly in the
WF1 `model/plot_results.py` script before importing pyplot if the import-order probe confirms lost Agg
selection. Keep evaluation's new fundamentals imports
inside drawing functions: `build_model.smk` imports its directory constant at parse time, which must
remain lightweight. Standalone callers of evaluation then own their backend, as callers of the new core
do. Its former transitive side effect is not a standalone API promise. The coordinator permits this
conditional twelfth file; never preserve Agg by
importing WF0 solely for its side effect.

### 3.3 Caption and export boundary

Move `add_caption` verbatim: character-count wrapping, height increase, `supxlabel`, font and positioning
remain unchanged. This preserves current behavior; it does **not** prove the plot-style requirement that
caption expansion preserves physical axes geometry. Measure existing and candidate geometry separately.
If the existing algorithm violates that requirement, retain parity and record a follow-up layout defect;
do not redesign it within extraction.

WF0 retains map-width measurement, tight bounding boxes and 2 mm borders in `diagnostic_render`.
Keep save order, ordinary-before-captioned mutation, DPI, metadata, closing and failure behavior at every
caller. Keep direct saves direct; `save_figure` retains directory creation, current-figure fallback and
successful-save bundle accounting. No new neutral export wrapper is useful until that distinct packet
specifies its callers and logging equivalence. Caption text, inventories and availability stay CST-owned.

## 4. Tree and compatibility

Proposed repository tree; `+` adds, `~` changes, `=` retains. No source files are deleted.

```text
blueearth_cst/
  plotting/
    __init__.py                         + inert package marker
    fundamentals.py                     + exact helpers and reviewed preset
  climate_analysis/
    diagnostic_figures.py               ~ import/re-export extracted names; keep artists
    diagnostic_render.py                ~ direct fundamentals imports
    diagnostic_maps.py                  ~ direct STYLE import
    diagnostic_subbasins.py             ~ direct STYLE/add_caption imports
  model/
    forcing_figures.py                  ~ direct STYLE import; keep WF0 artists
    plot_results.py                     ~ explicit script-owned Agg selection
  projections/
    projection_suite_figures.py         ~ replace WF0 fundamentals import
    plot_proj_timeseries.py             ~ direct STYLE/add_caption imports
  shared/
    func_plot_signature.py              ~ direct fundamentals; retain private WF0 artists
    plot_evaluation.py                  ~ lazy fundamentals imports; preserve compositions
    plot_style.py                       = legacy preset and runtime overrides
    snake_utils.py                      = export and logging
    cartographic_map.py                 = spatial map composition
dev/reference/plot-style.md              ~ update implementation ownership only
```

WF0 re-exports moved names for existing imports, including retained scratch previews. These are simple
aliases, not wrappers or a second implementation. Migrate all nine active consuming/owning modules shown;
new code imports fundamentals directly. No public external package or API stability promise is added.

| User-facing surface | Current → proposed |
|---|---|
| Commands, config and workflow steps | Unchanged |
| WF0 products and optional subbasins/captioned PNGs | Same declared paths and availability |
| WF1 forcing | Same nine `forcing_<variable>_<kind>.png` products |
| WF1 summaries and station sheets | Same stems, conditional outputs and caption records |
| WF2 | Same `SUITE_PRODUCTS`, folders and availability/manifest bijection |
| Formats, readable captions, machine records | Unchanged; no generated-path migration |
| Source imports | Add internal package; preserve old WF0 imports |

Generated output tree remains the one declared by existing producers, including WF0's existing
`plots/_engine/figure_captions.json`, WF1 family inventories and WF2's ensemble `_engine/` manifest.
Do not opportunistically migrate these differing locations. No new runtime artifact is generated.

## 5. Acceptance and evidence

No visual acceptance has run for this design. Baseline capture is independently underway under
`.tmp/scratchpad/shared-rendering/baseline/`; results remain pending. Use matching inputs with separate
immutable baseline and candidate directories. Record commands,
code revision, input hashes, configuration and Pixi lock identity in existing task evidence.

| Claim | Check | Input/output |
|---|---|---|
| Narrow imports and compatible aliases | Fresh-process import/state probe | Scratch; Agg and chosen backend |
| Caption and inventory contracts | Focused pytest command below | Existing producer-derived fixtures |
| Appearance and values preserved | Render all affected families; inspect | Retained inputs below |
| Caption parity and geometry | Measure axes boxes in inches | Short/long captions |
| Preview state preserved | Mutate/restore STYLE; exercise cartographic overrides | Scratch render probes |
| Missing/dense/optional behavior | Fixtures and edge renders | Subbasins, unavailable, long years |

Existing focused command:

```powershell
pixi run pytest tests/test_wf0_diagnostic_contracts.py tests/test_projection_suite_figures.py tests/test_wf1_plot_outputs.py tests/test_plot_evaluation.py tests/test_func_plot_signature.py
```

Run Ruff lint/format on touched Python paths; final batch uses `pixi run lint` and
`pixi run format-check`. Figure-only sharing requires affected renders, not a numerical baseline or
all-five execution. The proposed script edit also requires `pixi run pytest tests/test_cli.py`; any wider
runtime/configuration change returns to the live validation ladder before implementation.

Preflight input candidates, with exact paths supplied by coordinator inspection:

- WF0: `C:/Users/taner/workspace/cst-cases/runs/sp2-liberia/active/data/climate/historical/`, containing
  `chirps_20000101_20161231`, `era5_20000101_20161231`, and `comparison` tables and diagnostic records.
- WF1: `test_case/test_rapid/models/hydrology/wflow/forcing/inmaps_historical.nc`, `staticmaps.nc` under
  the same model root, and `run_default/output_q.csv`, `output_gwr.csv`, `output_aet.csv`.
- WF2: `C:/Users/taner/workspace/wf0-lab/outputs/wf2/gabon-ntoum-dev-ensemble/results/`.
  Existing `.tmp/scratchpad/plot-verification/render-lab.py` shows required table adaptation; freeze its
  prepared inputs before both runs rather than allowing changed preparation to explain a difference.

**Preflight blockers:** executable render commands, overlay/observation identities, complete source
schemas and matching baselines remain unverified. Materialize and run bounded scratch drivers before
source edits; do not overwrite retained inputs. Rapid lacks WF0 diagnostic tables. The lab adaptation
omits multi-period products, so supplement them from existing fixtures; add 4–5-scenario, 10–20-model
coverage if retained inputs are smaller. Include optional subbasins and captioned maps. Unreadable old
pytest scratch folders prevent a claim of exhaustive scratch-preview discovery.

The python-engineer implements and reports exact removals of duplicate definitions. A fresh Python
reviewer checks dependency/state contracts; coordinator inspects exported PNGs and reconciles captions,
availability, plotted arrays and geometry. Rendering success alone is insufficient. Scientific
qualification is unchanged; any calculation change requires domain review.

## 6. Alternatives, consequences and decisions

A style-only extraction is cheaper and preferable if helper signatures prove unstable, but leaves
cross-workflow layout ownership unresolved. Moving all WF0 artists removes more imports immediately,
but exports `View`, scientific assumptions and backend side effects; reject it for this packet.
Independent packaging adds release obligations before a second external use case exists.

The selected extraction removes WF2's fundamentals dependency on WF0 and leaves WF1's private drawing
dependency visible. Two style systems remain deliberately. Caption geometry may expose existing defects;
acceptance must distinguish preserved behavior from satisfying a future geometry contract.

The coordinator accepted eleven Python files plus conditional WF1 backend ownership in a twelfth, based
on the import-order probe. One reference update is additional. Detailed G2 acceptance and completed
baselines remain
pending. Overall Python-first/internal-core direction is already approved and is not reopened.

Revisions (append-only): 2026-10-10 — v1 proposed; first extraction bounded, export decoupling deferred,
active subbasin caller included, backend allocation and preflight blockers exposed.
