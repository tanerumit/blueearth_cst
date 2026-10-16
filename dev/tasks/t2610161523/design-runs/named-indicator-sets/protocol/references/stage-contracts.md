# Stage contracts

Load before executing a stage. Stage IDs remain stable for run records; their
execution order and optionality follow the decision cycle below. The driver
owns gates and status, the author owns design content, and reviewers are
independent and read-only. `workflow-driver` owns dispatch mechanics.

## Worker inputs and recovery

Give the author `intake.md`, the current design if any, original reviews being
answered, the ledger, exact gate rulings from `status.md`, and read access to
relevant repo paths. Give reviewers the candidate design, review contract,
settled framing, and lens-specific evidence. Keep packets sufficient and
bounded; a continuation may reuse the author for related work. Ask authors to
write a section skeleton or copy the current version before substantial edits
so partial work survives transport failure. Review placeholders use
`verdict: IN_PROGRESS`, never a valid empty verdict. A retry or continuation
counts against the run's total worker-call budget.

The driver may make deterministic format/schema repairs or owner-approved
editorial-span corrections when the exact scope is recorded and whole-diff
verification is available. It may not decide design content. Preserve failed
candidates and immutable raw reviews.

## Stage table

- **0 — Intake:** driver records `intake.md`, status, evidence and
  derived-artifact registers, domain flag, and budget. Use `design-exploration`
  dialogue only where intent remains open.
- **1 — Draft:** author produces self-contained `design-v1.md` with journey
  and alternatives, or seeds it from an existing design.
- **1b — Domain review:** independent domain reviewer produces immutable
  `internal-review-domain.md` before G1 when scientific content exists;
  otherwise record a waiver.
- **G1 — Framing:** user resolves outcome, problem, criteria, provisional
  alternative, tradeoffs, and material domain findings.
- **2 — Risk review:** independent reviewer produces immutable
  `internal-review-risk.md`; driver indexes conflicts with domain findings.
- **4 — External review:** independent reviewer evaluates the same initial
  candidate as stage 2 in immutable `external-review-r1.md`.
- **5 — Triage:** driver records finding admissibility, exact candidate
  identity, and empty closure or bounded revision scope.
- **3 — Consolidated revision:** author makes a new `design-vN.md` only when
  admitted issues require it; ledger dispositions cover every original ID.
- **6 — Targeted verification:** check changed decision IDs mechanically or
  with one bounded reviewer/probe where judgment remains unresolved.
- **6a — Arbitration revision:** when a ruling requires it, author makes a
  confined candidate with ruling-linked ledger entries and scope check.
- **G2 — Approval:** user approves exact path, SHA256, date, and any precise
  editorial spans.
- **7 — Finalize:** driver verifies final pointer and task link, then retains
  claim falsifiers and implementation obligations in the existing handoff record;
  author helps only with approved editorial spans.

If G1 redirects the selected alternative or domain framing, update the
candidate under the owner's ruling and show the remaining call/probe budget
before initial review. Stages 2 and 4 must review that same current version;
do not send stale v1 with contradictory status rulings. The G1 redirect
authorizes this bounded candidate refresh. Count its worker call toward the
total and show remaining capacity; the one consolidated post-review revision
remains available within that total.

Stages 2 and 4 may dispatch in parallel only when the runtime and ownership
permit it. Stage 3 follows their indexed findings and triage. The initial
review can approve v1 unchanged; no revision floor exists. The shared
recovery allowance retries an incomplete or invalid stage only. It cannot fund
an additional design revision, extra whole-document review, or panel through a
renamed stage. An additional full external review needs an explicit owner
continuation with a concrete unresolved question, scope, and limit.

## Gate 1 and gate return

Lead G1 with the user outcome, ordinary end-to-end journey, smallest useful
change, selected approach, meaningful alternatives, tradeoffs, complexity,
migration, and choices requiring the owner. Present scientific framing findings
before a provisional alternative is locked. Include file/output tree and
user-facing change inventory where they affect that decision; see
`journey-and-sketch.md`. Ask only questions that remain unresolved after
checking prior user intent.

If a review finding or suggested fix admits materially different problem,
scope, constraints, or selected alternatives, return to G1 before revision.
Show each candidate resolution and its consequence. Record the ruling in
`status.md` and pass it as settled input to the author. Reviewers cannot
silently replace the owner's framing.

## Stage 5 and G2

Preserve each raw review's severity and suggested fix. Triage separately
through `findings-and-closure.md`; verify factual premises against the repo,
distinguishing pre-existing conditions from design regressions. A review may
approve with no findings. If every admitted issue is resolved in the named
candidate and the ledger closes, send that exact candidate to G2. If a
material revision occurs, check its changed decisions deterministically where
possible and with at most one targeted judgment pass within budget. A
reviewer verdict on v1 is not a verdict on changed v2; record the narrow
verification or owner arbitration that covers the delta.

An owner-directed arbitration revision still needs a deterministic scope and
whole-diff check, plus targeted judgment on any new consequential mechanism
within authority and budget. The owner's ruling does not prove the fix works.

G2 records path, SHA256, approval date and owner identity in `status.md`.
Present remaining obligations and eligible risk decisions. A decision,
interface, stage, contract, or framing change returns to review or G1. For
editorial changes, record exact before/after spans with unique anchors,
including header transitions. Approval of a ledger rationale alone does not
authorize a content delta.

## Stage 7 — finalize review

With no approved delta, keep the reviewed base as final pointer, byte for
byte. For approved editorial spans, the driver may apply them directly when
deterministic whole-diff verification suffices; otherwise use the author only
within remaining budget and authority. Write a new monotonically suffixed
`design-vN-editorial-<k>.md` candidate. Record pending, verified, or failed in
status; retain invalid candidates as immutable failed evidence and use the
next suffix on retry. Failure leaves the approved base authoritative.

Verify the entire candidate diff against the owner's exact spans. Record base
and successor identities before repairing the task link. On resume, reuse a
valid candidate and finish missing records without another author call.
Reconcile twice to the same status pointer; status overrides a stale task
link. Mark review done only when final identity, verification, and task link
agree. Review completion does not establish implementation completion or grant
implementation authority. Carry each runtime claim's falsifier and producing
command forward under `evidence-and-gates.md`; use `task-brief` only for a requested
or workflow-required assignment. Task closure uses `run-artifacts.md` retention rules.

## Seeding from an existing doc

Check genre structure and intake-scope completeness separately. A complete,
well-structured seed is copied mechanically to `design-v1.md` with its source
recorded and no author call. A complete but unstructured seed gets a bounded
genre reshape. An incomplete seed requires the author to preserve every
previously ruled decision in substance while filling declared scope gaps.
Record `seeded-from-existing-draft` in status.

## Derived-artifact register

At stage 0, list each downstream task brief, map, roadmap line, or spec that
would go stale after design revision and how to regenerate it after G2. Author
workers do not edit those artifacts while the design is under review.
