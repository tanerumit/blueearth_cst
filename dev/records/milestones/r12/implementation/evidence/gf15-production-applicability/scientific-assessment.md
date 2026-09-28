# GF15 candidate C: production applicability assessment

Date: 2026-09-13
Assessor: model-validator `/root/model_validator_production_applicability`
Status: bounded recommendation for adapter review; no production acceptance
Scope: repository contract and retained evidence assessment; no new fits or validation data

**Recommend a separately reviewed, metric-stage-only integration of candidate C for provisional operational point estimates, conditional on the controls below.** The existing evidence supports reviewing that implementation; it does not support calling actual discharge bundles validated. Real-bundle scientific adequacy is not a prerequisite imposed by the accepted provisional-use contract, but the complete persisted limitations are a prerequisite. Production currently lacks that complete metadata contract, so adoption cannot be justified merely by retaining today's metadata.

This recommendation separates a method-policy decision from implementation acceptance. The owner approved the 8x performance policy; that did not automatically authorize production adoption. The next bounded decision is whether to adopt the qualified algorithm under the existing provisional scope, following review of a concrete adapter and its evidence/identity contract. This assessment neither executes that adapter nor approves a successor baseline or R12 seal.

## Evidence and permitted claims

Controlling sources are the frozen [candidate design](../../../gf15-alternative-estimator-design.md), D1–D6 and “Parameters and defaults”; the [identity design](../../../wf3-simulation-identity-design.md), §§7.5, 7.6 and 8.4; and the accepted [8x policy](../gf15-accuracy-8x/README.md), [scientific handoff](../gf15-accuracy-8x/scientific-handoff.md), and [signed verdict](../gf15-accuracy-8x/results/signed-verdict.json). Older design references to original benchmark thresholds and the predecessor estimator are historical scope, not evidence that production already implements C.

| Evidence | Exact interpretation |
|---|---|
| C passes 144/144 individual cells at 8x | Deterministic conjunction on the retained development matrix under `gf15-accuracy-8x-v1`; 24/24 baseline and 72/72 eligible combined cells. |
| Error limits | Absolute signed median error ≤0.80 in scale and eligible relative coordinates; P90 absolute error ≤4.00 upper / ≤2.00 lower. Relative limits permit 80%, 400% and 200%, respectively. These are owner-selected targets, not uncertainty intervals or precision guarantees. |
| Qualified grid | SciPy shape c ∈ {-0.2, 0, 0.2}; n ∈ {10, 18, 30, 60}; p ∈ {0.9, 0.5}; eligible relative ratios rho ∈ {0.5, 2, 10}. Baseline and rho=0 relative errors are null; rho=0.05 remains diagnostic. |
| Acceptance and translation | All C valid-fit rates are 1.0 in the retained cells; 120/120 translation cells pass, with 120,000 both-accepted pairs and maximum scale-error delta 5.88373794130348e-12 against 1e-6. This supports numerical equivariance on those pairs. |
| Predecessor comparison | A and B pass 143/144 under diagnostic 8x scoring. C's all-cell pass is not evidence of meaningful out-of-sample superiority. Original C and 3x C remain failed at 15/144 and 124/144. |

The evidence permits the statement “candidate C passed the retained synthetic GEV development matrix under the owner-approved eightfold policy.” It permits carrying a `reviewed_bounded` benchmark status only when the exact candidate, policy, evidence digest and scope are bound to the new implementation. It does not permit attaching C's result to the current xclim/SciPy fitter, claiming independent validation, validating the count rule, or extrapolating accuracy to other shapes/counts/ratios, dependent/nonstationary samples or real discharge.

The error regimes remain consequential despite the pass. At c=-0.2, n=10, p=0.9, rho=0.5, C's absolute signed median relative error is 0.7096987457437947 and relative P90 is 3.8309444134013266. At diagnostic rho=0.05, c=-0.2, n=10, p=0.5, relative P90 is 14.856985611770813. A passing flag must not hide these limitations. The low-flow quantity remains the median of annual minima of seven-observation rolling means, with no sign reversal; the fixture does not validate extraction from discharge.

## Uncertainty and validation status

