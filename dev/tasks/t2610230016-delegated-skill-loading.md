---
title: Investigate incomplete skill loading in delegated workers
type: todo-item
status: backlog
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

Next: Inspect the worker handoff and tool reads before choosing a reproducible comparison.

- [ ] Reproduce the partial-read behavior with a bounded task and inspect actual skill reads.
- [ ] Separate handoff, role activation, output truncation and model/effort explanations.
- [ ] Propose a correction in the owning guidance and verify it in a fresh session.

## Observation and scope

Observed 2026-10-23 in Claude Code 2.1.308, Sonnet 5.5 / medium, conversation
`eafeaedc-56d8-45d5-ad9e-bafec530c3f3`: the worker initially reported reading only excerpts of governing
skills, despite an assignment to apply the full role and applicable bindings. It also reported a missing
diff check and an uninspected file-change warning. Coordinator follow-up requested full SKILL.md bodies,
inspection and checks; the corrected documentation landed at `09cd7e6d` after review.

This is one observed failure and a reported recovery, not evidence of a Claude-wide defect or an effort-level
cause. Inspect tool reads rather than relying only on worker self-report. Compare equivalent fresh tasks
before attributing the issue to runtime, prompt, role projection or model selection.

Candidate shared owners: `agent-routing`, role activation and the `technical-writer` contract under
`BRAIN_INFRA_ROOT/artifacts/`. Inspect existing guidance before adding instructions. Shared fixes belong
in brain-infrastructure; this project task tracks the observed consumer issue and does not authorize
cross-repository edits. No change has yet been selected or tested for general adoption.
