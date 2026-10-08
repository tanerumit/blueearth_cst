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
invalidated. A final fast run on the committed correction will supersede the historical blocker
above; its result is recorded after completion.
