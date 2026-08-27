Master Brief — R14 config shape implementation

### Goal

Implement `dev/milestones/r14/config-shape-design.md` (DRAFT **v3**, 2026-08-24,
revised against external round 1):
reshape the project config within R13's tier split — sections by KIND, one
naming policy, `schema_version: 2`, a register-driven v1→v2 rewriter, and the
`snake_config_` → `project_config_` file rename — landing as ONE user-visible
migration. Success is G6: no number moves, except at the two rows ruled
otherwise, each carrying its invariant.

Canonical ruleset: `AGENTS.md`. Argument by `C-nn`:
`config-shape-scoping.md`. Contract and evidence `E1`–`E10`:
`config-shape-intake.md`.

### Subsystem map

| Phase | Owner | Input | Expected output |
|---|---|---|---|
| P0 | `general-purpose` (runs from the PRIMARY, not a lane) | `t2608220920`, `dev/baseline/manifest.json` | The baseline's provenance resolved AND the four data targets' hashes recorded into a tracked file. **Blocks every other phase.** |
| P1 | `python-engineer` | design §10 | Loader, seam re-derivation and parse-time refusals against the new layout; `HOISTED_SECTIONS` retired |
| **P1b** | `python-engineer` | design §7.2–§7.5, P1 | **The per-workflow (T2) key readers.** Added 2026-08-25 by owner ruling — no phase owned them, and without them no entry point runs v2 |
| **P1c** | `python-engineer` | design §7.3, §5.5, P1b | **The per-variable registry.** `C-57`'s short form is "registry-resolved" and `C-64` puts `min_reference` in the same place — but no registry exists, so `C-66` cannot dissolve `relative_change:` either. Added 2026-08-26 by owner ruling |
| P2 | `python-engineer` | design §9, P1 | Guard derived from the snapshot; `compute:` excluded from `CONFIG_PROJECTION` |
| P3 | `python-engineer` | design §11, register | The v1→v2 rewriter, register-driven, with the two non-preserving hooks |
| P4 | `python-engineer` | design §7, §13, P3 | Templates (5, incl. the new WF0 one), four `test_case/` sets, fixture, `presplit/` v1→v2 pair — migrated BY the rewriter |
| P5 | `python-engineer` | design §12 | `C-85`: file rename + derived identifiers + the `.gitignore` glob, atomically |
| P6 | `technical-writer` | design, P1–P5 | Migration note, `docs/guide/*.qmd`, `README.md`, `AGENTS.md`, and the `C-75` technical-note sweep |
| P7 | `python-engineer` | — | `C-35` and `C-83`, independently landable at any time |

### Sequencing

- **P0 BLOCKS EVERY OTHER PHASE.** *(Revised 2026-08-24 after external round 1,
  finding `ext1-3`.)* v1 of this brief let P1–P5 run concurrently with P0 and
  blocked only the G6 claim. That was wrong for a repo-specific reason: the
  baseline fixture is **untracked, so within any one worktree it survives branch
  switches and reflects whatever last ran there.** The moment a phase migrates a
  `test_case/` config and a WF3 run touches it, that worktree's pre-change state
  is gone and cannot be recovered from git — it was never in git. No
  implementation commit lands until P0 has recorded the four data targets'
  hashes and provenance into a TRACKED file (design D-14.3).
  *(Corrected 2026-08-25: an earlier wording said "shared between worktrees".
  It is not — each worktree holds its own copy, verified by distinct inodes. The
  hazard is per-worktree and the conclusion is unchanged.)*
- **P1 → P2.** The guard reads the composed document; the composition must be
  correct before the guard is re-pointed at it.
