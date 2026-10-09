# WF0/WF2 plotting integration verification

## Candidate and scope

Owner brief: finalize the approved WF0/WF2 plots on `feat/plot-improvements`, starting at `594b4bc0`.
Session entry confirmed a clean branch and local `main` (`ec411b78`) already ancestral to HEAD;
`git rebase main` reported up to date. No landing, pushing, output cleanup or baseline regeneration.

The branch initially changed 39 files. Changes are terminal WF0/WF2 graphics, figure inventories,
caption/analysis record placement, their tests and live documentation. Shared plotting callers were
searched in `blueearth_cst/` and `scripts/`: diagnostic rendering, maps, subbasins and the WF2 suite.
There are no affected WF1/WF3/WF4 runtime consumers. Fast is the final software gate; full/all-five
execution is not owed by this terminal-figure scope. `.testing-policy.yml` pins rapid; the owner brief
explicitly requires broader integration verification. The numerical axis is affected for displayed
reductions, while retained climate calculations must remain unchanged.

## Acceptance map

| Claim | Check / input | Output and added coverage |
|---|---|---|
| Fresh execution | WF0 then WF2, copied rapid config set | Scratch `rapid/`; reused for inventory and images |
| Canonical products | Declarations, availability, caption/PNG bijections | Same rapid root and focused contract tests |
| Large ensemble | Retained Gabon tables, read-only | Scratch `gabon/`; 13 models, 25 members, four SSPs |
| Conditional products | Synthetic optional WF0 source/comparison | Scratch `optional-wf0/`; captioned subbasins |
| Multiple windows / gaps | Analytic synthetic cloud and annual series | `combined-cloud.png`, `annual-gaps.png` |
| Numerical preservation | Matched main/candidate synthetic series | 187 change rows, maximum absolute delta zero |
| Model weighting | Independent geometric oracle | Model A ratios 1,9 → 3; model B 1; median √3 |
| Software integration | Focused tests, CLI, lint, format, fast | Logs and final candidate evidence below |

All scratch paths are relative to `.tmp/scratchpad/plot-verification/`. Disposable scripts and logs
remain there; durable evidence is retained with this record at completion.

## Corrective changes

- Availability now includes precipitation SD in the approved three-metric annual member comparison.
  The regression test failed before the predicate fix (`member-availability-red.log`).
- ACF plot limits include finite confidence limits; the approximation remains ±1.96/√pairs. The
  pre-fix ten-pair case clipped ±0.619806 to ±0.5 (`review-boundaries.log`); the focused test protects it.
- Historical-only trajectory rendering guards an empty scenario tail. The pre-fix boundary raised
  `ValueError: arange: cannot compute length` (`review-trajectory.log`).
- Tests now assert split climatology/monthly-change products, 19 declared products, three variability
  metrics, model weighting captions and the updated coverage schema. Scientific assertions remain.
- Branch-owned Python formatting, import order and unused imports were corrected for the final gates.

No scientific method, approved style, external dataset, lab source, sealed record or lock file changed.
No files or existing run outputs were deleted.

## Inputs and numerical evidence

Fresh rapid retains the source config's basin, ERA5/CHIRPS, 2000–2016 historical period, two CMIP6 models,
one SSP and one configured future window. Its scratch project root is the only path override; WF2 also
enables captioned figures. Rapid does not cover multiple SSPs/windows, unequal member counts, the
ten-model IQR threshold or optional WF0 subbasin figures. Gabon and synthetic cases cover those claims.

The authoritative retained case is
`C:/Users/taner/workspace/wf0-lab/outputs/wf2/gabon-ntoum-dev-ensemble`. Its analysis window is
2036–2065 relative to 1985–2014. The scratch adapter selects analysis rows, maps identity fields and
sign-agreement `n_agree/n_models` to `k/n`, resolves existing family metadata, and reconstructs the
unsmoothed model envelope from `c3_model_trajectories.csv`; it does not use the lab's smoothed fan.
Input hashes are checked before/after rendering. Lab-render availability is explicitly supplied;
production availability acceptance comes from fresh workflow execution and contract tests.

