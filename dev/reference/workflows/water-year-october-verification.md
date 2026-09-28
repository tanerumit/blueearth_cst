# WF2 October water-year verification

Verified 2026-09-28 on the rapid basin with the two configured CMIP6 models, `ssp245`, and the 2000–2014 reference window. Two fresh scratch project roots copied the same retained `test_case/test_rapid/data` inputs; their project configs differed only in `project_dir` and `climate.water_year_start` (`Jan` versus `Oct`). Both ran rule 2.01, four 2.03 fetch jobs, four 2.04 reductions, and rule 2.05 through `scripts/run_workflow.py`. The fetch jobs reused the staged CMIP6 slices. Both runs completed successfully.

| Start month | Effective reference window | Complete reference years | Effective future window |
|---|---|---:|---|
| Jan | 2000-01-01 / 2014-12-01 | 15 | 2046-01-01 / 2054-12-01 |
| Oct | 2000-10-01 / 2014-09-01 | 14 | 2046-10-01 / 2054-09-01 |

The effective reference window and year count appear for both resolved model rows in `summary/provenance.json`; `summary/cmip6_change_factors_annual.csv` reports the same windows. All 12 annual factor rows changed between the controlled runs. For example, GFDL-ESM4 mean precipitation change was 3.859% (Jan) versus 2.771% (Oct); INM-CM4-8 was 6.165% versus 4.862%. The October result includes exactly 14 complete October–September years, confirming the boundary behavior previously flagged in the [R08 finding](../../records/milestones/r08/2026-07-30_wf2-5f-hydyear-offbyone.md).

The disposable run trees and output tables are in `session-1/.tmp/scratchpad/2026-09-28_2134/wf2-oct/` while that worktree exists. They are not a retained project dataset. This check establishes the WF2 arithmetic and reporting for this rapid fixture; it does not inventory production projects or test other water-year start months.