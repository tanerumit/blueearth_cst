# Scoped verification — stage 6a delta (ext2-1..ext2-7)

```yaml
verdict: pass
doc_version: design-v4.md
scope: 6a-delta (ext2-1..ext2-7)
findings:
  - id: sv-1
    severity: minor
    arbitrated_id: ext2-7
    section: "§13 Step 8 — Performance floor confirmation (repetition and counterbalancing bullet)"
    finding: >-
      The predeclared protocol is ">= 3 AB/BA pairs ... alternating strictly"
      starting batch-first, and explicitly permits an odd count ("odd or even
      count, alternation kept"). At the declared minimum of 3 pairs the leg
      order is B,P | P,B | B,P — the pool leg runs second in 2 of 3 pairs and
      the batch leg in 1 of 3. The adjacent sentence claims "Counterbalancing is
      what removes the systematic filesystem/OS-cache warming advantage the
      second leg of any pair inherits."
    rationale: >-
      With an odd pair count the warming advantage is reduced, not removed, and
      the residual is biased toward the second-position leg — which at the
      declared minimum is the pool, i.e. biased toward passing G7 and retaining
      the architecture. That is a weakened form of the exact gameability ext2-7
      raised. The arbitrated ruling (>=3 pairs, all spans + dispersion, median
      gate) is satisfied literally, so this is not a ruling failure; the doc's
      claim of removal is what overstates.
    suggested_fix: >-
      Require an even number of pairs (>= 4), or state the rule as "equal counts
      of pool-first and batch-first legs, minimum 3 pairs", and downgrade the
      claim to "balances" rather than "removes".

  - id: sv-2
    severity: minor
    arbitrated_id: ext2-2
    section: "§5.2 Ledger schema — identity fields / finalization"
    finding: >-
      After the split, the reduce's completeness identity check compares
      sweep_completeness.csv's `invocation_id` against ledger_final.csv's
      uniform `finalization_invocation_id`. Both are written by the same runner
      in the one normative finalization sequence, so the two values are equal by
      construction on every in-contract path. No gate and no C-24 falsifier
      injects a mismatched completeness record.
    rationale: >-
      The check's remaining discriminating power (a completeness record that does
      not describe the surface published beside it — a restored/stale
      ledger_final.csv, a record copied between experiments) is entirely
      unexercised. GF-2 and GF-13 exercise only the pass side; C-24's falsifiers
      are all false-failure shapes. An implementation that satisfies the check
      trivially (comparing a value to itself, or dropping it) would pass every
      declared gate, silently removing the guarantee §5.2 states the field pair
      exists to provide.
    suggested_fix: >-
      Add one sub-case to GF-3 or GF-22 (hand-edit sweep_completeness.csv's
      invocation_id, --forcerun the reduce, expect the named hard-fail), or add
      the false-pass shape to C-24's falsifier list.

  - id: sv-3
    severity: minor
    arbitrated_id: ext2-4
    section: "§5.3 corrupt-ledger recovery, step 4 — vs §7.4 (unchanged)"
    finding: >-
      Recovery step 4 newly moves every current manifest-owned member output
      into the quarantine generation, then step 5 starts a fresh ledger. §7.4's
      unchanged sentence states "A ledger `quarantined` row records what moved
      and why."
    rationale: >-
      The corrupt-ledger recovery is now the one quarantine path that moves
      member products with no `quarantined` row anywhere — the ledger it would
      be written to is the one being retired, and the fresh ledger starts empty.
      §7.4's invariant therefore has an unstated exception introduced by the
      v4 inventory. Observable consequence: after GF-22, `sweep_status.py` and
      the fold have no record that 12 member products were quarantined; only the
      directory itself testifies.
    suggested_fix: >-
      One clause in §5.3 step 5 or §7.4: the recovery is the sole quarantine
      without a `quarantined` row, because the record it would be appended to is
      the corrupt one; the generation directory is self-describing.

  - id: sv-4
    severity: minor
    arbitrated_id: ext2-4
    section: "§5.3 corrupt-ledger recovery preamble vs §7.3 step 1"
    finding: >-
      §5.3 declares the recovery "executed by the runner before any other action
      of that invocation", while its own step 1 names the quarantine directory
      with "the *adopted* workflow invocation id" — which §7.3 step 1 obtains as
      the runner's "first action" (read the lock, adopt its id, or raise
      ExperimentLockMissingError).
    rationale: >-
      Two normative "first action" statements introduced in the same revision.
      Read literally, §5.3 has the runner create
      `_state/quarantine/<invocation_id>/` before it has an invocation id.
      An implementer must silently reorder to make either statement true.
    suggested_fix: >-
      Restate as "before any other action except §7.3 step 1 (lock read and id
      adoption), which it depends on".

  - id: sv-5
    severity: minor
    arbitrated_id: ext2-6
    section: "§4.2 Stage 2 — checked publication (`publish_file`)"
    finding: >-
      The mechanism choice rests on a platform premise stated as fact — "on
      Windows `file.rename` onto an existing destination fails" — which is
      unprobed (PR-1..PR-7 do not cover it; convergence-r2 graded ext2-6's
      premise "confirmed-plausible", not confirmed). It is load-bearing: it is
      why the design adds a preceding `file.remove` and accepts a
      non-atomic two-step publish over a bare checked `file.rename`.
    rationale: >-
      If R's `file.rename` already replaces an existing destination on Windows,
      the delta introduces a window in which the published sidecar is absent and
      an extra failure point, in exchange for nothing — and the reviewer's
      preferred "temporary publication followed by replacement" was declined on
      that premise. GF-24(a) passes under either platform behaviour, so no
      declared observation discriminates. The confidence-evidence gap, not the
      mechanism, is the defect: the arbitrated ruling is satisfied either way.
    suggested_fix: >-
      Either add a two-line probe at §13 step 2 (rename onto an existing file in
      R on Windows, record the return value), or restate the remove step as
      defensive-regardless and drop the factual assertion.

  - id: sv-6
    severity: minor
    arbitrated_id: ext2-6
    section: "§8.2 GF-24 sub-case (b)"
    finding: >-
      Sub-case (b) specifies only "`sim_dates_rlz_1.csv` held open by a second
      process during the publish". On Windows, whether an open handle blocks
      `file.remove` depends on the share mode the holder requested; a naive
      holder (e.g. `Get-Content -Wait`) does not necessarily block deletion.
    rationale: >-
      Unlike GF-1/GF-2/GF-12, which name the exact injection command and (for
      GF-2) explain why the obvious command would not produce the intended
      state, GF-24(b) leaves the injection to the implementer. If the holder
      does not block deletion, the publish succeeds and the gate's expected loud
      failure never occurs — the gate fails spuriously rather than proving the
      loud-failure half of C-27. Fail-safe in direction, but it makes the only
      gate for that half unreliable as written.
    suggested_fix: >-
      Name the holder explicitly, e.g.
      `[System.IO.File]::Open($p,'Open','Read','None')` in a second PowerShell,
      matching GF-2's precedent of pinning the injection command.

  - id: sv-7
    severity: minor
    arbitrated_id: ext2-1
    section: "§5.1 Manifest schema — field notes (baseline members)"
    finding: >-
      The new baseline-member note fixes `st_csv: null` and
      `precip_variance: null` but is silent on where a baseline member's `tavg`
      and `prcp` come from, while the very next bullet derives them "exactly as
      the reduction derives them today (`export_wflow_results.py:196-198`)" —
      a line range that is only the perturbed branch. The reduce's actual
      baseline branch is `:192-194` (`if st_nb == "0": tavg = 0; prcp = 0`).
    rationale: >-
      Baseline members are newly declared first-class manifest members and
      `tavg`/`prcp` are terms of `member_hash`, so the value choice is
      hash-affecting and must be specified, not inferred. The §5.1 example does
      encode 0.0/0.0 (matching the repo), but the example is illustrative while
      the derivation bullet is the normative sentence, and it cites only the
      branch that cannot apply. GF-21 observes no `tavg`/`prcp` value, so a
      divergent choice (NaN, or cst_1's scalars) is unobserved by the gate.
    suggested_fix: >-
      Extend the citation to `:192-198` and add "baseline members take
      `tavg = 0.0`, `prcp = 0.0` (the reduce's own `cst_0` branch)" to the new
      bullet.
```

