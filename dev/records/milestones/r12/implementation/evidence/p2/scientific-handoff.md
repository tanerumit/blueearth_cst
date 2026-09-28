# P2 retained collection, native response and metric scientific handoff

**ACCEPT — bounded scientific preservation and retained-artifact handoff.**
Reviewer: `model-validator` (`/root/model_validator_p2`), 2026-09-11.
This accepts the named ERA5 reference experiment and its published artifacts;
it is not overall P2 acceptance or approval of a new scientific method.

## Accepted artifacts and reference

The current `run_stress_test.smk` carrier completed `all` for the fresh
`p2_explicit` experiment in one invocation: 25/25 jobs, 7 minutes 32 seconds.
The experiment used explicit-manifest selection of a previously published
collection. Independent checks below read its completed artifacts, not interim
outputs from the earlier refused namespace.

| Artifact | Identity |
|---|---|
| Collection | `2f7d2f6c97bd90af43f272b7d7ba4ed166d68e76eb895ce65a9776208a28169b` |
| Collection revision | `fed6fdc9fdc437a5184b766db7d99e59050b5b8af5e962de5c58fdd972a2bf2b` |
| Simulation | `04ab1bc6153034c0bfdad77b137466587bdec9833089c7164b047f0e70a005eb` |
| Metric set | `2ce17970c2b2f5406987acb356858cf1b62ad64cdbbbc255154819e61ec00ade` |

[Compact comparison evidence](scientific-comparison.json) records the response
and metric manifest digests, all native CSV hashes, forcing-member associations,
reference selection, counts and numerical comparisons. The frozen reference is
`C:/Users/taner/workspace/_workbench/blueearth-cst-r12/2026-09-10/prechange/experiments/experiment`.
Its accepted interpretations are documented in [P1 forcing units](../p1-forcing-units.md),
[P1 simulator acceptance](../p1-simulator-handoff.md) and
[P1 response/metric acceptance](../p1-response-metric-handoff.md).

## Independent results

| Check | Result |
|---|---|
| Collection completeness and ancestry | 14 evaluated members: two roots, each with six descendants paired to that same root; the scenario-table associations select the corresponding P0 members |
| Generated forcing | All 14 NetCDFs pass `xarray.testing.assert_identical` against P0 and have identical SHA256 hashes |
| Source clock and grid | Every member retains 16,790 daily no-leap steps, 2010-01-01 through 2055-12-31, on a 5 by 4 grid; all seven forcing variables have zero non-finite values |
| Retained physical contract | `read_collection` recomputes manifest, forcing and preparation hashes and physical descriptors successfully; effective ERA5 units remain separate from native labels |
| Native responses | All 14 CSVs match P0 exactly in numeric values, times and SHA256 hashes: 126 series, each with 3,286 observations, 2046-01-02 through 2054-12-31 |
| Full response request | Exact coverage of 14 runs by five ordered q gauges and four ordered gwr locations; no missing or extra series |
| Native physical/time metadata | q in `m3 s-1`, gwr in `mm dt-1`; standard calendar, daily interval-end labels; request, native TOML, temporal sidecar and observed timestamps agree |
| Metric result coverage | 756 unique expected keys: 700 q rows and 56 gwr rows; no missing or extra result keys |
| Class A/B preservation | All 616 formatted values equal their P0 values after the explicit run/bundle key crosswalk |
| Class C run migration | All 140 run-grain values equal an independent calculation from frozen P0 native responses; all 70 mean-of-run projections reproduce the corresponding P0 pooled values at published precision |
| Long unit index | 28 membership rows: 14 self-member run units and seven two-member bundles, including the unperturbed bundle; every bundle pairs the same design point across realizations |
| Retained readers | `read_simulation(require_complete=True)`, `read_response_inventory` and `read_metric_set` all pass on the published experiment |

Exact array and byte equality establishes zero observed numerical drift in these
forcing and native-response comparisons. It is not a predictive uncertainty
bound. Metric equality is assessed at the established four-significant-digit,
float32 publication representation; no tolerance was introduced or widened.

## Class C and return-level evidence

Class C uses roots `01` and `08` and the first native q gauge, `101`. An independent
monthly-sum calculation selects wet month **11** and dry month **8**, matching the
persisted reference. Each root contributes nine finite-observation years and
108 year-months. The recorded tie rule remains the first label in ascending
calendar-month order. Per-run values are the mean of annual means for the
selected month, using the recorded `YS-JAN` anchor. The comparison independently
derives those values from P0 CSVs rather than invoking the production run reducer.
The pooled projection is computed from unrounded run values before applying the
established publication representation. Unequal missingness or year/month
weighting is outside this complete-data comparison.

All **70** return-level location fits retain **9 + 9 = 18** finite annual blocks,
against the existing operational requirement of **10**. Independent counts use
annual maxima for high flows and seven-observation rolling means followed by
annual minima for low flows, separately within each member and then pooled.
The anchor is `YS-JAN`; inherited partial-year handling is preserved. Recorded
fit parameters are finite with positive scale, and every published return level
matches P0. The existing ten-year high-flow and two-year low-flow definitions,
xclim/SciPy estimator, floor 10 and blocks-per-return-period ratio 1.0 are unchanged.

The manifest explicitly retains `status=provisional_operational` and
`benchmark=not assessed`. This accepts implementation and preservation of those
preconditions, **not** their scientific adequacy or GF-15. No estimator benchmark,
confidence interval, independence test or stationarity validation was performed.
Two realizations provide a migration reference, not evidence that ensemble or
tail uncertainty is adequately sampled.

## Temporal correction and execution evidence

The reviewed sidecars record the observed `hydromt_reader_to_datetime64` conversion
from source no-leap values before clipping and TOML endpoint refresh. Prepared
forcing uses proleptic-Gregorian datetime64; native Wflow responses use the
prepared TOML's standard calendar. Existing physical operations were preserved.
The earlier `p2_simulation_final` namespace was correctly refused because its
frozen request added the first-response offset twice and inherited the WF1
calendar instead of the prepared clock. The producer was corrected and
`p2_explicit` executed freshly; no frozen request was patched to admit old outputs.
The final comparisons and acceptance concern `p2_explicit`.

Verification posture: **rapid / numerical affected**. Independent commands used
the existing environment via `pixi run --as-is python -B`; no model, forcing or
production file was modified by this reviewer. Logs and the comparison script
are in `.tmp/scratchpad/2026-09-11_0010/`:

- `p2-final-collection-validator.log`: 14-member retained forcing comparison.
- `review-p2-final.py p2_explicit`, with `p2-explicit-scientific-validator.log`:
  native, request, unit-index, Class A/B/C and GEV-record checks; exit 0.
- `p2-explicit-all.log`: the coordinator's completed current-carrier execution.

The compact JSON is the durable numeric record; scratch logs/scripts are
disposable. Software lint, CLI, full-suite, forced-reuse, metrics-only and other
orchestration gates remain the coordinator's evidence and are not implied by
this scientific verdict. The earlier [portable-preparation handoff](portable-preparation.md)
retains the separate four-branch GF-31 evidence and its fixture limitations.

This verdict is limited to exact preservation of the accepted seed-123 ERA5
reference with two realizations, six design points and the 2046–2054 simulation
window. It establishes no held-out hydrological skill, observational accuracy,
real CHIRPS response equivalence, alternate-simulator equivalence or predictive
uncertainty bounds. Parameter, structural, observational and internal-variability
uncertainties were not quantified; GF-15 and the remaining P2/P3 gates stay separate.
