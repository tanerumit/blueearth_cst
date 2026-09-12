---
verdict: approve
doc_version: design-v1.md
findings:
  - id: domain-1
    severity: minor
    section: "Context and motivation, opening recommendation; Alternatives considered, L-moment/PWM; Method, D1 step 2"
    finding: "The estimator-specific limits of the cited PWM evidence and of the word unbiased should be explicit."
    rationale: "Hosking et al. (1985), section 5, states that its reported PWM simulations use plotting positions (j-.35)/n, whereas D1 deliberately specifies unbiased order-statistic PWMs. Unbiasedness applies to the raw sample PWMs and linear L-moments under IID sampling with existing expectations, not generally to t3, fitted GEV parameters, or return levels. The present wording can blur these distinctions even though it makes no guaranteed performance claim."
    suggested_fix: "Describe D1 as GEV estimation from unbiased sample PWMs/L-moments; explicitly disclaim unbiased fitted parameters and quantiles, and label the 1985 simulation results as indirect evidence for this exact variant. Retain the selected algorithm and unchanged gates."
  - id: domain-2
    severity: minor
    section: "Uncertainty treatment, final paragraph; Validation regime, artifacts paragraph"
    finding: "Name the finite Monte Carlo uncertainty and effective independent unit alongside the fixed-matrix pass/fail record."
    rationale: "The 1,000 retained draws per base cell provide finite Monte Carlo information; the probabilities, translations, and A/B/candidate comparisons share those draws. Exact replay and 120,000 translation pairs do not supply 120,000 independent accuracy replications. The current development-matrix caveat is sound but does not explicitly name this remaining uncertainty source."
    suggested_fix: "Require the handoff to state that empirical medians/P90s and valid rates have unquantified Monte Carlo uncertainty, with 1,000 independent draws per generating shape/count cell and correlated derived rows. Preserve deterministic GF15 decisions. Any later intervals or replication should use draw-level pairing and separate authorization, without treating interval overlap as a threshold waiver."
---

# Scientific review — design-v1.md

Approved as a **bounded proposal for a candidate qualification study**, with two minor clarifications. This is not estimator acceptance, an execution authorization, a GF15 pass, or an owner G1 ruling. No blocking or major scientific defect was found within the expressly limited scope. The absence of evidence that the candidate can pass every criterion is not itself a defect in a candid, prospective qualification study.

## Claim and evidence assessment

The decision under review is whether one fully specified L-moment GEV estimator is worth a separately authorized qualification against the existing retained IID fixtures. Its intended output is an empirical cell-level adequacy record, including failure. It does not estimate observed-basin performance or validate the provisional screening policy.

The predecessor evidence supports the motivation without establishing a computational explanation for all error. The original handoff reports 3/24 baseline accuracy cells passing and 118,457 translation deviations. The full-B handoff confirms 3/24 baseline and 6/72 eligible scale-and-relative cells passing, with 30 accepted-pair numerical failures, 70 both-refused pairs and one acceptance mismatch. All n=18 baseline fits were accepted while every corresponding accuracy cell failed. The 974 nonfinite physical log-density diagnostics have no isolated causal explanation. The proposal preserves these failures and does not convert successful termination into adequacy.

The scientific rationale for considering another estimation principle is reasonable. Its superiority is untested. Hosking et al.'s small-sample evidence supports PWM as a serious family of alternatives, but its reported simulation variant differs from D1 (domain-1). See [Hosking et al. (1985), section 5](https://www.stat.cmu.edu/technometrics/80-89/VOL-27-03/v2703251.pdf). MPS and regularization are credible alternatives with distinct implementation or prior commitments; the proposal does not conceal them or pretend their published comparisons establish GF15 performance. [Wong and Li](https://arxiv.org/abs/math/0702830) and [Martins and Stedinger](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/1999wr900330) support that bounded interpretation.

## Mathematical and API checks

D1's raw PWM formula, conversion to the first three L-moment quantities, GEV shape equation, scale/location inversion and c=0 limit are consistent. Its quantile formula uses the correct SciPy c=-xi convention. Requiring c>-1 matches the finite-mean domain; it is disclosed estimator-domain handling, not a hidden generating-shape prior. Nonlinear ratios and fitted quantities do not inherit unbiasedness (domain-1). The [sample implementation](https://lmoments3.readthedocs.io/stable/_modules/lmoments3.html) and [SciPy convention](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.genextreme.html) support the specified paths.

Read-only inspection of the documented GEV source confirmed the named API, returned parameter keys, rational/iterative branch structure, iteration limit, convergence criterion and Gumbel approximation described by D1. The specification appropriately makes pinned implementation behavior authoritative and forbids a silent solver replacement. A notable control precaution is to calculate population L-moments independently: the documented distribution's own forward c=0 L-moment branch is unsuitable as an unquestioned oracle. The design already requires independently calculated controls. [GEV source](https://lmoments3.readthedocs.io/stable/_modules/lmoments3/distr.html).