Matched synthetic monthly inputs give exact main/candidate equality for analysis change tables,
model changes and member ratios. The independent ratio oracle rejects a member-count-weighted
alternative. Differences in approved graphical estimands are intentional: annual overview member
summaries, trajectory equal-model medians, and variability geometric member/equal-model summaries.
The already documented seasonal precipitation rate-versus-lab-total exception is unchanged.

## Validation status

Initial sandboxed launches sometimes resolved global Python or denied pytest temp directories/native
libraries. Normal `pixi run` execution succeeded. Those setup failures are not counted as passes.
Every check writes a separate log; no check output is piped through tail.

- Focused unchanged coverage: 252 passed; four superseded expectations corrected.
- Corrected focused coverage: 34 passed; remaining monthly-render test corrected and the complete
  artist suite then passed 13 tests.
- `pixi run pytest tests/test_cli.py -q`: 20 passed (`cli.log`).
- `pixi run lint`: passed after four import/unused-import fixes (`lint-final.log`).
- `pixi run format-check`: passed, 432 files formatted (`format-final.log`).
- Fresh WF0: succeeded, 11 jobs (`wf0-fresh.log`); catalog precedence and adjusted output-location
  warnings are expected. Temperature normalization warning prevents a second Kelvin conversion.
- Gabon: 18 ordinary and 18 captioned figures; one combined-cloud product unavailable because only
  one distinct retained future window exists (`gabon-render-complete.log`).

Eleven opt-in P0/lab parity checks skipped because the expected retained production analysis directory
is absent. This is not a parity pass; matched synthetic main/candidate equality and the read-only Gabon
render provide separate evidence. No stale baseline or PNG byte comparison was used.

## Final candidate and execution evidence

Executable candidate: `001b958c`, after corrective commits `8e254d35` and `001b958c`. The latter adds
a 90 mm minimum canvas width only to small-ensemble sign-agreement matrices: the one-SSP legend
previously extended beyond the canvas. The regression failed before this fix and passed afterward
(13 artist tests). Four-SSP approved canvas dimensions remain unchanged.

Windows 11, Pixi local default environment, Python 3.12.13, pytest 9.0.3. Lock SHA-256:
`797afdad5a8f8c37dd62b2f1e2f88f3fea120c3fc53b7e7c792b860700a6782b`.
No dependency or lock changes were made.

Workflow commands (logs under the scratch root):

```powershell
pixi run python scripts/run_workflow.py analyze_climate --config .tmp/scratchpad/plot-verification/project_config_rapid.yml --project-dir .tmp/scratchpad/plot-verification/rapid --cores 3
pixi run python scripts/run_workflow.py analyze_projections --config .tmp/scratchpad/plot-verification/project_config_rapid.yml --project-dir .tmp/scratchpad/plot-verification/rapid --cores 3 --keep-going
pixi run python scripts/run_workflow.py analyze_projections --config .tmp/scratchpad/plot-verification/project_config_rapid.yml --project-dir .tmp/scratchpad/plot-verification/rapid --cores 3 -- --forcerun plot_climate_projections
pixi run pytest tests/test_projection_suite_figures.py -q
pixi run pytest tests/test_cli.py -q
pixi run lint
pixi run format-check
pixi run python dev/scripts/verify_landing.py record --evidence .tmp/scratchpad/plot-verification/gates-final.json --gate test-fast --log .tmp/scratchpad/plot-verification/test-fast-final.log --input .tmp/scratchpad/plot-verification/project_config_rapid.yml -- pixi run test-fast
```

WF0 fresh execution passed 11 jobs; WF2 passed 13 jobs. WF0 was then run with
`subbasin_figures: true` and `diagnostics.captioned_figures: true` in its scratch config, passing
in 2m43s while reusing the same climate inputs. Optional inventory: CHIRPS 25 ordinary + 25 captioned;
comparison 25 + 25; ERA5 33 + 33. There are respectively 8, 8 and 12 ordinary subbasin products,
each with a captioned copy. Caption paths exactly cover all 166 WF0 PNGs.

