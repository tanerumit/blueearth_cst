# Run artifacts and schemas

File layout, ownership, and schemas for a design-review-loop run. Load at run
start and on resume. Stage semantics: `stage-contracts.md`.

## Run directory

`<target-repo>/<working-docs>/design-runs/<slug>/`; slug = 2–5 kebab-case words
naming the change.

**A documented repo grammar wins.** If the target repo documents its own folder
layout (e.g. a `dev/README.md` table naming which folder holds what), put the run
dir under the folder it names for ephemeral working material — do not create a
sibling. For a tracked `todo-board` task, use `dev/tasks/<id>/design-runs/<slug>/`.
Only where the repo has no board or documented convention does a generic
working-docs default apply.

| Artifact | Writer (single) | Notes |
|---|---|---|
| `status.md` | Driver | Sole review stage, gate and acceptance authority; resume source |
| `intake.md` | Driver | Request verbatim, framing, journey, evidence and artifact registers |
| `review-brief.md` | Driver | Fixed contract; created at first external dispatch |
| `design-vN.md` | Author | One file per version, never overwritten; append-only series |
| `internal-review-<lens>.md` | Lens reviewer/capture | Immutable verbatim verdict |
| `internal-review-index.md` | Driver | Groups by ID and preserves conflicts; no re-grading |
| `external-review-r<n>.md` | Independent review capture process | Immutable verbatim output |
| `ledger.md` | Author; driver when no author runs | Append-only; created when findings need dispositions |
| `observations.md` | Driver | Created on first process observation; append-only |
| `design-vN-editorial-<k>.md` | Author or scoped driver | Approved successor; immutable after check |
| `review-brief-r<N>.md` | Driver | Conditional immutable brief snapshot or labelled dispatch supplement |
| `scoping-g1-<k>.html` | Driver | Conditional pre-edit sketch snapshot |

Require intake/status/design; create reviews and index only when dispatched.
Record required/conditional inventory and stage/gate/acceptance identities in the existing
status body; add no required schema keys or tool. Record the six/seven-call limit,
completed calls, continuations, retries, and the bounded non-agent probe list in
that body. Count every attempted worker call. A historical run retains its own
recorded contract and fields; do not rewrite its provenance on resume.
Keep journey, registers and G1 displayed revision/digest with recoverable sketch bytes.
Use `external-review-brief.md` for component hashes, verbatim status framing and pre-edit recovery.
With no findings, record explicit empty findings/disposition closure in status, checked against every
completed review; ledger absence alone proves nothing. Any finding requires its ledger row.

One writer per artifact, per `workflow-driver`'s invariant.

## Index conflicts section (required)

Grouping duplicates is the index's obvious job; recording **disagreements** is
its valuable one. Two independent lenses reaching opposite conclusions marks the
place a design is under-determined, so the index carries a conflicts section
holding both original readings intact alongside separate driver triage:

- **Factual contradictions** — one lens raises a finding another lens checked and
  deliberately declined to raise. Record both, with the evidence each cited and,
  where one exists, the cheap empirical test that would settle it.
- **Severity divergences** — the same defect graded differently by two lenses.
  Each original ID is dispositioned at *its own* filed severity; the "never
  re-grade" rule already forbids harmonizing them, and the conflicts section is
  where that is made visible rather than silently preserved.

The driver preserves both readings in the raw index and separately records
evidence-backed admissibility triage. The author responds to admitted design
issues; consequential or scientific disputes go to the owner. A driver that
flattens the raw contradiction into one reading destroys useful evidence.

## Verdict schema

Every review — internal lens or external round — must reduce to:

```yaml
verdict: approve | revise | reject
doc_version: <design-vN.md reviewed>
findings:
  - id: <lens-or-round>-<seq>        # e.g. risk-3, ext1-1
    severity: blocking | major | minor
    section: <design-doc heading>
    finding: <one-paragraph claim>
    rationale: <why it matters>
    suggested_fix: <optional>
```

IDs are stable and never reused. Consistency rule and severity definitions:
`findings-and-closure.md`.

**Reviewer placeholders are schema-invalid on purpose.** A reviewer spawn told to
put its file on disk first writes `verdict: IN_PROGRESS` with an empty findings
list, and swaps in a real verdict only when its findings are complete. A
placeholder that used a *valid* verdict would be indistinguishable on disk from a
genuine "revise, no findings" review, so a driver reconciling on `status.md`
alone would mark the stage done and carry empty verdicts into the ledger. Treat
any verdict outside `approve | revise | reject` as unfinished. Retry only
within the shared same-stage recovery allowance; if unavailable, report the
blocker. An unfinished or invalid review blocks G2 even if other reviews
have empty findings.

## Ledger schema

Append-only, one row per **original finding ID**:

```
| ID | Review | Severity | Disposition | Resolution or rationale | Doc version |
```

Disposition and escalation: `findings-and-closure.md` § Ledger and decision closure.
Keep raw severity in this ledger; put evidence-backed admissibility triage in
the existing status body or index, linked by original ID. Triage never
rewrites a reviewer file.

## `status.md` run-state manifest

```yaml
---
run: <slug>
target-repo: <bare repo name>
genre: workflow-spec | method-spec | decision-record   # stable run-state vocabulary
  # For a technical system or milestone spec, use the nearest value and record
  # its actual document form in intake.md. This compatibility mapping does not
  # force the candidate into ADR headings; design-document owns its structure.
author-binding: <role or "generic">
started: YYYY-MM-DD
stage: <id of the stage currently open>
external-rounds-completed: <n>
allocation: <frontier plan or path to its run note; include effective settings>
dispatches: <n>             # all attempted worker calls, incl. continuations/retries
gates:
  G1: pending | approved YYYY-MM-DD | returned YYYY-MM-DD <why>
  G2: pending | approved YYYY-MM-DD | returned YYYY-MM-DD <why>
flags: []          # e.g. independence-unavailable, rejected-major-pending-G2,
                   # allocation-revised-<stage>, owner-continuation
---
```

