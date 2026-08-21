# Process observations — config-modularization run

Process friction only; no design content.

- 2026-08-20 (run start): the atomic-lane system and an interactive
  design-loop driver conflict: the claim token reaches only a fresh child
  session via env, so the interactive session that owns the human gates can
  never satisfy the native-write guard. Owner ruled: allocate the claim via
  task-start with a no-op child, hold the token, write run artifacts through
  shell commands carrying GIT_TASK_CLAIM; registry transitions use --claim.
  Candidate lesson for git-workflow/workflow-driver: a sanctioned "adopt
  claim into a running session" path.
- 2026-08-20: first claim attempt used slot-start --admin (recovery), which
  checked out a branch WITHOUT registering a claim — lane read UNCLAIMED with
  a branch present. Parked and re-allocated via task-start. Leftover: stray
  zero-commit branch docs/config-modularization-design at the then-main tip
  (47c8f1c); branch deletion is topology-guard-blocked for this session —
  needs git-steward cleanup.
- 2026-08-20: board note deferred: dev/tasks + dev/TODO.md sit in
  session-1's READY claim scope, and the registry refuses overlap. Add the
  board note (and extend task scope) after that lane integrates.
- 2026-08-20: the stage-0 verification agent was dispatched without a model override and INHERITED the driver model (Fable) instead of Opus — tier policy says workers run Opus. Counted under dispatches.fable. Lesson: every Agent dispatch in this loop must set model explicitly.
- 2026-08-20 (stage 1 return): author reported an intake evidence-register gap: E5 did not record that two forwarded-to scripts RE-READ the source YAML from disk (prepare_weagen_config.py:89-91, prepare_cst_parameters.py:162-165) nor that config_path is a declared rule INPUT in six rules. All three were load-bearing for the design (its N1/N2/N8). Lesson for the skill: the stage-0 register should ask what CONSUMES the artifact being restructured, not only what produces/validates it.
- 2026-08-20 (stage 2): the three parallel lens spawns SHARE one scratchpad directory; the risk lens reported its generically-named appendix.md overwritten mid-run by architecture-lens content (it recovered by switching to lens-prefixed names; delivered file clean). Lesson for the skill/workflow-driver: parallel spawn briefs must mandate agent-unique scratch filenames or subdirectories.
- 2026-08-20 (stage 2): the panel worked — 52 findings, 5 blocking, with near-zero overlap between lenses (only 3 same-defect duplicates across 52). The three-lens split by concern (adversarial / mechanism / conventions) produced genuinely disjoint coverage.
- 2026-08-20 (owner ruling, session-scoped): this session acts as PRIMARY INTEGRATION OWNER for docs/config-modularization — no git-integrator dispatch. The atomic registry is used for ownership and cleanup only; the driver session performs the mechanical READY checks (full-diff review, testing-policy check), integrates from the primary, and runs integration-complete itself. task-ready still runs only after the review (ready_sha freeze discipline).
- 2026-08-20 (stage 3): driver index error — group F cited a phantom risk-19 (the path-normalization finding is risk-18). Caught by the completing author; documented in the ledger closing note. Lesson: the index writer should validate every cited ID against the per-lens files mechanically before landing the index.
- 2026-08-20 (stage 3): the two-spawn resume-in-place worked as designed — the completion spawn extracted all 52 dispositions from the partial without re-authoring, and additionally caught a real §12.6 contradiction (D-12.6b) the first spawn had left inconsistent.
- 2026-08-21 (resume): board debt CLEARED — t2608211256 boarded (blocked, branch feat/config-modularization, origin R13). The overlap that deferred it is gone: the READY lane holding dev/tasks integrated at 21f0368, so this session's own claim could take dev/tasks + dev/TODO.md in its scope declaration.
- 2026-08-21 (resume): the stage-0 claim workaround was NOT needed this time — the interactive driver session was itself allocated the lane and carries GIT_TASK_CLAIM in env, so shell writes satisfy the guard without a no-op child. Strengthens the candidate lesson already logged for git-workflow: the friction is specific to adopting a claim into a session that was already running, not to interactive drivers as such.
- 2026-08-21 (resume): status.md's RESUME block named the wrong worktree — it said session-2 / branch docs/config-modularization, but the run artifacts had landed on main (390c069) while session-2 stayed at 47c8f1c with no run dir at all. Lesson for the skill: a resume block should name the run dir's TRACKED path and the claim id, never a worktree or branch, since both are reallocated between sessions and the run dir travels with the commit.
- 2026-08-21 (stage 6 return): SECOND driver ID misattribution in this run — status.md's stage-5 line said ext1-3 faults `risk-18`; the faulted row is `risk-17` (the `--config` passthrough finding), risk-18 being path normalization. Caught by the revising author, not the driver. This is the same class as the stage-3 phantom `risk-19`, so it is now a PATTERN, not a slip: the driver writes finding IDs into status.md and the index from working memory without validating them against the per-lens files. Lesson for the skill: every driver-written artifact citing a finding ID should have those IDs checked mechanically against the source files before it lands — the same rule already proposed for the index at stage 3, widened to status.md.

