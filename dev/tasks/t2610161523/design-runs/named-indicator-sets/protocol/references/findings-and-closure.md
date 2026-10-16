# Findings and closure

Load when triaging reviews, writing ledger rows, or approaching a gate. Raw
review files are immutable. `run-artifacts.md` defines their schema and the
append-only ledger; `stage-contracts.md` defines stage order.

## Severity and admissibility

Reviewers use `blocking` when the design would fail, produce wrong results,
or cannot be implemented; `major` for material degradation, cost, or risk;
`minor` for a nonessential improvement. A verdict of `approve` cannot coexist
with a `blocking` or `major` finding in that same raw review. Reject an
invalid verdict once for schema correction within budget; retain both raw
attempts.

Before author revision, the driver records a separate, evidence-backed triage
for every original finding ID:

| Class | Decision test | Next step |
|---|---|---|
| Design issue | Consequential design choice that cannot safely wait | Resolve in design or ask owner |
| Implementation obligation | Real consequence; mechanism can wait | Add acceptance check to handoff |
| Duplicate | Same underlying issue as another ID | Link IDs; keep both original rows |
| Preference | No consequential change demonstrated | Record rationale; do not block design |
| Unsupported | Premise lacks support | Record evidence gap; escalate if consequential |

Triage does not rewrite raw severity. A contested consequential or scientific
finding goes to the owner rather than being silently downgraded. Verify each
surviving factual premise against the target repo and note whether it is
pre-existing or introduced by the design. A `suggested_fix` is a proposal:
record which underlying requirement is satisfied, why, and by which design
decision or implementation check. Do not force every proposed substep into
the document.

## Ledger and decision closure

Give every original finding ID one append-only disposition row, including
duplicates and minor items. `accepted` names the resolution and its version
or implementation acceptance check; `rejected` gives counterevidence and
reason; `withdrawn` requires the issuing reviewer or owner; `deferred` is
available only for minor items and names its tracking destination.
Arbitrate rejected `blocking` findings immediately. Present rejected `major`
findings for owner ratification at or before G2. A status or ledger label
cannot itself authorize edits.

The candidate is ready for G2 when each admitted design issue is resolved in
that exact version or ruled on by the owner, implementation obligations have
acceptance checks, and all original IDs are dispositioned. Record explicit
empty closure if reviews have no findings; an absent ledger alone is not
evidence. If a changed version lacks a whole-document verdict, record the
narrow deterministic or reviewer verification of its changed decision IDs,
or an owner ruling plus deterministic scope/whole-diff checks and targeted
judgment where a new consequential mechanism requires it. Never treat budget exhaustion as an
implicit approval or scientific waiver.

## Structural checks

- Check the applicable `design-document` content contract, including credible
  alternatives and their consequences; heading presence alone is insufficient.
- At G1, check the journey, smallest useful alternative, material tradeoffs,
  domain findings, and recoverable sketch bytes where a sketch was shown.
- Check every raw finding ID against ledger and triage; preserve conflicting
  readings and reviewer severities in immutable files.
- If stage 1b raises a scientific finding and later risk/external reviews are
  empty, keep the domain ID open until resolved or owner-ruled; empty later
  reviews never erase it.
- Check budget accounting across calls, retries, continuations, and agent
  probes. The recovery allowance is for an incomplete or invalid stage only.
- Check that each verdict names an existing `doc_version` and is inside
  `approve | revise | reject`; `IN_PROGRESS` is unfinished, not a verdict.
- At G2, check exact reviewed path/SHA256, owner/date, eligible risk rulings,
  and approved anchored editorial spans. Material changes return to review.
- At stage 7 and task closure, check authoritative pointer, whole-diff
  verification, retained exact bytes, and the claim-to-falsifier handoff per
  `run-artifacts.md` and `evidence-and-gates.md`.

At the budget limit, present concrete choices to continue with an explicitly
bounded scope, narrow the design, accept an eligible risk, or stop. State
which scientific or consequential questions cannot be accepted as risk.
