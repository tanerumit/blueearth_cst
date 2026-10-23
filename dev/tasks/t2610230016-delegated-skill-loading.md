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

*Blocked — Awaiting owner disposition of the shared-guidance proposal; revisit on the owner's reply.*

Next: Decide whether to adopt the tested handoff clarification with its recorded reference-trigger limitation.

- [x] Reproduce partial reads — fresh control delivered only 90 lines from each of three skill bodies.
- [x] Separate causes — explicit read limits confirmed; no model/effort attribution established.
- [x] Test a correction — treatment delivered four complete bodies; reference-trigger compliance still failed.
- [ ] Obtain disposition of the proposed shared handoff clarification; no infrastructure edits authorized.

- [x] Inspect the original trace — explicit line-limited skill reads preceded the first edit.

Investigation and proposed comparison: [evidence](t2610230016/investigation.md).

## Work location

- Owner: session-2; branch: chore/t2610230016; base: d0802bf0; no implementation commit.
- Scratch: session-2 :: .tmp/tasks/t2610230016/{control,treatment}.md; retain until proposal disposition.
- Coordination: main :: dev/tasks/t2610230016/; both trial agents exited after completion.

## Observation and scope

The original Claude Code 2.1.308 incident and fresh 2.1.309 comparison are recorded in the evidence note.
Both used Sonnet 5.5 / medium; no model/effort cause is established. The tested handoff paragraph corrected
body loading in one pair, but linked-reference trigger application remains unresolved.

Shared fixes belong to `agent-routing` under `BRAIN_INFRA_ROOT/artifacts/`. This project task does not
authorize cross-repository edits. No shared correction has been installed or adopted.
