# Roles and recovery

Load at run start to bind responsibilities and again when a stage fails.
`agent-routing` allocates live registered roles, context, model, and effort;
`workflow-driver` executes dispatches. These bindings add no delegation
authority. A generic surface may implement a selected role only with its full
contract and host authorization. Preserve explicit pins and scientific review.

## Role bindings

| Responsibility | Contract |
|---|---|
| Driver | Gates, status, triage, checks; scoped deterministic repairs only |
| Author | Project design role loading `design-document`; drafts and related revisions; may be continued |
| Domain reviewer | Independent domain role with `claim-evaluation` before G1 |
| Risk reviewer | Independent `critical-thinker` or suitable live role; tests assumptions and alternatives |
| External reviewer | Different model family by default, via `workflow-driver` |
| Focused reviewer | Named consequential question outside current competence; within budget |

Every reviewer must be independent of the author in role and judgment.
The external review additionally defaults to a different model family;
calling the same GPT family through another runtime does not meet that
diversity requirement. If unavailable, report it and ask the owner whether
to authorize a same-family fallback. Label that review `single-family`;
it remains an independent reviewer but is not cross-family or cross-vendor.
A focused reviewer is not an automatic architecture or repo-fit panel.

The domain reviewer tests method fit, governing assumptions, uncertainty,
data treatment, and falsifiability; it dispositions evidence-register rows.
Wrong or unjustified method can be `blocking`. Its framing findings reach G1
before the owner approves a provisional choice.

## Recovery within the shared allowance

Classify failure before retry. Every agent attempt or continuation counts
against the six/seven-call total; the single shared recovery call may retry
only the same incomplete or invalid stage. It cannot fund a second design
revision, whole-document review, panel, or new question. The host's stricter
no-progress limit still applies.

| Failure | Action |
|---|---|
| Transient transport or partial | Inspect; continue or retry same stage within budget |
| Quota or spend exhaustion | Preserve partial and wait for a changed external condition or owner action |
| Silent stall | Change diagnosed input, environment, or binding before one bounded retry; record cause |
| Invalid review schema | Preserve raw output; one bounded schema retry, then invalid |
| Failed targeted verification | Present issue and choices to owner; no automatic extra revision/review |
| Material framing change | Return to G1 before another review or revision |
| Rejected blocking or disputed scientific issue | Verify premise against repo, then ask owner to arbitrate |

For a partial author artifact, inventory completed sections and brief the
continuing worker to finish only missing scope. On resume, recheck checkout,
branch, identifiers, role availability, status, and exact on-disk evidence.
For stage-7 editorial candidates, preserve failed bytes and use the next
suffix under `stage-contracts.md`; do not overwrite.

At budget exhaustion, give the owner the surviving question, raw findings,
author rationale, verified factual premise, and whether it is pre-existing or
introduced by the design. Present continuation with explicit question, scope,
and limit; narrowing; eligible risk acceptance; or stopping. Do not treat a
budget as a reason to waive scientific validity or exact G2 approval.
