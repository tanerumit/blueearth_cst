---
run: config-modularization
target-repo: blueearth_cst
genre: decision-record   # milestone/refactor design (goal, what-changes, plan,
  # alternatives) mapped per the status schema note; recorded in intake.md
author-binding: cst-architect
started: 2026-08-20
variant: full            # crosses every workflow's config contract + shared seam
stage: 6b
external-rounds-completed: 1
dispatches:
  opus: 6
  fable: 3
cost:
  expensive-checks: 1   # framework-feasibility probe, 2026-08-21
  doc-lines: 1341 -> 3012
findings:
  unique: 57
  re-raised: 3
gates:
  G1: approved 2026-08-20
  G2: pending
flags: []
---

- [done] 0-intake — outputs: intake.md (evidence register E1-E10, gate check); verification dispatch 1 (fable, model-inherit slip)
- [event] scope-amendment 2026-08-20 — owner: milestone wiring (R13; R12 taken by WF3 execution model) + workflow-naming reconsideration in scope; intake amended pre-G1; in-flight author notified
- [done] 1-draft — outputs: design-v1.md (1341 lines, 20 sections, decision IDs D-7.1..D-15.3, naming candidates A/B/C rec A, premises N1-N8 added); author confirmed scope amendment incorporated
- [done] G1 — approved 2026-08-20. Rulings: (1) framing approved as drafted (problem, constraints, decision criteria); provisional alternative: path-referenced composition — T1 closed {enabled, config_path} stanzas + per-workflow T2 files, loader-composed, in-memory config shape unchanged; (2) naming: Candidate A, keep current workflow names (provisional, final at G2); (3) migration posture: clean break, no dual-mode loader, report-only split_project_config.py. All three chose the recommended option via AskUserQuestion.
- [done] 2-internal-panel — outputs: internal-review-risk.md (revise, 1B/8M/9m), internal-review-architecture.md (revise, 0B/15M/6m), internal-review-repo-fit.md (revise, 4B/4M/5m), internal-review-index.md (9 groups, 3 conflicts, gate-return check: no scope fork)
- [open] 3-revision-r1 — author dispatched (cst-architect, Opus)
  - [recovery] 2026-08-20 15:10 — spawn died: RESOURCE EXHAUSTION (session limit, reset 15:10 CET). Partial preserved: design-v2.md sections 1-15 revised (finding resolutions embedded, incl. D-13.4 removing the advanced-settings interior move from R13); MISSING: sections 16-20 + ledger.md (0 of 52 rows). Per roles-and-recovery: waited for reset, completion spawn dispatched 15:15 scoped to the remainder (opus +1)