WF2 inventory: 17 ordinary + 17 captioned PNGs. Analysis availability, captions and actual files agree.
The two unavailable products have explicit reasons: one member per model and one future window.
All generated graphics are under `plots/`; period folders and both `_engine` records are canonical.
Gabon contributes 18 ordinary + 18 captioned products and the larger model/member case.

Visual inspection covered all ordinary WF0/WF2/Gabon products, all optional WF0 contact sheets,
the two-window paired cloud and the missing-year annual case. Source colors, units, captions,
map overlays, subbasin products and annual ticks survive fresh execution. The final WF2 rule is
explicitly forced because Snakemake does not detect an imported helper edit through its script path.
Temporary HTML reviews were rebuilt from the tracked comparison template.

## Remaining gate blocker

The first fast gate on `8e254d35` returned 3994 passed, 17 skipped, one expected failure and one
failure: `tests/test_spatial_geoms_parity.py::test_the_relationships_hold_on_a_really_built_project`.
The existing `test_case/test_local` geometry fixture differs in `locations.snapped_y` by about
7.1e-15 degrees between the exported geometry and Wflow static geometry. The test and validator
have no branch diff; loading the `main` validator against the same read-only fixture reproduces
`locations: column 'snapped_y' values differ`. This is unrelated to the plotting branch.

The fixture, validator and assertion were preserved. Repairing/rebuilding existing outputs or
revising this spatial contract is outside the authorized task. Landing readiness remains blocked
until this failing gate is resolved under separately authorized scope. No landing or push occurred.

The final run on executable candidate `001b958c` reproduced exactly the same totals and failure
in 462.85 seconds. Its complete log and candidate/environment observation are retained in `evidence/`.
The `verify_landing.py record` command ran the gate but refused its post-run JSON write because
this verification document had been updated while the gate ran. No executable edits intervened;
the evidence-only dirty diff is documented rather than rerunning an unchanged failing gate.
The earlier helper-written failed gate record is also retained. Neither record authorizes landing.

Final lint and format checks passed (432 files). The forced WF2 figure rule and its consumers passed
in 1m51s; final captions/availability/PNG bijection passed for all 17 ordinary and 17 captioned files.
Evidence-only additions after testing do not invalidate executable coverage. Disposable contact
sheets and HTML remain in scratch; input/config hashes, complete check logs and numerical evidence
are retained under this task record. No required skip was suppressed.

The 17 skips are explained: five Linux-only fixed-tolerance controls on Windows, eleven opt-in
production/lab parity cases missing their production input tree, and one all-five integration case
requiring `--run-integration`. The xfail is the known HydroMT catalog preprocess round-trip defect.
All-five execution/full tests are not required by this figure-only diff. Matched synthetic numerical
parity is exact; it does not replace the missing real production/lab parity case.

## Owner-authorized coordinate tolerance follow-up

The owner approved treating snapped coordinate rounding as negligible on 2026-10-08.
The validator now uses absolute tolerance `1e-12` degrees, relative tolerance zero, only for
`snapped_x` and `snapped_y`. Other attributes remain exact; dtype, row identity and missingness must
still agree. Geometry keeps its existing separate tolerance. No stored outputs were changed.

Regression evidence: four rounding cases and the existing built fixture failed before the fix;
all 31 spatial-parity tests passed after it. Tests reject `2e-12` degree drift, finite/missing and
finite/infinite mismatches, and even tiny changes to other numeric attributes. Matching missing
coordinates still pass. Commands: `pixi run pytest tests/test_spatial_geoms_parity.py -q`, touched
Ruff lint/format checks, then `pixi run lint` and `pixi run format-check`.

