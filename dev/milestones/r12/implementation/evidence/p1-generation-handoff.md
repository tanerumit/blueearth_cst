# P1 generation acceptance handoff

Status: **ACCEPT — bounded ERA5 generation binding**; named review below.
Date: 2026-09-10. Parent implementation commit: `6ce20844`.

## Change and carrier boundary

Current WF3 rules 3.11/3.12 now call `scenario_provider.py` through `script:`.
The provider executes the unchanged R programs via the existing `run_and_tee`
helper, preserving arguments, logs and exit codes. Pure rows determine roots
and ancestor dependencies. The transform receives the exact ancestor path
selected by `derived_from`; its output cannot overwrite that path.

The current Snakefile retains native wildcard/output paths and a run-only
transient capacity equal to the configured run count. These are P1 compatibility
addresses, not a durable collection namespace. P2/P3 must replace that carrier
with the required visible capacity and final run-id paths; this increment does
not claim their contracts. Existing R bodies, generation seed, lookup values,
spell factors, rounding and calendars are unchanged.

The new forcing descriptor requires explicit effective-unit interpretation,
revision and evidence for every variable. It retains native attributes separately,
inspects CRS, variable dimensions, calendar, actual coverage and timestep, and
counts non-finite values. It neither repairs nor converts data. The accepted
[unit trace](p1-forcing-units.md) covers the existing ERA5 binding only.

A standalone neutral-response validator also has tests for explicit metadata,
missingness, evaluated-run membership, location ordinals and bundle compatibility.
Its current time binding is datetime64/Gregorian; other calendars refuse. It is
not yet connected to the Wflow reader or metrics and does not establish GF-21.

## Verification

- `pixi run --as-is pytest tests/test_scenario_rows.py tests/test_scenario_provider.py -q`:
  **16 passed in 7.81 s**. Tests distinguish ancestor bytes, preserve exact R argv,
  propagate failure, refuse missing outputs and preserve native unit labels.
- `pixi run --as-is pytest tests/test_response_series.py -q`:
  **15 passed in 1.70 s**, standalone protocol checks only.
- `pixi run --as-is pytest tests/test_cli.py -q`: **20 passed in 43.00 s**.
- `pixi run --as-is test-full`: **3,439 passed, 9 skipped, 1 xfailed,
  2 failed in 689.75 s**. Both failures were the retired-key spelling sweep
  misclassifying the intentional `run_historical` refusal and its negative test.
  Added a specific refusal-guard classification and named test allowance;
  the targeted sweep then passed **8 tests** using the existing environment's
  Python and a writable scratch `--basetemp`. No numerical code changed for
  this repair; the full suite was not repeated. Complete log:
  `p1-provider-full.log`, repair log: `p1-spelling-recheck.log` in scratch.
- Real R rehearsal via `snakemake all -c 3 -s
  .tmp/scratchpad/2026-09-10_2046/provider-rehearsal/provider.smk`:
  **14/14 jobs**, exit 0 (one root-generation job, twelve transforms, collector).
  The scratch-located graph required the repository root on `PYTHONPATH`; the
  first attempt refused import before jobs ran, then succeeded with that explicit
  fixture context. This is actual script execution, not only mocked argv.
- Inputs are the accepted P0 historical extraction, basin cells, lookup and
  weather-generator config; only the latter's output directory changes. Native
  outputs land in scratch. Every one of the **14 NetCDF files is byte-identical**
  to P0. Independent Xarray comparison also found identical values, coordinates
  and attributes. [Retained comparison](p1-provider-comparison.json) includes
  file hashes, source hashes, descriptors and missing counts.
- Every inspected generated file has calendar `noleap`, 86,400-second steps,
  coverage 2010-01-01 through 2055-12-31 and zero non-finite physical values.
  The descriptor preserves those observations rather than relabelling them as
  prepared or response time axes.

