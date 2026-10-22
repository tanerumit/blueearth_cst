---
title: Herdr multi-agent work setup
type: todo-item
status: active
effort: 1
area: tooling
queue:
created: 2026-10-22
updated: 2026-10-22
---

> [!note] Overview
> **What changes** — Propose a visible coordinator and three reusable session spaces for agent work.
> **Why it matters** — Make worker ownership, progress, verification and integration easy to follow.
> **What it takes** — Review the proposal and trial it on one bounded task before adopting maintained guidance.

## Progress

Next: Review the session-1 worker return for t2610130703 and record the trial outcome.

- [x] Save the suggested setup and its relationship to the current Git policy.
- [ ] Review and trial the setup on one bounded task using a visible Herdr worker.
- [ ] Verify explicit model/effort selection, console justification and startup settings on a fresh launch.
- [ ] Verify a reused lane starts unrelated work in a fresh conversation, with prior ownership resolved.
- [ ] If adopted, incorporate operational guidance into the existing development workflow reference.

## Proposal

Trial started on 2026-10-22 with owner-approved `session-1` and task `t2610130703`.
Worker `python-engineer-cmip6` runs in `cst · s1`, agents pane `w8:p1`, on `fix/t2610130703`.
Herdr inventory requires execution outside the restricted sandbox in this environment.
The short prompt wait timed out; a targeted read confirmed delivery and working state, so no retry was sent.
Implementation, verification, return review and approved landing remain to be demonstrated.
Owner correction: select and pass model/effort explicitly before launch, print a one-sentence reason,
and verify effective settings before assigning work. The first launch inherited defaults and failed
this criterion; the running worker is preserved. The proposal records the corrected procedure.
Owner correction: new assignments require a verified fresh conversation; Git cleanliness and an idle
pane do not establish clean context. Related follow-ups may retain their existing conversation.

[Read the suggested work setup](t2610221413/herdr-work-setup.md).