Caller search confirms the validator is used only by its tests; this changes verification tolerance,
not shared workflow runtime/configuration or calculated outputs. Full/all-five execution is not
invalidated.

Final executable candidate `d1a2ad02` passed `pixi run test-fast`: 4007 passed, 17 explained skips,
one expected failure, no failures, in 154.56 seconds. `verify_landing.py record` successfully recorded
the clean candidate and environment; `evidence/spatial-gates.json` retains that passing gate with
its complete log. Lint and format checks passed. This supersedes the historical blocker above.
The branch is ready for owner-approved landing; no landing or push has been performed.

Post-gate changes contain only this record and its retained logs/JSON. The helper's `verify` adapter
accepts only exact Markdown exceptions, so it cannot certify newly committed log/JSON evidence.
The recorded pass remains valid for `d1a2ad02`; an explicit Git diff excluding this task record
confirms no executable or other repository changes after that candidate. No check was rerun merely
to absorb evidence files into the tested tree.

## Owner-approved local landing — 2026-10-08

`task-land feat/plot-improvements --target main --verify` ran the recorded fast gate on candidate
`c7b47b34`: 4007 passed, 17 explained skips, one expected failure, in 184.97 seconds.
Local main merged it at `566abca4`; committed-tree equality and candidate ancestry both passed.
Session-1 is detached and EMPTY; the merged local branch was removed. No push occurred.
The complete landing gate and lifecycle logs are retained in `evidence/`.

## WF1 forcing alignment — 2026-10-09

Owner-approved follow-up: apply WF0's reviewed style and methodological choices to the nine model-grid
forcing figures. Tested executable commit: `8a2ebccb`. Verification scope is focused, with numerical
claims affected intentionally. This is separate from the earlier WF0/WF2 batch and its landing.

WF1 now shares the reviewed map, annual-series and monthly-climatology artists. A chunked model adapter
uses WF0 completeness, start-year reporting labels, Theil–Sen trends and mean/p10–p90 monthly summaries.
It preserves the nine forcing filenames and adds declared Markdown/JSON caption outputs. The shared
artists retain their WF0 defaults. Fine model-cell outlines are suppressed; outside-basin cells are
white and unavailable values within the basin are gray. No dependencies or configuration keys changed.

### Acceptance and inputs

| Claim | Check / case | Result |
|---|---|---|
| WF0 method parity | Analytic masking/quantiles, Sen outlier, cellwise WF0 oracle | Three tests passed |
| Workflow declarations | CLI and WF1 output/deletion contracts | Included in 51 passing focused tests |
| Real forcing render | Retained Liberia model forcing and spatial overlays | Nine PNGs, nine caption records |
| Shared caller safety | Retained ERA5/CHIRPS WF0 tables and maps | Six source figures and annual comparison |
| Visual acceptance | Opened forcing figures and shared caller PNGs | Labels, palettes, legends and axes inspected |
| Rapid DAG | WF1 plotting target with rapid project config | Passed; nine prerequisite jobs planned |
| Python quality | Repository lint and format check | Passed; 434 files formatted |

Environment: Windows 11, session-2 Pixi default, Python 3.12.13, Matplotlib 3.11.0, xarray 2026.4.0,
hydromt_wflow 1.0.2. Lock SHA-256:
`797afdad5a8f8c37dd62b2f1e2f88f3fea120c3fc53b7e7c792b860700a6782b`.

Real input root: `C:/Users/taner/workspace/cst-cases/runs/sp2-liberia/active/`.
Forcing: `models/hydrology/wflow/forcing/inmaps_historical.nc`; SHA-256:
`56b1213999320c9968cd9e7ee6840d207380bcce3d1e6e0bc4950f8650a04e1d`.
The grid is 231 × 223 cells, with 20,983 model-basin cells and 6,209 daily timestamps from
2000-01-02 through 2016-12-31. WF0's full-year policy excludes partial 2000, leaving 2001–2016.
This is an intended QA-method change, as are the revised trend estimator and monthly spread encoding;
the underlying forcing and simulation calculations are unchanged. The forcing precipitation slope is
now approximately −183 mm per decade rather than the older OLS figure's −151.