- **P1 → P1b → P2, and P1b → P4.** *(Added 2026-08-25; see the revision line.)*
  P1 moved the T1 reads only. The T2 key renames (`C-22`, `C-25`, `C-29`,
  `C-31`, `C-32`, `C-33`, `C-34`, `C-56`, `C-57`, `C-59`, `C-60`, `C-63`,
  `C-66`, `C-67`, `C-68`, `C-69`) plus `C-54`'s destination were owned by no
  phase. Both orderings are forced rather than preferred:
  **P1b before P2**, because P2's three rung-2 falsifiers each say *"build a
  model … run WF3"* and WF3 can run against nothing until the T2 readers move —
  a v1 config hits P1's `schema_version` refusal, a v2 config hits
  `KeyError: 'stress_test'`;
  **P1b before P4**, because P4's rung 1 (*"dry-runs all four entry points
  against every migrated set"*) proves nothing while the readers still want v1
  keys. That second constraint is what ruled out widening P4 to absorb them.
  P1b needs no rewriter — the readers are code written against design §7 — so
  it may run concurrently with P3.
- **P3 → P4.** The `test_case/` sets are migrated BY the rewriter, which makes
  P4 the rewriter's first real test rather than a parallel hand-edit.
- **P5 after P4**, and **P5 is one atomic commit** (see its brief). Renaming
  the files before their contents are migrated means two breaking passes over
  the same 76 files.
- **P6 last**, because it documents what the others landed.
- **P7 is concurrent with everything** and touches disjoint paths: `C-35` is a
  de-duplication in two modules, `C-83` a contraction sweep that touches no
  config key.

P1c and P3 may run concurrently — disjoint paths, no shared file. (This read
"P1 and P3", then "P1b and P3"; each successor inherits the property for the
same reason — they touch readers and a registry, P3 adds a script.)

**P1c does NOT block P2 or P4**, which is what separates it from P1b. P1b's
position was forced because WF3 could not RUN without it; P1c's three rows are
reachable-but-unmigrated config surface, so every entry point already dry-runs
clean on v2 without them. It must land before Gate 5, not before P2.

> [!warning] **`P1b → P2` is necessary and NOT sufficient — open, needs a
> ruling.** *(Found 2026-08-27 at the end of P1b.)* The `P1b before P2` clause
> above names two refusals and P1b removes only one of them. The
> `schema_version` refusal is cleared by **P4**, not P1b, so P2's rung-2
> falsifiers — all three of which say "build a model … run WF3" — still have no
> config they can run against. Verified: no `test_case/*.yml` carries
> `schema_version`, and the v2 probe fixture has no built model.
> **Do not start P2 until this is ruled.** The options and a recommendation
> (reorder to `P3 → Gate 3 → P4 → P2`) are in
> `config-shape-p2-sequencing-decision.md`. P3 is unaffected and may start now.

### Shared constraints

- **K1 (AGENTS.md hard constraint).** No key inside `config/defaults/*` or a
  data catalog is renamed, moved or removed. This already withdrew one row
  (`C-82`, `E3`). If a phase finds itself editing `config/defaults/`, stop.
- **K2.** `HOISTED_SECTIONS` retirement amends accepted R13 decision D-10.4.
  Record it as an amendment; do not edit it quietly.
- **K3.** The digest moves ONCE. Commits may stage, but nothing merges to
  `main` until the whole bundle is green together.
- **K5.** `get_config` contract preserved: raise on missing required, return
  the default for optional.
- **K6.** `workflow.configfiles[0]` forwarded as `config_path` to downstream
  **Python** scripts.
- **`dev/milestones/**` is never swept** by any rename. These are milestone
  records and their value is that they are unedited: freshening paths in one
  makes a stale document read as current while its line numbers and module
  paths still lie. *(Corrected 2026-08-25: they are NOT "frozen by
  `tests/test_sealed_records.py`" — `dev/reference/sealed-records.yml` is the
  entire list of sealed documents and no R14 file is in it. The no-sweep rule
  is a convention, enforced by review; only a REGISTERED record is enforced by
  a test. AGENTS.md says to read the registry rather than guess, and this
  clause was the guess.)* Amending a brief's own text — as the revision line
  below does — is a different act from sweeping it, and its revision clause
  invites it.
- No new dependencies without owner approval.

### Human gates

