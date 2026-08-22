---
title: Implement the R13 config tier split once the design lands
type: todo-item
status: active
branch: feat/r13-config-tiers
effort: 2
area: config
origin: R13
queue:
created: 2026-08-21
updated: 2026-08-22
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

- [x] Commit 1 — `config_composition.py` + seam checks + D-9.6 scan (`072dfc1`)
- [x] Commit 2 — `split_project_config.py`, report-only (`14ecd54`)
- [x] Commit 3 — seeds/fixture/template migrated, four Snakefiles wired (`b505233`)
- [x] Commit 4 — composed snapshot, record-only T2 registration (`0496d44`)
- [x] Commit 5 — the raw-T1 tools compose (`a457157`)
- [x] Commit 7a — migration guide + reference sweep (`a18352b`)
- [x] Commit 7b — **split-phase baseline re-record** (`b4c58d8b`). Pass 1 run
      from the primary detached at `9cbb72a`, read, and recorded 7/7 green.
      **The split is output-neutral.** Result:
      `dev/milestones/r13/baseline-pass-1-result.md`; runbook acceptance
      criteria corrected the same day.
- [x] Commit 8 — the `wflow_outvars` hoist (`e3c9cbb`). Landed AHEAD of 7b by
      owner decision: D-9.7 sequences the validation, not the history, and
      pass 1 runs against a detached checkout at `9cbb72a` which carries none
      of it. Consequence: `check_baseline.py check` at HEAD is expected to
      disagree with `dev/baseline/manifest.json` until commit 9
- [ ] Commit 9 — hoist-phase baseline re-record; **the last step, R13 sealable
      after it**. Needs the primary re-detached at this branch's tip (it now
      sits at `9cbb72a`, below the hoist), then the same five runbook steps.
      Pass 2's acceptance differs from pass 1's: all THREE yaml snapshots move
      there, because the hoist changes `shared:` and `shared` is in every entry
      point's projection. `check_baseline check` at HEAD is EXPECTED to disagree
      until it lands.

## Pass 1 outcome (2026-08-22)

Verified from the primary, not argued:

- **wf1 discharge unchanged**, **both CMIP6 change-factor CSVs unchanged** — the
  split's output-neutrality test, passed.
- WF1's and WF2's config snapshots moved off the shared `00ef44f7` to distinct
  hashes, as designed (D-11.1).
- **WF3's snapshot did NOT move, and that is the WF3 neutrality proof.** Its
  `CONFIG_PROJECTION` is derived from `guarded_sections`, so R(run_stress_test)
  covers every populated stanza of this config and composition is an identity on
  it. Because the snapshot is a dump of the mapping WF3's rules actually read,
  an unchanged digest means WF3 reads value-identical config across the split.
  The runbook predicted this one would move; it was wrong, and is corrected.
- `q_indicators.csv` differs (610/630 rows) — **not R13's**. The reference was
  recorded under weathergenr 1.2.0 on 2026-08-16; `cf5daa0` completed the 2.0.0
  transition on 2026-08-17. Boarded as `t2608220920`.
- Blocking DAG defect found and boarded for `main`: `t2608220915`.

Verified in the lane: `test-full` 3043 passed / 9 skipped / 1 xfailed,
`test-contract` 70, `tree-check` MAP CLEAN, lint + format clean. Six of the
nine skips ARE the fixture layer, so that green is not evidence about the
composed snapshot — see `dev/milestones/r13/migration_config-tiers.md`.
