---
verdict: approve
doc_version: design-v1.md
findings:
  - id: domain-1
    severity: minor
    section: D2, Moments and final paragraph
    finding: >-
      Framing-level wording clarification: explicitly attach unbiasedness to raw-sample
      or back-mapped linear L-moments in exact arithmetic, not moments of the randomly
      range-normalized distribution. The frozen candidate D2 makes this distinction;
      this draft shortens it to an unspecified reference to assumptions.
    rationale: >-
      Proposed reporting ambiguity, not a demonstrated numerical regression. The
      normalization endpoints depend on the same sample. Readers could otherwise
      interpret the normalized diagnostic moments as unbiased population moments, or
      transfer the property to fitted parameters. The draft correctly denies the
      latter transfer but leaves the former implicit.
    suggested_fix: >-
      Restore the frozen D2 qualification in one sentence: the unbiasedness claim
      concerns raw-sample/back-mapped linear moments under the sampling assumptions
      in exact arithmetic; random normalization and float64 recovery do not create
      a new unbiasedness or exactness guarantee. Settling observation is that this
      qualification appears beside the moment formula; no new fit is required.
  - id: domain-2
    severity: minor
    section: Evidence E7; D7-D8; Validation plan
    finding: >-
      Implementation-detail prerequisite: E7 production/environment parity is
      untestable in the current review state because no production adapter or
      qualified production environment exists. Available accepted controls establish
      the reference, not the proposed mapping's successful execution.
    rationale: >-
      Pre-existing evidence absence, explicitly acknowledged and already gated by
      this design; not a proposed regression or a reason to reject provisional
      framing. Treating design approval as an observed E7 pass would permit a
      numerically different adapter/environment to inherit C's benchmark verdict.
    suggested_fix: >-
      Carry E7 as outstanding into the implementation handoff and acceptance record.
      Settle it with the specified source-verified production-versus-frozen-control
      parity evidence on each supported platform, unchanged frozen tolerances,
      exact refusal/acceptance checks, and a wrong-result mutant that fails. No new
      scientific study or pre-G1 execution is requested; the existing gate suffices.
---

Approve the scientific framing of design-v1.md for the owner's G1 choice, with
two minor findings and no blocking or major finding. This is a design-review
verdict, not production acceptance or a fit-for-purpose verdict for discharge
threshold decisions. Reviewed SHA-256:
`d8fb9320061d42081093266dbb14004b198b0868c41bae991f26d7ebd6f090ba`.

The claim under review is that fixed candidate C can be mapped into WF4 while
preserving extraction, screening, refusal semantics and immutable bounded evidence
for provisional operational point estimates. It is not that C is superior on
fresh data or adequate for an actual basin. The proposed design maintains this
distinction. Alternative A is supportable within that limitation; B preserves
continuity but cannot inherit C's evidence and still needs truthful metadata;
C is the appropriate broader prerequisite when the intended use requires
decision-relevant accuracy or estimator uncertainty. Neither A nor B supplies
that adequacy by default. Owner choice remains pending.

| Premise | Disposition | Basis and settling observation |
|---|---|---|
| E1 | supported | The retained 8x signed verdict, summary and criteria agree on C 144/144, 24/24 baseline and 72/72 eligible cells; original 15/144 and 3x 124/144 remain failed. The handoff reports 120,000 accepted translation pairs. These are recorded development rescore outcomes, not independently rerun results in this review. |
| E2 | supported | Current `metric_registry.py::reduce_bundle` imports xclim fit/parametric_quantile, fits genextreme and broadly wraps exceptions. It differs from the retained `candidate_adapter.py`. |
| E3 | supported | Current `metric_plan.py::metric_request` requires exact equality with the minimal provisional/unassessed object; recorded `inspection.json` confirms rejection of the reviewed annotation. Current publication has no candidate report contract. This is pre-existing. |
| E4 | supported | Recorded inspection has null lmoments3 metadata and null Pixi-on-PATH; retained effective environment records isolated lmoments3 1.0.8 and the D7 Python/NumPy/SciPy versions and source hashes. This supports availability at assessment only; current setup must be rechecked as D7 requires. |
| E5 | supported | Current inventory traverses static imports; the request contains the code inventory, stage environment and validation declaration. New report/source/dependency mutations remain proposed falsifiers, not measured identity coverage. |
| E6 | supported | Accepted R12 sections 7.5-7.6 require operational-screen-only use and explicit unvalidated near-zero error/unestablished actual-bundle applicability, and retain point estimates without Class-B fit intervals. The applicability assessment preserves that boundary. |
| E7 | untestable as stated | The independent readiness verdict accepts attempt-2 and binds its adapter, controls and environment. Production preservation cannot yet be observed. See domain-2; the settling observation is production parity and discriminating mutant evidence on each supported platform. |

