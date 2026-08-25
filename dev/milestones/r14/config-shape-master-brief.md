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
- **P3 → P4.** The `test_case/` sets are migrated BY the rewriter, which makes
  P4 the rewriter's first real test rather than a parallel hand-edit.
- **P5 after P4**, and **P5 is one atomic commit** (see its brief). Renaming
  the files before their contents are migrated means two breaking passes over
  the same 76 files.
- **P6 last**, because it documents what the others landed.
- **P7 is concurrent with everything** and touches disjoint paths: `C-35` is a
  de-duplication in two modules, `C-83` a contraction sweep that touches no
  config key.

P1 and P3 may run concurrently — disjoint paths, no shared file.

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
- **`dev/milestones/**` is never swept** by any rename — sealed records,
  frozen by `tests/test_sealed_records.py`.
- No new dependencies without owner approval.

### Human gates

1. **Gate 1 — RELEASED 2026-08-24.** The design's two new decisions are ruled:
   `C-48` withdrawn (D-7.10) and `C-85` at full breadth (D-12.1). Kept in the
   list because P5's scope derives from the second.
2. **Gate 2 — after P0, and it releases the PROGRAM.** Report which outcome
   held and show the tracked hash record. **No implementation commit lands
   before this gate** (design D-14.3, finding `ext1-3`). If the indicator
   reference needed re-recording, the baseline changed underneath the milestone
   and every later comparison is against the new record.
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
| P0 | `config-shape-p0-baseline-provenance.task.md` | not started |
| P1 | `config-shape-p1-loader.task.md` | not started |
| P2 | `config-shape-p2-identity.task.md` | not started |
| P3 | `config-shape-p3-rewriter.task.md` | not started |
| P4 | `config-shape-p4-configs.task.md` | not started |
| P5 | `config-shape-p5-rename.task.md` | not started |
| P6 | `config-shape-p6-docs.task.md` | not started |
| P7 | `config-shape-p7-independent.task.md` | not started |

---

*Revision: v2, 2026-08-24 — re-sequenced after external round 1 (`ext1-3`):
P0 promoted from concurrent to a blocking pre-implementation gate. P3 gains the
normative mapping (`ext1-1`), the transactional contract (`ext1-4`) and the
experiment-record migration (`ext1-5`); P4 gains the equivalence suite
(`ext1-6`). Treat as settled once phase work starts; record deviations in the
affected phase brief's `Progress`, or reissue with a dated revision line.*
