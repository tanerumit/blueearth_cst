# P1 simulator preparation and execution handoff

Status: **ACCEPT — bounded P1 simulator handoff**; named review below.

Final formatter reconciliation normalized mixed line endings in the preparation
module and its pointer test. Byte comparison after CRLF-to-LF normalization
proved no textual change. Original reviewed hashes and before/after formatter
hashes are both retained in `p1-simulator-comparison.json`; no execution behavior
changed. Final repository format check passed (309 files).

The extracted adapter preserves the observed P0 result for one ERA5 member (`run_id=01`, existing `rlz_1_st_0`, 2046–2054). The prepared forcing matches in values, coordinates and attributes; the native CSV is byte-identical. This is implementation evidence for the named scientific review, not acceptance of the entire P1 workflow. Machine-readable comparisons, commands and raw checkout source hashes are in [p1-simulator-comparison.json](p1-simulator-comparison.json).

## Implemented boundary

- `simulator_adapter.py` carries explicit neutral forcing, model requirements, preparation settings and prepared outputs. Validation names the run, incompatible field, required/observed values and input artifact. It checks forcing and context digests, physical variables/units, dimensions, CRS, calendar, step, time label, coverage and missing values. Public HydroMT grid alignment checks reject an incompatible elevation grid before constructing the model.
- `downscale_climate_forcing.py` resolves catalog arithmetic, PET selection and ancillary provenance outside the adapter. The existing HydroMT preparation algorithms and corrections remain in the extracted preparation function. ERA5 interpretation is bound to the actual catalog operations, without converting already-effective values again. CHIRPS/CHIRPS-global use the existing hybrid ERA5 auxiliary binding and local elevation sidecar. E-OBS remains rejected by WF1; its dormant Makkink helper mapping remains.
- WF3 rules 3.14/3.15 pass explicit run IDs and existing output paths. Julia accepts ordered `(run_id, toml_path, native_output_path)` records; it does not infer IDs from filenames. Execution failures report the batch and all affected run IDs. Snakemake retains its existing batch cleanup semantics.
- Native response opening is a thin re-export of the separately owned neutral reader. No durable IDs, manifests, config keys or output layout changes are introduced in this facet.

## Validation

All commands used the activated host environment through `C:/Users/taner/AppData/Local/pixi/bin/pixi.exe run --as-is`.

```text
python -m pytest tests/test_simulator_adapter.py tests/test_downscale_climate_forcing.py tests/test_run_wflow_batch.py tests/test_snake_utils.py::test_the_log_pointer_is_keyed_the_same_way_as_the_other_two -x -q
42 passed in 9.14s

python -m pytest tests/test_cli.py -x -q
20 passed in 37.12s

python .tmp/scratchpad/2026-09-10_2046/rehearse-simulator.py
exit 0; real preparation and Julia execution completed
```

The focused tests include arbitrary filename/run-ID association, explicit batch ordering, Julia parser execution, physical incompatibilities, changed input/context bytes and elevation-grid misalignment. The initial narrow run caught a retired source-text assertion; it was changed to inspect the explicit log-path expression through the AST. The initial scratch rehearsal had a missing package import path; correcting the scratch script allowed the real run. Neither failure required a numerical change.

Logs are under `.tmp/scratchpad/2026-09-10_2046/`: `p1-simulator-narrow-fixed.log`, `p1-simulator-cli.log`, `p1-simulator-rehearsal-import-fixed.log`, and `simulator-rehearsal/batch.log`. No full suite was run by this facet; the coordinator owns the combined gate, including later rule 3.16 changes.

## Real comparison and limits

The frozen source was read from `C:/Users/taner/workspace/_workbench/blueearth-cst-r12/2026-09-10/prechange`. Its built Wflow model was copied into scratch before any write-capable model handle was opened. All preparation and execution outputs landed under `simulator-rehearsal/`. No production, standing baseline or frozen-P0 path was an output target. The source NetCDF hash was checked unchanged; this was not a whole-tree post-run hash audit.