Scratch execution/comparison logs are under the rehearsal directory; narrow
test and CLI logs are its parent's `p1-provider-tests.log`, `p1-responses.log`
and `p1-provider-cli.log`. Repository lint/format checks accompany the commit.
No Wflow rerun, estimator benchmark or GF-9 successor comparison is claimed.

## Required review

Judge generation pairing, forcing completeness, and preservation of the current
ERA5 units/calendar/perturbation behavior from these tests and the retained
comparison. Accept only this bounded binding; other source interpretations and
the simulator/metric contracts remain separate work. Record a clear acceptance
or specific blocker here before treating this as the P1 generation handoff.

## Named model-validator review

**ACCEPT — bounded ERA5 generation binding**, 2026-09-10.
Reviewer: `model-validator` (`/root/model_validator_p0`). The wrapper preserves
generation pairing, declared-ancestor consumption and the complete generated
forcing for the accepted P0 configuration. No blocker or new tolerance applies
to this handoff.

Independent review inspected the production rule mappings, provider, row
enumerator/validator, descriptor, ancestor-byte test and scratch rehearsal graph.
The production ancestor resolver selects `_rows_by_id[row.derived_from]`;
`transform` passes that selected artifact path to the unchanged R command,
checks the ancestor id, and refuses an output path that resolves to its ancestor.
The verified configuration yields two roots and twelve transforms, each paired
with the root from the same realization. The retained test uses distinct draw
contents and checks the selected bytes, not merely matching identity labels.

Read-only verification in the existing environment independently established:

| Check | Result |
|---|---|
| Compared execution source | All six recorded source hashes match current files; all three recorded R-source hashes also match the pre-execution P0 inventory |
| Rehearsal configuration | Exact mapping equality with P0 after removing only `generate_weather.out_dir` |
| Forcing completeness | Expected and actual sets agree for all `rlz_{1,2}_st_{0..6}.nc`; no missing or extra NetCDF members |
| Numerical and native-metadata preservation | SHA-256 equality to P0 and the retained comparison for all 14 files; independent `xr.testing.assert_identical` passes for every pair |
| Descriptor observations | All 14 files: EPSG:4326, `noleap`, 86,400-second steps, 2010-01-01 through 2055-12-31, zero non-finite values in all seven physical variables |
| Pairing and command evidence | Production and rehearsal graphs follow the same declared ancestor edges; unchanged R arguments and recorded root/transform execution support the file comparison |

The descriptor check used an explicit review binding for the previously accepted
ERA5 effective units: temperature/minimum/maximum in °C, precipitation in
mm/day, pressure in hPa, and incoming/outgoing radiation in W/m². Native
attributes remain preserved, including their known stale unit labels. This
observation does not authorize new conversions or substitute a source-name
default for the versioned, evidenced interpretation accepted in
[the unit trace](p1-forcing-units.md#named-model-validator-review).

Verification scope was `rapid`, numerical claims `affected` for the wrapper's
potential to change generated values; the paired pre-change/current-output
comparison supplies the independent numerical reference. Existing provider/row
and CLI pass logs were inspected rather than rerunning those software gates.
The first reviewer probe stopped on its own mistaken spelling check for the
output-directory key; repeating with the actual `generate_weather.out_dir`
exclusion passed. No production or scientific artifact was changed, and no R or
Wflow execution was repeated during this review.

Acceptance is limited to this two-realization, six-design-point ERA5 binding
and the source hashes retained in the comparison. It establishes preservation
of generated forcing, not weather-generator statistical adequacy or uncertainty
bounds. The scratch rehearsal exercises the production wrapper through a small
Snakemake graph; production WF3 integration additionally has the reported CLI
gate, not a fresh full WF3 execution. Transitional native paths/run-only capacity,
durable collection identity, other forcing sources, Wflow preparation/response
binding, metric semantics and the full GF-9 crosswalk remain outside this
acceptance. The standalone response validator is not scientifically accepted
by this generation handoff.