Numerical discrimination includes an independent analytic quantile case and a nine-year temperature
outlier case: Sen is 10 °C per decade while OLS exceeds 50. The old annual helper retains partial 2000
on a January-2 input, violating the revised full-year expectation. The vectorized map calculation
matches WF0's cellwise oracle with tolerated gaps, excessive monthly/yearly gaps and non-January years.

### Commands and artifacts

Commands run against the executable candidate:

```text
pixi run pytest tests/test_forcing_figures.py -q -o cache_dir=.tmp/scratchpad/wf1-forcing-style/pytest-cache -o addopts='' -p no:cacheprovider
pixi run pytest tests/test_cli.py tests/test_wf1_plot_outputs.py tests/test_wf0_diagnostics.py tests/test_wf0_diagnostic_contracts.py -q
pixi run snakemake plot_model_forcing --snakefile build_model.smk --configfile test_case/project_config_rapid.yml --dry-run --cores 1
pixi run lint
pixi run format-check
pixi run python .tmp/scratchpad/wf1-forcing-style/render.py
pixi run python .tmp/scratchpad/wf1-forcing-style/shared.py
pixi run python .tmp/scratchpad/wf1-forcing-style/publish.py
```

The three-test command passed with one cache-option warning from disabling pytest's cache plugin.
The 51-test command passed without failures or skips. Initial sandboxed checks encountered temporary
fixture access errors and a blocked Snakemake subprocess; that process tree was terminated and the
focused command passed outside the sandbox. An initial scratch inventory reader omitted UTF-8;
the reader was corrected and the final rendering/inventory command passed.

Rapid configuration identity: `test_case/project_config_rapid.yml`, SHA-256
`ba8d72cbc0d178188b3309483e5fe1effc48b61e1343160848b5d63bc39013bd`.
Full-suite, baseline and all-five execution gates were omitted for this terminal-figure task.
No non-figure output consumer changed; no model construction or simulation was run.

Output root: `.tmp/scratchpad/wf1-forcing-style/`. `revised/` holds the nine forcing PNGs and captions;
`wf0-callers/plots/` holds the inspected shared-caller renders. `comparison.html` uses the tracked
comparison template, with originals preserved under `before/`. Retain this scratch folder for the
owner's visual review and recovery of the refreshed figures; earlier unrelated scratch was untouched.

The nine approved PNGs and two caption records were copied into the actual Liberia forcing plot
directory after inspection. Before replacing each PNG, its bytes were checked against the preserved
original to reject concurrent edits. The forcing NetCDF size and modification time were unchanged
across publication. No files were deleted. No branch landing or push occurred.

## WF1 station hydrograph review — 2026-10-09 (approved)

The owner requested plot-type iteration, methodology suggestions before revisions, and commits only
on an explicit `commit` instruction. The hydrograph renderer now uses the common style, five titled
panels and separate station captions. The owner subsequently authorized completeness-aware means,
paired comparison dates, valid-value FDC ranks and explicit zero-flow handling. Panel b includes
the preceding calendar-grid label (2000 for Liberia); preview captions use measured axes edges.

The retained Liberia `models/hydrology/wflow/run_default/output_q.csv` supplies all eleven station
series. The native `output.csv` was absent, so these read-only review renders use the retained
five-decimal discharge export. Both versions use the same input and exclude the first simulation
year as the production adapter does. The remaining daily span is 2001-01-02 through 2016-12-31.
The new annual boundary policy excludes partial 2001, leaving 2002–2016; it also excludes January
2001 from the monthly climatology. Other full months remain eligible independently of annual support.