The proposed wheel SHA-256 matches the published wheel entry. That verifies the proposed artifact identity, not compatibility or the bytes of a future installation. Those remain explicit pre-execution readiness checks. [PyPI 1.0.8 file metadata](https://pypi.org/project/lmoments3/1.0.8/#files).

Local xclim source confirms PWM delegation to a distribution with `lmom_fit` and MPS delegation to SciPy. The installed-tree inspection found no matching lmoments3 package directory; the lock entry is under xclim `constrains`. Direct D1 calls therefore avoid an assumed installed production wrapper. The MPS discussion correctly identifies the need to free location and scale and freeze stochastic behavior. [SciPy fit API](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fit.html).

## Gates, validity, and falsification

The 132,000 fits, 144,000 scalar quantile rows, 144 summary cells, 120,000 pairs, generating-scale denominators, conditional error summaries, all-attempt validity denominators and numerical thresholds match the retained criteria. At rho=.5 the relative gate indeed implies P90 scale-error limits .25 upper/.125 lower and absolute median bias .05. No additional criterion is inferred from that algebra.

The Gumbel known-nuisance information illustration is correctly calculated and correctly qualified as asymptotic intuition. It does not prove a finite-sample impossibility, especially for biased procedures or conditional-on-acceptance summaries. Conversely, the evidence provides no defensible all-cell success promise.

Diagnostic-only support handling is coherent for this explicitly defined quantile estimator. An L-moment fit can yield an endpoint inconsistent with a supplied observation without a failure of the moment computation. That prevents a likelihood-style validity test from being smuggled into the method. It also means computational acceptance cannot certify a plausible data-generating model; D2 states this limitation. G1 should consider this policy explicitly before selecting the candidate. No retrospective B refusal or denominator change is warranted.

Independent population-moment/quantile controls can reveal sign, parameter mapping and approximation errors; invalid and boundary controls can expose acceptance mistakes. The complete translated matrix can falsify implementation-level equivariance. Exact replay tests repeatability only. Independent recomputation of criteria from raw records tests evidence correctness, not independent statistical replication. A/B are paired method references, analytical quantiles supply truth, and an empirical-quantile comparison is a possible later diagnostic rather than an undeclared extra candidate. No naive predictive-baseline requirement is imposed on this narrowly fixed known-truth estimator qualification.

Freeze-before-execution, no truth metadata in the adapter, all-draw reporting and stopping after one failed candidate constrain adaptive selection. Fresh-seed replication remains necessary before broader validation claims, and the proposal correctly reserves it for separate scope. Monte Carlo precision remains unquantified (domain-2); exact fixed-matrix decisions remain possible without claiming population-level certainty.

## Premise disposition

"Supported" below refers to the precisely bounded register statement, not an enlarged adequacy or causality claim. Existing audited records were inspected; the full numerical audit was not rerun.

| Premise | Disposition | Finding ID | Assessment and observation needed where unsettled |
|---|---|---|---|
| E1 | supported | — | Original handoff and criteria confirm the reported accuracy and translation failure. No new observation needed for that historical result. |
| E2 | supported | — | Full-B handoff confirms counts and lack of qualification. Numerical improvement does not establish accuracy. |
| E3 | supported | — | Full-B record confirms all four pair categories and maximum accepted deviation above 1e-6. |
| E4 | supported | — | Accepted n=18 accuracy failures and 974 mapped-density diagnostics are recorded. Isolating the latter's cause would require targeted support/rounding analysis; it is not presently an established optimizer or model-support diagnosis. |
| E5 | supported | — | Investigation and full-B evidence support an incomplete decomposition. Quantifying sampling versus optimization effects would require additional controlled analysis; observed n-dependence alone cannot partition them. |
| E6 | supported | — | The retained criteria and accepted R12 section 7.5 preserve the benchmark/applicability separation. Owner authority is taken from the supplied intake. |
| E7 | supported | — | Current metric_registry.py calls xclim GEV fitting/quantiles; R12 section 8.4 specifies immutable metric identity. No alternative has replaced production. |
| E8 | supported | domain-1, domain-2 | Supported as an explicitly untested hypothesis and statement of ignorance. Actual improvement or fixed-matrix adequacy remains unsettled pending the specified complete qualification; independent generalization requires fresh draws under separate approval. |
| E9 | supported | — | Local stats.py and lock/package-directory inspection support the interface and bounded availability statement. Import compatibility and actual frozen wheel/source identity require future authorized readiness checks. |

## G1 framing and residual uncertainty

G1 should decide whether the value of one transparent alternative-estimator study justifies proceeding despite demanding targets and no evidence of an all-cell pass; whether the finite-mean domain and diagnostic-only support policy are acceptable for that study; and whether a development-matrix answer is useful with independent replication still outstanding. These are owner decisions, not adjudicated here. They do not reopen the numerical criteria.

The proposal is fit for the limited purpose of specifying a falsifiable IID GEV qualification. It is not sufficient for real-bundle applicability, screening validation or production integration. Residual uncertainty includes finite-sample estimator error, Monte Carlo precision, adaptive method-selection effects, runtime behavior and the unresolved B mapping diagnosis; dependence, nonstationarity, distributional misspecification and observational error are outside this study. None is removed by a computational pass.

## Review verification

Applied claim-evaluation and testing-policy; consulted time-series and determined its temporal methods are inapplicable to the IID qualification. Verification was a scientific structural/traceability review for an owner decision, with numerical claims in scope. Read the design/intake, retained criteria, predecessor handoffs, selected accepted-design/source sections, installed xclim source and dependency entries; compared formulas and official primary sources. No package installation/import, estimator fit, benchmark, simulation, production edit, threshold change or test suite was run. Only this review file was authored.
