# P3 direct-run scientific handoff

**ACCEPT — bounded direct-run GF9 numerical migration and GF28 temporal
preservation.** Reviewer: Astra `model-validator`
(`/root/model_validator_p3`), 2026-09-12.
This accepts the named collection, complete native responses and q/gwr metric
publication for scientific preservation. The runner addendum below also accepts
the completed all-workflow-runner artifacts for the same bounded claim. GF27,
coordinator orchestration signoff and the final software gate remain pending;
this is not full P3 acceptance or milestone seal.

## Accepted artifacts

| Artifact | Identity |
|---|---|
| Collection | `71bf34ef8db1122bb91f097ac63ff01e450cf0a16ad9a9d3cca64128fd23ba88` |
| Collection revision | `5c21f75dc5cc4354ee32bd9983e1a39d55fea09944eb5bc20657dd8318010885` |
| Simulation | `3a8c1fc6c633687bb95736f3c5f76cf8ac323927db32af7f767f8bde03a41a10` |
| q/gwr metric set | `49ca015882e8396f4fd46930b9a95be3ccbd4dfcaf2d5c7840bf1b3df95aa665` |
| Retained-only gwr metric set | `d354a347e50cb03dbc5c538e929cf7411be8758c38f3cdcc15aec36f323790ff` |

The final experiment is
`.tmp/scratchpad/2026-09-11_0010/p3-final-direct/project/experiments/p3_final`.
Its old side is the immutable, freshly captured P0 experiment under
`C:/Users/taner/workspace/_workbench/blueearth-cst-r12/2026-09-10/prechange`.
The [final GF9 comparator](gf9-direct-comparison.json) passed without its
development flag and records scientific configuration, source/model/environment
provenance, run/bundle crosswalks and immutable artifact identities.
The [independent review](gf9-independent-review.json) binds that report and the
reviewed manifests, repeats the native/metric checks independently, and records
all Class-C and return-level-block checks. The executed code belongs to frozen
runtime inventory digest
`b12a76551cf13b9bce3f96e5d8125954ae70dbfc88278e32f93a90f3e980be98`.

## Numerical and temporal results

| Check | Result |
|---|---|
| Generated collection | GF9 compares all 14 forcing files exactly against P0; two roots and six descendants per root are fully mapped |
| Native responses, independently repeated | All 14 CSVs have identical bytes, numeric values, column order and time axes to P0: 126 series, each with 3,286 observations |
| Class A | All 546 per-run values match P0 exactly at publication precision |
| Class B | All 70 pooled values match P0 exactly, including the unperturbed bundle |
| Class C | All 140 run publications match independent annual-within-selected-month calculations; all 70 raw mean projections reproduce the old pooled publication exactly |
| Coverage | 686 old rows map to 756 new rows; 21 units and 28 membership rows; zero duplicate joins, missing counterparts or unexplained new rows |
| Reference | Independently selected first native q gauge `101`; unperturbed runs `01`, `08`; wet month 11, dry month 8 |
| Return-level blocks | All 70 location fits independently retain 9 + 9 = 18 finite annual blocks, requirement 10, finite fitted parameters and positive scale |
| Retained-only metric values | All 56 gwr rows in the separate retained-only publication exactly match the corresponding full metric-set values |

The independent Class-C calculation groups selected-month observations by
calendar year and averages the annual means, without invoking the production
run reducer. It uses unrounded values before applying the unchanged float32,
four-significant-digit publication representation. A mean of individually
rounded run publications can differ from the old pooled publication; the GF9
crosswalk records a maximum such difference of 0.005. The independent raw
projection explains these differences fully. No tolerance was relaxed, and no
Class-A/B value changed.

Reference-order discrimination is supplied by the executed GF9 comparator and
reviewed source: four independent combinations of native-artifact and
neutral-series order preserve the persisted reference and resolved months.
The opposite-season fixture has native-first gauge `9` peaking in July and
gauge `2` peaking in January; its deliberately swapped ordinal selects the
wrong gauge and month, demonstrating that the fixture can detect that error.
The recorded numeric perturbation, lost-row and duplicate-row controls reject
their wrong answers. The reviewer independently derives the real-run reference
from raw CSV columns and pooled monthly sums, matching the persisted result.