Analytical assertions passed for omitted leap dates, paired support, negative-value exclusion,
monthly/yearly completeness, partial boundary periods, equal-weight monthly means, valid-day Weibull
positions, zero-flow mass, an observed 1e-8 positive tail, all-zero flows and disjoint records.
The former method retains the partial boundary year and hides that low tail, discriminating the
revised cases from the predecessor. Numeric regression cases were added to the existing evaluation
test module and passed through standalone invocation (see `regression-probe.log` in the review
scratch folder), including rejection of sixteen distributed missing days in one year. Formal
test/lint gates remain deferred during the active visual iteration.

```text
pixi run python .tmp/scratchpad/wf1-evaluation-style/probe_methods.py
pixi run python .tmp/scratchpad/wf1-evaluation-style/render_hydrograph.py before --all
pixi run python .tmp/scratchpad/wf1-evaluation-style/render_hydrograph.py after --all
pixi run python .tmp/scratchpad/wf1-evaluation-style/render_hydrograph.py before --synthetic
pixi run python .tmp/scratchpad/wf1-evaluation-style/render_hydrograph.py after --synthetic
pixi run python .tmp/scratchpad/wf1-evaluation-style/render_hydrograph.py before --all --geometry-only
pixi run python .tmp/scratchpad/wf1-evaluation-style/review.py
```

All render/probe commands passed. The same Pixi environment as the forcing task was used.
The review page contains eleven real before/after pairs and a synthetic paired-series example with
deliberate missing observations and omitted timestamps, explicitly identified as synthetic.
Measured caption bounds are strictly inside the canvas for all eleven station renders. Exported
outlet, upstream and synthetic figures were inspected for panel/legend readability; the updated
outlet includes the requested 2000 tick, all positive flow tails and zero-flow frequency.

Retain `.tmp/scratchpad/wf1-evaluation-style/` for the active owner's review, baseline recovery,
numeric probe evidence and caption geometry. No production evaluation files were overwritten,
no performance metrics or other evaluation figure methods changed, and no files were deleted.
The owner approved committing this plot type. The work stays on the pinned session branch;
landing and pushing remain separate decisions.

### Commit checks

```text
pixi run pytest tests/test_plot_evaluation.py tests/test_func_plot_signature.py tests/test_wf1_plot_outputs.py -q
pixi run ruff check blueearth_cst/shared/plot_evaluation.py tests/test_plot_evaluation.py
pixi run ruff format --check blueearth_cst/shared/plot_evaluation.py tests/test_plot_evaluation.py
git diff --check
```

All 49 focused tests passed in 37.84 seconds; touched-file lint, formatting and whitespace checks
passed. The focused suite includes the three new numeric cases and the existing evaluation sheet,
station identity, metric and declared-output contracts. Pytest ran outside the sandbox to permit
its external temporary fixtures, as in the forcing task. Logs remain under the retained review root.
The changed renderer has only the WF1 station-evaluation caller; other evaluation sheet methods
were retained and checked by the focused suite. No Snakefile or public script signature changed.
Full-suite, baseline and all-five gates are omitted for this confined terminal-figure change.

Verified implementation commit: `c7ddb673` (`feat(plots): standardize Wflow evaluation hydrographs`).
It contains the unchanged executable candidate covered by the checks above; the following evidence
update changes this review record only. The worktree was clean immediately after that commit.

## WF1 hydrological output figures — active owner review

The owner approved two standard single-axis products per configured zonal hydrological variable:
basin-average annual series and seasonal cycles. Individual subbasin versions of both products are
optional through `evaluation.subbasin_plots` in the WF1 workflow YAML, defaulting to false.
The native discharge station family and the forcing precipitation family retain their separate homes.

The adapter excludes the first simulation year once, before both discharge and zonal summaries.
The same WF0 calendar-completeness choices apply throughout: full boundary periods, three missing
days per month and fifteen per year. Flux amounts use monthly mean gap adjustment and totals;
rates and stored quantities use available-day means. Negative recharge is retained. Snow is native
snowpack liquid-water depth and now uses means in mm. Annual trends use the WF0 Sen treatment;
seasonal bands use the owner-approved 10th–90th percentiles of equally weighted eligible months.