1. **Gate 1 — RELEASED 2026-08-24.** The design's two new decisions are ruled:
   `C-48` withdrawn (D-7.10) and `C-85` at full breadth (D-12.1). Kept in the
   list because P5's scope derives from the second.
2. **Gate 2 — RELEASED 2026-08-25.** P0 confirmed the baseline needs no
   re-record, so the second branch of this gate never fired and every later
   comparison stands against the manifest as it was. `t2608220920` is closed on
   commit-level evidence: `b4c58d8b` re-recorded 624 of the indicator table's
   630 rows on 2026-08-22, 33 minutes after `da9fa7fc` boarded the note — the
   premise was true as written and was fixed by the commit that boarded it.
   The green is not a fixture artefact: the run-path diff from the recording
   commit `0d256a41` to HEAD is EMPTY, so nothing capable of moving a number
   changed. The tracked hash record is `dev/baseline/provenance.md`.
   **Read it before trusting a 7/7:** the manifest hashes only the two CMIP6
   CSVs, while `q_indicators.csv` and `run_default/output.csv` are compared
   against tolerance reference tables and carry no sha256 anywhere — so a
   sub-tolerance move passes the gate and still changes the file. Byte-level
   claims go against that record, not against `check_baseline` alone.
3. **Gate 3 — after P3, before P4.** Show the rewriter's output for ONE
   `test_case/` set as a diff, and the refusal message for a
   `water_year_start: Oct` fixture. PAUSE for approval before migrating the
   other three.
4. **Gate 4 — before P5's commit.** `C-85` is the atomic move. Show
   `git ls-files test_case/` output proving the seeds are still tracked, BEFORE
   committing.
5. **Gate 5 — before merge.** Full validation ladder green, and the four data
   baseline targets unchanged.

Rollback: any phase may be reverted independently except P5, which reverts as
one commit. If the four data targets move and the cause is not one of the two
ruled exceptions, revert to the last green commit and report — do not
re-record the baseline to make the gate pass.

### Cross-cutting validation

Per-phase rungs live in the phase briefs. These make sense only across phases:

- **`pixi run test-full`** — required, not optional: R14 touches `shared/` and
  `script:` signatures, which is the `workflow_contract` / `process_isolation`
  tier's own trigger. Run at Gate 5, and once after P2.
- **`check_baseline.py check`** — the four DATA targets only
  (`cmip6_change_factors_annual.csv`, `_monthly.csv`, `q_indicators.csv`,
  `run_default/output.csv`). The three `snake_config_*.yml` snapshot targets
  WILL move and are re-recorded, not defended (design D-14.1). **Run WF1 with
  `--notemp`** or the gate fails "target missing" and reads as a defect.
- **`semantic_tree_diff.py`** — `C-67`/`C-71` change `params:`-threaded values
  and `C-61` renames WF2 figure directories, so the tree shape moves. Expected;
  capture it rather than being surprised by it.
- **Stale-spelling sweep** — no tool exists; P3 ships one. It **classifies**
  rather than simply greps: active config, code identifiers, command lines and
  live docs must carry ZERO retired spellings, while the migration mapping, the
  `presplit/` v1 fixtures, the migration note's tables, the loader's refusal
  literals and the rewriter's tests are allowlisted and must each carry a
  declared reason. It **fails closed** on an unknown classification (design
  D-14.4, finding `ext1-2`) — "fail on any hit" was unsatisfiable by a correct
  implementation. `C-37` is its mechanical successor, under the same rule.
- **Resolved-config equivalence across all four shipped sets** (design §14.3,
  finding `ext1-6`) — `check_baseline` records from `snake_config_baseline`
  alone, so without this `rapid`, `baseline_linux` and `wf2_fast` have no
  numerical check at all.
- **The frozen-experiment invariant** (design §11.6, D-14.8) — migrate a
  project with a completed experiment, re-run WF3 untouched, assert
  `_frozen_differences` is EMPTY. This is the falsifier for "the digest break
  is paid once".
- **Every commit on the branch imports cleanly** — `pytest tests/test_cli.py`
  per commit; it is the only place a malformed `config/defaults/*.yml`
  surfaces.

