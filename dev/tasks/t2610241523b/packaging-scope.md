# Packaging scope for the plotting core

Status: scoping record from t2610082103 step 7 (design-v2 §2.6), 2026-10-23; that design and its
evidence are recoverable from Git at the task's closure. Not a release decision. It creates no distribution,
build metadata, package name or public commitment. Basis: branch `refactor/t2610082103` at `f4c06321`.

## Boundary as implemented

The portable core is `blueearth_cst/plotting/`, plus the empty `blueearth_cst/__init__.py` it sits in.
Under `python -I`, a copy of only those files imports and renders with numpy and matplotlib. No CST
module, pandas, PyYAML, xarray, Snakemake or HydroMT module is loaded, and the backend is unchanged.
`dev/scripts/plotting_standalone_demo.py` checks this, as the step 7 implementation evidence recorded.

## Candidate public API

| Module | Candidate API | Notes |
|---|---|---|
| `preset` | `Preset`, `NEUTRAL`, `use_preset`, `active`, `chart_rcparams` | The style contract; field keys follow `style.yml` `charts:` |
| `fundamentals` | `new_fig`, `ygrid`, `year_ticks`, `five_year_ticks`, `heatmap_frame`, `top_legend`, `inside_legend`, `colourbar`, `add_caption`, `blank`, `MM`, `MONTH_ABBR` | `add_caption` freezes layout at the save DPI; document that contract |
| `prepared_charts` | `AnnualLine`, `MonthlyBand`, `TrendSegment`, `annual_series`, `monthly_cycle`, `draw_annual_lines`, `draw_annual_trends` | Prepared-input charts; no statistics |
| `prepared_maps` | `MapFrame`, `MapScale`, `RasterMap`, `draw_raster_map` | Units currently restricted to `degC` and `mm/year` |
| `export` | `export_figure` | Explicit figure, no logging |

## Explicit non-API

- **CST adapters stay in CST:** `shared/plot_preset.py` and the `CST_PRESET` token names,
  `shared/plot_style.py`, and the workflow renderers.
- **`figure_titles`, `figure_captions` and `location_labels`:** these encode CST output naming and
  record formats.
- **Underscore-prefixed helpers:** the map class norm and the label placement helpers.

## Known gaps before any extraction

- **Map literals:** `prepared_maps` uses literal sizes, fonts and colours, so presets don't reach it.
  It also limits units to two CST quantities. A general map API needs both lifted.
- **Neutral styling unexercised in CST:** `NEUTRAL` keeps CST's physical sizes; no CST path draws with it.
- **Naming:** `colourbar` is the only British spelling in the API.
- **No tests:** the core has no API tests of its own. CST behaviour is covered through workflow tests
  and the matched render harness.

## Dependencies

Required: `numpy`, `matplotlib`. Optional: none today. Geospatial libraries would be optional extras
if a cartographic layer joins later. Python ≥ 3.12 matches the current environment and is unverified
for older versions.

## Name options (availability not checked)

1. `hydroviz-core`: domain-neutral within hydrology and climate.
2. `climplot`: short; possible collisions unverified.
3. `cst-plotting`: honest provenance, but narrower than the intended audience.

## Extraction trigger

Extract a distribution only when a named second use case outside CST execution adopts the core and
confirms the API above (task framing decision, 2026-10-23). Until then the core stays in this
repository behind the boundary that `plotting_standalone_demo.py` checks.
