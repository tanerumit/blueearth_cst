---
run: named-indicator-sets
target-repo: blueearth_cst
genre: workflow-spec
author-binding: cst-architect
started: 2026-10-16
stage: G1
external-rounds-completed: 0
allocation: inline frontier plan below
dispatches: 3
gates:
  G1: pending
  G2: pending
flags: [allocation-revised-reviews]
---

# Review status

Canonical owner: main :: dev/tasks/t2610161523/design-runs/named-indicator-sets/.
User authorized review, not implementation. Driver writes under the primary maintenance exception.
Main's unrelated wf0-lab-integration deletions remain outside scope.

## Allocation

Coordinator: current Codex session; inline planning; effective model unknown.
Maximum seven worker calls including continuations/retries; at most one same-stage recovery.
No planner worker. One consolidated revision; at most one targeted verification.
Concurrency: one worker before G1; up to two independent reviewers after G1 if isolation permits.

| Stage | Allocation / ownership | Dependency / check |
|---|---|---|
| 1 | cst_architect, GPT-6.1-sol/high; candidate | Seed/intake; explicit complete proposals. |
| 1b | model-validator, Claude Opus/high; review only | Frozen candidate; claim-evaluation and E1-E6. |
| G1 | User | Domain findings and framing before further review. |
| 2 | critical-thinker, Claude Opus/high; review only | G1; same candidate as external review. |
| 4 | Independent Claude reviewer, Opus/high | G1; cross-family versus author. |
| 3 | Same author continuation | Triage; one revision, every finding dispositioned. |
| 6 | Relevant independent reviewer if needed | Unresolved changed decisions only. |
| G2/7 | User exact approval, driver finalization | Retained bytes, closure, implementation obligations. |

Requested allocations are recorded; effective settings remain unknown unless runtime reports them.
Claude is installed and authenticated. Restricted-tool enforcement remains to be verified before
review dispatch. Native reviewers have no demonstrated read-only enforcement; hold that stage if
required isolation cannot be established. No silent weakening or same-family external fallback.

## Stage log

- [done] 0-intake — intake.md records journey, premises, domain flag, and evidence needs.
- [done] 1-draft — call 1: /root/indicator_design_author; terminal; design-v1.md retained.
- [held] 1b-domain — call 2 launch rejected before execution by automatic approval review.
- [pending] G1 — start authorization is not framing approval.

## Provenance and inventory

Installed design-review-loop v0.17.1; consumed installed bytes retained in protocol/.
SHA256 identities are in protocol/manifest.csv. Those identify observed files, not harness loading.
Pin additional references on first consumption; preserve raw reviews and candidate versions.

Required: intake.md, status.md, initial candidate, protocol record. Reviews on dispatch;
index/ledger on findings; external brief at external dispatch. No acceptance identity before G2.
No execution probes scheduled. Usage/cost/effective settings unknown unless observed.

## Candidate and held domain dispatch

Candidate: design-v1.md.
SHA256: 527FF4E325965EFE7F57797C064CCE7349F00DC7AAE64FF4A8A90BA2FF45BE0F.
Author requested GPT-6.1-sol/high; effective settings not independently observable.
The author inspected sources; no scientific calculation, DAG, or implementation ran.

Call 2 requested a fresh Claude Opus/high model-validator review with the full role and
claim-evaluation contract. CLI 2.1.301 supports restricted mode, Read/Glob/Grep-only tools,
dontAsk permissions and no MCP. Effective enforcement was not observed because no process started.

Automatic approval review rejected the launch: private repository/design content would be sent to
Anthropic, and the general review request was not considered explicit payload/destination consent.
No retry or indirect execution. User was asked to authorize the scoped Claude transfer or keep the
review within Codex. The denied launch is conservatively counted against the seven-call budget.
One successful author call, one denied launch, zero completed domain/risk/external reviews.
Five calls remain; any additional recovery or expanded review needs budget reassessment.

Pending transfer scope: candidate, intake, reviewer instructions and relevant WF4 registry, metric
planning, response-reader, grouping and calculation source files; no datasets, credentials or outputs.
Reviewer packet is in the task's .tmp/named-indicator-review/; it has not been transmitted.
G1 remains pending and cannot proceed until the independent domain review is complete.

## Owner continuation, 2026-10-16

Owner: "Lets have one round of reviews with Claude Opus" in response to the scoped-transfer question.
This authorizes the named design/source payload to Anthropic Claude and one review round, not
implementation or automatic extra rounds. All remaining review allocations use Opus as requested.
The author remains GPT-family, so Claude reviews preserve cross-family independence from the author.
G1/G2 remain required; no framing approval is inferred from model/transfer authorization.

- [open] 1b-domain — call 3, authorized retry after the pre-execution permission rejection.
  Candidate hash unchanged; restricted CLI tool list will be checked from its initialization record.

Observed call 3 initialization: claude-opus-5-5; tools exactly Read, Glob, Grep;
permissionMode=dontAsk; no MCP servers. No shell, write, edit or delegation tools exposed.
Requested effort high; effective effort not reported in initialization.

## Domain completion and G1 presentation

- [done] 1b-domain — call 3 exit 0; internal-review-domain.md retained verbatim.
  Verdict: revise; domain-1/2/3 major, domain-4/5/6 minor. E1-E5 supported with qualifications;
  E6 is a future hypothesis requiring parity evidence, not established equivalence.
- [done] preliminary triage — internal-review-index.md preserves raw severity, source checks,
  limitations, and unresolved unit interpretation. Ledger contains all six pending IDs.
- [open] G1 — owner framing question presented; no reply recorded yet.

Displayed candidate: design-v1.md, SHA256
527FF4E325965EFE7F57797C064CCE7349F00DC7AAE64FF4A8A90BA2FF45BE0F.
Raw domain report SHA256:
41494F32CE44719A55F1D370BA47F6B4C8DE8F0F3AF859198D0AEFCE62F4BD20.

G1 proposed framing shown to the owner: preserve the agreed interface and existing calculations;
add a readable indicator dictionary beside each named result; state temporal/missingness policies;
map parity checks to retained outputs and targeted fixtures; reject ambiguous null selections in
new configurations. Exact unit wording remains an explicit issue to resolve before G2.
Use a neutral example_subset name until a second scientific set is commissioned.

The domain review's approximate bias magnitude and unconditional direction claims are not adopted
as measured evidence. No code/numerical behavior is changed by this proposal. External review must
resolve or narrow the unit interpretation; owner framing approval does not waive scientific validity.

Budget: three attempted worker calls (author, rejected launch, successful domain review); four remain.
No risk review or external round has run. User's one-round limit remains in force.
Resume after G1: refresh candidate only if the ruling materially changes framing, then risk and
external Opus reviewers examine the same current candidate. Count any author continuation and
targeted verification against the remaining budget; request a bounded extension only if necessary.
