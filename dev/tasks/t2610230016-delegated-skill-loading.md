---
title: Investigate incomplete skill loading in delegated workers
type: todo-item
status: blocked
branch: chore/t2610230016
effort: 1
area: tooling
origin: t2610221413
queue:
created: 2026-10-23
updated: 2026-10-23
---

> [!note] Overview
> **What changes** — Reproduce partial governing-skill reads and verify a correction in fresh delegated sessions.
> **Why it matters** — The Claude trial needed coordinator intervention to complete skill obligations and checks.
> **What it takes** — Inspect routing and activation, distinguish possible causes, then test a bounded correction.

## Progress

*Blocked — Awaiting brain-infrastructure's shared-guidance result; revisit when its agent returns.*

Next: Reconcile brain-infrastructure's result against the recorded body-loading and reference-trigger evidence.

- [x] Reproduce partial reads — fresh control delivered only 90 lines from each of three skill bodies.
- [x] Separate causes — explicit read limits confirmed; no model/effort attribution established.
- [x] Test a correction — treatment delivered four complete bodies; reference-trigger compliance still failed.
- [ ] Reconcile the authorized brain-infrastructure handoff and record its correction and verification limits.

- [x] Inspect the original trace — explicit line-limited skill reads preceded the first edit.

Investigation and proposed comparison: [evidence](t2610230016/investigation.md).
Recipient assignment: [brain-infra handoff](t2610230016/brain-infra-handoff.md).

## Work location

- Owner: session-2; branch: chore/t2610230016; base: d0802bf0; no implementation commit.
- Scratch: session-2 :: .tmp/tasks/t2610230016/{control,treatment}.md; retain until proposal disposition.
- Coordination: main :: dev/tasks/t2610230016/; both trial agents exited after completion.

## Observation and scope

The original Claude Code 2.1.308 incident and fresh 2.1.309 comparison are recorded in the evidence note.
Both used Sonnet 5.5 / medium; no model/effort cause is established. The tested handoff paragraph corrected
body loading in one pair, but linked-reference trigger application remains unresolved.

Shared fixes belong to `agent-routing` under `BRAIN_INFRA_ROOT/artifacts/`. On 2026-10-23 the user
authorized handing the correction to brain-infrastructure through Herdr. Its fresh recipient conversation
is `01a169c7-99e2-7140-9d97-761053630c68`, role skill-artifact-developer, observed GPT-6-Astra / low.
No shared adoption result has yet been received.

## Closure result — 2026-10-23

The user approved closure after the infrastructure correction and fresh refinement trial.
Shared changes are committed on infrastructure master: `9b61b3b` requires complete governing skill-body
reads; `458a990` resolves reference triggers before each governed action, including verification.
Static case 41 and infrastructure history/status are aligned.

Fresh refinement conversation `68aa92e6-d59c-4581-ba6c-2f03350bc707`, Claude Code 2.1.309 / Sonnet 5.5 /
medium, delivered all four applicable bodies and all three required references before editing, including
the formerly missed documentation-review reference. This supports the loading correction in one reused,
unblinded development scenario; general reliability and fresh-coordinator discovery remain unverified.
Task-quality/reporting limits survive in the infrastructure commit body. Author conformance passes;
strict infrastructure health retains unrelated navigation and assessment-coverage failures.

Durable outcomes: infrastructure commits `9b61b3b` and `458a990`; original BlueEarth comparison and prompt
are recoverable from `1df74b5cfd4b951bd6e8728b3c553a15d3c5fb0b` at their original task paths.
The previously untracked handoff and pre-closure task note were preserved byte-for-byte in ignored
infrastructure scratch. No further shared correction is required by this bounded task.
Session-2 has no commits outside main; its branch and trial scratch are retained under the handoff's
no-merge/no-deletion boundary. No push is authorized.