Evidence abbreviations above resolve through the design/intake register under
`dev/milestones/r12/implementation/evidence/`. The accepted candidate design,
R12 sections 7.5-7.6/8.4, readiness adapter, independent verdict and effective
environment were inspected against the proposed contract and current reducer /
planner / import-inventory seams.

The numerical mapping preserves SciPy's shape convention c=-xi, the strict
finite-mean domain c>-1, range normalization, named parameter mapping, and the
zero-shape quantile limit. Member-local annual blocks and seven-observation
rolling minima, finite-block selection and numeric member order match the
current extraction. The existing floor and ratio remain a heuristic count gate;
pooled block count is not an effective independent sample size. Separate scalar
peak/low calls correctly avoid importing the study's joint-baseline acceptance
into two physically different production samples. Low p=.5 remains the median
of annual rolling minima; the design does not introduce a sign reversal or a
physical positivity claim.

D3's exact type/message/raising-frame/code-object/line/source-hash guard matches
the retained candidate's two allowed inversion exceptions. Source mismatch and
foreign exceptions remain faults. Preserving strict support comparisons and
separate normalized/physical nonfinite-density counts avoids converting an
L-moment estimator into an unreviewed likelihood-screened estimator. Endpoint
rounding is diagnostic; the independent physical CDF/quantile controls remain
readiness controls. Finite negative estimates are not censored into apparently
plausible discharge. Computational acceptance therefore cannot imply physical
or distributional suitability, which the proposed limitations correctly state.

The validation plan contains actual falsifiers for wrong sign, missing affine
mapping, invalid shape acceptance, cross-member rolling, foreign exceptions,
support-veto drift and quantile perturbation. Its explicit warning that 1e-6
translation tolerance is not general parity tolerance is necessary. Frozen
population-gate precedence, branch characterization and independent quantile
enclosures must survive implementation unchanged. D8's old/new comparison is a
migration check: expected return-level changes are an estimator change, while
changed extraction, non-return-level rows or upstream bytes are regressions.

D4-D6 bind the estimator, relaxed policy, report bytes and limitations into the
new immutable metric identity, while preserving legacy interpretation. A report
digest is evidence identity, not evidence of statistical adequacy. Reading a
retained report without the currently installed package preserves historical
meaning; it must not relabel predecessor results as C. The report's embedded
scientific handoff carries adaptive-selection and Monte Carlo limitations, and
its exact source-text/hash scheme makes the abbreviated public status auditable.
The design explicitly separates this report from a full rerun archive.

The numerical error limits remain permissive: eligible relative signed-median
magnitude up to 80%, upper absolute-error P90 up to 400%, and lower P90 up to
200%. The retained handoff illustrates c=-.2, n=10, p=.9, rho=.5 with relative
signed-median magnitude 0.7096987457437947 and P90 3.8309444134013266; the
diagnostic near-zero case c=-.2, n=10, p=.5, rho=.05 has P90
14.856985611770813. These retained errors are not confidence intervals around a
production estimate. There are 1,000 draws per shape/count base cell and twelve
base cells; probabilities, estimators and translations reuse those draws, so
144 cells or 120,000 pairs are not that many independent replications.

No holdout, new naive benchmark, interval coverage, or actual-bundle regime
assessment is available. Generating truth and paired A/B comparators support
the declared development comparison only. Finite Monte Carlo uncertainty,
post-results policy selection, parameter uncertainty, dependence and
nonstationarity, distribution mismatch, observational error, forcing and model
uncertainty remain unresolved. The report must not collapse them into its
passing flag. Replaying retained controls can settle implementation parity;
it cannot resolve these scientific limitations or guarantee their elimination
by further work.

Verification scope: documentary decision review with numerical claims affected,
using claim-evaluation and testing-policy. Checked the named design's SHA-256
and inspected retained source/contracts/evidence. No new fits, source downloads,
workflow runs, scientific tests, dependency installs, code edits or Git actions
were performed. Only this assigned review file was written. Full production
acceptance and platform checks remain unexecuted as the design states.
