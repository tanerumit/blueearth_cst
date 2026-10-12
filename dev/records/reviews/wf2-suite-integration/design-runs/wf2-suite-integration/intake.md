# Intake — WF2 starter-suite integration

> **Window contract superseded (2026-10-12).** The owner now requires diagnostics to use the configured
> reference/future calendar bounds, retaining only complete water years inside them. Recentring, extension,
> and reference fallback described below no longer apply. The seasonal minimum remains 27 observations.
> Current behavior: `docs/site/toolbox-reference/workflow-analyze-projections.qmd`. The original decisions
> and verification below are retained as historical evidence.


Run: `wf2-suite-integration` · Task: `t2610071652` · Target repo: `blueearth_cst` · Lane:
`feat/wf2-cmip6-improvements` (session-1) · Genre: `decision-record` (milestone-style design: goal, what changes,
alternatives, commit plan) · Opened 2026-10-07.

## Change request (verbatim, owner, 2026-10-07)

> "yes, update it. And then lets call this done and move on to integration to blueearth_cst"

With the owner's three rulings the same day (AskUserQuestion):

| Question | Ruling |
|---|---|
| How much of the lab moves into blueearth_cst? | **Analysis + figures**: port the calculations behind the 15 figures into `blueearth_cst/projections` as a new WF2 rule and draw the revised figures from its tables. One calculator: the analysis window extends `get_change_climate_proj` rather than running beside it. |
| Which figure conventions? | **Lab style**: captions outside the image (`captions.json` + optional captioned copies), scenario key top-right, no model labels on the cloud, WF0 size classes. Revises the 2026-08-11 toolbox rulings (in-figure caveat via `supxlabel`, model-annotated cloud) for WF2. |
| Process? | **Design doc + review loop**, then implement commit-to-commit on this lane. |

## Source material (read-only)