The earlier [GF28 prepared-clock review](gf28-temporal-review.md) independently
verified all 14 source/prepared clocks, including both leap days, daily spacing,
the complete TOML time sections, and the recorded conversion/clip/endpoint
sequence. Completed native responses now independently confirm daily interval-end
observations from **2046-01-02 through 2054-12-31**, identical to P0. They close
the pending observed-response part of that review. Return-level blocks are
derived separately within each member, preserving the partial first year and
seven-observation rolling completeness. Current non-January behavior retains
the accepted P2 semantics and inspected existing checks; this does not imply
that a non-January Wflow run was executed during P3.

`read_simulation(require_complete=True)`, `read_response_inventory`, and both
`read_metric_set` calls pass on the retained direct experiment. The coordinator
reports 25/25 jobs for direct simulation and 3/3 jobs for the physical-offline
retained-only publication. This reviewer confirms their final artifacts and
value equality; the offline execution conditions and scheduling remain the
coordinator's command-log evidence.

## GF15 and the acceptance boundary

The published validation record remains `provisional_operational` with benchmark
`not assessed`. The 18-block counts and valid parameters establish preserved
operational screening and fit validity, not estimator adequacy, independence,
stationarity or precision. No GF15 benchmark was executed by this review.

A **bounded P3 migration-preservation handoff may be accepted with GF15 estimator
adequacy explicitly pending**. The master brief assigns the separately
owner-gated benchmark to milestone seal; the P3 validation paragraph and
ADR 0009 likewise keep its qualification separate. P1/P2 already accepted the
operational mechanism without a benchmark. These scoped claims must not become
an assertion that every GF1–GF32 requirement passed or that the milestone is
sealed. GF15 criteria still require the owner's acceptance before execution,
and the benchmark/seal requirement remains open. The concrete proposed criteria
and review recommendation are in
[scientific-review-preparation.md](scientific-review-preparation.md).

## Verification and limits

Verification: release / numerical affected at the migration boundary. A read-only
independent command through `pixi run --as-is python -B` compared all native
CSVs and derived the run/bundle joins, selected reference, Class-C values and
annual-block counts from actual retained files. It completed with exit 0 and
wrote only `gf9-independent-review.json`. No workflow, pytest, preparation,
simulation, estimator refit or benchmark was launched by the reviewer.
The existing final software gate is still required before P3 acceptance.

The planned comment-only runner correction must retain the original executed
source inventory and have a separate exact pre/post hash and diff reconciliation.
It must not silently replace executed-run provenance. This handoff supplies
GF9/GF28 scientific evidence; it does not waive GF27, runner or software gates,
nor authorize a standing-baseline re-record or milestone seal by itself.

## All-workflow-runner addendum

**ACCEPT — matching bounded GF9/GF28 preservation through the final runner.**
The coordinator completed fresh runner generation (37/37 jobs) and simulation
(25/25 jobs) in the separate `p3-final-runner` root. Its
[GF9 comparator](gf9-runner-comparison.json) passes the same unchanged criteria.
An additional [independent read-only review](gf9-runner-independent-review.json)
reopens the complete simulation, response inventory and metric set, and checks
the raw files against the independently reviewed direct run.

All 14 generated forcing files, 14 native CSVs and 14 temporal sidecars are
byte-identical between direct and runner executions under the same run crosswalk.
Both metric tables and `unit_index.csv` are also byte-identical. This establishes
that the direct review's native, metric and temporal conclusions apply to these
runner artifacts without repeating identical numerical calculations. The final
reference-reversal and discrimination evidence agrees with the direct report.

The runner collection is
`382ea628574513c6d1d31c75d6f9904b943e553c51fb8f8061b0476b85b6cd6d`,
revision `4f49e542fd40f546cd92fcc9f697e29592b33d70475e51c3ed7f9dfeb5969991`;
its metric set is
`c1f94aa4045882507887735472aec069fa39ec4985fd524e00fe400019d0c5f2`.
The independent JSON records its simulation ID and all comparison hashes.
The read-only command completed with exit 0; no workflow or test was launched.
GF27, final software and coordinator orchestration signoff remain separate.

The limit of applicability is exact preservation of the accepted seed-123 ERA5
reference, two realizations, six design points and the 2046–2054 simulation
window. The four-branch preparation limitation remains in
[GF31 acceptance](gf31-acceptance.md). No held-out hydrological skill or
observational accuracy is established. Parameter, structural, observational,
scenario and internal-variability uncertainties are not quantified; two
realizations do not establish adequate ensemble sampling, and the pooled
Class-B point estimates carry no fit-uncertainty interval.
