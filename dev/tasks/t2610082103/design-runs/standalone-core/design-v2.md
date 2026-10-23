# Step 7 design v2: portable plotting core, standalone proof and packaging scope

Status: revision after the independent review ([review-v1](review-v1.md), verdict "revise"), 2026-10-23.
Not approved; no implementation. Supersedes [design-v1](design-v1.md), which stays as the reviewed record.
Task: t2610082103, step 7. Branch: `refactor/t2610082103` (session-1), base main `a860d6da`.
Framing decisions: task note § "Step 7 framing decisions (2026-10-23)". Plan: `../../landscape-and-plan.md` §5.4.

## 1. Problem

`blueearth_cst/plotting/` (8 modules, ~1,200 lines) loads no Snakemake, HydroMT, xarray, geopandas or
Cartopy and selects no backend. Both `__init__.py` files have no side effects, and no module reads rcParams
at import. Three couplings still prevent use outside a CST checkout:

| Coupling | Where | Effect outside a checkout |
|---|---|---|
| Style values | `fundamentals.py` imports `shared.plot_style`, `plot_colors`, `plot_setup` | Reads `config/plotting/*.yml` relative to the repo; fails without it |
| PyYAML | via `shared.plot_setup` | Extra dependency for a style lookup |
| pandas | `location_labels.py:17`, one `pd.isna` call | Extra dependency for one missing-value test |

`blueearth_cst` is not installed (`pyproject.toml` is deliberately not a packaging manifest).

Constraints found by inspection and review:

- **Token reads take two forms.** By-value imports (`from blueearth_cst.plotting.fundamentals import W_FULL,
  INK, ...`: 45 names, `STYLE` in 6 modules) and attribute reads on a module alias
  (`artists.FS_LABEL`, `.OUTER_PAD_X_MM`, `.LABEL_BOX` in `plot_evaluation.py:276-1394`;
  `fundamentals.H_SINGLE`, `.STYLE`, `.MONTH_ABBR` in `func_plot_signature.py:325-366`). Both break if
  the tokens leave `fundamentals` and only import lines are moved.
- **Token use inside the core.** `fundamentals.py` uses 34 token names, some as default arguments;
  `prepared_charts.py` uses 9 via `f.`. `prepared_maps.py` (literal sizes at `:226,257,309`), `export.py`,
  `figure_captions.py` and `figure_titles.py` read none. `add_caption` and export read `savefig.dpi` and
  `pad_inches` from rcParams at call time.
- **Ten STYLE scopes.** `plt.rc_context(STYLE)` appears at `diagnostic_render.py:312`,
  `diagnostic_subbasins.py:121`, `forcing_figures.py:206,341`, `plot_proj_timeseries.py:210`,
  `projection_suite_figures.py:983`, `plot_evaluation.py:395,853,1272`, `func_plot_signature.py:325`.
  Every save and caption inside them runs before the `with` block exits.
- **Two unscoped core paths.** Core helpers are reached outside any STYLE scope through
  `plot_spatial_maps.py:855-861` (`add_caption` under only `{"savefig.dpi": ...}`) and
  `shared/plot_map.py:283,352` (`save_figure(annotation=...)` → `snake_utils.py:1102` → `add_caption`,
  which reads `FS_LABEL`, `FS_NOTE`, `INK`, `MUTED` at `fundamentals.py:284-285`).
- No code mutates `STYLE`, and no render module uses threads or process pools.
- **Code-identity inventories.** `repository_code_inventory` for generation (18 files), simulation (22) and
  indicators (5 sets, 47 files) contains no plotting or style path.
- **The map-reference digest is separate.** `map_reference.REFERENCE_FILES` (`map_reference.py:69-79`)
  hashes `plotting/fundamentals.py`, `plotting/__init__.py`, `plotting/prepared_maps.py`,
  `shared/plot_style.py`, `plot_setup.py` and `plot_colors.py` into `reference_code_digest`, which is a
  rule parameter (`:193`), part of the record's `code` (`:389`), and checked by validation (`:646`).
  Any edit to `fundamentals.py` therefore makes retained WF0 historical map references stale.

## 2. Design

### 2.1 Preset object (portable)

New `blueearth_cst/plotting/preset.py`, importing only the standard library and Matplotlib:

- `Preset`: a frozen dataclass holding exactly the values the core reads today: widths, heights, outer
  padding, fonts, neutral colors (ink, muted, axis, grid, boundary), line widths, marker sizes, `band_alpha`,
  `label_box`, and an `rcparams` mapping. Field names follow the current `charts:` YAML keys.
- `NEUTRAL`: the built-in default. It uses CST's physical sizes, because these are layout rules rather
  than branding, with neutral greys and Matplotlib's default property cycle.