- Lab code: `C:\Users\taner\workspace\wf0-lab\wf2_lab\` (`inputs.py`, `core.py`, `coverage.py`, `means.py`,
  `agreement.py`, `seasonal.py`, `trajectories.py`, `variability.py`, `sensitivity.py`, `figures_wf2.py`,
  `captions_wf2.py`, `run.py`, `report_wf2.py`), lab `main` at `7560e71`.
- Lab report of results and method per figure: `wf0-lab/docs/wf2-suite-report.md`.
- Lab integration notes with candidate functions and the earlier proposed path mapping:
  `wf0-lab/docs/wf2-integration-notes.md` § Candidates for BlueEarth, § Mapping onto WF2's figure grammar.
  The mapping table there predates the 2026-10-07 figure revision (it lists 31 figures, both windows); the
  revised set below supersedes it.
- Ideas note and lab brief: `dev/tasks/t2610022259/wf2-climate-projections-ideas.md`,
  `dev/tasks/t2610022259/wf2-lab-suite-brief.md`, `wf2-starter-suite-proposal.md`.

## Problem

WF2 today derives change factors (aligned windows, annual and monthly) and draws five figures: two annual
overviews, the faceted and combined change-factor cloud, and one monthly change figure per horizon
(`projection_figures.figure_relative_paths`). The lab suite, reviewed figure by figure with the owner on
2026-10-07, adds the analyses the ideas note asks for — evidence coverage, mean change by season with model
spread, seasonal cycle, IPCC-style trajectories, interannual variability ratios, sign agreement — on a 30-water-
year analysis window, with a revised figure style. None of it is in the toolbox. The design must decide how
the analysis enters WF2 (rule boundaries, which module owns each calculation), how the figure contract changes,
and how the toolbox's figure conventions are revised for WF2.

## The revised figure set (owner-accepted, 2026-10-07)

All figures use the analysis window only (aligned rows stay in tables). Development ids as in the lab:

| Id | Figure | Window | Lab folder |
|---|---|---|---|
| F3.1 | Availability table: model, Kuma et al. (2023) family + institution/country, ✓ per run with member count | full | `full-period/` |
| F3.2 | Annual + 4 seasons change, per scenario: whisker range, outline IQR box, median, faint jittered model points (temp °C, precip %, precip mm d⁻¹) | future | `period-<a>-<b>/` |
| F3.3 | a) monthly climatology, reference + each scenario envelopes; b–e) monthly change boxes per scenario (temp, precip) | future | `period-<a>-<b>/` |
| F3.4 | IPCC AR6 Fig. 4.2-style time series, all scenarios overlaid: median, range band, faint per-projection traces, future window shaded, current-year line (temp, precip) | full | `full-period/` |
| F3.4b | Annual overview per scenario (toolbox carry-over): values + anomalies, member ribbon, scenario and historical medians | full | `full-period/` |
| F3.5a | Variability ratio per model, F3.2 style (temp SD, precip CV) | future | `period-<a>-<b>/` |
| F3.5c | Member variability ratios pooled across models per scenario (temp SD, precip CV) | future | `period-<a>-<b>/` |
| F3.6b | Change-factor cloud (toolbox carry-over): ΔT vs ΔP per model, square axes, circles, no labels | future | `period-<a>-<b>/` |
| F5.1 | Sign-agreement tables, temp and precip side by side, annual + 12 months, blue/red by median sign | future | `period-<a>-<b>/` |

Dropped by the owner and not to be integrated as figures: F3.5b, F3.6 (scaling), F3.7 (slope), F3.8
(sensitivity), the combined multi-horizon cloud for one horizon. Their tables may still be written (decision for
the design).

## User journey and actor/artifact boundary

1. The user enables `analyze_projections` (WF2) in the project config and runs it via `scripts/run_workflow.py`
   or `scripts/run_workflows.py`.
2. Existing stages fetch CMIP6, reduce to basin scalars (`scalar/*.nc`), and derive change factors
   (`summary/cmip6_change_factors_{annual,monthly}.csv`) — unchanged contracts, consumed by the CST-API/frontend
   and as a plausibility overlay.
3. **New:** a WF2 analysis step reads the composition, the scalar series and the stage-B settings, writes
   analysis tables (CSV), the figures and their captions, in the project's WF2 output tree.
4. The user reads the figures (PNG, with `captions.json`) and, optionally, a tabbed HTML page (the lab's
   `wf2-projections.html`; inclusion is a design decision).

Actors: Snakemake rules (producers), the user (reader), CST-API/frontend (consumer of change-factor tables only —
`web-app-independence`: never constrains this repo).

## Constraints

- **One calculator.** The analysis-window change must extend or share code with `get_change_climate_proj`, not
  run a second implementation beside it (owner ruling). The aligned change factors must stay byte-identical:
  they feed the baseline manifest (`dev/baseline/manifest.json` lists `cmip6_change_factors_{annual,monthly}.csv`).
- **CMIP6 is a plausibility overlay** (AGENTS.md § Background); nothing here drives generation or simulation.
- **Any CMIP6 model must work**, not just the 13 development models (memory `any-cmip6-model-supported`):
  the Kuma family lookup must degrade gracefully for an unlisted model.
- **No silent caps**; a product whose inputs are empty is reported as unavailable with its reason.
- **Figure contract discipline:** every figure written is declared (projection_figures single source).
  Figures are terminal artifacts; verify by rendering (AGENTS.md § figures).
- **Naming** per `dev/reference/naming.md`; rules per `dev/reference/workflows/rule-index.md`; new config keys
  follow the `get_config` contract and the closed advanced-settings schema.
- **No new dependencies** without approval (memory `new-dependency-requires-approval`); the lab uses only numpy,
  pandas, xarray, matplotlib.
- Identity hashes follow imports (memory `identity-hashes-follow-imports`): editing shared modules imported by
  WF3/WF4 changes their run ids — check `repository_code_inventory` before touching `shared/`.
- Lab-style conventions revise the 2026-08-11 toolbox rulings **for WF2 only**; WF1/WF0 conventions unchanged.

## Decision criteria

1. Numerical fidelity: the integrated tables reproduce the lab's on the P0 ensemble, and aligned change factors
   stay byte-identical.
2. One owner per calculation; no duplicated calculator.
3. Contract clarity: every declared output is produced, every produced output declared; dry-runs pass.
4. Robustness to any model/scenario/member composition; graceful degradation.
5. Cost: run time and figure count acceptable for rapid configs; opt-in vs default decided explicitly.
6. Minimal blast radius on WF3/WF4 identity and on the baseline.

## Success criteria

- WF2 on the development ensemble writes the accepted figures and tables; the figures match the lab renders
  visually; table values match the lab within a stated tolerance.
- `pytest tests/test_cli.py`, the WF2 test modules, `pixi run test-fast` pass; `test-e2e` WF2 leg passes.
- Aligned change-factor tables are byte-identical before/after on the fixture and on P0.

## Non-goals

- Dropped lab figures (F3.5b, F3.6, F3.7, F3.8) as figures.
- Daily extremes, drought, warming levels, emergence, maps, weighting, formal partitioning (excluded in the lab).
- CST-API/frontend changes.
- Fixing t2610070255 (monthly water year) — but the design must state how it interacts.
- Changing WF0/WF1 figure conventions.

## Derived-artifact register

Regenerate from the accepted design after G2; authors must not touch these during review:

| Artifact | Regeneration action |
|---|---|
| Implementation task brief `dev/tasks/t2610071652/task-brief.md` | Write with `task-brief` from the accepted design |
| Board note `t2610071652` progress steps | Fill from the design's commit plan |
| `dev/reference/workflows/rule-index.md` entry for the new rule | Write in the implementation commit that adds the rule |
| `docs/` WF2 user docs (figure list) | Update in the implementation |
| `wf0-lab/docs/wf2-integration-notes.md` mapping table | Mark superseded by the accepted design (lab repo) |

## Evidence register

| Premise | Source | Exact observation | Precision | Reproduction | Confidence |
|---|---|---|---|---|---|
| Lab aligned change table reproduces the toolbox tables | lab `summary.json` reconciliation on P0 | 15,600 gated comparisons, 0 failed; worst deviation 0.00051 (IPSL-CM6A-LR ssp126 Nov %) | tolerance 0.001 on values the toolbox rounds to 3 dp | `pixi run python -m wf2_lab.run --config examples/wf2-input-paths.local.yml` in wf0-lab, read `summary.json` `reconciliation` | high |
| The baseline covers WF2 change-factor CSVs but no WF2 figure | `dev/baseline/manifest.json` | 4 `projections` entries: run record (×2 path forms), `cmip6_change_factors_annual.csv`, `cmip6_change_factors_monthly.csv` | exact string match | `grep projections dev/baseline/manifest.json` | high |
| The baseline manifest is stale for the current config | AGENTS.md § Validation ladder | "stale after the switch to the P-drive catalog and GlobCover"; last fresh record 2026-10-04 | as stated | read AGENTS.md | high |
| WF2's figure set is declared from one function | `projection_figures.py` docstring; `analyze_projections.smk:352` `WF2_FIGURE_RELATIVE_PATHS = projection_figures.figure_relative_paths(future_horizons)` | consumers: Snakefile, `get_change_climate_proj_summary.py`, `plot_proj_timeseries.py`, `projection_plots.py`, `tests/test_projection_figures.py` | grep of `blueearth_cst`, `tests` | `rg "projection_figures|figure_relative_paths" blueearth_cst tests` | high |
| WF0 layout tokens already exist in the toolbox | `blueearth_cst/climate_analysis/diagnostic_figures.py` | 25 occurrences of `W_FULL|H_SINGLE|FS_LABEL|OUTER_PAD|def new_fig` | grep count | `rg -c ... blueearth_cst` | medium (values not yet compared with `wf0_lab/figures.py`) |
| Monthly change factors ignore a non-January water year | board `t2610070255` | `derive_point_datasets` passes `water_year_start` to the annual path only | code reading, not a run | read `get_change_climate_proj.py`, `derive_change_factors.py` | medium |
| The lab suite runs in acceptable time on P0 | lab runner on P0 (13 models × 4 SSPs, 25 members) | full run including 15 figures and page ≈ 1–3 min wall clock | observed, not timed precisely | time the lab runner | low — hypothesis; settle by timing |
| Kuma et al. (2023) families cover the P0 models | Zenodo 7920408 `models.csv`, fetched 2026-10-07 | all 13 P0 models found; mapping in `wf2_lab/coverage.py MODEL_FAMILIES` | exact | re-read `models.csv` | high for P0; unknown for other models |
| Temperature CV is replaced by SD ratio | lab F3.5c decision | CV in °C depends on the zero point; in K the ratio equals the SD ratio within the mean change | analytical | — | high (domain lens to confirm) |

## Domain-content flag

**yes** — analysis windows (30 complete water years centred on the horizon), member-then-model reduction,
OLS detrending inside windows, geometric-mean ratios, pooled member ratios, sign-agreement counting, the use of
Kuma et al. code-genealogy families, unsmoothed IPCC-style anomaly bands. Stage 1b is mandatory.

## Gate materialization

| Gate | Verdict |
|---|---|
| `pytest tests/test_cli.py` (four WF2 dry-runs) | Runnable |
| WF2 test modules (`tests/test_projection_figures.py`, `test_plot_proj_timeseries.py`, `test_get_change_climate_proj*.py`, …) | Runnable |
| `pixi run test-fast`, `test-full`, `test-e2e` | Runnable (e2e local only; network/data mirror needed) |
| Aligned change factors byte-identical | **Needs a pre-change artifact**: copy `cmip6_change_factors_{annual,monthly}.csv` from the fixture/rapid run and from P0 (`C:/data/cmip6/gabon-ntoum-dev-ensemble`) before the first implementation commit |
| Lab-parity of the new tables | **Needs a pre-change artifact**: the lab's `results/*.csv` for P0 at lab `7560e71` (present under `wf0-lab/outputs/wf2/gabon-ntoum-dev-ensemble/`; copy to a task scratch location) |
| `check_baseline.py check` | Runnable but thin and stale: covers only the two CSVs, manifest stale for the current config — use the byte-identity snapshot above instead |

## Next decision

Draft v1 (stage 1), then the domain lens (stage 1b), then G1.
