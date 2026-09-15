---
verdict: approve
doc_version: design-v1.md
findings:
  - id: risk-1
    severity: minor
    section: "D3; D8 handoff 3/4; Validation plan / Metrics-only"
    finding: "The migration comparison does not specify how to report incomplete coverage after the first refusal or fault."
    rationale: "D3 preserves abort-on-failure publication, while the metrics-only acceptance row asks for comparison by key and documentation of every change/refusal. The existing reduction loop propagates the first reduce_bundle exception, so a failed attempt cannot produce a complete old/new comparison or enumerate later refusals. This is an ambiguity in the proposed acceptance handoff, not a new numerical or publication regression."
    suggested_fix: "State that an aborted comparison is incomplete and cannot pass migration acceptance; record the first failure and explicitly identify remaining keys as not evaluated. Any later diagnostic continuation must be a separately identified nonpublishing check and must not turn the failed production attempt into acceptance. No G1 framing change is needed."
---

The core claim is bounded: WF4 can map the frozen candidate C into provisional operational point estimation, retain its benchmark limitations, and preserve old-set readability and upstream artifacts. This review accepts the G1 Option A decision of 2026-09-13. It does not reopen the 8x policy or require actual-bundle validation as a new prerequisite.

The design earns review approval within that scope. It separates retained development rescores from independent production parity, carries original and 3x failures, and expressly prohibits inferring real-bundle adequacy from fitted parameters or sample count. The portable report supplies inspectable evidence rather than claiming a raw-data reproduction archive. None of these provisions establishes improved real-system accuracy, and the draft does not claim it.

The consequential assumptions are exposed and gated: the pinned source and numerical closure must be obtainable in an isolated environment; production mapping must pass independent frozen controls on supported platforms; a suitable pre-change experiment must exist; and copied evidence must remain readable without the current package asset or numerical dependency. If any fails, setup, migration, or acceptance stops. These remain unexecuted prerequisites, not evidence that the proposed mechanism already fails. The G1 actions concerning unbiasedness wording and outstanding parity remain applicable; they are not duplicated as new risk findings.

The single minor finding concerns the completeness of failure reporting. Direct inspection of the cited `metric_plan.py::reduce_metric_plan` shows sequential reduction with propagated bundle exceptions. Keeping that behavior avoids publishing incomplete results. The acceptance handoff should also prevent unvisited keys from being mistaken for compared keys. This clarification leaves the fixed estimator, refusal policy, and approved scope intact.

The dismissed alternatives remain coherent within G1: retaining predecessor numerics preserves continuity but cannot inherit C's evidence; requiring actual-bundle validation would answer a broader scientific question. Failure to demonstrate C parity would warrant returning the failed prerequisite to the owner, not silently choosing either alternative or relaxing pins. All-or-nothing publication may prevent a whole set from becoming ready when one fit refuses; that is an explicit retained policy consequence, not a hidden new regression.

Scope and verification: reviewed design-v1.md and the G1 record in status.md; narrowly inspected the directly cited metric-plan reduction loop and metric-registry fit/error locations. Used the claim-evaluation framework. No prior review or ledger was opened; no fits, tests, network calls, source/environment changes, or Git operations were performed. Traceability check: the one finding names its contract sections, mechanism, pre-existing/proposed distinction, and framing impact. Verdict: approve; 0 blocking, 0 major, 1 minor. Approval is of the design under these gates, not implementation or scientific acceptance.