- `use_preset(preset, *, rcparams=True)`: a context manager that sets a module `ContextVar`, resetting
  it in `finally` and nesting LIFO. With `rcparams=True` it also enters `plt.rc_context(preset.rcparams)`.
  With `rcparams=False` it sets only the preset, for callers whose rcParams must not change.
  `active()` returns the current preset, or `NEUTRAL` outside any scope.

### 2.2 Core reads the active preset

`fundamentals.py` and `prepared_charts.py` replace module-level tokens with `active()` lookups at call time.
Default arguments that use tokens become `None`, resolved inside the function. `MM` and `MONTH_ABBR` are
constants, not style, and stay in the core.

`location_labels.py` replaces `pd.isna` with a local test of identical meaning for the value types it
receives. It treats None, float NaN, `numpy` NaN/NaT (`np.datetime64("NaT")`), and `pd.NA`/`pd.NaT` as
missing, recognising the pandas sentinels by type name without importing pandas. A temporary probe
compares it with `pd.isna` over these values and ordinary strings and numbers.

### 2.3 CST preset (stays in CST)

New `blueearth_cst/shared/plot_preset.py` builds `CST_PRESET` from `STYLE_SETTINGS`, `NEUTRAL_COLORS` and
`plot_style`; the YAML stays authoritative. `CST_PRESET.rcparams` is the current `STYLE` dict stored
verbatim, so key precedence is unchanged (YAML `rcparams` first, then overrides). The module re-exports
the current token names (`W_FULL`, `INK`, `STYLE`, ...) with unchanged values.

### 2.4 Caller migration

The implementation inventory is built mechanically from both by-value imports and `<alias>.<TOKEN>`
attribute reads of `plotting.fundamentals`, and fixed before editing:

- **Ten scopes:** `plt.rc_context(STYLE)` becomes `use_preset(CST_PRESET)`, with the same rcParams plus
  the active preset.
- **Token reads:** by-value imports move to `shared.plot_preset`. Attribute reads switch alias, e.g.
  `artists.FS_LABEL` → `cst.FS_LABEL` with `from blueearth_cst.shared import plot_preset as cst`. Function
  imports stay on the core. `tests/test_plot_colors.py` moves the same way.
- **Two unscoped paths:** `plot_spatial_maps.py:855-861` and `plot_map.py:283,352` (via `save_figure`)
  are wrapped in `use_preset(CST_PRESET, rcparams=False)`. Their caption fonts and colours stay CST, and
  their rcParams are untouched. Wrap at the nearest render entry, not inside `snake_utils`.

### 2.5 Standalone proof (not shipped)

`dev/scripts/plotting_standalone_demo.py` is a maintenance/proof script, never a run dependency.

1. **Isolation.** The script copies only `blueearth_cst/__init__.py` and `blueearth_cst/plotting/` into
   `.tmp/scratchpad/t2610082103-step7/standalone/` and runs there with `python -I` and that copy on
   `sys.path`. An import guard asserts that no `blueearth_cst.shared`, `snakemake`, `hydromt`, `xarray`,
   `pandas` or `yaml` module is loaded and that importing changed no backend. A file-relative read into
   `config/` then fails visibly.
2. **Inputs.** WF0 annual and monthly tables are read as CSV with `csv` and `numpy`. Map fields come
   from `.npz` files exported once by a Pixi helper (`--export`) from the retained WF0
   `annual_climatology.nc`. The standalone run reads only the `.npz`.
3. **Renders.** One annual chart, one monthly chart and one prepared map with `NEUTRAL`, and the same
   three inside `use_preset(<explicit mapping>)`, show injection without CST.

A second, minimal environment (Python, numpy and matplotlib only) runs step 1 and step 3. Build it with
`python -m venv .tmp/scratchpad/t2610082103-step7/venv-min` and
`pip install --cache-dir .tmp/scratchpad/t2610082103-step7/pip-cache numpy matplotlib`, using the Pixi
Python as the base interpreter. It is never added to Pixi.

### 2.6 Packaging scoping record

`t2610082103/design-runs/standalone-core/packaging-scope.md` records:

- the candidate public API: `Preset`, `use_preset`/`active`, fundamentals, prepared charts and maps,
  export and caption placement;
- explicit non-API: CST adapters, figure titles and naming;
- the dependency set, two or three unchecked name options, and the extraction trigger: a named second,
  non-CST use case.

It creates no distribution, build table or release.

### 2.7 Map-reference identity (one declared rebuild)

Add `plotting/preset.py` and `shared/plot_preset.py` to `REFERENCE_FILES`. Without them, later style
edits would no longer invalidate references. The edits to `fundamentals.py` and the new files change
`reference_code_digest` **by design**. The next WF0/WF1 run rebuilds each historical reference once, and
map captions that cite the reference ID change accordingly.

