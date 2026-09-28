# GF15 production adapter — intake

Date: 2026-09-13
Genre: decision-record (milestone software/method integration design)
Domain-scientific content: yes — estimator mapping, refusal policy and bounded validation claims.

## Request and authorization

Owner request, verbatim: "continue to next step and onwards. Do not pause until the next gate or a user-side decision point".
Preceding step: production applicability assessment committed as `d761a65b`.
Proceed through drafting and pre-G1 scientific review, then present the concrete
G1 framing decision. No production implementation occurs in this design run.
Earlier "8x" approves policy `gf15-accuracy-8x-v1`; it does not approve an unseen
production adapter or waive G1/G2. Existing reviewed candidate method stays fixed.

## Problem and scope

Production still fits xclim/SciPy GEV, while the range-normalized L-moment
candidate C passes the owner-selected eightfold policy on retained synthetic
data. The planner rejects reviewed benchmark annotations and does not package
the report required by accepted R12 section 7.5. Design the production adapter,
dependency/environment handling, full validation declaration and immutable
report/metric-identity integration together. This is provisional operational
point estimation, not a claim of real-bundle adequacy.

Authoritative inputs, paths relative to repository root:

- `dev/milestones/r12/gf15-alternative-estimator-design.md`: frozen method D1–D6, parameters/defaults; requires separately reviewed production adapter.
- `dev/milestones/r12/wf3-simulation-identity-design.md`: accepted sections 7.5–7.6 and 8.4; preserve existing R12 interfaces except explicitly designed integration delta.
- `dev/milestones/r12/implementation/evidence/gf15-lmoments-readiness/`: accepted attempt-2, frozen adapter/reference controls and environment.
- `dev/milestones/r12/implementation/evidence/gf15-accuracy-8x/`: exact criteria and signed bounded pass; original and 3x failures remain intact.
- `dev/milestones/r12/implementation/evidence/gf15-production-applicability/`: scientific assessment and measured integration readiness at `d761a65b`.
- `blueearth_cst/experiment/{metric_registry,metric_plan,content_identity,export_wflow_results}.py` and their existing tests: current seams and compatibility behavior.

## Constraints, decision criteria and success

Preserve member-local annual maxima/seven-observation rolling minima, calendars,
partial years, units, pooling order, p=.9/.5 and operational screen ratio1/floor10.
Preserve candidate finite-mean domain, source-qualified library exception
allowlist, unexpected-fault propagation and diagnostic-only support behavior.
No silent alternate estimator, fallback, retry, shape bound or sample censoring.
Use shipped code and report assets; no runtime import from `dev/` or scratch.
Pin the selected lmoments3 implementation and record resolved numerical
environment. Do not mutate shared Pixi environment or hand-edit locks.

The design must specify concrete adapter/error/diagnostic contracts; report asset
content and portability; complete validation metadata; digest/identity rules;
old-ready-set reader compatibility; environment setup and parity checks; affected
files, migration sequence, independent falsifiers and executable gates. New
estimator/evidence creates a new metric set, reusing retained upstream identities.
Ready sets and all prior scientific evidence stay immutable.

Prefer the smallest explicit production mapping of C with complete provisional
metadata. Compare seriously against keeping the predecessor and requiring
real-bundle validation before all use. Decision criteria: method fidelity,
truthful claims, reproducibility, portable evidence, existing-set compatibility,
bounded implementation cost and automation scope.

Do not conceal permissive thresholds: absolute signed median .80, absolute P90
upper4/lower2 in scale/relative units; relative limits80%/400%/200%. No fresh-data,
policy-validity, actual-bundle adequacy or estimator-improvement claim follows.

Non-goals: new estimator research, holdout/bootstrap/intervals, screening changes,
real-basin validation, Wflow/generation reruns, successor baseline execution,
milestone sealing, pushes/merges or edits to frozen designs/evidence.

## Evidence register

