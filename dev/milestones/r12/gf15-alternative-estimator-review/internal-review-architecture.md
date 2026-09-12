---
verdict: revise
doc_version: design-v2.md
findings:
  - id: architecture-1
    severity: major
    section: Method
    finding: The estimator-exception refusal boundary does not distinguish known statistical failures from unexpected implementation or runtime failures.
    rationale: D1 step 4 permits estimator exceptions as refusals without an exhaustive classification, while Stage 2 stops on input, coverage or control failures. Unexpected exceptions could therefore produce complete-looking rows and depress the valid rate instead of stopping a broken run. The library uses a generic non-convergence Exception, so exception type alone is insufficient.
    suggested_fix: Enumerate approved exception-derived refusal cases at the narrowly scoped library call, identify generic non-convergence by source context, retain exception diagnostics, and propagate all unclassified exceptions as run failures. Validate this boundary at Stage 1; do not blanket-accept every ValueError or every exception from the adapter.
  - id: architecture-2
    severity: minor
    section: Validation regime
    finding: The readiness manifest does not explicitly require verification of predecessor comparison join mappings.
    rationale: Input hashes and comparison keys are already required, but byte identity does not establish unique and complete mappings from both predecessor formats to those keys. A late mapping failure could delay the required paired deliverable after qualification work.
    suggested_fix: Make Stage 1 verify fixture and predecessor inventories, hashes, key mappings, uniqueness and coverage, including deterministic derived keys. Stop before qualification if comparison requires new fitting or altered cohorts.
  - id: architecture-3
    severity: minor
    section: Method
    finding: Shared baseline acceptance and per-probability quantile refusal need an explicit precedence rule.
    rationale: D2 shares acceptance across both baseline probabilities whereas D1 step 5 can refuse a particular quantile. The contract does not state whether this revokes both rows or only one, affecting cell denominators and translation checks. This is an edge-path ambiguity, not evidence of an actual matrix failure.
    suggested_fix: Define fit-level and quantile-level status precedence and which enters each cell and paired check, preserving authoritative GF15 refusal semantics. Escalate only if resolution changes those semantics.
  - id: architecture-4
    severity: minor
    section: Validation regime
    finding: Branch controls are required but their reference cases and tolerance coverage remain readiness work rather than reviewable examples.
    rationale: The document explicitly requires every disclosed branch, so the three generating-shape controls are not the entire suite. The readiness reviewer still needs an agreed distinction between branch characterization and pass-fail controls before qualification.
    suggested_fix: Include branch-to-control and independent-oracle mapping in Stage 1, with fixed inputs and pass or characterization semantics. Preserve the solver and GF15 gates; return analytical-tolerance changes to design review rather than silently tune them.
---

# Architecture and internal-consistency review

Reviewed frozen `design-v2.md` under settled G1: range-normalized lmoments3 1.0.8, finite-mean domain, diagnostic-only support, unchanged criteria and proposal-only authority. The revision request concerns the exception contract. It does not reject qualification because the candidate may fail. External IDs below are not regraded.

The architecture is coherent at proposal level. `performance_analysis` binds the candidate to Python implementation and independent model validation; `orchestrator` binds the three-stage sequence to architect ownership. Other slots have reasons for non-applicability consistent with the outputs. Truth stays outside the estimator interface. Individual and common-cohort summaries remain separate, all-draw refusal denominators are retained, and independent validation precedes integration. Reproducibility is planned, not demonstrated. No managed-root run enters readiness here; namespace claim and run-control conformance are correctly inapplicable at this stage.

## Exact external-premise checks

### ext1-1: supported arithmetic; contested scope extension and causal interpretation

The translated-fixture relation is exact: q=rho with generating scale one, so the lower relative P90 gate at rho=.5 becomes .125 in generating-scale units. The quoted 1.645/sqrt(n) values, approximately .520, .388, .300 and .212, are consistent with the stated approximation. For c=0, the density gives score (1-exp(-z))/sigma. Since exp(-z) has unit exponential distribution, location information is 1/sigma squared. This is an independent algebraic check using the [official Gumbel density](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gumbel_r.html), not a candidate computation.