Record the allocation before worker dispatch and update it only for affected
unfinished stages when conditions change (`agent-routing` § frontier planning).
For runs created under the earlier `variant: lean|full` and `round-2` fields,
retain those fields and the pinned contract; do not reinterpret completed
stages under the revised procedure. For earlier `dispatches: {opus, fable}`
maps, retain
that map on resume and sum its values when reporting the total; do not rewrite
historical counts without observed dispatch evidence. Precise per-worker token
counts are not tracked unless the runtime returns them.

The dispatch count is an effort signal, not a cost measurement. Any post-run review of
this loop labels every cost and benefit it states **measured / estimated /
assumed** — an unlabelled estimate reads as a measurement.

Body: a stage log, one line per completed stage in execution order:

```
- [done] 0-intake — outputs: intake.md
- [done] 1-draft — outputs: design-v1.md
- [done] G1 — approved 2026-07-19 (provisional alternative: <name>)
- [done] 2-risk — outputs: internal-review-risk.md, internal-review-index.md
- [done] 4-external-r1 — outputs: external-review-r1.md (doc_version: design-v1.md)
- [done] 5-triage — admitted design issue risk-1; implementation check ext1-1
- [done] 3-consolidated-revision — outputs: design-v2.md, ledger rows risk-1, ext1-1
- [open] 6-targeted-verification — changed decision D2 only
```

Every external-review line records the `doc_version` its verdict covers, and
arbitration events get their own lines (`- [done] arbitration — ext1-4:
user ruled accepted, ledger updated`). An owner-directed arbitration fix gets
a stage-6a line tied to the ruling. Record every attempted call separately in
the stage log, including retries, continuations, and an owner-approved
additional external review. Keep non-agent probe/repair count and stop
condition visible; a stage label never resets the budget.

## Acceptance identity

Record G2 in the existing status body: exact revision path, SHA256 of retained file bytes,
owner approval and date. Keep the original `design-vN.md` byte-identical, including PROPOSED.
With no owner-approved delta, it remains the final pointer. Retained local bytes permit recovery
before commit but are not guaranteed backup; a hash is not a Git object. An optional later
repository/commit/path/blob binding requires exact byte comparison and appends to the approval
hash, never replaces it. The same rule applies to base and successor; closure needs no binding
or second binding commit, only the whole-run pin and approval SHA256 below.

For an editorial successor, status lists the owner's approved literal before/after spans with
unique anchors, including any header transition. Ledger rationale is not delta authority.
Use `stage-contracts.md` § Stage 7 for pending/verified/failed reconciliation. Record reviewed
base and verified successor identities before repairing the task link. Status wins over a stale
link; repair idempotently. Final identity, verification and task pointer must agree before done.
Missing approval evidence stops finalization; file existence is not approval.
The task note owns overall task state and next implementation action, without a review checklist.

## Contract provenance and selection

At start record the bounded installed review contract in the existing status body: repository,
entry-point/reference paths, installed-path SHA256 and recoverable pinned bytes. At first
consumption record each additional reference's installed bytes/hash before depending on it.
Use one tree for unchanged consumed bytes and snapshots only for differences. These identities
describe observable installed bytes, not unobservable harness-loaded instructions or assumed
source equivalence. Keep this skill unchanged throughout a run.

On resume select recorded bytes for remaining stage logic under the installed resume procedure.
Current host permissions and runtime safety still apply; a contradictory loaded rule needs an
explicit owner ruling before affected work. A version label or absent new fields alone does not
establish a historical contract. Recover matching entry point and consumed references from pinned
bytes, then record recovered identity and selection in status on resume only.

For completed or unfinished legacy runs, load `retention.md` § Legacy resume
before selecting or changing a historical finalization contract.

## Ordering and resume rules

- **Write-then-mark:** an artifact is written to disk before its stage line is
  marked `[done]`. A crash between the two leaves a written artifact and an
  open stage — safe, because of the reconcile rule below.
- **Edit `status.md` with a mechanism that FAILS LOUDLY on a missed anchor.**
  Write-then-mark guards a crash between artifact and mark; it does not guard a
  *mark that silently no-ops*. A scripted `str.replace()` (or any
  search-and-replace returning the input unchanged when the pattern misses)
  writes nothing, exits 0, and commits clean while the stage log loses entries.
  Use an editor that errors on a non-matching anchor, or a script that exits
  non-zero when any anchor is absent. This inverts the reconcile rule's failure
  mode into its worst case: the *artifacts* are on disk and the *log* is missing,
  so a resume re-runs a recorded-as-absent stage and spends a budgeted call
  regenerating a file that already exists.
- **Reconcile on resume:** select the contract above, list the run and compare
  required/conditional artifacts with status. Verify existing unrecorded outputs before
  finishing missing records; retry only genuinely unfinished work within budget.
  Recorded-but-missing = corruption; stop and report rather than regenerate silently.
  Reconcile stage-7 candidates per `stage-contracts.md`; conditional absence is not failure.
- **Idempotent retry:** re-running a stage overwrites nothing — a retried
  review writes the next unused `r<n>` file without overwriting a prior
  attempt; a retried revision continues the `design-vN` series. Ledger rows
  are keyed by finding ID: a retry updates no existing row and adds only rows
  for IDs that have none.
- Resume comes from `status.md`, never from conversational memory
  (`workflow-driver` invariant).

## Retention

At task closure, load `retention.md` for exact-byte preservation, historical
contract handling, pinned Git context, and citation resolution. Stage 7 leaves
the run evidence intact; review completion does not close implementation.
