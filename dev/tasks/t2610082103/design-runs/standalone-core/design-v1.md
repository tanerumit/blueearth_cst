# Step 7 design v1: portable plotting core, standalone proof and packaging scope

Status: draft for owner review, 2026-10-23 (revised once after an advisory pass). Not approved; no implementation.
Task: t2610082103, step 7. Branch: `refactor/t2610082103` (session-1), base main `a860d6da`.
Framing decisions: task note § "Step 7 framing decisions (2026-10-23)". Plan: `../../landscape-and-plan.md` §5.4.

## 1. Problem

`blueearth_cst/plotting/` (8 modules, ~1,200 lines) loads no Snakemake, HydroMT, xarray, geopandas or
Cartopy and selects no backend. Three couplings still prevent use outside a CST checkout:

| Coupling | Where | Effect outside a checkout |
|---|---|---|
| Style values | `fundamentals.py` imports `shared.plot_style`, `plot_colors`, `plot_setup` | Reads `config/plotting/*.yml` relative to the repo; fails without it |
| PyYAML | via `shared.plot_setup` | Extra dependency for a style lookup |
| pandas | `location_labels.py`, one `pd.isna` call | Extra dependency for one missing-value test |

`blueearth_cst` is not installed (`pyproject.toml` is deliberately not a packaging manifest).

Constraints found by inspection:

- Callers import tokens **by value**: `from blueearth_cst.plotting.fundamentals import W_FULL, INK, ...`
  (45 names; `STYLE` in 6 modules). Changing a module attribute after import does not reach them.
- `fundamentals.py` uses 34 token names internally, some as default arguments; `prepared_charts.py` uses 9
  through `f.`; `prepared_maps.py`, `export.py`, `figure_captions.py` and `figure_titles.py` use none.
- Nine render entry points already scope style with `plt.rc_context(STYLE)`: `diagnostic_render.py:312`,
  `diagnostic_subbasins.py:121`, `forcing_figures.py:206,341`, `plot_proj_timeseries.py:210`,
  `projection_suite_figures.py:983`, `plot_evaluation.py:395,853,1272`.
- No code mutates `STYLE` (`STYLE[...] =`, `.update`, `.setdefault`: no match in `blueearth_cst/` or
  `tests/`). Freezing it inside `CST_PRESET` therefore changes no behaviour.
- No render module uses threads or process pools (no `threading`, `concurrent.futures`, `multiprocessing`
  or `joblib` in the plotting, climate-analysis, forcing, projection or shared plot modules). A
  `ContextVar` therefore has the same reach as the process-global rcParams it accompanies.
- Identity hashes are unaffected. A probe of `repository_code_inventory` on this branch found no
  `plotting/`, `shared/plot_*` or `config/plotting` path in the generation (18 files), simulation (22) or
  indicator (5 sets, 47 files) inventories. Re-run the probe on the implementation commit.

## 2. Design

### 2.1 Preset object (portable)

New `blueearth_cst/plotting/preset.py`, importing only the standard library and Matplotlib:

- `Preset`: a frozen dataclass holding exactly the values the core reads today: widths, heights, outer
  padding, fonts, neutral colors (ink, muted, axis, grid, boundary), line widths, marker sizes,
  `band_alpha`, `label_box`, color cycle, raster dpi, plus the remaining `STYLE` rcParams. Field names follow
  the current `charts:` YAML keys so the CST mapping is mechanical.
- `NEUTRAL`: the built-in default. It uses ordinary Matplotlib-like values: neutral greys, the default
  property cycle, and the same physical sizes as today. Physical sizes are layout rules, not CST branding.
- `use_preset(preset)`: a context manager that sets a module `ContextVar` and enters
  `plt.rc_context(preset.rcparams())`. `active()` returns the current preset, or `NEUTRAL` outside any scope.

### 2.2 Core reads the active preset

`fundamentals.py` and `prepared_charts.py` replace module-level tokens with `active()` lookups at call time.
Default arguments that use tokens become `None`, resolved inside the function. `MM` and `MONTH_ABBR` are
constants, not style, and stay in the core. `location_labels.py` replaces `pd.isna` with a local
NaN/None/NaT test of identical meaning (decision: numpy + matplotlib only).

### 2.3 CST preset (stays in CST)

New `blueearth_cst/shared/plot_preset.py` builds `CST_PRESET` from `STYLE_SETTINGS`, `NEUTRAL_COLORS` and
`plot_style` (the YAML stays authoritative). It re-exports the current token names (`W_FULL`, `INK`, `STYLE`, ...)
with unchanged values so that by-value imports keep working after a one-line import path change.

### 2.4 Caller migration

- The nine entry points change `plt.rc_context(STYLE)` to `use_preset(CST_PRESET)`. This sets the same
  rcParams plus the active preset.
- The token imports in the 8 consumer modules plus `tests/test_plot_colors.py` move from
  `plotting.fundamentals` to `shared.plot_preset`. Function imports stay on the core.
- Paths that call core helpers without an entry-point scope get an explicit `use_preset` at their nearest
  render entry. Candidates: `func_plot_signature.py`, `plot_spatial_maps.py` (`add_caption`), and
  `map_reference.py`. The implementation inventory must list every core call reached outside the nine scopes
  and show it covered. An uncovered call silently renders with `NEUTRAL`, which the preservation check
  must catch.

### 2.5 Standalone proof (not shipped)

`dev/scripts/plotting_standalone_demo.py` is a maintenance/proof script, never a run dependency. It:

