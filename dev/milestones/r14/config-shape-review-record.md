# R14 — Config shape: review record

> The durable audit trail for the design's one external review round. The
> verbatim review and the brief that produced it are committed beside this file
> and are IMMUTABLE; only the session transcript stays in prunable scratch.

## Run shape

The `design-review-loop` was **partially waived** by the owner (2026-08-24):

| stage | status |
|---|---|
| Stage 0 — intake | done (`config-shape-intake.md`) |
| Stage 1 — draft v1 | done, **authored by the driver** rather than a fresh author spawn |
| G1 — framing gate | waived |
| Stage 2 — internal lens panel | **waived** |
| Stage 4 — external round 1 | **done** — the owner asked for this one round |
| Stage 4 — external round 2 | not dispatched; the owner set a cap of 1 |
| G2 — approval | pending: the owner approves or returns v3 |

**Assurance note, stated plainly.** With the lens panel waived and the round cap
at 1, this design carries the assurance of *one* external pass over a
driver-authored draft. That is materially less than R13's (panel + two external
rounds + arbitration). It is the owner's ruling and is recorded here so a later
reader does not read "reviewed" as equivalent between the two milestones.

## Round 1

| field | value |
|---|---|
| reviewer | `gpt-5.6-sol` via headless `codex exec` |
| dispatched | 2026-08-24, against `config-shape-design.md` DRAFT v2 (`90fba308`) |
| invocation | `--sandbox read-only --ephemeral -c approval_policy=never`, brief on stdin |
| banner confirmed | `model: gpt-5.6-sol` · `approval: never` · `sandbox: read-only` |
| read-only verified | `git status --short` empty and HEAD unmoved after the run |
| verdict | **`revise`** — 3 blocking, 3 major, 0 minor |
| brief | `config-shape-external-review-1-brief.md` (committed beside this file) |
| verbatim report | `config-shape-external-review-1.md` (committed beside this file) |
| session transcript | `.tmp/scratchpad/2026-08-24_r14-review/ext1-transcript.log` — 124 KB of diagnostics, deliberately NOT committed and treated as prunable |

The brief scoped the read list to the design plus the intake and **excluded the
2,400-line scoping document deliberately**, on the reasoning that a
specification which cannot be evaluated without its own argument document is
itself a finding. `ext1-1` is that finding, so the exclusion did its job.

## Ledger

Every finding is dispositioned. **All six accepted; none rejected.** The driver
verified each premise against the repository before disposition, per the loop's
fact-check duty, and graded each as a regression introduced by the design
rather than a pre-existing condition.

| id | sev | premise verified | disposition | landed in |
|---|---|---|---|---|
| `ext1-1` | blocking | CONFIRMED — the design said "driven by the register" and the register is 85 rows of markdown prose in an argument document | **ACCEPTED** | `D-11.2a`: a normative, machine-readable `config/migrations/v1_to_v2.yml` with a per-row schema; a register row without a mapping entry, or the reverse, fails the build |
| `ext1-2` | blocking | CONFIRMED — `D-13.3`'s v1 fixture, the migration note, the mapping itself and the loader's refusal literals all necessarily contain retired spellings | **ACCEPTED** | `D-14.4`: the sweep partitions the tree, carries a classified allowlist, and **fails closed** on an unknown classification |
| `ext1-3` | blocking | CONFIRMED, and sharper than stated — the fixture is UNTRACKED and shared between worktrees, so a contaminated before-state cannot be recovered from git because it was never in git | **ACCEPTED** | `D-14.3`: promoted from "before G6 depends on it" to a **hard pre-implementation gate** with four ordered steps, including recording the four data targets' hashes into a TRACKED file |
| `ext1-4` | major | CONFIRMED — no preflight, staging, rollback or idempotence was specified, and `N8`'s refusal can fire part-way through a set | **ACCEPTED** | `D-11.2b`: preflight over the complete set before any write, stage, validate, atomic commit, `.v1.bak` retention, and defined rerun behaviour for v1 / complete-v2 / partial |
| `ext1-5` | major | CONFIRMED **and under-graded by the reviewer.** `_frozen_differences` diffs `set(was) \| set(now)` over `run_stress_test`, and R14 renames every key in it. `RETIRED_EXPERIMENT_KEYS` rescues only keys that DISAPPEAR (`key not in now`), so the arriving new names still flag. The refusal recurs on every attempt, permanently — not once | **ACCEPTED** | new **§11.6**: the rewriter migrates `experiment.yml` with the same mapping. Invariant: an untouched experiment yields an EMPTY `_frozen_differences` post-migration (`D-14.8`). The `run_historical: false` case is the declared exception and carries a `results_superseded` marker |
| `ext1-6` | major | CONFIRMED — `check_baseline` records from `snake_config_baseline` alone, so `rapid`, `baseline_linux` and `wf2_fast` had no numerical check at all | **ACCEPTED** | new **§14.3**: resolved-config equivalence across all four shipped sets at the resolved-value and `params:` seams, plus targeted execution assertions for `C-69` and `N8` |

## What the round changed, in one line

The design claimed the digest break was "payable once". `ext1-5` is the finding
that it was not: without §11.6 every already-run experiment in every project
would have been permanently unrunnable under its own name. That alone justifies
the round.

## Consequences for the brief set

`ext1-3` re-sequences the program. P0 was concurrent with P1–P5 and is now a
**blocking pre-implementation gate**; the master brief and P0's own brief are
updated. `ext1-1`, `ext1-2` and `ext1-4` land in P3; `ext1-5` adds work to P3
and a falsifier to P4; `ext1-6` adds the equivalence suite to P4.

## Revision log

| version | date | change |
|---|---|---|
| v1 | 2026-08-24 | Created at round 1's dispatch; ledger completed at disposition. |
| v2 | 2026-08-24 | Verbatim review and dispatch brief PROMOTED out of `.tmp/` and committed beside this file. The record's primary evidence had been citing a gitignored, prunable path — a dangling citation waiting to happen, and the failure the loop's own pre-commit check exists to catch. Only the session transcript remains in scratch, and it is now labelled as prunable diagnostics rather than cited as evidence. |