`xarray.testing.assert_identical` passed against the frozen prepared forcing. Binary NetCDF bytes differed. Parsed TOML dictionaries matched after excluding three explicitly reported physical pointers: staticmaps and initial states now point into the scratch model; the forcing pointer itself was unchanged. All remaining settings, including native log/output paths and simulation clock, matched. Native CSV tables matched exactly and their SHA256 digests matched. Julia used `+1.11.7 --project=. --threads 2` and the explicit one-record batch.

This is one ERA5 member, not all 14 P0 members or an empirical CHIRPS/global rehearsal. The CHIRPS binding has a separate code-derived scientific disposition. Requirements currently come from the explicit P1 Wflow preparation binding; this does not claim comprehensive model introspection. Preparation context fingerprints current catalogs and selected ancillary inputs but is transient, not the P2 portable preparation package. The adapter trusts the supplied prepared TOML/output association and verifies output existence after execution. No general failure rollback or concurrency safety claim is made.

## Named model-validator review

**ACCEPT — bounded P1 simulator/preparation binding**, 2026-09-10.
Reviewer: `model-validator` (`/root/model_validator_p0`). The inspected extraction
preserves the existing ERA5 preparation and execution for the rehearsed member;
the explicit forcing/context compatibility interface is suitable for this P1
carrier. No scientific method change or new tolerance is accepted or required.

Independent read-only checks reproduced the retained evidence:

| Check | Result |
|---|---|
| Execution provenance | All six recorded raw-checkout source hashes match current files |
| Prepared forcing | Independent `xr.testing.assert_identical` passes against P0; binary NetCDF inequality is retained as a serialization difference, not hidden |
| Model configuration | Parsed TOMLs match after excluding exactly the three reported pointer fields; excluded values independently match the comparison record, including the unchanged forcing pointer |
| Native response | Rehearsal and P0 CSV SHA-256 values match exactly |
| Response interpretation | Separately checked all 14 P0 q/gwr native readers against native values/times; see the [response/metric review](p1-response-metric-handoff.md#named-model-validator-review) |

Code review verified that the adapter checks the forcing digest and explicit
required variable units, dimensions, CRS, calendar, interval label, step,
coverage and missing counts; it checks catalog/ancillary hashes and reruns
validation before preparation. The public HydroMT alignment predicate checks
elevation compatibility before model construction. Existing precipitation/PET
methods, pressure/temperature corrections, daily clock, CFTime conversion,
configured-window clip and TOML endpoint refresh remain present. Explicit native
paths replace filename-derived run identity in the execution association.

The ERA5 effective-unit interpretation remains separate from native attributes
and is checked against the reviewed catalog arithmetic. The CHIRPS/hybrid branch
retains the previously accepted code-derived interpretation and source-grid
elevation sidecar; this review adds no CHIRPS numerical execution evidence.
The existing E-OBS support boundary remains unchanged. No simulator or model
adequacy claim follows from a physically compatible descriptor alone.

Verification scope: `rapid`; numerical claims `affected` by the refactor, checked
against the frozen P0 reference. Existing narrow/CLI and real-execution records
were reviewed; no broad tests, preparation or Wflow runs were repeated. The
independent numerical checks read existing outputs only and introduced no tolerance.

This acceptance is limited to the reviewed P1 binding and the one executed ERA5
member, with response-reading evidence for all 14 P0 members. Model requirements
are explicitly supplied by the binding, not comprehensively inferred from any
arbitrary model. The context is transient and the descriptor is supplied by the
current trusted call path; this is not acceptance of portable artifact publication,
untrusted descriptor exchange, durable model/simulation identity, resumability
or concurrent writers. The final integrated workflow gates and GF-9 comparison
remain separate requirements. No held-out model skill or uncertainty bounds are
established by this preservation review.