## Ruling-satisfaction record (per arbitrated finding)

| ID | Ruling satisfied | New contradiction | Falsifiers / gates executable |
|---|---|---|---|
| ext2-1 | **yes** — baseline branch normative in §6.6; excluded from every deletion surface checked: member steps (§6.6), fold RUN-set cleanup (§7.3 step 8), quarantine inventory (§5.3 step 4), `retain_member_artifacts` (§6.6), plus §5.1 field note, §5.2 `inputs`/`seconds`, §5.5 condition 5 defined-absent, §4.4 asymmetry reconciled. Repo premises verified: `ST_START = 0 if run_historical` (`Snakefile_climate_experiment:55-56`), 3.07's `st_num=r"[1-9][0-9]*"` at `:403-404`, 3.09's unconstrained `st_num` pass-through, and `export_wflow_results.py:161-162` emitting no `cst_0` row under `aggr_rlz` | none found (the `p × 1` bound is unaffected: a baseline member's transient set is a subset of the perturbed one; §6.6's "declared input of rules 3.07/3.08" is correct in **v2** numbering per §4.5) | GF-21 executable: `run_historical` and `experiment_name` both exist in the tracked config as single keys; `ST_NUM = (1+1)*(2+1) = 6` (`snake_utils.stress_test_grid`), so `ST_START=0` ⇒ K = 2 × 7 = 14 as stated; C-23's falsifiers can all fail. **sv-7** is the one under-specified field |
| ext2-2 | **yes** — `onstart` mints, `run_sweep` adopts from `_state/experiment.lock` as its first action, `ExperimentLockMissingError` on absent/unparseable, never a fallback mint (§6.6, §7.3 step 1); `ledger_final.csv` splits `succeeded_invocation_id` (per-member, mixed by design) from `finalization_invocation_id` (uniform), and the identity check binds the latter only (§5.2). §10b updated. Mixed-invocation resumes now pass by construction | none — §7.2's `sweep_incomplete.json` "fresh `invocation_id` every time" still holds (the lock id is per-workflow-invocation); attempt scoping unchanged; `_state` is wholly excluded from `semantic_tree_diff`, so the renamed columns need no tooling registration | GF-2/GF-13 extended through reduction with observable mixed-vs-uniform assertions; C-24 falsifiable on the false-failure side. **sv-2** is the unexercised catch-half |
| ext2-3 | **yes** — §4.4 gains the "Full-completeness cleanup" row (`Path.unlink(missing_ok=True)` before publishing); propagated to §9.4's Reduce row and §10's HM-7+ row; GF-13's final observation asserts absence; C-17's falsifier extended | none — GF-7 (present after a partial reduce) and GF-13 (absent after the retry) are consistent; the "absent on every clean run" disposition is now enforced rather than assumed | executable and falsifiable (a surviving file is directly observable) |
| ext2-4 | **yes** — five-step explicit inventory replaces "everything else moves": quarantine root, `experiment.lock` and `members.json` preserved in place; ledger/finalization state and `_state/members/` moved; every manifest-owned member output moved under `member_products/<member_id>/`; baseline NCs excluded; fresh ledger last | **sv-3** (unstated exception to §7.4's "a `quarantined` row records what moved") and **sv-4** (two competing "first action" statements). No layout collision with §7.4's `<invocation_id>/<member_id>/` quarantine path | GF-22 executes the command to completion with per-step observations; C-25's falsifiers can fail |
| ext2-5 | **yes** — decoupling branch: §5.3's table splits schema-violation (corruption) from schema-valid out-of-manifest rows (legal history, epoch-checked within their own sub-sequence, orphan-reported only when artifacts exist); the out-of-manifest clause is removed from the illegal set; §7.4 gains "Pruning never rewrites history"; §8.1's row reference correctly re-pointed to the **final** (transition-legality) row after the table grew by one | none — §7.3 step 7's disk-based ORPHAN classification and GF-9's 6 orphan rows remain consistent | GF-23's chain is executable (GF-9's state is already a declared gate; `prune_experiment_orphans.py` is this design's own §7.4 tool); C-26 falsifiable |
| ext2-6 | **yes** — one `publish_file(src, dest)` helper with checked remove + checked rename and a named `stop()`, applied to both the two date CSVs and the pre-existing figures loop; §10's two WG-3+ rows, §2.5's r-developer brief and §13 step 2 updated. Premise verified in-repo: `generate_weather.R:62-73` is an unchecked `file.rename` loop over four PNGs, guarded by `file.exists(src)`, with the per-figure `tryCatch` claim confirmed by the in-file comment | none | GF-24(a) executable from §13 step 2. **sv-5** (unprobed platform premise) and **sv-6** (under-specified (b) injection) |
| ext2-7 | **yes** — >= 3 predeclared AB/BA pairs, per-leg dispersion reported, gate on the median, near-tie reported not silently passed; C-12, G7 (§1.2), §13 steps 4 and 8, §14.1's reinstatement trigger all restated to the median | none | executable at fixture scale. **sv-1** (odd pair count leaves a residual order bias in the pass direction) |

## Out of scope, confirmed untouched

Settled rulings were not re-litigated: risk-7 part 3, ext1-1..ext1-6 mechanisms, the G1 rulings, and the §3 architecture are unchanged in the delta (verified by `git diff --no-index design-v3.md design-v4.md`: 294 insertions / 69 deletions, all inside the sections the 6a revision declares).
