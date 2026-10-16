# Focused independent review — v2 unresolved decisions

Owner requests one more independent review after the recommendation for a bounded follow-up.
This supplement overrides the task scope, inputs and output slots of review-brief.md; its read-only
authority, scientific evidence burden and severity/verdict consistency remain binding.
This is decision adjudication on unchanged v2, not verification of a nonexistent v3.

Review design-v2.md (SHA256 C3EB945A1B2842D4326D36C833C77586F1A1BAD5DE2828D076651140449C477B)
in C:/Users/taner/workspace/blueearth_cst/dev/tasks/t2610161523/design-runs/named-indicator-sets/.
Form your own assessment first, then read external-review-r1.md, internal-review-index.md and ledger.md
there. Assess existing findings critically; do not simply endorse them or broaden to a fresh audit.

Settled framing (same as prior dispatch):
- Operations are a list of simulations and/or indicators; indicators-only never launches Wflow.
- Named YAML sets select reusable registered Python methods; separate readable results per set.
- User-facing definitions/configuration stay in YAML; hashes and machine JSON stay under _engine.
- Preserve existing arithmetic; expose temporal/missingness semantics and a readable dictionary.
- Require proportionate pre-change parity evidence; reject ambiguous nulls in new configuration.
- Use example_subset until a second scientific set is commissioned; unit interpretation remains open.
- Owner requested application of the domain findings as v2 before remaining independent reviews.

Resolve these two questions with a concrete minimal recommendation, alternatives/tradeoffs and exact
proposed contract wording (proposals only; do not edit the design):
1. ext1-1/domain-2: What units and coverage disclosure truthfully describe annual-sum reductions while
   preserving arithmetic? Distinguish block-depth estimand from normalized annual depth/rate. Check the
   assumptions behind N/(N+1), avoid presenting conditional algebra as measured bias. Reconcile the
   recorded 2026-08-08 ruling explicitly. Is a new coverage CSV necessary or is a smaller disclosure
   sufficient? Specify the minimum fields/evidence, with a hand-checkable example and applicability limits.
2. ext1-2: Retain authored calculation entries or defer them? Consider the user's intended reusable
   indicator template. If retained, specify authored-ID numerical identity, alias handling, equality
   across sets, metadata edits and truthful method semantics. Do not assume a descriptive title can
   prove scientific meaning. Explain the smallest coherent alternative and its cost.

Check ext1-3 through ext1-6 only as consequences of these resolutions. Existing import-closure hashing
may already cover a newly imported resolver; don't assert stale reuse without tracing that boundary.
Do not start a broad review or propose new formulas, plugins, run-control machinery or a new test suite.

Tools: Read/Glob/Grep only. No code execution, writes, data access, credentials or delegation.
You may narrowly inspect cited WF4 source. No empirical execution evidence is available in this review.

Return only Markdown:
## Verdict
verdict: approve | revise | reject
doc_version: design-v2.md
scope: annual coverage and authored-ID decisions only
## Finding dispositions
Address ext1-1 through ext1-6 as confirmed, qualified or unsupported, preserving original severities
when referring to them. Give evidence and distinguish concerns that must change v2 from future checks.
## Proposed resolutions
Two concrete recommendations, alternatives and insertion-ready proposed wording with affected headings.
## Remaining findings
Use ext2-N [blocking | major | minor] only for residual material issues in this focused scope; each needs
section, finding, rationale and suggested_fix. Do not duplicate an original ID under a new ID.
## Acceptance and limits
Minimal checks that could falsify each recommendation, what is statically established versus untested,
and whether another reviewer call is necessary after a faithful revision. Approval cannot coexist with
an unresolved major/blocking issue; a proposal is not an implemented or approved design revision.