- [done] 3-revision-r1 — outputs: design-v2.md (2719 lines, +D-12.6b), ledger.md (52 rows: 5B+27M+20m all accepted; 3 part-level declines argued in-doc; no rejected blocking/major). Two-spawn completion after session-limit crash. Driver verify: 52/52 rows, no blocking deferred/rejected. Phantom-ID note: index cited risk-19, actual id risk-18 (driver index error, documented in ledger)
- [open] 4-external-r1 — dispatched 2026-08-20 ~16:00 CET: codex exec (GPT, codex-cli 0.145.0, ChatGPT auth), clean-room round on design-v2.md, brief instantiated as review-brief.md (settled-framing block filled from G1 + scope amendment; OV-1..5 explicitly reviewable). Posture: --sandbox read-only + -c approval_policy=never; Windows sandbox helper missing on this machine (known wart), so read-only is intent + escalation-denied + post-run git verification. Output: external-review-r1.md via -o; transcript in session scratchpad; PID 22796, Monitor armed
- [done] 4-external-r1 — outputs: external-review-r1.md (verdict: revise, doc_version: design-v2.md, 4 major: ext1-1 S4 exception via Q2/wflow_outvars; ext1-2 --write vs report-only ruling; ext1-3 --config passthrough breaks (faults risk-17 resolution — corrected 2026-08-21 from risk-18, which is the path-normalization finding); ext1-4 --touch provenance hazard (faults risk-16 fix)). Post-run git verification clean
- [done] 5-convergence-r1 — NOT converged (revise + 4 major). ext1-1/3/4 fault prior-round resolutions -> stage-6 revision escalates to FABLE per tier policy
- [event] gate-clarification 2026-08-20 — owner ruled on ext1-2 interpretation via AskUserQuestion: STAGING-EMIT — split_project_config.py is strictly report-only against user files; it emits proposed T1+T2 into a staging directory plus a report; application is a user step. No --write / in-place mutation mode
- [event] gate-clarification 2026-08-21 — owner ruled on ext1-3 via AskUserQuestion: NARROW G4. G4 is restated as covering the `--configfile` path contract, the wrapper invocation, and `config_path` forwarding; ad-hoc `snakemake --config workflows.<name>.<setting>=value` overrides of workflow settings are WITHDRAWN, not preserved. Rationale given: an override that bypasses the T2 file is exactly the shared-seam hole D-9.1 exists to close, and the withdrawal is consistent with the G1 clean-break posture. The revision owes a migration mapping: every formerly supported override form -> its T2 edit. Option 'route overrides into the composed T2' was offered and declined.
- [event] resume 2026-08-21 — run resumed in worktree session-1, branch feat/config-modularization, claim claim_nnajOoglxqjJ5EFJn24WW7VfVKuDnp07 held by the interactive session directly (GIT_TASK_CLAIM in env — no child-session workaround needed this time); scope extended to the run dir + dev/tasks + dev/TODO.md. RESUME item 1 below is superseded: session-2 sits at 47c8f1c with no run dir, the run artifacts landed on main at 390c069, and this lane holds them tracked.
- [open] 6-revision-r2 — PAUSED. Fable spawn dispatched then STOPPED by owner request (2026-08-20, session end) BEFORE its skeleton step: NO design-v3.md exists, NO ext1 ledger rows appended. Clean resume point.

## RESUME INSTRUCTIONS (next session — read before acting)

