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

Final fast gate, WF2 execution, inventory totals, visual findings and candidate commit are recorded
below after completion. Until then this record does not assert readiness for landing.
