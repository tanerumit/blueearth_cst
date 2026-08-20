---
run: config-modularization
target-repo: blueearth_cst
genre: decision-record   # milestone/refactor design (goal, what-changes, plan,
  # alternatives) mapped per the status schema note; recorded in intake.md
author-binding: cst-architect
started: 2026-08-20
variant: full            # crosses every workflow's config contract + shared seam
stage: 3
external-rounds-completed: 0
dispatches:
  opus: 6
  fable: 1
cost:
  expensive-checks: 0
  doc-lines: 1341
findings:
  unique: 52
  re-raised: 0
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
