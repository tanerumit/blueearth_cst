# R12 P0 fresh pre-change snapshot

Lifecycle: maintained-current through the P0 acceptance handoff.
Status: ACCEPT — named model-validator comparison-evidence review passed on 2026-09-10.
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

**ACCEPT**, 2026-09-10, by the named `model-validator` handoff
(`/root/model_validator_p0`). The preserved snapshot is fit to serve as GF-9's
current-config old-side comparison evidence. The P0 snapshot prerequisite for
P1 numerical call-site edits is discharged; no prerequisite repair or new
tolerance is required. This acceptance does not establish calibration skill,
estimator validity, old/new equivalence, or managed run-control conformance.

Independent review used read-only Python/Pandas/YAML checks in the existing
Pixi environment, the current model-reference comparator, and Xarray metadata
inspection. Verification scope was `rapid`, numerical claims `unaffected`:
this review changes no calculation and accepts evidence fitness only. No model
rerun, software test suite, or new scientific criterion was used.

| Evidence checked independently | Result |
|---|---|
| Current baseline, frozen pre-change and frozen post-change composed mappings | Exact equality after removing only `project.project_dir`; recorded scientific mapping and advanced settings also match |
| Scientific payload digest | Recomputed `64287bea…515a1`; payload comprises `composed_scientific_config`, `advanced_settings`, and `resolved_seed`, excluding the descriptive wrapper and digest field |
| Execution/config integrity | All 159 source hashes and all six frozen-config hashes match |
| Output inventory | All 242 file sizes and SHA-256 values match; filesystem enumeration finds no uncovered files |
| WF1/WF3 execution | Logs finish at 20/20 and 41/41 jobs; WF3 project-consistency and model-reference checks completed before simulation |
| Model reference | Current `compare_reference` returns no differences; recomputed model digest matches `f0f5c03b…adec6bc` |
| Raw response coverage | WF1 plus exactly 14 WF3 members; recorded row counts/endpoints match; all daily timestamps unique, increasing and gap-free; all nine numeric response columns finite |
| Indicator coverage | 630 Q and 56 groundwater rows, finite values and unique four-column keys; seven Q metrics have 70 rows each and four pooled Q metrics have 35 each |
| Run/environment records | Both run records retain seed 123 and matching `Manifest.toml`/`pixi.lock` hashes; Python package inventory is retained; sampled native simulation log identifies Wflow v1.0.2 |
| Recorder check | Retained log reports four matching targets; the raw inventory supplies the broader evidence needed for GF-9 |

The predecessor encodes pooled Q rows with `rlz_id = 0`, including `st_id = 0`
for the unperturbed pool. The later comparator must account for these rows
explicitly and preserve first-native reference gauge **101**; this review does
not execute the Class-C crosswalk or the iteration-order reversal fixture.

Metadata spot checks covered historical Wflow forcing, generated
`rlz_1_st_0.nc`, and Wflow forcing for `rlz_1_st_0` and `rlz_2_st_6`.
Historical forcing contains 6,210 days from 2000-01-01; the sampled generated
neutral series contains 16,790 daily entries from 2010-01-01 through 2055-12-31.
Both sampled WF3 Wflow forcing files contain 3,287 days from 2046-01-01 through
2054-12-31. Native responses begin one day later, as recorded above. Preserve
these observed boundaries for the later temporal comparison. These metadata
checks sampled four NetCDF files; the byte-integrity check covered every file.

Sampled Wflow forcing files label both `temp` and `pet` units as `m`, while
generated temperature is labelled `K`. This is an observed predecessor metadata
limitation, not a finding that numerical unit conversion is correct or incorrect.
It does not invalidate capture of existing behavior and must not be silently
"corrected" as part of an identity-only numerical comparison. Negative
groundwater responses likewise remain captured predecessor behavior.

This verdict is limited to the retained basin, seed and two-realization
experiment. No uncertainty interval, held-out skill assessment, return-level
adequacy claim, or broader basin/scenario generalization is supported by this
review. Original global datasets are not exhaustively content-hashed; the
extracted inputs, model, generated forcing and responses are preserved instead.
The run home remains reference-only by workflow discipline. GF-9 must still
demonstrate bidirectional row coverage and the accepted numerical/identity
criteria against the fresh successor run before equivalence is accepted.

### Separate P1 forcing-metadata disposition

**Superseded hold, 2026-09-10:** the named model-validator
[ERA5 unit-trace acceptance](../p1-forcing-units.md#named-model-validator-review)
discharges the binding hold for the verified ERA5 path. The original findings
and prerequisite below are retained as the reason for that review; they do not
block the accepted explicit interpretation. Other bindings remain outside its
scope.

**HOLD the production forcing-descriptor/compatibility binding for the named
metadata consultation; P0 ACCEPT and pure scenario-row extraction remain valid.**
The follow-up inspection required by design §§5.3/6.4 found a broader distinction
between native attributes and effective physical units:

| Boundary inspected | Observed metadata, identical across all 14 WF3 files |
|---|---|
| Generated forcing | `temp`, `temp_min`, `temp_max`: `units=K`; `kin`, `kout`: `units=J m**-2`; `press_msl`: `units=Pa`; time calendar `noleap` |
| Prepared Wflow forcing | `temp`: `units=m` alongside `unit=degree C.`; `pet`: `units=m` alongside `unit=mm`; `precip`: `units=mm d**-1` alongside `unit=mm`; time calendar `proleptic_gregorian` |

In the generated neutral member's first ten days, temperature ranges from
23.4500 to 27.3700, pressure from 1009.2177 to 1014.1734, and incoming radiation
from 103.0191 to 239.9392. These values suggest Celsius, hPa and W/m² despite
the native labels; ranges alone do not establish units. The installed
`hydromt_wflow.WflowSbmModel.setup_temp_pet_forcing` contract requires those
physical units, and its existing `hydromt.model.processes.meteo.temp` call
performs lapse correction/reprojection and writes `unit=degree C.` without a
Kelvin conversion. The current member catalog contains no unit adapters.
Consequently, a successor that trusts the generated `units=K` and introduces
a Kelvin-to-Celsius conversion could change the existing numerical behavior.

The bounded repair prerequisite is an explicit, reviewed trace from the existing
generation/catalog transformations to each required variable's effective unit,
with raw attributes retained separately in provenance. That trace can support
a versioned adapter interpretation while preserving native bytes and existing
algorithms; it must not infer units from value ranges, silently prefer one
conflicting attribute, or invent defaults. If the trace establishes current
behavior, documenting it is an implementation binding decision. Any proposed
numeric conversion, calendar repair or unresolved physical interpretation needs
the separate scientific/method decision already required by the accepted design.
No upstream diagnosis, metadata rewrite, numerical conversion or calendar change
was made during this review.
