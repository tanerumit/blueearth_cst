---
run: config-modularization
target-repo: blueearth_cst
genre: decision-record   # milestone/refactor design (goal, what-changes, plan,
  # alternatives) mapped per the status schema note; recorded in intake.md
author-binding: cst-architect
started: 2026-08-20
variant: full            # crosses every workflow's config contract + shared seam
stage: 6
external-rounds-completed: 1
dispatches:
  opus: 6
  fable: 2
cost:
  expensive-checks: 0
  doc-lines: 1341
findings:
  unique: 53
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
- [done] 4-external-r1 — outputs: external-review-r1.md (verdict: revise, doc_version: design-v2.md, 4 major: ext1-1 S4 exception via Q2/wflow_outvars; ext1-2 --write vs report-only ruling; ext1-3 --config passthrough breaks (faults risk-18 resolution); ext1-4 --touch provenance hazard (faults risk-16 fix)). Post-run git verification clean
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
