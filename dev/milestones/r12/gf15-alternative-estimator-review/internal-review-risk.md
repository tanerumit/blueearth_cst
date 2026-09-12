---
verdict: approve
doc_version: design-v1.md
findings:
  - id: risk-1
    severity: minor
    section: "Validation regime / artifacts and paired A/B/candidate error summaries"
    finding: >-
      The planned paired estimator comparisons do not explicitly define their
      acceptance cohort, although the estimators can refuse different draws.
    rationale: >-
      Each estimator's GF15 error summaries correctly condition on its own
      accepted fits. Comparing those summaries alone can attribute an apparent
      accuracy improvement to the estimator when it partly reflects a different
      retained subset. The required raw rows and refusal denominators permit
      this distinction, so the omission limits comparative interpretation
      rather than invalidating the fixed candidate qualification.
    suggested_fix: >-
      Specify paired accuracy comparisons on the explicitly identified
      intersection of accepted draw/probability keys, with that denominator and
      the acceptance-disagreement counts. Keep each estimator's original
      conditional GF15 summaries and full-draw valid rates alongside them;
      neither common-cohort comparisons nor changed cohorts may replace a gate.
---

The claim under examination is that one fully specified alternative can undergo
a meaningful, bounded qualification against the retained GF15 matrix. It is not
a claim that the estimator will pass or that a pass establishes operational
suitability. G1's estimator selection, finite-mean domain and diagnostic-only
support policy are settled.

The design supports that limited claim. It separates the fit adapter from truth,
keeps all original draws, freezes numerical choices, exposes refusals, requires
independent analytical checks, and prohibits using a failed cell to retune the
study. The complete-matrix reporting rule prevents statistical early stopping;
input or control failures instead stop an invalid execution. Reuse of the
development matrix is disclosed, with replication and real-bundle applicability
left unresolved. These are adequate safeguards for the proposed qualification,
without supporting stronger claims.

No blocking or major vulnerability was identified. The one minor finding above
addresses a plausible alternative explanation for comparative improvements:
acceptance selection rather than reduced error on the same observations. It does
not change the authoritative criteria or require a new estimator study.

Review evidence: design-v1.md, the G1 decision in status.md, the directly cited
original criteria.json, and read-only inspection of the directly cited official
[GEV implementation](https://lmoments3.readthedocs.io/stable/_modules/lmoments3/distr.html)
and [sample-moment source](https://lmoments3.readthedocs.io/stable/_modules/lmoments3.html).
The disclosed branch choices agree with the inspected source; runtime behavior
remains untested. No fits, installations, benchmark execution or code changes
were performed.

Scope disclosure: the initial status.md read also exposed its non-G1 driver
summaries. No prior review artifact or ledger was opened; those summaries are
not evidence for this finding. This review therefore does not claim complete
blinding to prior-review metadata.