Daily basin values reconstruct Wflow's native mean reducer using the cell counts of the disjoint
`subcatchment` raster. The Liberia zones contain 20,983 cells. Every zone must have finite daily
support; weights never renormalize around missing zones. These are model-cell means, with no claim
of physical-area weighting. Numeric probes cover unequal weights, absent zones, omitted leap dates,
partial calendar boundaries, completeness thresholds, stock/rate means and caption-inventory refresh.

The read-only Liberia AET/recharge exports produced four standard basin and 44 optional individual
figures under `.tmp/scratchpad/wf1-evaluation-style/basavg/basin-after/`. Ten explicitly synthetic
figures under `synthetic-all-variables/` cover all five zonal quantity types, including rate/state
handling not represented in Liberia's configured outputs. The HTML review holds these 58 records;
previous seasonal panel sheets serve as context, while new annual products have no predecessor.
Captions use measured horizontal plotting bounds. All four standard Liberia renders and an
individual recharge example were inspected. A synthetic near-constant rate exposed a y-axis offset
overlapping the support title; absolute tick labels fixed it, and all affected drafts were rerendered.
Final inventories contain 4 basin, 44 individual and 10 synthetic records. Production outputs and
previous review renders remain
intact; no files were deleted. Retain this scratch for the owner's active visual review.

Focused checks in the session's default Pixi environment passed:

```text
pixi run pytest tests/test_wf1_plot_outputs.py tests/test_indicator_glossary.py tests/test_plot_evaluation.py -q
pixi run pytest tests/test_func_plot_signature.py -q
pixi run python .tmp/scratchpad/wf1-evaluation-style/basavg/probe_basin.py
```

The suites passed 55 and 16 tests respectively; the standalone probe passed six acceptance cases.
Pytest required external temporary-fixture access, granted through the sandbox escalation mechanism.
Touched-file Ruff lint and formatting checks passed. The full suite, numerical baseline and all-five
execution are deferred under the confined figure validation policy. The owner approved committing
this plot family after the caption and title revisions.

The owner requested publication-style captions during review. The renderer now uses short prose
covering quantity, spatial support, eligible period and visual encodings, with a brief warm-up note.
Detailed aggregation, cell counts, completeness thresholds and exclusions remain in JSON methods
metadata. Caption-only review refreshes regenerated all 58 records without rewriting the inspected
PNGs; the HTML keeps the same measured caption bounds.

The owner clarified that no titles should be displayed. Annual and seasonal basin/subbasin figures
therefore have no titles, inside or above the axes; captions and review-page headings identify them.
The temporary header padding was removed, restoring the canonical data limits and adaptive inside
legend. All 58 review figures were rerendered and their caption geometry refreshed. Touched-file Ruff
lint and formatting checks passed; the scientific calculations were unchanged. Render logs are
`no-title-render.log` and `no-title-synthetic.log` in the active review scratch.

### Commit checks

```text
pixi run pytest tests/test_cli.py tests/test_func_plot_signature.py tests/test_plot_evaluation.py tests/test_wf1_plot_outputs.py tests/test_indicator_glossary.py -q
pixi run ruff check blueearth_cst/model/plot_results.py blueearth_cst/shared/func_plot_signature.py blueearth_cst/shared/wflow_outputs.py tests/test_func_plot_signature.py tests/test_plot_evaluation.py tests/test_wf1_plot_outputs.py
pixi run ruff format --check blueearth_cst/model/plot_results.py blueearth_cst/shared/func_plot_signature.py blueearth_cst/shared/wflow_outputs.py tests/test_func_plot_signature.py tests/test_plot_evaluation.py tests/test_wf1_plot_outputs.py
git diff --check
```

All 91 focused tests passed; touched-file lint, formatting and whitespace checks passed. The CLI and
declared-output checks cover the new optional WF1 setting, script parameter and annual/seasonal output
inventory. The default Pixi environment and Liberia/synthetic review inputs described above were used.
Logs remain under the retained review root. No production output files were modified or deleted.
The work remains on the pinned session branch; landing and pushing require separate instructions.

