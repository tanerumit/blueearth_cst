# Internal review — aggregation index

Round: internal panel (stage 2), reviewing `design-v1.md`. Written by the
driver. This index GROUPS; it decides nothing. The three per-lens files are
authoritative for every finding's text, severity, and rationale — where this
index's tag and a lens file disagree, the lens file wins.

| Lens | File | Verdict | blocking / major / minor |
|---|---|---|---|
| risk & assumptions | `internal-review-risk.md` | revise | 1 / 8 / 9 |
| architecture & consistency | `internal-review-architecture.md` | revise | 0 / 15 / 6 |
| repo fit & conventions | `internal-review-repo-fit.md` | revise | 4 / 4 / 5 |

Totals: 52 findings — 5 blocking, 27 major, 20 minor.

## Groups (by concern; tags are the driver's shorthand)

**A. Gates and test surfaces the design breaks or cannot see** —
`repofit-1` (B: clean break bricks `tests/snake_config_fixture.yml`, the
design's own `test_cli` gate; 23 referencing modules), `repofit-3` (B: T2 seed
names collide with `test_prepare_cst_parameters.py` discovery glob),
`repofit-12` (B: `test_copy_config_files.py` asserts byte-verbatim snapshots —
the invariant D-11.1 abolishes), `repofit-6`, `repofit-7`, `arch-19`
(`tests/conftest.py:138-145` breaks inside the skip-not-fail fixture layer),
`arch-20` (`test_snapshot_config_rules.py` asserts Snakefile source text the
design moves), `arch-21` (`semantic_tree_diff.compare_copied_config` deep-equal
fails on composed snapshots, no expected-result line), `risk-8` (stale-spelling
sweep blind to dict-literal config shapes: 23 occurrences, 9 test modules),
`repofit-13` (m), `arch-15` (m).

**B. Unlisted consumers of the raw T1** — `risk-1` (B:
`snapshot_project_tree.py` / the pinned `tree-check` gate, silently masked by
fallback defaults; `prune_series_cache.py` KeyError; `plot_workflow_dag.py`
drops experiment id), `arch-2` (same two tools, graded major), `arch-3`
(third config read in `suggest_experiment_name.py:283-294` — pinned-name
refusal never fires), `repofit-4` (its `_plan_edit` appends a bogus nested
block at EOF and the verifier masks it), `risk-11` (m).

**C. Identity and provenance mechanisms under the split** — `arch-4` /
`risk-2` (same concern: `configuration_inputs_sha256` computed on two paths,
T2 registered on only one — arch-4's premise self-flagged as argued-not-run),
`arch-11` (advanced-settings move lands inside the digested document,
falsifying §10.2 "unchanged by construction"), `arch-12` (composition must
REBIND the Snakefile-global `config`; `check_project_consistency.py:225` reads
`sm.config`), `arch-17` (m), `risk-9` (m), `risk-14` (m: four snapshots move,
not three), `repofit-10` (m).

**D. Rule-retrigger semantics and the migration re-run cost** — `arch-7` /
`risk-7` (same defect: §10.3's rerun rationale is false for rule 3.09 —
`ancient()` input is not a trigger; the real trigger is D-10.6's param),
`risk-16` (migration's rewritten T1 bytes cascade into a full silent WF3
re-run to identical results — unbudgeted), `risk-15` (m).

**E. Loader/composition underspecification** — `arch-1` (no channel from
composition to the `CONFIG_PROJECTION` literals; ordering vs `:41`), `arch-5`
(closure scope undefined: all four stanzas vs `R(entry)` — one reading
legalizes half-split configs), `arch-6` (T1 top level never closed; leftover
top-level `reporting:` has undefined precedence), `arch-8` (WF2's T2 becomes
hard-required for every WF3 run, against the overlay-never-required
invariant), `risk-3` (D-9.3 unreachable for wf0/wf1/wf2), `risk-4`
(`reporting` absent from `REJECTED_IN_T2`), `risk-5` (shared-T2-across-T1s vs
in-place mutation by `suggest_experiment_name.py`), `risk-17` (m), `risk-18`
(m: Snakemake `--config` passthrough unexamined), `arch-13` (m), `repofit-9`
(m: loader into 4658-line `snake_utils.py` vs a topic module).

**F. Paths, locations, filenames** — `repofit-2` (B: splitter's
T2-beside-T1 advice contradicts §8.4 CWD-relative resolution for production
projects), `arch-9` (recommended real-project T2 location sits in the
run-written, inventory-enumerated bin → fails `tree-check`), `repofit-5`
(§7.1's canonical example cites the retired `config/workflows/` bin),
`risk-19`-class path-normalization note (see risk file), `repofit-8` (m),
`repofit-11` (m: Q1 call — keep `config_path`).

**G. Snapshot machinery details** — `arch-10` (record-only registration not
implementable against `_snapshot_references` as claimed), `risk-10` (m),
`risk-12` (m).

**H. Migration splitter robustness** — `risk-6` (no story for YAML
anchors/aliases/merge keys/block scalars; round-trip gate covers only
implementer-controlled files, not the user's), `arch-16` (m: `reporting:`
exists in no shipped config, so the hoist/splitter branch ships ungated),
`risk-13` (m).

**I. Editorial** — `arch-14` (m), `arch-18` (m).

## Conflicts (required section — both readings kept, driver resolves nothing)

1. **Factual contradiction — does the `tree-check` gate survive?** Repo-fit's
   appendix CLEARED the pixi surfaces: "`tree-check` … read no path the design
   moves" (checked and declined to raise). Risk-1 (blocking) asserts the
   opposite mechanism: `snapshot_project_tree.py` consumes raw-T1 keys and
   breaks *silently* because the baseline seed's values coincide with the
   tool's fallback defaults. These are answering different questions (path
   moved vs shape read) but land on opposite conclusions about the same gate.
   Cheap empirical test: read `snapshot_project_tree.py`'s config-key reads
   and run `pixi run tree-check` against a hand-split baseline config.
2. **Severity divergence — unlisted consumers**: the same two tools
   (`prune_series_cache.py`, `plot_workflow_dag.py`) are `risk-1` (blocking,
   bundled with the tree-check claim) and `arch-2` (major). Each ID is
   dispositioned at its own filed severity; no harmonization.
3. **Factual tension — "exactly three baseline targets move"**: repo-fit
   verified §16's seven-target enumeration and called the three-config
   prediction demonstrated; `risk-14` (minor) counts FOUR in-project config
   snapshots (wf0's uncounted). Cheap test: enumerate `config/runs/
   snake_config_*.yml` writers per workflow and compare against
   `dev/baseline/manifest.json` targets.
4. **Same-defect duplicates (grouped, no conflict):** `arch-7`≡`risk-7`;
   `arch-4`≈`risk-2`; `arch-2`⊂`risk-1`. Ledger rows stay per original ID.

## Driver's gate-return check (stage-contracts § Gate return from the panel)

Checked each blocking/major finding for resolutions that would widen or narrow
scope, constraints, or the selected alternative. None found: the risk lens
states explicitly that every finding is fixable inside the G1 framing, and the
candidates the driver examined (`arch-8` — required-vs-optional WF2 T2 is a
contract detail inside the composition mechanism; `risk-16` — accept-and-
document vs engineer-avoidance is a cost choice, surfaced to the owner at G2
either way) do not fork the milestone. No G1 return; revision dispatched.
