# P1 response and metric handoff

Status: **ACCEPT — bounded P1 response/metric handoff**; named review below.
Date: 2026-09-10. Generation checkpoint: `11ea019e`.

## Scope and call graph

Current WF3 rule 3.16 now supplies explicit run-to-CSV/TOML associations and
provider-resolved design groups, unperturbed reference members and legacy table
labels. It declares those TOMLs as inputs. Native filenames and columns terminate
in `wflow_response_reader.py`; `metric_registry.py` consumes only neutral series.
The public legacy `analyze_wflow_results` helper remains for existing callers and
tests, but the production rule uses `analyze_response_runs`.

The reader preserves native location order, values and missingness. The actual
run TOML supplies calendar, timestep and expected output coverage (start plus one
step through end); its declared physical parameter must match the requested
canonical variable. The Wflow 1.0.2 binding follows `src/standard_name.jl`: q and
overland flow are `m3 s-1`; precipitation, evapotranspiration and recharge are
`mm dt-1`; snowpack liquid water is `mm`. `run_timestep!` in `src/Wflow.jl`
advances the clock, updates the model, then calls `write_output`; `write_csv_row`
in `src/io.jl` writes that clock time. The reader therefore explicitly binds
interval-end labels without changing values. Other native parameter bindings
refuse rather than inheriting a unit from a matching header.

Declarations retain current metric names, explicit daily response requirements,
grains, grouping/reference rules, implementation digests and value policies.
The Class-C reference records explicit native-first gauge id, contributing runs,
coverage, finite-observation year/month counts, selection statistic and tie rule.
Per-run Class-C calculations use that resolved reference. **P1 compatibility:**
the current five-column tables still receive the predecessor's pooled projection;
P2 owns the result-grain and output-contract migration. The run values are
available in the transient calculation evidence, not a prematurely published
P2 manifest. The logical three-column unit-index planner is tested in memory;
production still uses the documented P1 run-only namespace.

Return-level blocks are extracted within each run, preserving partial water
years, the configured anchor, seven-observation rolling alignment and finite
block filtering. The operational floor/ratio are 10/1.0 and remain provisional.
Count refusals precede fitting; constant samples, estimator exceptions, invalid
parameters/scale or non-finite quantiles refuse before table publication.
There is no estimator fallback, clipping, new tolerance or benchmark claim.

## Evidence

- Initial neutral/legacy regression gate: **64 tests passed in 30.34 s**.
- Final focused metadata/reference/count/fit/dummy checks: **17 passed in 8.23 s**,
  including high/low estimator parity, undercount, constant/invalid-parameter/
  exception refusals, unevaluated references and the ascending-month tie rule.
- Native-reader probe: all 14 P0 runs preserve every q/gwr value and timestamp;
  all use standard calendar, daily intervals, first native q gauge `101`, and
  zero missing values. The probe was repeated after adding the TOML coverage check.
- Real P0 reduction: **630 q + 56 gwr rows match exactly after key alignment**.
  The existing numerical inputs are read-only. All new indicator files are in
  `.tmp/scratchpad/2026-09-10_2046/neutral-metrics/`.
- Test-only synthetic provider has no stochastic payload; its dummy simulator
  consumes `RunForcing`, emits NPZ responses, and reaches the same run metric.
  Its test passed. Neither fixture is registered in production configuration.
- Actual Snakemake metric `script:` witness completed **2/2 jobs**, using the
  explicit serialized parameters and the frozen 14 native runs. The first
  scratch graph pointed one directory too far upward and refused before script
  execution; correcting that scratch-only path completed the run. Log:
  `p1-neutral-script-fixed.log`. Outputs remain in scratch `neutral-script/`.
  Both output tables are byte-identical to the direct neutral-function witness.
- Combined final gate: `pixi run --as-is test-full` — **3,473 passed, 9 skipped,
  1 xfailed in 720.17 s** (`p1-integrated-full.log`). The later-added focused
  refusal/tie fixtures also passed in the separate 17-test gate. Combined CLI:
  **20 passed in 36.78 s**. Repository lint and format passed (309 files).
- Scratch logs: `p1-neutral-tests.log`, `p1-native-responses.json`,
  `p1-neutral-metrics.log`, `p1-dummy-tests.log`. The retained comparison is
  `p1-neutral-comparison.json`; final gate results accompany the implementation.

## Review request and limits

Judge response physical/time binding, metadata/bundle refusals, explicit reference
selection, run/bundle grain, operational block/fit semantics and preservation of
the current table carrier. Generation acceptance remains separately recorded.
Simulator preparation/execution evidence is in `p1-simulator-handoff.md`.
No complete cross-backend scientific adequacy, GF-9 successor comparison,
GF-15 benchmark or P2 durable artifact acceptance is claimed.

