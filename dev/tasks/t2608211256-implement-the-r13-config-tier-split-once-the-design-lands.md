---
title: Implement the R13 config tier split once the design lands
type: todo-item
status: backlog
branch: feat/config-modularization
effort: 2
area: config
origin: R13
queue:
created: 2026-08-21
updated: 2026-08-21
---

> [!note] Overview
> **What** — Split the monolithic project config into a T1 project file carrying closed {enabled, config_path} workflow stanzas plus per-workflow T2 files, composed by a shared loader so the in-memory config shape is unchanged. Ships a report-only split_project_config.py that emits proposed T1+T2 into a staging directory, migration docs, and the parse-time shared-seam checks (D-9.1).
> **Why** — The design is ACCEPTED: G2 approved it on 2026-08-21 (run-dir
> `design-v5.md`, landed as `config-tiers-design.md`) after a
> three-lens internal panel, two external rounds, a driver framework probe that
> refuted a mechanism, and owner arbitration at the round cap. 63 findings, all
> dispositioned. Read `dev/milestones/r13/config-tiers-design.md` (the normative
> contract) and `config-tiers-review-record.md` (why it says what it says) before
> starting; §15.7 carries the commit sequencing and §16 the validation plan.
>
> **Scope note the owner ruled at arbitration:** R13 is NOT split-only. It carries
> the `wflow_outvars` hoist as a required final phase (D-9.7) — validate split-only
> neutrality first, then hoist, then verify the *expected* digest shift, with
> `CROSS_WORKFLOW_READS` empty before the milestone completes. That means **two**
> baseline-scale validation passes, not one. Do not descope it back to the split.
> **Effort** — large

## Progress

- [ ] <first step>