1. imports only `blueearth_cst.plotting.*` with `sys.path` set to the checkout and an import guard. It
   asserts that no `blueearth_cst.shared`, `snakemake`, `hydromt`, `xarray`, `pandas` or `yaml` module
   was loaded, and that the backend was not changed at import.
2. reads retained WF0 annual and monthly tables and one native map array from a named test_local output
   root, using `csv` and `numpy` only.
3. renders one annual chart, one monthly chart and one prepared map with `NEUTRAL`, and once more inside
   `use_preset(<explicit mapping>)`, to show injection without CST.

A second, minimal environment (python, numpy, matplotlib only) runs the same script. This confirms the
dependency claim independently of the Pixi environment. Build it with
`python -m venv .tmp/scratchpad/t2610082103-step7/venv-min` and install with
`pip install --cache-dir .tmp/scratchpad/t2610082103-step7/pip-cache numpy matplotlib`, using the Pixi
Python as the base interpreter. It is never added to Pixi.

### 2.6 Packaging scoping record

`t2610082103/design-runs/standalone-core/packaging-scope.md` records:

- the candidate public API: the `Preset` fields, `use_preset`/`active`, fundamentals, prepared charts and
  maps, export and caption placement;
- explicit non-API: CST adapters, figure titles and naming;
- the dependency set, 2–3 name options with availability checked, and the extraction trigger (a named
  second, non-CST use case).

It creates no distribution, build table or release.

## 3. Alternatives considered

| Option | Why not selected |
|---|---|
| Explicit `preset=` argument on every core call | Touches every call site (~29 files); noisy; the scoped form already exists as `rc_context` |
| Import-time global set by the CST adapter | Hidden import-order dependence; wrong style if the adapter is not imported first |
| Ship the YAML as package data | Rejected by the owner: keeps PyYAML and makes CST the only preset |

## 4. Acceptance

The main risk is the change from module constants to scoped values. A core call made outside a
`use_preset` scope silently gets `NEUTRAL`, for example a caption, legend or export after a `with` block
exits. The checks below target that risk.

**Matched render harness.** The internal-v1 harness (`.tmp/scratchpad/shared-rendering/...`) no longer
exists in any worktree, so commit 1 rebuilds one under `.tmp/scratchpad/t2610082103-step7/verification/`:

- `render.py before|after` captures saved PNGs plus artist and geometry records: line data, colors,
  widths, fonts, axes/figure boxes and caption text.
- The baseline is rendered from main `a860d6da` in a separate detached checkout, using the same inputs.
- It covers **every migrated caller**, using retained `test_case/test_local` outputs where they exist and
  synthetic inputs fingerprinted in the harness otherwise:

| Caller group | Source | Minimum coverage |
|---|---|---|
| WF0 diagnostics and subbasins | `diagnostic_render`, `diagnostic_subbasins` | All chart kinds, all source maps, captioned variants |
| WF1 forcing | `forcing_figures` (both scopes) | All nine products |
| WF1 evaluation | `plot_evaluation` (3 scopes), `func_plot_signature` | Hydrograph/performance, extremes, basin/subbasin summaries |
| WF1 spatial captions | `plot_spatial_maps` | Captioned and uncaptioned spatial maps |
| Map reference | `map_reference` | Reference record bytes and rendered frame |
| WF2 | `plot_proj_timeseries`, `projection_suite_figures` | All 17 suite products |

The inventory of input roots and counts is fixed in the harness before the `before` render.

| Claim | Check |
|---|---|
| CST output unchanged | Matched before/after harness over all caller groups. Values, artists, saved geometry, caption text and map-reference bytes must be identical. |
| No silent neutral fallback in CST | A temporary `active()` that **raises** outside any `use_preset` scope, run across the full harness and the plotting-related tests. Every hit is either covered with a scope or recorded as an intentional neutral call. |
| Portable import | Demo import guard passes in Pixi and in the minimal environment |
| Neutral and injected presets render | Visual inspection of the 6 demo PNGs, published for review |
| Identity hashes unchanged | Repeat the §1 inventory probe on the implementation commit |
| Software | Affected tests (`test_plot_colors.py`, plotting/caption/map-reference tests), lint and format. The broader gate follows `dev-validation.md` at landing. |

Temporary probes stay under `.tmp/scratchpad/t2610082103-step7/`. None are added to the test suite.

## 5. Commit plan

| # | Lands | Estimate |
|---|---|---|
| 0 | (not a commit) Build the harness and capture the `before` render from `a860d6da` | 0.5 day |
| 1 | `preset.py`, CST `plot_preset.py`, core reads `active()`; `location_labels` drops pandas | 0.5 day |
| 2 | Migrate the 9 scopes and the token imports; cover the unscoped calls | 0.5 day |
| 3 | Standalone demo script plus minimal-environment run | 0.25 day |
| 4 | Docs: `dev/reference/toolbox-plot-style.md` and `config/plotting/README.md` name the CST preset as authoritative and describe `NEUTRAL`/`use_preset`; `fundamentals.py` docstring no longer claims the CST preset | 0.25 day |
| 5 | Preservation and visual evidence; packaging scoping record (main, docs-only) | 0.5 day |

Total is about 2.5 focused days, plus review. Commits 1–2 may squash if splitting them leaves an
intermediate commit that renders CST output with `NEUTRAL`.

## 6. Open points for the reviewer

- Whether `NEUTRAL` should keep CST's physical sizes (proposed) or use Matplotlib defaults.
- Whether to keep the `fundamentals` token names as deprecated aliases for one release instead of a
  same-commit migration. Proposed: no aliases, since every caller is internal.
