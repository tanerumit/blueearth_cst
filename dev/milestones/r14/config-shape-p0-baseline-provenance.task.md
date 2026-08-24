Task Brief — P0: resolve the baseline's provenance

### Context

Canonical ruleset: `AGENTS.md`. Program: `config-shape-master-brief.md`.

- R14's whole safety argument is G6 ("no number moves"), and
  `check_baseline.py check` is its only falsifier.
- The gate reports `OK - 7 target(s) match manifest` today, but warns that the
  fixture is UNTRACKED and therefore SHARED BY EVERY BRANCH, so a pass may mean
  the tree matches another branch's code.
- `t2608220920` is still `status: backlog`, claiming the `q_indicators.csv`
  reference was recorded 2026-08-16 under weathergenr 1.2.0 and has been
  permanently red since `cf5daa0` completed the 2.0.0 transition on 2026-08-17.
- Those two facts cannot both be current. `dev/milestones/r13/baseline-pass-2-result.md`
  and the manifest's mtime suggest R13's pass 2 may have re-recorded it.

**Must run from the PRIMARY checkout, not a lane** — the fixture is shared, so
a lane-local WF3 run contaminates every other worktree's gate.

### Goal

Establish which is true, with commit-level evidence, so G6 rests on a falsifier
of known provenance.

### Non-goals

- Changing any R14 code. This phase touches no config and no module.
- Re-recording the baseline to make a gate pass.

### Allowed scope

- **Permitted:** `dev/tasks/t2608220920-*.md`, `dev/LOG.md`.
- **Approval-gated:** `dev/baseline/**` — only if a re-record is genuinely
  required, and only after reporting at Gate 2.
- **Forbidden:** every `blueearth_cst/` module, every config, every `*.smk`.

### Required changes (checklist)

1. Date the current `indicator_ref/*.csv` against `cf5daa0` (weathergenr 2.0.0,
   2026-08-17) using `git log` on the manifest and the reference file.
2. Determine whether R13's pass 2 re-recorded the indicator reference.
3. Report ONE of: (a) already resolved — close `t2608220920` with the evidence
   and a `dev/LOG.md` row; or (b) still stale — the green gate is a
   shared-fixture artefact and a WF3 re-record from the primary is required.
4. If (b): PAUSE at Gate 2 before re-recording.

### Validation

- Rung 1: `pixi run python dev/scripts/check_baseline.py check` from the
  primary on a clean `main`; record the exact output.
- **Falsifier for "the green is real, not a shared-fixture artefact":** check
  out a DIFFERENT branch in another worktree and re-run the same command. If
  both report 7/7 against the same untracked fixture, the pass is telling you
  about the fixture, not about the branch.

### Acceptance criteria

- The question is answered in writing with commit-level evidence, not inferred
  from the gate being green.
- `t2608220920` is either closed with its reason or confirmed live, with what
  re-recording requires.
- No baseline artefact changed without Gate 2 approval.

### Output requirements

A finding in `dev/LOG.md` (if closing) or an updated board note (if live), plus
the exact `check_baseline` output from the primary.

### Task constraints

- Run from the primary checkout only.
- Do not re-record to make a gate pass. If the gate should be red, it stays red
  and the milestone learns that before trusting it.
