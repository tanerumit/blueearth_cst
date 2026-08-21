# R13 config tiers — consolidated review record

> Lands as `dev/milestones/r13/config-tiers-review-record.md`. This is the durable
> audit trail for the design-review-loop run that produced the accepted R13 design;
> it is what makes pruning the run directory safe. Rationale, superseded
> alternatives and round-by-round argument accrue **here**, not in the design,
> whose body carries the normative contract.

- **Run:** `config-modularization`, 2026-08-20 → 2026-08-21, variant `full`
- **Accepted design:** `config-tiers-design.md` (was `design-v5.md`, 3416 lines)
- **Intake:** `config-tiers-intake.md` (was `intake.md`)
- **Author binding:** `cst-architect` · **Dispatches:** Opus ×6, Fable ×4
- **Expensive checks:** 2 (one framework-feasibility probe, one CLI verification)

## Verdict table

| Round | Reviewer | Doc reviewed | Verdict | Findings |
|---|---|---|---|---|
| Internal panel (stage 2) | risk lens (`critical-thinker`) | `design-v1.md` | revise | 1 blocking, 8 major, 9 minor |
| Internal panel (stage 2) | architecture lens | `design-v1.md` | revise | 0 blocking, 15 major, 6 minor |
| Internal panel (stage 2) | repo-fit lens | `design-v1.md` | revise | 4 blocking, 4 major, 5 minor |
| External r1 (stage 4) | `codex exec` (GPT), clean-room | `design-v2.md` | revise | 4 major (`ext1-1..4`) |
| Driver probe (stage 6b) | framework-feasibility probe | `design-v3.md` §15.6 | refuted | 1 blocking (`probe-1`) |
| External r2 (stage 4) | `codex exec` (GPT), with ledger + index | `design-v4.md` | revise | 2 blocking, 4 major (`ext2-1..6`) |
| Arbitration (round cap) | repository owner | `design-v4.md` findings | ruled | 6 findings + 1 withdrawal |
| **G2** | repository owner | **`design-v5.md`** | **approve** | no editorial edits |

63 unique finding IDs, every one dispositioned. Full dispositions: `ledger.md`
(64 rows — 63 findings plus one arbitration entry against `risk-3`).

## Version history

| Version | Produced by | Answering |
|---|---|---|
| `design-v1.md` (1341 lines) | stage 1 draft | — |
| `design-v2.md` (2719) | revision r1 | the 52-finding internal panel |
| `design-v3.md` (3012) | revision r2 | `ext1-1..4`; minted **D-9.6** |
| `design-v4.md` (3057) | corrective pass 6b | `probe-1` |
| `design-v5.md` (3416) | arbitration revision 6a | `ext2-1..6`; minted **D-9.7**, **D-15.3a** |

Verbatim reviews are preserved in git rather than retained on disk — the run
directory was drained at closure per `dev/README.md`. The commits holding each:

| Artifact | Commit |
|---|---|
| `internal-review-{risk,architecture,repo-fit}.md`, `internal-review-index.md` | `8b85c4c` |
| `external-review-r1.md` | `ef498a9` |
| `external-review-r2.md` | `b0a5607` |
| `ledger.md` (final, 64 rows incl. arbitration entries) | `1c788ec` |
| `status.md` (gate records, probe measurements) | `c657365` |
| `observations.md` (process-friction log) | `c657365` |
| `design-v1..v4.md` (superseded) | `git log -- dev/working/design-runs/config-modularization/` |

## What the review actually caught — the load-bearing history

**The panel's three lenses were genuinely disjoint.** 52 findings with only 3
same-defect duplicates across three lenses split by concern (adversarial /
mechanism / conventions). The split is worth repeating.

**Two external rounds each faulted a prior round's resolution, which is what
external review is for.** `ext1-3` faulted `risk-17`'s `--config` passthrough
resolution; `ext1-4` faulted `risk-16`'s `--touch` fix; `ext2-1` faulted
`ext1-1`'s own resolution.