| Source | What is established; what remains unresolved |
|---|---|
| Parameter-estimation variability | Empirical signed medians and absolute-error P90s from 1,000 IID stationary GEV draws per shape/count cell. No parameter or return-level interval coverage is established. |
| Finite Monte Carlo variability | Twelve independent base-cell experiments, each with 1,000 draws; methods, probabilities and translations share draws. Uncertainty in estimated medians/P90s/valid rates remains unquantified. Derived rows are not independent replications. |
| Adaptive choice | Candidate development and the 8x threshold selection used already observed evidence. No held-out sample, fresh-seed replication or selection adjustment exists. The pass is development qualification. |
| Numerical uncertainty | Inherited readiness/reference controls and retained translation checks support the qualified implementation in its recorded environment. A production wrapper/environment requires its own fidelity checks. |
| Structural, observational and forcing uncertainty | Real block dependence, nonstationarity, distribution mismatch, observation errors, hydrological-model errors and forcing/scenario/internal variability are absent from these fixtures. |

There is no new naive benchmark, temporal/spatial validation split or hydrological adequacy result. Generating truth defines the fixture loss; A/B are paired predecessor comparators. Therefore this assessment supplies no fit-for-purpose validation for hydrological decisions. Replaying retained draws cannot remove adaptive-selection or real-system uncertainty. More evidence may characterize those sources; it cannot be assumed to eliminate structural or observational uncertainty.

## Existing production gaps

Read-only inspection of `blueearth_cst/experiment/metric_registry.py::reduce_bundle` shows per-member block extraction, finite-block filtering, count screening and an xclim `fit(..., dist="genextreme")` / `parametric_quantile` path. Its broad `except Exception` maps every caught fault to `InvalidReturnLevelFit`. Candidate D1 instead has a narrow source-verified exception allowlist; unrelated adapter or dependency faults must stop the operation. This is a required integration change, not a new statistical refusal policy.

`metric_plan.py::current_metric_request` supplies only `{"status":"provisional_operational","benchmark":"not assessed"}`; `metric_request` rejects every different validation object. This is a pre-existing gap against §7.5, distinct from replacing the estimator. The complete screening fields, benchmark domain/criteria/status, report binding and copy, application scope and limitations must be implemented together with adoption. The old object does not establish compliance simply because it contains the word “provisional.”

Current `tests/test_metric_registry.py::test_bundle_preserves_estimator_and_records_per_member_blocks` intentionally compares bundle output with the predecessor reducer. Preserve the block-extraction assertion, but a future C test must use the qualified candidate reference rather than asserting unchanged predecessor return levels. `tests/test_metric_plan.py` already exercises environment-based metric identity and persisted bundle evidence; extend that seam to the new method/evidence contract. These observations are inspection results, not tests run in this assessment.

## Bounded adapter invariants and acceptance checks

The following checks are prospective implementation acceptance conditions. They do not requalify the estimator statistically and do not authorize a new fitting campaign.

| Invariant | Discriminating check for the reviewed implementation |
|---|---|
| Preserve the estimand and blocks | For fixed multi-member daily inputs, compare the exact per-member finite block arrays/counts and pooled ordering with the predecessor extraction. Include a member boundary where concatenating daily data first would change the seven-observation minimum, and retained partial-year/missingness cases. Keep peak p=0.9 and low p=0.5. |
| Preserve operational screening | `required=max(ceil(1.0*T),10)` remains location-specific. A required-minus-one input refuses before fitting; required count proceeds to fit-validity checks. Include T>10 to discriminate the ratio from an unconditional floor. Do not treat a passing count as a precision claim. |
| Implement the same candidate | On frozen representative readiness/reference inputs, compare acceptance, normalized moments, shape convention, named parameters and quantiles against the qualified C implementation in the declared environment. Preserve range normalization, `lmoments3` 1.0.8 algorithm, c>-1 domain, float64 quantile expression, ties and absence of fallback/retry. Do not let generating truth or fitted-ratio classification enter the production adapter. |
| Match the requested-probability contract | Production maxima and minima arise from different samples and each request its own scalar quantile. Use D2's conjunction over the probabilities actually requested; if an API accepts several, one invalid requested quantile refuses the entire request. Never import the benchmark's joint-baseline valid rate as a measured production valid rate. |
| Preserve refusal versus fault distinction | Constant/invalid-domain/nonfinite-quantile cases refuse without a metric row. Correct source-origin allowlisted library exceptions refuse; identical messages from an unrelated frame and unexpected faults propagate as execution failures. No enclosing broad catch may relabel them as statistical refusals. Support/log-density diagnostics must not become a new likelihood-based refusal. |
| Carry the complete bounded claim | Persist ratio 1.0, floor 10, `screening_policy_status: provisional_operational`, `benchmark_status: reviewed_bounded`, exact candidate/policy/domain/criteria, immutable report path/digest, `application_scope: operational_screen_only`, and explicit unvalidated near-zero relative error and unestablished actual-bundle applicability. Preserve the adaptive-policy history and original/3x failures in the bound report. Reject a report/estimator mismatch or missing/tampered report. |
| Make identity sufficient | Changes to candidate implementation, imported reducer code, effective metric environment, validation declaration or report digest must change the metric definition/set as applicable. Each isolated mutation must produce a new metric identity; replay must preserve it. Candidate dependency identity must be included. Collection/simulation/retained response identities must remain reusable. Ready predecessor manifests are immutable. |
| Publish self-contained evidence | The ready metric set contains the referenced immutable report and verifies its digest; it must remain interpretable without reading a mutable live registry or an evidence file under `dev/`. Persist sample counts/coverage and actual estimator/environment identity in fit evidence/refusal context. Test publication/read-back and report tampering at the existing metric-plan boundary. |