## Named model-validator review

**ACCEPT — bounded P1 neutral-response and metric binding**, 2026-09-10.
Reviewer: `model-validator` (`/root/model_validator_p0`). The inspected reader,
logical declarations and reductions preserve the current response values and
five-column table carrier for the retained q/gwr experiment. The accepted Class-C
run semantics are explicit in memory; their durable result migration is not
claimed here. No new scientific criterion or tolerance is introduced.

Independent review checked current source hashes against the retained comparison,
native-reader values and timestamps for every P0 run, both stored indicator
tables, and the real Class-C reference under reversed series/member iteration.

| Check | Result |
|---|---|
| Source revision | All five recorded neutral-binding source hashes match current files |
| Native responses | All 14 runs × nine q/gwr series match their native numeric arrays and timestamps exactly; 3,286 daily observations per series, 2046-01-02 through 2054-12-31 |
| Physical interpretation | q `m3 s-1`, gwr `mm dt-1`, standard calendar, interval-end daily clock, explicit TOML physical-parameter and endpoint checks |
| Reference invariance | Roots `01`/`08` resolve gauge **101**, wet month **11**, dry month **8**; complete reference records remain equal under reversed member and neutral-series iteration |
| Reference coverage | Each root contributes nine finite-observation years and 108 year-months over the retained response window |
| Published P1 carrier | **630 q + 56 gwr rows**, unique keys, exactly equal to P0 after key alignment |
| Return-level record | Per-location evidence retains member block counts, total, required count and fitted parameters; the retained current experiment supplies 9 + 9 blocks, with the operational minimum 10 |

The reader terminates native headers at an explicit Wflow parameter/unit binding;
matching header text alone is insufficient. It preserves location ordinals and
NaNs, rejects infinity and inconsistent time/missing masks, and checks observed
coverage against the run TOML's start plus one model step through end. The
Gregorian datetime64 restriction is explicit. The reviewed Wflow clock trace
supports the interval-end interpretation without shifting output values.

The metric registry retains the authoritative vocabulary, declared response
units and daily interval requirements. Class A remains per run; Class B groups
the provider-declared members, including the unperturbed empty key; Class C
resolves one native-first gauge and one wet/dry month before per-run reduction.
The synthetic two-gauge test inspected here distinguishes the native-first gauge
from lexical order, reverses iteration while retaining ordinals, and refuses
inconsistent first-gauge membership. P1's separate legacy Class-C projection
preserves the predecessor pooling/weighting; it does not claim that the eventual
mean-of-run-values equivalence has passed full GF-9 for all missingness regimes.

Class-B code extracts blocks independently within each run, applies the inherited
water-year end anchor and seven-observation rolling mean before annual minima,
and concatenates only finite scalar blocks in numeric run order. Count screening
occurs before fitting. Constant samples, estimator exceptions, non-finite
parameters, non-positive scale and non-finite quantiles refuse before publication;
the xclim/SciPy estimator and probabilities remain unchanged. This accepts the
operational implementation of the provisional ratio **1.0** and floor **10**,
not their scientific adequacy. `benchmark_status=not_run` and
`screening_policy_status=provisional_operational` remain applicable. The two-year
low-flow return level uses probability 0.5; no stronger tail claim is implied.

The in-memory unit-index planner preserves self-membership for evaluated run
units, omits unevaluated run units, starts bundles after the complete collection's
run count, orders members numerically, retains an empty grouping key and refuses
insufficient capacity or invalid/duplicate declared membership. It consumes
provider-resolved declarations; this is not an independent durable grouping or
result-key validator. Native response requests currently select every observed
location for requested variables. A separately persisted location request and
independently derived exact expected result-key inventory remain necessary for
P2 publication/consumption guarantees; their absence is not concealed by the
successful current-table comparison.

Verification scope: `rapid`; numerical claims `affected`, checked against the
pre-change reference and the order-reversal diagnostic. Software test records
were inspected rather than rerunning the suite, and no model or estimator
benchmark was executed during review. Acceptance covers the current q/gwr
binding and explicit logical semantics, not empirical validation of other native
variables, alternate simulators, CHIRPS simulations, estimator precision,
dependent/nonstationary-block applicability, durable artifacts or full GF-9.
The test-only neutral provider/dummy simulator establishes interface traversal,
not scientific interchangeability of models. No uncertainty interval or
held-out predictive-skill claim is supported by this handoff.