**The probe killed a mechanism that prose review had passed twice.** v2 proposed
a bare `snakemake --touch` shortcut for the post-migration cascade; `ext1-4`
faulted it and v3 replaced it with a four-step records-first sequence whose final
step claimed a dry-run "must schedule nothing". A five-minute experiment refuted
it: `--touch` succeeds (32/32 jobs) but the very next dry-run still schedules 28,
because `--touch` cannot touch a file that does not exist and the four rules it
names are exactly the `temp()`-wrapped ones (`run_stress_test.smk:736, 931, 975,
1021/1029`). Reaped `temp()` is the normal end state of every completed WF3 run —
`run_stress_test.smk:556-560` already said so in-tree. Recorded as premises
N19–N20. **A mechanism asserting an absence gets an experiment, not a paragraph.**

**The revision then found the better argument the probe had not reached:** the
residual reaped chain *contains the dominant cost*, since `run_wflow_batch_*`
consumes the downscale and perturb outputs. No shortcut could ever have saved the
Wflow cascade. The sequence was withdrawn outright rather than repaired.

**One finding was reached independently from two directions.** The driver flagged
`ext1-1`'s third part as an unratified `deferred` on a `major` finding (the ledger
permits deferral only for `minor`) *before* round 2 ran; `ext2-1` then reached the
same defect from the design's own text. That convergence is why R13's scope was
widened rather than the exception being carried forward.

**"Verify rather than assert" corrected a ruling's premise.** The `ext2-5` work was
instructed to check `--config` parsing against the pinned toolchain. Snakemake
9.6.2 rejects a dotted `--config` key at `cli.py:312` before any configfile is
read, identically pre- and post-split — so the dotted workflow-setting form was
never accepted syntax, and S8's withdrawal bites only on the mapping-valued form.
Confirmed independently by the driver. The ruling stands; its blast radius was
smaller than the finding it answered had claimed.

## Owner rulings

**G1, 2026-08-20 — framing.** Path-referenced composition (T1 closed
`{enabled, config_path}` stanzas + per-workflow T2 files, loader-composed,
in-memory shape unchanged); naming Candidate A (keep current names, provisional);
clean break, no dual-mode loader, report-only migration script.

**S7, 2026-08-20 — staging-emit.** `split_project_config.py` is strictly
report-only against user files: it emits proposed T1+T2 into a staging directory
plus a report, and application is a user step. No `--write`.

**S8, 2026-08-21 — narrow G4.** G4 claims only the `--configfile` path contract,
the wrapper invocation and `config_path` forwarding; ad-hoc workflow-setting
overrides are withdrawn. The alternative — routing them into the composed T2 —
was declined, because a second write path into workflow settings is the hole
D-9.1 exists to close.

**Round-cap arbitration, 2026-08-21.** Two external rounds is the full-variant
cap, so the six surviving findings went to the owner rather than a third review.
All ruled as recommended: `ext2-1` **widened R13's scope** to require the
`wflow_outvars` hoist (neutrality-first ordering, so the digest shift is expected
and attributable — the `arch-11`/D-13.4 objection dissolved by sequencing, not
overruled); `ext2-2`/`ext2-4`/`ext2-5` accepted; `ext2-6` restricted D-9.3 to
declared identities, partially withdrawing `risk-3`. `ext2-3`'s second half was
*dissolved* rather than declined — an empty-registry requirement makes the gaming
path unconstructable.

**G2, 2026-08-21 — approval.** All five owner-visible items confirmed as
recommended; `design-v5.md` accepted with no editorial edits.

## Consequences the owner accepted at G2

- **R13 carries two baseline-scale validation passes** — the §16.5 ordering plus
  `test-full` plus the falsifier plus a re-record, once for the split and once for
  the hoist. The price of discharging S4 in-milestone.
- **Migration completes at the dry-run**; the first post-migration *execution* of
  a project with a completed experiment re-runs the stress test to produce
  identical results, and no shortcut mechanism exists. N20 bounds it: most of that
  cost pre-exists migration.
- **D-9.7 and D-15.3a carry no reviewer verdict.** Both were minted after the
  external cap, under arbitration authority. This is the documented consequence of
  the cap, recorded rather than papered over.

## Process notes

`observations.md` in the run dir carries the process-friction log feeding skill
improvement — including two driver finding-ID misattributions (a phantom
`risk-19`, and `risk-18` written where `risk-17` was meant), a parallel-spawn
scratch-file collision, a session-limit crash that lost 52 batched ledger rows,
and a stale resume block that named a worktree the run dir had never been in.