Same-environment replay should preserve exact qualified behavior. A changed numerical environment needs an explicit discrepancy classification against the existing controls; do not invent a tolerance from observed differences. Differences in Class-B values from the predecessor are an intended estimator change and require later migration evidence. Unrelated block, grouping, unit or Class-A/C changes would indicate scope drift. A later successor baseline records an accepted implementation; its creation cannot substitute for these checks or actual-bundle validation.

## Applicability evidence and decision boundary

| Claim or action | Evidence required first |
|---|---|
| Implement a provisional operational adapter | Reviewed method mapping and metadata/identity contract above; then measured technical acceptance. No real-basin accuracy claim is necessary or conferred. Current production and metadata gaps block adoption until resolved. |
| Say the result replicates beyond development draws | Separately authorized independent data/seeds, prospective unchanged criteria and declared dependence-aware comparisons. No such work is authorized or executed here. |
| Say an actual bundle meets useful accuracy requirements | Define its decision use and tolerable errors first; establish member/block construction and temporal coverage, dependence/nonstationarity and distribution applicability; assess against suitable independent observations/reference and a relevant naive comparator, stratified by relevant regimes. Address observational uncertainty and near-zero behavior explicitly. Fitted c or fitted quantile/scale alone cannot identify the generating benchmark cell. |
| Validate `1.0`/`10` screening as a policy | Separately reviewed domain and block-dependence assessment linking usable counts to performance for the intended systems, including failure regimes. A synthetic-grid pass or a single bundle's successful fit is insufficient. |
| Use estimates for threshold-crossing decisions with estimator uncertainty | Separately specified and validated uncertainty treatment and decision-relevant adequacy; §7.6 explicitly leaves Class-B intervals outside this seam. The 8x P90 error limits are not intervals around an emitted estimate. |

The real-bundle assessment would require data not supplied by the synthetic fixtures: provenance and coverage for actual members/locations, relevant independent reference observations with their uncertainties, and an explicit use/accuracy criterion. The table states evidence obligations, not a selected new method or a request to run those analyses now.

## Alternatives and recommendation

| Option | Tradeoff and disposition |
|---|---|
| Reviewed C adapter with complete provisional metadata | Advances the existing automation scope using the owner-approved policy while exposing its limits. Recommended next bounded scope; technical fidelity, dependencies and immutable evidence remain acceptance blockers. |
| Require real-bundle validation before any operational use | Supports a stronger future scientific claim, but expands this migration into a new modeling/validation program with presently unspecified data and use criteria. Not required by §§7.5–7.6 for provisional point estimates. |
| Retain predecessor fitter and failed/unassessed evidence | Avoids an immediate estimator/dependency change, but cannot inherit C's 144/144 result and does not resolve the owner-selected replacement path. Metadata completeness still needs repair. |

Candidate C is suitable to proceed to a bounded production-adapter review under `operational_screen_only`; it is not yet accepted in production and is not validated for actual hydrological decisions. The retained pass is adaptive, permissive and limited to the declared synthetic matrix. Real-bundle suitability, finite Monte Carlo uncertainty, dependence, distribution mismatch and observational/model uncertainty remain unresolved and must remain visible in every adopted metric set.

Verification: release decision assessment / numerical claims affected, constrained to a documentary traceability review. Read the repo testing-policy pin and applied the testing-policy and Python-discipline skills for check scope and read-only integration inspection. Inspected the named frozen contracts, 8x handoff/verdict, production entry points and existing targeted tests; checked this document's local links. No new fits, data, empirical results, code tests, workflow runs, dependency changes, baseline checks or git writes were performed. The future adapter checks above remain unexecuted.
