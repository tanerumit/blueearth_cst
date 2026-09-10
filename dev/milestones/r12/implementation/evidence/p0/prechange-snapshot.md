# R12 P0 fresh pre-change snapshot

Lifecycle: maintained-current through the P0 acceptance handoff.
Status: capture and integrity checks passed; named model-validator acceptance pending.
Date: 2026-09-10. Execution checkout: session-3, `feat/wp3-improvements`.

## Scope and isolated paths

Only the current `build_model` and `run_stress_test` workflows are executed.
WF2 is excluded because its projection overlay does not drive the migration's
forcing. This is a fresh numerical reference for GF-9, not a re-record of the
standing baseline or a scientific validation of model performance.

Machine-local run home:
`C:/Users/taner/workspace/_workbench/blueearth-cst-r12/2026-09-10`.
It was absent before setup. All paths below are relative to that home:

| Role | Path |
|---|---|
| Pre-change project config | `config/project_config_prechange.yml` |
| Post-change project config | `config/project_config_postchange.yml` |
| Pre-change output root | `prechange/` |
| Post-change output root | `postchange/` |
| Effective scientific settings | `config/scientific-config.json` |
| Pre-execution code/environment/config inventory | `records/prechange-provenance.json` |
| Full WF1 / WF3 command logs | `records/prechange-wf1.log`, `records/prechange-wf3.log` |
| Recorded comparison manifest and reference sidecars | `records/prechange-manifest.json`, `records/` |
| Complete post-run artifact inventory and coverage | `records/prechange-completeness.json` |
| Recorder and check logs | `records/record-baseline.log`, `records/check-baseline.log` |

The project configs copy the baseline project file and change only
`project.project_dir`. The three referenced baseline workflow files are copied
byte-for-byte beside them. Every other path still resolves from the repository
run directory, preserving the existing catalog, observation and output-location
bindings. The post-change config is the frozen scientific seed; P3 must migrate
its shape without changing those settings. `test_case/test_local` and
`dev/baseline/manifest.json` are not write targets.

## Pre-run checks

- Composed pre-change, post-change and baseline mappings are exactly equal after
  removing **only** `project.project_dir`. No settings were narrowed or defaulted
  differently to obtain the match.
- The frozen config plus advanced settings resolves seed **123** and has SHA-256
  `64287bea79775fd31a0921dd680dd95d3320f251a058f42b75eec672ff1515a1`
  (sorted compact JSON of the recorded payload).
- Settings: ERA5, historical years 2000–2016, two realizations, 2 × 3 perturbation
  grid, simulation years 2046–2054, `experiment_name: experiment`.
- Execution-source inventory at commit
  `affd477cb68165c853d2d4b899733c0122f2b067`: 159 tracked files selected from
  package, scripts, Snakefiles, configs, environment descriptors and baseline
  inputs; actual file bytes hashed with SHA-256. Inventory digest:
  `c0db1de5586990cd112cc2b965e66249fac1786df87fd41bd4f2793dfa907802`.
  Python package versions and raw copied-config hashes are recorded alongside it.
  Concurrent changes during this run concern feasibility fixtures and design
  records; numerical call sites are not being edited.
- Fresh WF1 dry-run passed: 20 jobs covering every declared WF1 rule. Source
  availability beyond DAG construction is established by execution, not inferred
  from that dry-run.

## Commands

Run from the execution checkout with the existing Pixi environment:

```powershell
pixi run --as-is snakemake all -c 3 -s build_model.smk --configfile C:/Users/taner/workspace/_workbench/blueearth-cst-r12/2026-09-10/config/project_config_prechange.yml --notemp
```

WF1 retained `run_default/output.csv` via `--notemp`; the rounded
`output_q.csv` does not substitute for it. WF3 was dry-run, then executed with
the same project file and retained temporary artifacts:

```powershell
pixi run --as-is snakemake all -c 3 -s run_stress_test.smk --configfile C:/Users/taner/workspace/_workbench/blueearth-cst-r12/2026-09-10/config/project_config_prechange.yml --notemp
```

After both workflows and the completeness checks passed, the following command
recorded four targets. Replacing `record` with `check` passed: **4 targets match**.

```powershell
pixi run --as-is python dev/scripts/check_baseline.py record --project-dir C:/Users/taner/workspace/_workbench/blueearth-cst-r12/2026-09-10/prechange --manifest C:/Users/taner/workspace/_workbench/blueearth-cst-r12/2026-09-10/records/prechange-manifest.json --workflow build_model --workflow run_stress_test
```

The manifest and its recorder-owned reference sidecars supplement the preserved
raw outputs. They are not GF-9's old/new identity and metric-row comparator.

## Completed capture checks

- WF1: **20/20 jobs**, exit 0, 4m23s. WF3: **41/41 jobs**, exit 0, 6m58s.
- WF1 raw response: 6,209 daily rows, 2000-01-02 through 2016-12-31.
  All 14 expected `rlz_{1,2}_st_{0..6}.csv` members exist, each with 3,286
  daily rows, 2046-01-02 through 2054-12-31. These observed predecessor
  endpoints must be preserved or explicitly reconciled by the later crosswalk.
- Each response has unique increasing daily timestamps and finite values in
  five Q and four groundwater columns. Groundwater values include negatives;
  this inventory does not impose a new nonnegative criterion. Native Q order is
  `101, 1040, 1020, 1010, 1030`; the first native reference gauge is **101**.
- Q indicators: **630 rows**; groundwater indicators: **56 rows**. Values are
  finite and `(metric, location, st_id, rlz_id)` keys are unique. Exact successor
  expected-key coverage and Class-C semantics remain GF-9 work.
- All 159 pre-execution source hashes and all copied-config hashes still match.
  Generated `climate/weathergenr/config/weathergen_config.yml` and both workflow
  run records preserve seed **123** (weather-generator path is below the experiment).
- The complete **242-file** output inventory hashes extracted climate/spatial
  inputs, generated forcing, model, raw responses, reports and run records.
  SHA-256 of `records/prechange-completeness.json`:
  `5c75592dbf4d1bb1413554e8608f1ca36613a7cc95aeafab626043a3079c0b1f`.
  The model-reference digest is
  `f0f5c03b91aba524b1fd3a5b7c192fbf2929fa413cb024ed9d45ee582adec6bc`.
- The inventory covers the extracted-source boundary and recorded catalog
  locators; it does not hash every original global dataset addressed by catalogs.
  Preserve the pre-change tree as reference-only. This is a workflow restriction,
  not an assertion that operating-system write permissions were changed.

## P0 acceptance handoff — model validator

The named model-validator review has **not run**. Review the frozen scientific
configuration, full command logs, model/run records, response coverage, and
post-run inventory above; decide whether the preserved evidence is complete and
current for the GF-9 old side. Check any scope-dependent model requirements and
record acceptance or a specific blocker here before P1 changes numerical call
sites. This gate concerns comparison-evidence fitness, not calibration skill,
estimator validity, or old/new scientific equivalence. No new tolerance is proposed.