That calculation applies to the Gumbel location submodel, c=0. Multiplying counts by three shapes does not establish the corresponding information reference at c=-.2 and c=.2. More fundamentally, an asymptotic normal efficiency reference is not a finite-sample P90 bound for this biased nonlinear estimator or its conditional-on-acceptance summaries. The design already states these limitations. Even a shape-specific asymptotic reference would not identify the cause of an observed failure.

The suggested rule attributing failure to threshold severity and declaring it not evidence about the candidate is therefore unsupported. Failure is evidence that this complete candidate does not meet fixed qualification on these retained draws. It is not proof that the L-moment principle is unsuitable generally, or that the thresholds are universally unattainable. An optional count-wise Gumbel illustration could improve context if restricted to that submodel and kept non-causal; it cannot justify dropping cells or bypassing qualification.

No owner ruling is needed to preserve this bounded interpretation. Redefining the study to identify attainable thresholds, change its target population, or excuse failures requires a new owner framing decision. This review does not recommend or authorize such a change.

### ext1-5: supported uncertainty limitation; contested contradiction and automatic expansion

The empirical summaries have Monte Carlo error as estimates of repeated-sampling performance. The design explicitly leaves it unquantified, explains shared-draw dependence and adaptive selection, limits a pass to the development matrix, and reserves intervals or replication for separate authorization. Its required uncertainty statement conveys substantive limitations. Requiring that statement while declining numerical intervals is internally consistent.

The assertion that an executor cannot reveal proximity to a threshold is too strong: point summaries and thresholds reveal numerical margins. They cannot establish the sampling uncertainty of those margins. A verdict about the retained matrix is observable and reproducible; a fresh-seed stability claim would exceed the scope. Bootstrapping the reused development draws would estimate a conditional uncertainty component, not remove adaptive-selection optimism or establish independent replication.

Two legitimate prospective scopes exist: retain deterministic qualification with the explicit limited claim, or add non-gating Monte Carlo diagnostics. The latter requires resampling, RNG, pairing, conditional-refusal and interpretation contracts. One-standard-error proximity flags would be descriptive, not a calibrated guarantee for the conjunction of dependent gates. This expansion needs an explicit owner ruling before design adoption and separate execution authorization. Review promotion supplies neither. A fresh-seed holdout answers a different question and is also additional scope. This review chooses neither expansion.

## Evidence and limitations

Read `design-v2.md`, `intake.md`, `review-brief.md`, G1 authority in `status.md`, `external-review-r1.md`, and the original `results/criteria.json`. Checked the criteria's coverage, thresholds, conditional-summary rule and claim boundary by inspection. Listed the initial 12 names in each predecessor result directory to confirm their different artifact conventions; this was not an exhaustive inventory, and compressed rows were not validated. Architecture-2 is therefore a readiness clarification, not a claim that joins are impossible.

The [official lmoments3 source](https://lmoments3.readthedocs.io/stable/_modules/lmoments3/distr.html) confirms generic non-convergence and separate invalid-moment errors, plus rational and iterative branches. This supports narrow classification of known failures; it does not force a blanket catch. The rendered stable source is not a verified installed wheel, so the future source-digest gate remains necessary. Branch accuracy and proposed tolerances were not numerically tested.

Applied scientific-workflows and reproducible-computing guidance to provenance and validation handoffs. No fits, Monte Carlo diagnostics, installations, imports of candidate code, candidate behavior tests, production integration or design changes occurred. Only this assigned review artifact was written. Empirical predecessor results were not recomputed. Remaining risks are runtime compatibility, control calibration, comparison-schema readiness and inadequacy under unchanged criteria, pending the specified handoffs.