Verified implementation commit: `75183c20` (`feat(plots): standardize hydrological output summaries`).
It contains the executable candidate covered by the focused checks and inspected renders above.

## Performance sheet revision — 2026-10-09

The active, uncommitted candidate revises WF1 performance scatter, cumulative volume and metrics
tables. It applies canonical typography, colours, light frames and grids, inside legends, no displayed
titles, and short external captions bounded by measured plotting edges. Daily scatter, sample counts,
volume and exported metrics share concurrent finite, nonnegative daily discharge pairs. Monthly
metrics use means over those same paired days. Missing days interrupt both cumulative curves without
infilling; undefined scores remain NaN in CSV and appear as dashes in the figure. Squared Pearson
correlation is identified as r². The existing 14-row metric export schema remains unchanged.

Review inputs use the read-only Liberia `run_default/output_q.csv`, excluding its first year, and
explicitly synthetic observations. No observed discharge record was supplied. The five-case review
under `.tmp/scratchpad/wf1-evaluation-style/performance/comparison.html` covers a complete record,
gaps/invalid values, a ten-day gap close-up, all-zero flows and non-overlapping dates. The complete
case retains its original figure for comparison; edge cases carry honest unavailable-predecessor
placeholders. All five revised cases were rendered; complete, zero and disjoint renders were inspected,
and the gap close-up visibly breaks both volume curves on the same ten days. Retain this scratch for
the owner's visual review. No production files were modified and no files were deleted.

Validation in the session's default Pixi environment:

```text
pixi run pytest tests/test_func_plot_signature.py tests/test_plot_evaluation.py -q
pixi run python .tmp/scratchpad/wf1-evaluation-style/performance/probe_clean_metrics.py
pixi run python .tmp/scratchpad/wf1-evaluation-style/performance/render_revision.py
pixi run ruff check blueearth_cst/shared/func_plot_signature.py blueearth_cst/shared/plot_evaluation.py tests/test_func_plot_signature.py tests/test_plot_evaluation.py
pixi run ruff format --check blueearth_cst/shared/func_plot_signature.py blueearth_cst/shared/plot_evaluation.py tests/test_func_plot_signature.py tests/test_plot_evaluation.py
```

The focused suite passed 46 tests. Two short-date locator warnings prompted a locator adjustment;
five final affected cases then passed without warnings, including real PNG export of zero/disjoint
records. The independent complete-record probe preserved all 14 original metric values within
1e-12 and the CSV shape. Touched-file Ruff checks passed. Logs are retained in the performance scratch.
Pytest required approved external temporary-fixture access. Broader batch/landing gates remain
deferred; this candidate changes metric handling for incomplete or invalid WF1 inputs as well as
terminal figures, and is covered here by independent paired-date numerical checks. Await owner
visual approval and an explicit commit instruction; no landing or push is authorized.

The owner then requested panel labels, publication captions and relocation of the line legend.
Performance panels now carry `a)` and `b)`; the observed/simulated legend occupies the upper-left
of panel a), below its label. Correlation and sample counts are not displayed; both remain in JSON
metadata. Captions explain the labelled panels, paired-day volume and undefined table values in
publication prose. The five-case review was rerendered using `render_revision.py`, with measured
caption bounds preserved. This revision changes decorations and captions only; numerical tests are
reused, with further focused checks deferred until the owner's commit instruction.

### Performance commit checks

The owner approved this family for commit. The final executable candidate passed all 48 tests in
`pixi run pytest tests/test_func_plot_signature.py tests/test_plot_evaluation.py -q` without warnings
(24.67 s), recorded in `performance/tests-commit.log`. Ruff lint and format checks passed on the four
touched Python files listed above; `git diff --check` passed. The revised five-case review retains
its original comparison image and measured caption bounds. No files were deleted. This scoped
commit does not land the batch or push it.