Frequency: `test_cli` and `lint`/`format-check` per commit. `test-fast` per
phase. `test-full`, `check_baseline`, `semantic_tree_diff` at Gate 5 and after
P2 only — they dominate the cost, so batch the SCHEDULE, never merge commits to
save gate cost.

### Phase brief index

| Phase | Brief | State |
|---|---|---|
| P0 | `config-shape-p0-baseline-provenance.task.md` | **LANDED 2026-08-25** (`3d3d29fe`, merged `f814c16b`) |
| P1 | `config-shape-p1-loader.task.md` | **DONE** 2026-08-25 (T1 reads only; see P1b) |
| P1b | `config-shape-p1b-readers.task.md` | **DONE** 2026-08-26 (readers for all three workflows + `C-54`; `C-57`/`C-64`/`C-66` deferred to P1c) |
| **P1c** | `config-shape-p1c-registry.task.md` | not started — **the variable registry**, added 2026-08-26 by owner ruling |
| P2 | `config-shape-p2-identity.task.md` | not started |
| P3 | `config-shape-p3-rewriter.task.md` | not started |
| P4 | `config-shape-p4-configs.task.md` | not started |
| P5 | `config-shape-p5-rename.task.md` | not started |
| P6 | `config-shape-p6-docs.task.md` | not started |
| P7 | `config-shape-p7-independent.task.md` | not started |

---

*Revision: v3, 2026-08-25 — **P1b added** by owner ruling on P1's finding that
the T2 key renames (~280 sites, 32 files, 16 register rows) and `C-54`'s
`advanced_settings` destination were owned by no phase, which made the bundle
unassemblable rather than merely incomplete. Its position is forced by P2's and
P4's own validation, not chosen. P1 is DONE and delivered the T1 reads only;
its declared-red set is tracked in `tests/data/r14_expected_red.txt`, and the
measurement behind P1b is board item `t2608251900`. One correction of record
from the same finding: `dev/milestones/**` is NOT sealed —
`dev/reference/sealed-records.yml` is the entire list and R14 is not in it, so
this file is amended here as its own revision clause instructs, not frozen.*

*Revision: v2, 2026-08-24 — re-sequenced after external round 1 (`ext1-3`):
P0 promoted from concurrent to a blocking pre-implementation gate. P3 gains the
normative mapping (`ext1-1`), the transactional contract (`ext1-4`) and the
experiment-record migration (`ext1-5`); P4 gains the equivalence suite
(`ext1-6`). Treat as settled once phase work starts; record deviations in the
affected phase brief's `Progress`, or reissue with a dated revision line.*


*Revision: v4, 2026-08-26 — **P1b LANDED** (four commits on
`feat/r14-p1-loader`), and **P1c added** by owner ruling. All four entry points
dry-run clean on a v2 config, which is the acceptance criterion P1 could meet
for only two of them, and `V2_BLOCKED` is retired. `C-54`'s coupled
`advanced_settings` edit landed with it, so `RETIRED_KEYS` no longer names a
destination that does not exist. The declared-red list shrank for the first
time, from 83 to 73, and what remains is only what P4 owes.

P1c exists because three rows turned out to need a per-variable REGISTRY that
no phase built: `C-57`'s short form is registry-resolved, `C-64` moves
`min_reference` into the same place, and `C-66` cannot dissolve
`relative_change:` without it — doing so would turn a configurable threshold
into an unfixable `ThresholdError` for any relative variable outside the
shipped defaults. `C-65`'s half also needs `config/advanced_settings.yml`,
which P1b's scope permitted for `C-54` only.

Six register defects were found by re-measuring, as P1b's brief instructed.
The load-bearing ones: `C-71` was already migrated by P1 and is not a P1b row;
`C-63` has three read sites, not the one the brief names; `C-57`'s "one read
site" is true of the read and not of the work behind it; and `C-66`'s refusal
names `min_denominator` where the code reads `min_reference`. That last one is
still unresolved and is P1c's to settle.*