| ID / Premise | Source | Exact observation | Precision | Reproduction | Confidence |
|---|---|---|---|---|---|
| E1 C passes only the named revised policy | `gf15-accuracy-8x/results/signed-verdict.json`, summary and criteria | C144/144 overall,24/24 baseline,72/72 eligible;120000 translation pairs pass. Original C15/144 and3x124/144. | Exact retained counts; no MC interval | Existing signed rescore into fresh scratch output, no fits | Measured development result; no population/real-bundle extrapolation |
| E2 Current reducer differs from C | `metric_registry.py::reduce_bundle` | xclim fit/parametric_quantile; broad exception wrapping | Source-level exact call path | Read function and existing test injection | Measured code fact |
| E3 Current metadata cannot carry accepted report | production-applicability `inspection.json`, metric_plan.py | Current minimal object accepted; reviewed annotation rejected with explicit ValueError; no report payload writer | Exact runtime JSON replay and source inspection | Recorded `inspect-integration.py` command | Measured pre-existing gap |
| E4 Candidate dependency/tooling absent | production-applicability `inspection.json`; pixi.toml/lock | lmoments3 metadata null in shared env; pixi absent from PATH; isolated study uses1.0.8 | Observed environment availability, not impossibility of setup | metadata.version / shutil.which and lock search | Measured at assessment; recheck before setup |
| E5 Imported code and validation participate in metric identity | content_identity.py and metric_plan.py | Static repository import closure; validation copied into definition/manifest | Source mechanism, future new-adapter behavior untested | Existing identity tests plus new isolated code/report/environment mutations | Existing mechanism supported; new integration hypothesis |
| E6 Provisional use does not imply real-bundle adequacy | accepted R12 sections7.5–7.6; scientific-assessment.md | operational_screen_only and provisional screening required; actual-bundle applicability unestablished | Contractual scope, no empirical adequacy | Read exact accepted clauses | Supported scope; adequacy remains unknown |
| E7 Production adapter/environment preserves C numerics | Stage1 independent reference controls available; no production adapter exists | Not yet measured | Hypothesis | Independent reference/parity checks in proposed locked environment with deliberate wrong-result mutant | Must be tested before implementation acceptance |

Evidence paths abbreviated above resolve under
`dev/milestones/r12/implementation/evidence/` unless a source filename is named.

## Gate materialization

| Gate | Present readiness and required action |
|---|---|
| G1 framing | Runnable after v1 and mandatory domain review; owner decides concrete alternative and framing findings. |
| Existing metric tests | `.pixi/envs/default/python.exe -B -m pytest --collect-only -q tests/test_metric_registry.py tests/test_metric_plan.py tests/test_content_identity.py` exited0:71 tests collected in37.69s on2026-09-13. Log in session scratch `gf15-production-adapter/test-collection.log`. Collection proves import/collection readiness only; tests were not executed. |
| Candidate parity | Stage1 retained independent controls and isolated interpreter exist. Production-environment parity is unexecuted; design must name its falsifiers and setup prerequisite. |
| Dependency solve | Pixi absent from PATH. Resolve executable and isolated win/linux lock setup during implementation preparation; do not promise a current solve pass. |
| Pre-change comparison | Original scientific records and current source preserved. Before first implementation commit, capture the selected retained metric responses/results/config and identities for a bounded metrics-only old/new comparison. The successor baseline is not a substitute. |
| External review | `codex` absent from current PATH; `claude.exe` present. External transport/auth/isolation unresolved and must be checked before that later dispatch. G1 occurs first; no fallback approval is inferred. |
| G2 acceptance | Requires converged named-version external verdict, complete ledger and user approval; unavailable before review. |
| Baseline/seal | Separate standing fixture requirements remain unresolved. Excluded from this design execution; plan must preserve ordering. |

## Derived-artifact register

| Artifact | Action after G2 |
|---|---|
| R12 task note / master brief / validation map | Update from accepted design and exact gate status; never label a proposal implemented. |
| Production implementation brief | Create from accepted decisions with scoped files, claim-to-falsifier table and pre-change snapshot requirement. |
| User-facing metric documentation | Update in implementation when actual behavior changes. |
| Existing frozen candidate/8x/applicability evidence | Preserve verbatim; new design cites rather than edits. |

Author owns only versioned design and later ledger dispositions; derived artifacts
are driver-owned and outside author scope. Target final design home is the R12
milestone, with verbatim review archive. Until G2 use this run's working directory.
