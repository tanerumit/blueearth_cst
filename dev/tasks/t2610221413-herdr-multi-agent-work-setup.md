---
title: Herdr multi-agent work setup
type: todo-item
status: active
effort: 1
area: tooling
queue:
created: 2026-10-22
updated: 2026-10-23
---

> [!note] Overview
> **What changes** — Propose a visible coordinator and three reusable session spaces for agent work.
> **Why it matters** — Make worker ownership, progress, verification and integration easy to follow.
> **What it takes** — Review the proposal and trial it on one bounded task before adopting maintained guidance.

## Progress

Next: Close the completed task; skill-loading reliability is tracked separately as t2610230016.

- [x] Save the suggested setup and its relationship to the current Git policy.
- [x] Trial visible workers through approved landing — CMIP6 and documentation changes are on main.
- [x] Verify explicit model/effort selection and console justification — session-2 UI confirmed Sol/medium.
- [x] Verify fresh conversation in a reused lane — session-2 preflight and new ID confirmed before assignment.
- [x] Adopt guidance in the existing reference — session-2 commit `57ba82aa` verified; landing pending.

## Proposal

Trial started on 2026-10-22 with owner-approved `session-1` and task `t2610130703`.
Worker `python-engineer-cmip6` used `cst · s1`, agents pane `w8:p1`, on `fix/t2610130703`.
Herdr inventory requires execution outside the restricted sandbox in this environment.
The short prompt wait timed out; a targeted read confirmed delivery and working state, so no retry was sent.
The owner completed its landing; merge `bb29a7df` is on main and session-1 is detached.
Owner correction: select and pass model/effort explicitly before launch, print a one-sentence reason,
and verify effective settings before assigning work. The first launch inherited defaults and failed
this criterion; the running worker is preserved. The proposal records the corrected procedure.
Owner correction: new assignments require a verified fresh conversation; Git cleanliness and an idle
pane do not establish clean context. Related follow-ups may retain their existing conversation.

[Read the suggested work setup](t2610221413/herdr-work-setup.md).

## Second trial

Task `t2610211349` used session-2 on `docs/t2610211349`, worker `technical-writer-docs`, pane `w9:p1`.
Explicit launch used `-m gpt-6-sol -c 'model_reasoning_effort="medium"'`; UI verified both settings.
GPT-6.1 Sol was absent from the local CLI catalog, so the coordinator announced a supported alternative.
New conversation `01a1659a-f6fd-7ea0-bc81-44c130dfa535` completed a preflight-only turn before assignment.
Herdr initially retained an old conversation ID; the new ID and blank startup UI resolved that ambiguity.
The CLI reports that configuration overrides require embedded mode. Herdr tracking works; shared-server
thread discovery did not list this worker. Preserve this limitation when adopting launch guidance.
Documentation commit `1f5228f2` landed with owner approval at `2945a397` on 2026-10-23.
Worker reports `pixi run --frozen docs-build` passed on the final candidate; coordinator verified ancestry
and identical document contents in the merge. Session-2 is detached and its task branch was removed.
The pre-existing main task-board edits survived. No full workflow execution or push was performed.
Both trials are complete through landing; maintained guidance adoption remains outstanding.

## Adoption and runtime probes — 2026-10-23

User authorized adoption, session-2 allocation and a Claude test. Branch: `docs/t2610221413`.
Current owner: `technical-writer-claude`, agents pane `w9:p1`; scope: development workflow reference
and its index. No landing or push authorized. Coordinator owns this task record.

- Codex 0.162.0: launch without `-c`, select model/effort through `/model`, and press `s` for this
  session on the effort screen. UI verified GPT-6.1 Sol / medium; `/daemon` reported a running server.
  Preflight-only thread `01a165a7-70ef-79b0-bae2-0b26f0fac773` appeared in shared-server discovery.
  The probe was exited while idle before Claude took the pane; no implementation had been assigned.
- The live picker exposed GPT-6.1 Sol despite its absence from the earlier local model cache.
  Treat cache absence as inconclusive; prefer the live supported model list.
- Claude Code 2.1.308: explicit `--model sonnet --effort medium` resolved to `claude-sonnet-5-5`
  with medium effort in startup/status UI. Fresh conversation:
  `eafeaedc-56d8-45d5-ad9e-bafec530c3f3`. Preflight confirmed no earlier task; Herdr observed completion.
  Claude's own interactive session is not a Codex shared-server thread.
- Both probes preserved global defaults and permission settings. Documentation implementation and
  verification were assigned to the Claude worker; broader runtime-version guarantees are untested.

Claude delivered `d63784a4`; coordinator review required complete governing skill reads, inspection of
a file-change warning, clearer prior-worker authority and session-only selection wording, and sources.
Corrections `ec62506a` and `57ba82aa` passed coordinator diff review. The warning was attributed to the
worker's own edits, and the final tracked worktree is clean. Coordinator independently ran
`git diff --check main HEAD` successfully. Worker checked local links; coordinator fetched the official
vendor pages. No software suite or site build was needed for the two developer-reference Markdown files.
Scope: `dev/reference/dev-task-and-session-workflow.md` and its `README.md` index.
Owner-approved landing completed at `09cd7e6d`; ancestry and committed-tree equivalence passed.
Session-2 is parked; no push. Follow-up `t2610230016` retains the skill-loading observation and scope.
