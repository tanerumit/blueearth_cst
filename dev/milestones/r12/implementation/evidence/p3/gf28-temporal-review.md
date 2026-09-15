# P3 GF28 temporal preservation review

Reviewer: Astra `model-validator` (`/root/model_validator_p3`), 2026-09-12.
**ACCEPT — bounded GF28 preservation for the completed final direct run.**
The [direct scientific handoff](direct-scientific-handoff.md) closes the final
response/reduction checks that were pending when the preparation comparison
below was performed. Full P3 acceptance remains pending its other gates.

The [independent comparison](gf28-prepared-temporal-review.json) identifies all
14 P0 `(rlz, st_id)` to final `run_id` pairs and records hashes of their prepared
files, TOMLs and temporal sidecars. It binds collection
`71bf34ef8db1122bb91f097ac63ff01e450cf0a16ad9a9d3cca64128fd23ba88`
and frozen runtime inventory digest
`b12a76551cf13b9bce3f96e5d8125954ae70dbfc88278e32f93a90f3e980be98`.

| Clock or operation | Independent observation, all 14 members |
|---|---|
| Generated source | Exact P0 time coordinates and attributes; 16,790 no-leap steps, 2010-01-01 through 2055-12-31 |
| Prepared forcing | Exact P0 time coordinates, attributes and proleptic-Gregorian encoding; 3,287 steps, 2046-01-01 through 2054-12-31 |
| Prepared timestep and leap days | Every interval is exactly one day; 2048-02-29 and 2052-02-29 are present in both sides |
| TOML time configuration | Entire parsed `time` section equals P0, including standard calendar, daily timestep and endpoints |
| Sidecar operations | Exactly `hydromt_reader_to_datetime64`, `clip_to_configured_window`, `refresh_toml_endpoints`, in that order |
| Native response | `interval_end`; start 2046-01-02, one timestep after TOML start, and end 2054-12-31; initial declarations are now independently confirmed by the completed GF9 response comparison |

These comparisons preserve the existing adapter conversion and its resulting
clock. They do not introduce an interpolation, a calendar conversion, a new
spin-up exclusion or any endpoint repair. Zero observed clock drift is an exact
preservation statement, not a predictive uncertainty bound. Physical-value and
selector-metadata preservation has its separate accepted
[GF31 comparison](gf31-acceptance.md).

## Non-January and partial-year coverage

The accepted [P2 scientific handoff](../p2/scientific-handoff.md) retains the
partial-year and within-member block-extraction semantics. The reviewer inspected
the final code and existing tests without running pytest or workflows:

- `tests/test_metrics_definition.py` uses a 2000–2004 New-Year-crossing peak
  fixture, including leap years, and verifies the default calendar-year
  reduction, a different result for `YE-SEP`, and the inherited contribution
  of partial edge years. Its annual-metric anchor cases and month-metric
  invariance cases remain present.
- `tests/test_metric_plan.py` verifies that configured October water years
  resolve to `YS-OCT` for retained-response metric configuration.
- `tests/test_metric_registry.py::test_bundle_preserves_estimator_and_records_per_member_blocks`
  compares the reducer against explicitly constructed within-member annual
  maxima or seven-observation rolling annual minima, followed by scalar-block
  pooling. It retains the 9 + 9 block counts for the reference window.
- `tests/test_wflow_response_reader.py` verifies interval-end labels and
  unchanged native values. `tests/test_response_inventory.py` refuses an
  incorrect response-start clock or omitted reader conversion before publication.

Source inspection confirms that bundle extraction performs the rolling operation
and annual reduction separately for each member, preserving partial water years
and existing missingness rules. No daily rolling window spans member boundaries.
The coordinator's final full software result must supply execution status for
these existing checks. This review does not claim that a non-January Wflow
experiment was executed in P3.

## Remaining checks and provenance

Completed GF9 and the independent direct-run review now verify all native
response times and bytes against P0, retained response-inventory coverage, and
annual/return-level preservation. All 126 series have 3,286 observations from
January 2, 2046 through December 31, 2054; all 70 location fits retain 9 + 9
annual blocks. This closes the originally pending observations. The bounded
GF28 acceptance retains the P2 fixture limitations; it does not establish
arbitrary calendar support or observational hydrological skill.

A planned comment-only correction in `scripts/run_workflows.py` occurs after
the frozen executions. Before final acceptance, preserve the executed inventory
above and record the exact pre/post file hashes and comment-only diff separately.
Do not rewrite executed-run provenance to imply that the later bytes ran.
Any executable change would require reassessing the affected evidence.

Verification: release / numerical affected at the migration boundary. An
independent read-only command through `pixi run --as-is python -B` compared the
14 retained source/prepared arrays and TOML clocks and wrote only the compact
review JSON. It printed a 14-member pass. No Snakemake, pytest, preparation,
simulation or benchmark was executed by this reviewer. Parameter, structural,
observational and internal-variability uncertainties remain unquantified.