This is a non-figure consumer change. Per the task note it escalates the gate, so the batch gate at
landing includes one fresh WF0→WF1 rapid run (§4). No other identity moves.

## 3. Alternatives considered

| Option | Why not selected |
|---|---|
| Explicit `preset=` argument on every core call | Touches every call site (~29 files); the scoped form already exists as `rc_context` |
| Import-time global set by the CST adapter | Hidden import-order dependence; wrong style if the adapter is not imported first |
| Ship the YAML as package data | Rejected by the owner: keeps PyYAML and makes CST the only preset |
| Keep `fundamentals` out of the reference digest | Hides real style changes from reference staleness; rejected |

## 4. Acceptance

The main risk is the change from module constants to scoped values. A core call outside a `use_preset`
scope silently gets `NEUTRAL`.

**Inputs.** The retained final all-five root from the internal-v1 landing:
`session-1 :: .tmp/pytest/run-4bf42bbc57744ddb8ec629e34230630c/test_all_five_workflows_run_en0/project`.
It holds WF0 (54 tables, `annual_climatology.nc`, ERA5/CHIRPS/comparison plots), WF1 forcing, evaluation
and spatial plots, and WF2 plots. It is retained until this step lands. Caller groups that need more
inputs use synthetic inputs fingerprinted in the harness.

**Matched render harness.** It lives under `.tmp/scratchpad/t2610082103-step7/verification/`.
`render.py before|after` re-renders every caller group from that root. Run `before` from main `a860d6da`
in a separate detached checkout and `after` from the candidate. Each run re-derives the map reference in
its own checkout. The primary check is equality of the scrubbed PNGs (metadata stripped) plus the
caption JSON. Artist and geometry records are collected only to diagnose a mismatch.

| Caller group | Source | Minimum coverage |
|---|---|---|
| WF0 diagnostics and subbasins | `diagnostic_render`, `diagnostic_subbasins` | All chart kinds, all source maps, captioned variants |
| WF1 forcing | `forcing_figures` (both scopes) | All nine products |
| WF1 evaluation | `plot_evaluation` (3 scopes), `func_plot_signature` | Hydrograph/performance, extremes, basin/subbasin summaries |
| WF1 spatial and basin maps | `plot_spatial_maps`, `plot_map` | Captioned and uncaptioned, including `elevation_basin.png` |
| Map reference | `map_reference` | Frame, scale, palette and class fields |
| WF2 | `plot_proj_timeseries`, `projection_suite_figures` | All 17 suite products |

| Claim | Check |
|---|---|
| CST output unchanged | Scrubbed PNGs identical over all caller groups. Caption JSON is identical except reference-ID fields. Map-reference frame, scale, palette and class fields are identical; only `reference_code_digest` and the derived ID differ. |
| No silent neutral fallback in CST | A temporary `active()` that **raises** outside any scope, run across the full harness and the plotting-related tests. Every hit is either scoped or recorded as intentional. |
| Portable import | The isolated demo passes in Pixi and in the minimal environment |
| Neutral and injected presets render | Visual inspection of the 6 demo PNGs, published for review |
| Code identities unchanged | Repeat the inventory probe on the implementation commit |
| Map-reference rebuild | At the batch gate, one fresh rapid WF0→WF1 run rebuilds the reference and passes validation |
| Software | Affected tests (`test_plot_colors.py`, plotting/caption/map-reference tests), lint and format. Broader gates follow `dev-validation.md` at landing. |

Temporary probes stay under `.tmp/scratchpad/t2610082103-step7/`. None are added to the test suite.

## 5. Commit plan

| # | Lands | Estimate |
|---|---|---|
| 0 | (not a commit) Fix the caller inventory, build the harness, capture `before` from `a860d6da` | 0.5 day |
| 1 | `preset.py`, CST `plot_preset.py`, core reads `active()`; ten scopes, token reads and two unscoped paths migrated; `REFERENCE_FILES` extended; `location_labels` drops pandas (one commit, so no commit renders CST with `NEUTRAL`) | 0.75 day |
| 2 | Standalone demo script with `.npz` export helper; isolated and minimal-environment runs | 0.25 day |
| 3 | Docs: `dev/reference/toolbox-plot-style.md` and `config/plotting/README.md` name the CST preset as authoritative and describe `NEUTRAL`/`use_preset`; `fundamentals.py` docstring updated | 0.25 day |
| 4 | Preservation, visual and identity evidence plus the packaging scoping record (main, docs-only) | 0.5 day |

Total is about 2.25 focused days, plus the fresh rapid WF0→WF1 run at the batch gate.

## 6. Settled points from v1

- `NEUTRAL` keeps CST's physical sizes.
- No deprecated token aliases in `fundamentals`: every caller is internal and migrates in commit 1.