1. Re-verify environment (roles-and-recovery § resume): worktree session-2, branch docs/config-modularization, claim in registry (claim id in .git/agent-slots via task-status; GIT_TASK_CLAIM for CLI + shell-write posture per the owner ruling logged in observations.md).
2. FIRST ACTION — board debt: add the todo-item for this run to dev/tasks/ and render, IF session-1's claim no longer holds dev/tasks + dev/TODO.md (it did at pause time; the registry refuses overlap). Item: resume R13 config-modularization design run at stage 6 (revision r2), run dir dev/working/design-runs/config-modularization/, origin R13.
3. Re-dispatch stage 6: fresh cst-architect on FABLE (re-raise trigger fired: ext1-1/3/4 fault prior resolutions). Inputs: intake.md, design-v2.md, ledger.md (52 rows, append ext1-1..4), external-review-r1.md, internal panel files for context, gate record INCLUDING the staging-emit ruling (split_project_config.py strictly report-only: emits proposed T1+T2 to a staging dir; no --write). Skeleton-first: cp design-v2.md design-v3.md. Scope confined to the four findings + forced cross-refs.
4. Then: driver scope-check of the v2→v3 diff, round-2 trigger check (findings-and-closure § Round 2), and round 2 or logged waiver + scoped pass → G2. Owner-visible at G2: OV-1..5 (§18 of v2) + staging-emit rework + ext1-4 resolution.
5. Session ruling still in force (observations.md): this session line acts as primary integration owner — mechanical READY checks, task-ready AFTER G2/finalize, integration-start/complete from primary, no git-integrator. Landing needs scope extension: dev/milestones/r13, dev/roadmap.md (+ dev/tasks for the board note).
6. Leftover for cleanup at integration: stray zero-commit branch docs/config-modularization-design at 47c8f1c (topology-guard-blocked from task sessions).
- [done] 6-revision-r2 — outputs: design-v3.md (3012 lines, +293; new decision ID **D-9.6**), ledger.md (4 ext1 rows appended, all `accepted`, 52 originals untouched — verified `git diff --stat` = 14 insertions / 0 deletions). Driver scope-check PASSED: 20 sections touched across 39 hunks, every one mapping to an ext1 finding's section or a declared forced cross-ref (heading-mapped diff, `.tmp/scratchpad/2026-08-21_1255/scope_check.py`). Decision-ID diff verified mechanically: exactly one added (D-9.6), none removed
- [event] framework-feasibility probe 2026-08-21 — driver-run, per `evidence-and-gates.md` § Framework-feasibility probes; §15.6's records-first refresh sequence is a mechanism whose feasibility rests on Snakemake execution semantics and asserts an absence ("must schedule nothing"), which is the named probe class. Run against `test_case/test_rapid` (a tree with a COMPLETED experiment) and a 56 MB copy at `.tmp/probe-touch/` for the mutating step. **RESULT: step 3 CONFIRMED, step 4 REFUTED.**
  - P-A `snakemake all --touch -s run_stress_test.smk` on the copy: **succeeded**, 32/32 jobs, 4 s. `--touch` does NOT error on reaped `temp()` outputs and does not resurrect them. §15.6 step 3's first half holds.
  - P-B post-touch `snakemake all -n` on the same copy: **schedules 28 jobs**, not zero. Reason given: `output files have to be generated: check_model_reference, downscale_climate_realization, generate_weather_realizations, perturb_climate_realization` — all four are exactly the `temp()`-wrapped rules (`run_stress_test.smk:736, 931, 975, 1021/1029`), with everything downstream inheriting `input files updated by another job`. `--touch` cannot touch a file that does not exist, so the reaped intermediates keep the DAG permanently dirty.
  - P-C pre-migration control, `all -n` on the untouched `test_case/test_rapid`: WF1 schedules 20 jobs, WF3 schedules 36 — so the tree does not schedule nothing even before any migration.
  - **Consequence:** §15.6 step 4 ("a final `--dry-run` per workflow must schedule **nothing**") cannot come back clean on any project whose `temp()` intermediates have been reaped — which AGENTS.md mandates as the normal state of a WF3 run, and which `run_stress_test.smk:556-560` already documents in-tree ("on a COMPLETED experiment every 3.12 output is temp() and already deleted"). The step-4 equivalence proof is unachievable as specified, and step 3's conclusion that "nothing consumes it" is wrong for `downscale_climate_realization` / `perturb_climate_realization`, which `run_wflow_batch_*` does consume. Same failure class as the r08 revalidate-and-skip cache the skill cites.
- [open] 6b-corrective-pass — the probe refutes a mechanism the revision introduced, which is a DESIGN change rather than a review finding, so it returns to the author before any reviewer sees it. Round 2 is already committed on trigger 3 (below) and will review the corrected document.
- [event] round-2 trigger check 2026-08-21 — **ROUND 2 FIRES.** Trigger 3 (`the revision introduced new decision IDs`) fires unconditionally: D-9.6, verified by mechanical ID diff, is a mechanism no reviewer has seen. Trigger 1 (`a BLOCKING fix changed or introduced a mechanism`) does **not** fire — it is blocking-scoped and all four ext1 findings are `major`; noted explicitly because the revision does introduce two new mechanisms and a later reader would otherwise assume it fired. Trigger 2 (`a blocking or major finding was rejected`) does not fire — all four rows are `accepted`, and the two declined parts (ext1-3 route-into-T2, ext1-4 remove-the-shortcut) are branches the reviewer's own `suggested_fix` offered as alternatives. Trigger 4 (`probe missing or contradicted`) was firing; the driver closed it by running the probe above, which contradicted the design — so it is folded into the corrective pass rather than cited as a second reason to review.

