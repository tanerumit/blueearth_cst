# Internal review — REPO-FIT & CONVENTIONS lens

**Target:** `dev/working/design-runs/wf3-experiment-v2/design-v1.md` (design-v1.md, 1903 lines, read in full)
**Lens:** will this land cleanly in *this* repo, and is the specified Python/Julia/R code implementable as written?
**Method:** every factual premise verified against the tree at `file:line`; two read-only Snakemake probes run in the scratchpad (no repo mutation, no wflow / weathergenr / hydromt / pixi install).

## What holds

Most of the design's repo-facing claims check out. Spot-verified and **correct**:
`Snakefile_climate_experiment:524-546` (batch loop), `:379-391`/`:385` (3.06 + `temp()`),
`:143-163` (guarded digest), `:174-175` (`file_digest_or_absent` params pattern),
`:296-301` (`.guard_ok` has no DAG consumer), `:359-376`, `:422-423`, `:501-519`, `:546`, `:552`,
`:190-196` (label-scoped log discovery), `:14`;
`check_project_consistency.py:142-184` (the pure comparator is genuinely reusable verbatim);
`export_wflow_results.py:96,97,153,161-162,192-198` — including the `cst_0` asymmetry, which the
design reads exactly right;
`prepare_weagen_config.py:54-68` (and `build_weagen_config` is already an importable function, so the
runner-written member spec can reuse it);
`generate_weather.R:56` vs `:90` (the two `out_dir`s really are independent arguments), `:76-102`, `:117`;
`impose_climate_change.R:45-57` (3 positional args, arity-checked at `:11-14`) — the per-member R
invocation in §6.6 step 2 matches the current CLI contract exactly;
`dev/scripts/semantic_tree_diff.py:145` (`EXCLUDED_DIR_NAMES`, one-line registration as claimed);
`check_baseline.py` wf3 slice is indeed 3 targets today (`:187-189`);
`merge_benchmarks.py:55-59` recursive glob **does** absorb per-member TSVs unchanged, as §6.5 claims;
`dev/followups.md` § Post-P3-3's two items are genuinely dissolved.
`os.replace` overwrite semantics (§5.3) and `O_CREAT|O_EXCL` (§6.6) are correct on NTFS, and the design
correctly avoids claiming directory fsync (impossible on Windows).

The findings below are the places where the design's repo premises do not hold, or where required work
is unassigned.

## Findings

### repo-fit-1 (blocking) — the stale lock makes the resume gate unexecutable

§6.3 "Orphan sweep": a `_state/sweep.lock` whose recorded pid is not alive is **reported as stale and
not auto-cleared**; §8.1 F11 restates it as "the sweep refuses to start". §8.1 F5 (orchestrator
hard-killed) says recovery is "re-invoke after `--unlock`". But a hard kill leaves the lock behind by
construction — the `finally` never runs — so F5's recovery lands in F11. §8.2 **GF-2**, the gate for
G2 ("resume is measured, not asserted", the design's headline claim), specifies exactly three commands
— `SM`; `SM --unlock`; `SM` — and `snakemake --unlock` clears `.snakemake/locks/`, not `_state/sweep.lock`.
As written GF-2 cannot reach its stated observation; the third command fails on the stale lock.

**Consequence:** the milestone's central resume claim has no executable gate, and a user who is
hard-killed once is left in a state whose only documented exit is "the message names the recovery
command" — a command the design never names.

**Interaction with repo-fit-14.** As *literally* written GF-2 may never reach the stale-lock state,
because `Stop-Process -Id <snakemake pid>` does not cascade on Windows and the surviving orchestrator's
`finally` removes the lock. The contradiction is with F5's general hard-kill path (any real crash, kill
of the orchestrator itself, or power loss), and it becomes reachable *in GF-2* precisely once the
injection is corrected per repo-fit-14. The two findings compound; neither cancels the other.

**Fix direction:** either (a) add the lock-clearing step to GF-2 and name the concrete command in
§6.3/§F11, or (b) make the liveness test strong enough to auto-clear safely — record `pid` **plus**
process creation time and `invocation_id`, and auto-clear only when the pid is dead *or* alive with a
different creation time. Pid alone is a weak liveness test on Windows, where pid reuse is routine, so
(b) needs the creation-time tiebreak regardless of which branch is chosen.

### repo-fit-2 (major) — `threads: workflow.cores` breaks every invocation without `-c`

§4.3 gives rule 3.08 `threads: workflow.cores`. `workflow.cores` **raises** when cores are unset
(`snakemake/workflow.py:583-593`), and for the default local executor `cli.py:1942-1948` leaves
`args.cores = args.jobs = None`. Rule directives are evaluated at parse time. Probe-verified in the
scratchpad on the pinned Snakemake 9.6.2 with a one-rule Snakefile carrying `threads: workflow.cores`:

```
snakemake --unlock  -s Snakefile   → WorkflowError: Workflow requires a total number of cores…
snakemake --dry-run -s Snakefile   → WorkflowError: (same)
```

**Consequence:** `AGENTS.md` § Key Commands documents `snakemake --unlock -s <Snakefile> --configfile <cfg>`
with no `-c`; that command stops working on wf3 — and it is precisely the command F5/GF-2 depend on for
crash recovery. Any bare `--dry-run` without `-c` breaks too. The Snakefile already guards this exact
hazard at `:486-489` (`try: int(workflow.cores) … except: 1`), so the design is reintroducing a trap the
repo has already paid for.

**Fix direction:** reuse the existing guarded `_cores` binding (or a callable `threads=`), and state
that the sweep's parallelism default degrades to 1 rather than raising when cores are unset.

### repo-fit-3 (major) — the new `staticmaps` input turns the wf3 dry-run test red in CI

§4.3 adds `staticmaps = ancient({basin_dir}/staticmaps.nc)` to `run_sweep`'s `input:`. `ancient()`
suppresses the mtime trigger, not the existence requirement, and no wf3 rule produces `staticmaps.nc`.
`tests/test_cli.py`'s `config_with_staged_region` fixture stages only
`hydrology_model/staticgeoms/region.geojson` and `config/runs/snake_config_model_creation.yml`
(`tests/test_cli.py:64-70`), and `test_snakefile_cli_climate_experiment` (`:214-230`) asserts
`returncode == 0` on that fixture.

**Consequence:** `MissingInputException` on the wf3 dry-run ⇒ `pytest tests/test_cli.py` fails on a
bare checkout, i.e. **both CI legs go red** (`.github/workflows/ci.yml` runs `pixi run pytest tests/`),
and the design's own per-step falsifier ("`pytest tests/test_cli.py`", §2.5) fails at step 4.

**Fix direction:** drop the input. §5.1 already threads `staticmaps_digest` through `params:` on the
`file_digest_or_absent` pattern, which is the mechanism that actually carries the freshness signal; the
DAG edge adds nothing. If the edge is wanted anyway, the fixture extension must be named in §13.

### repo-fit-4 (major) — `merge_logs` cannot merge a flat label log *and* a label part-dir

§6.5 writes both `_parts/3.08_run_sweep.log` (the rule's own `log:`) and
`_parts/3.08_run_sweep/rlz_<n>_cst_<m>.log`, and asserts per-member parts merge "with **no change to
`merge_logs`**". `merge_logs._members` (`blueearth_cst/shared/merge_logs.py:106-108`) checks the flat
file **first and returns early**:

```python
flat = os.path.join(parts_dir, f"{label}.log")
if os.path.isfile(flat):
    return [(None, flat)]
```

No label in any of the three workflows currently has both forms; 3.08 would be the first.

**Consequence:** every per-member log is silently dropped from `wf3_climate_experiment.log`, and
because the dropped paths never enter `merged`, `_remove_parts` never deletes them — the
"clean full run leaves one file in `logs/`" invariant (`Snakefile_climate_experiment:182-188`) breaks
and `_parts/3.08_run_sweep/` grows without bound across runs. This is a silent loss of exactly the
per-member visibility G4 exists to deliver. (`merge_benchmarks` is unaffected — its recursive glob at
`:55-59` picks up both.)

**Fix direction:** cheapest is to put the orchestrator log inside the dir
(`_parts/3.08_run_sweep/_orchestrator.log`) so the label has one shape; otherwise register two labels,
or change `_members` to union both — the last option changes shared cross-workflow code and needs its
own test.

### repo-fit-5 (major) — the two in-slot Python bodies are not callable as written

§6.6 step 3 says the member runs "`downscale_climate_forcing.py`'s body, in-slot". That module reads
the `snakemake` global at **module top level** and wraps the whole body in `tee_to_log`
(`blueearth_cst/experiment/downscale_climate_forcing.py:11-25` — its own comment says "no `__name__`
guard … `snakemake.*` reads run at import before any function"). Importing it from a slot raises
`NameError` on the first line of real work. Extracting it into a callable with an explicit log path is
required, behaviour-preserving work that neither §2.5's ownership table nor any §13 step names.
Same class, smaller: §4.3/§10 describe the WG-5 catalog change as "only the producer's `input:` set
changes", but `prepare_climate_data_catalog.py:132-133` derives its entry list from
`sm.input.cst_nc` / `sm.input.rlz_nc`, so a manifest-derived entry list is a **script** change too.

**Consequence:** the milestone's core step (§13 step 4) has an unscoped refactor of a hydromt-touching
module inside it, and §9.6's "Downscale — Identical … same script body" is asserted about a body that
does not yet exist in callable form, so the parity leg has nothing to run against until the extraction
lands.

**Fix direction:** add the extraction as an explicit, separately-verifiable sub-step (R5 already did
this once for `prepare_weagen_config.py` — see its module docstring — so there is a precedent shape to
copy), and name `prepare_climate_data_catalog.py` in §13 step 5.

### repo-fit-6 (major) — `allow_partial` cannot work against the unchanged reduce body

§9.4's `allow_partial` branch says `Qstats.csv` becomes a "grid with holes; the missing `(tavg, prcp)`
rows simply absent", while §4.4 states `analyze_wflow_results` "keeps its body" and §9.6 classes Reduce
as "Identical". Under the **default** `aggregate_rlz: True` (`Snakefile_climate_experiment:563`) the
body cannot express a hole:

- the loop is `for i in range(np.size(df_out_mean, 0))` over `st_num` rows with
  `csv_fns_i = [x for x in csv_fns if x.endswith("cst_" + str(i+1) + ".csv")]`
  (`export_wflow_results.py:153,161-162`); a missing member makes `csv_fns_i` empty and
  `pd.concat([])` at `:167` raises `ValueError: No objects to concatenate`;
- `df_out_mean` / `df_out_basavg` are **pre-allocated** `np.zeros((st_num, …))`
  (`:103-107,137-141`), so even without the raise a hole yields a **zero row**, not an absent one —
  `basin.csv` would silently report `0.0` indicators for an unrun stress-test cell.

**Consequence:** GF-7 (an in-scope gate — OQ-4 is settled as fail-loud + `allow_partial`) cannot pass,
and the failure mode of the naive implementation is a silently-zero response surface, which is exactly
the distortion §9.4 exists to prevent.

**Fix direction:** specify the reduce change: size the frames from the ledger's succeeded member set
rather than from `st_num`, skip empty groups, and give the `allow_partial` path its own falsifier
distinct from C-10 (which must stay a full-grid byte-identity check).

### repo-fit-7 (major) — the guard fusion and the 4th baseline target break two CI-running tests

Neither is named in §13 or in C-15 (which cites only `tests/test_check_project_consistency.py`):

1. `tests/test_guard_invalidation.py` targets the sentinel **path** and executes the guard rule for
   real: `sentinel = pdir / "experiments" / experiment / ".project_consistency_ok"` (`:95`), then
   `_seed_guard` / `_dry_run_output` run `snakemake <sentinel>` (`:104-115`) for the i–l and 2c–2h
   cases. Replacing the sentinel with `_state/members.json` and absorbing 3.00b into 3.01 invalidates
   the whole file's target, and each case now drives a manifest builder rather than a guard writer.
2. `tests/test_check_baseline_scope.py:86-95` pins the exact per-workflow cardinality
   `{"model_creation": 5, "climate_projections": 6, "climate_experiment": 3}`, and `:147`/`:180`
   assert `len(targets) == 14`. §10b/§13 step 9's 4th wf3 target (`response_long.csv`) makes these
   3 → 4 and 14 → 15.

**Consequence:** both files run on a bare checkout, so both CI legs go red at the step that lands the
change, and C-15's "guard failure modes are unchanged" is not verifiable by the test it names.

**Fix direction:** name both files in §13 (step 1 and step 9 respectively), and widen C-15 to include
`test_guard_invalidation.py` with an explicit statement of which of its assertions are *contract*
(verdict + message) and which are *plumbing* (the sentinel path).

### repo-fit-8 (major) — `multiprocessing` spawn inside a `script:` module is unaddressed

§6.1 runs the orchestrator as a `script:` module (`blueearth_cst/experiment/run_sweep.py`, §4.3) that
spawns `p` slot processes with the spawn start method. Snakemake does not import a `script:` module: it
writes preamble+source to a generated temp file under `.snakemake/scripts/` and runs it as a subprocess
(`snakemake/script/__init__.py:634-645`), with the preamble rebinding
`__file__` to the real module path (`:778-786`). `multiprocessing.spawn` records
`sys.modules['__main__'].__file__` and each child calls `_fixup_main_from_path`, so **every slot
re-executes `run_sweep.py` top level** under `__mp_main__`.

**Consequence:** (a) all of `run_sweep.py`'s module-level imports are paid `p` times, which directly
contradicts §6.1's "the orchestrator never imports hydromt" cost model unless the module is kept
import-cheap by construction; (b) correctness depends on the repo's guarded form
`if __name__ == "__main__": if "snakemake" in globals():` (`check_project_consistency.py:219-231`) —
and the sibling module in the same package does the **opposite** (repo-fit-5), so the wrong pattern is
the locally available one. H4/C-5 test pool stability, not this.

**Fix direction:** state the invariant (no module-level side effects, guarded entry, slot body in a
separate importable module), or — more repo-idiomatic — make 3.08 a `shell:` rule through
`run_logged.py` exactly as `Snakefile_climate_experiment:546` already does for a long-lived Julia
child, which sidesteps `__main__` entirely and gives §6.5's orchestrator log the same
header/relativization/UTF-8/exit-code handling every other tee'd rule gets (`:21-25`). Keeping
`run_sweep.py` import-cheap has a second payoff: §13 step 4's Julia-free unit tests then need no
`sys.modules.setdefault` stubs, avoiding the collection-order pollution documented in
`dev/followups.md` § R3+.

### repo-fit-17 (minor) — the worker line protocol never pins its codec

§6.2 specifies newline-delimited JSON over the worker's stdin/stdout and pins flushing (rule 1,
PR-5-verified) but never states an encoding. Julia writes UTF-8; Python text-mode pipes default to the
locale codec, which is cp1252 on this dev box. `.github/workflows/ci.yml` names "cp1252/CRLF/file-locking"
as *the* Windows defect class this repo owns, and `Snakefile_climate_experiment:21-25` records that
`run_logged.py` exists partly to do "UTF-8/exit-code handling" for exactly these R/Julia children.
(CRLF itself is benign — `json.loads` tolerates a trailing `\r`.)

**Consequence:** a Wflow error string carrying a non-cp1252 character raises `UnicodeDecodeError` in
the orchestrator's reader — i.e. the decode fails on the very message the failure path exists to carry,
and the member is recorded `class=worker` with a decode traceback instead of the real error.

**Fix direction:** pin `encoding="utf-8"` and an explicit `errors=` policy on the worker pipes in
§6.2's rules, and say the same for the `Rscript` per-member capture.

### repo-fit-9 (minor) — `sweep_status.py`'s home contradicts the three-homes split

§7.5 places `dev/scripts/sweep_status.py` while calling it the user-facing replacement for the
`--dry-run` visibility the milestone removes and "a *required* deliverable". `AGENTS.md` splits the
three homes by invocation model: `dev/scripts/` "inspects or maintains the **repository** and is never
part of a run"; `scripts/` is "what a user runs". `prune_experiment_orphans.py` in `dev/scripts/` is
right (it mirrors `prune_series_cache.py`); a status command a user runs against their own
`project_dir` mid-run is not. §2.5's ownership table also lists `run_sweep.py`/`sweep_status.py`
without naming their homes.

**Fix direction:** `scripts/sweep_status.py`, or state explicitly why the exception is taken.

### repo-fit-10 (minor) — `master_seed` has no home in the sectioned config

§4.2/§9.5 take `master_seed` from `generateWeatherSeries.seed` in
`config/templates/weathergen_config.yml:17` — a **tracked repo template** shared by every project —
while §7.6 lists `master_seed` as a user-facing invalidation lever ("every realization's seed changes
⇒ regeneration"). Changing it today means editing a tracked template, which is a repo change, not a
project change, and it cannot differ between two projects on one checkout.

**Fix direction:** add `workflows.climate_experiment.master_seed` on the `get_config` optional contract
with the template value as the default, and record it in the manifest from there.

### repo-fit-11 (minor) — retired-key rejection has no mechanism and no precedent

§4.5 says a config still carrying `batch_size` / `batch_size_max` is "rejected with a named migration
message" (and §9.1 branch (b) says the same for `stress_test.precip.variance.*`). `get_config`
(`blueearth_cst/shared/snake_utils.py:122-154`) has only present/optional/required semantics — there is
no reject mode — and a repo-wide grep finds no precedent for rejecting a retired key anywhere,
including the R01 sectioned-schema migration. The only parse-time key validator is the local
`_positive_batch_key` (`Snakefile_climate_experiment:501-508`).

**Fix direction:** specify where the rejection lives (a small parse-time helper mirroring
`_positive_batch_key`, pinned by a unit test), and note the consequence that a parse-time raise also
blocks `--unlock` until the config is edited — acceptable, but it should be a stated choice.

### repo-fit-12 (minor) — C-11's "cell-for-cell" re-pivot is fragile against a string table

§4.4 types `response_long.value` as `float` and C-11 requires the re-pivot to reproduce
`Qstats.csv`/`basin.csv` "cell-for-cell". `Qstats.csv` is not a float table: the frames are created
`dtype="str"` and filled by `np.concatenate([["mean"], cst_stat, df.values.round(2)])`
(`export_wflow_results.py:103-119, 205-239`), i.e. every cell is numpy's stringification of a rounded
float. A float-typed long table round-tripped through pandas will agree in the common case and diverge
on formatting edge cases (trailing zeros, exponent forms).

**Fix direction:** state the comparison as parsed-value equality at the declared rounding, not byte
equality of cells — or declare the string formatting itself part of the contract.

### repo-fit-13 (minor) — the step-6 doc/tooling inventory is incomplete

Five items the design changes or invalidates but does not list:

- `dev/scripts/estimate_batch_makespan.py` and `tests/test_estimate_batch_makespan.py` — P3-3 tooling
  for a lever this design deletes; §6.4 cites the estimator as an argument but never dispositions it
  (retain as evidence vs. retire with its test).
- `dev/conventions/naming.md:77-84` — the `st_num` paragraph names
  `downscale_climate_realization`, `run_wflow`, `export_wflow_results` and
  `generate_climate_stress_test`, three of which the design deletes. §13 step 6 only adds the
  member-id vocabulary.
- `dev/scripts/semantic_tree_diff.py:201` — an allowlist entry for
  `experiments/{experiment_name}/.project_consistency_ok`, dead once the sentinel retires
  (and `:381`'s explanatory comment with it).
- `tests/test_workflow_climate_experiment.py:9,28` — docstring pins "12 Wflow runs" and
  "56 jobs under `--forceall`" against §4.5's 13 jobs. Integration-gated, so neither CI nor
  §13 step 7's `pytest tests/` catches the drift.
- **§9.1's own recommendation.** The body still recommends *activating* the `precip_variance` axis;
  gate G1 ruled OQ-1 **DEFERRED** (no call-site change, axis inert, field retained). An implementer
  reading the accepted body will read §9.1 as authority. Step 6 must correct the section, not only
  the appendix.

### repo-fit-14 (minor) — two Windows process/file semantics the gate set assumes away

1. **`os.replace` over an open file.** §5.3 relies on `os.replace` for `members.json`,
   `ledger_final.csv` and `sweep_completeness.csv`. On Windows this raises `PermissionError` when
   another process holds the target open — and §7.5 makes `sweep_status.py` a first-class **concurrent
   reader** of exactly those files (plus editors and AV scanners). POSIX has no equivalent failure.
2. **`Stop-Process` does not cascade.** GF-2 injects a hard kill with
   `Stop-Process -Id <snakemake pid> -Force`. The orchestrator is a *child* process (Snakemake runs
   `script:` via a subprocess, `script/__init__.py:857+`), and Windows has no process groups, so
   killing the Snakemake pid leaves the orchestrator and its `p` slots and Julia workers running.
   GF-2 would not produce the state it is written to produce.

**Fix direction:** give the whole-file writes a short bounded retry with a named error on exhaustion,
and specify GF-2's injection as a process-tree kill (`Stop-Process -Id <pid> -Force` on the
orchestrator's own pid, or `taskkill /T /F`).

### repo-fit-15 (minor) — `file_digest_or_absent` on `staticmaps.nc` reads the whole file at parse time

§5.1 threads `staticmaps_digest` through `params:` "on the same pattern" as the snapshot digests.
`file_digest_or_absent` slurps the entire file (`snake_utils.py:177-181`, `f.read()`) and runs at
Snakefile **parse** time, i.e. on every invocation including `--dry-run` and `--unlock`. Today's uses
are small YAMLs; `staticmaps.nc` is not. Invisible on the 152 KB fixture, scale-dependent on a real
basin.

**Fix direction:** a chunked digest helper (or reuse only the `wflow_sbm.toml` digest plus
size+mtime for the grid) — a small change that keeps the invalidation semantics.

### repo-fit-16 (minor) — the reduce's newly-undeclared reads invert R07 B6 without saying why

§3.2 and R-6 justify the undeclared *writes*. But 3.09's per-member CSV reads also become undeclared
(§4.4 replaces `rlz_csv_fns` with `ledger_final`), and that is the same class of thing R07 B6
deliberately *corrected* in the opposite direction — see the comment at
`Snakefile_climate_experiment:553-557`, which declares `st_csv_fns` precisely because an undeclared
runtime read was invisible to `--dry-run`. The reason declaration is impossible here (no rule produces
the member CSVs any more, so declaring them raises `MissingInputException`) is sound but unstated.

**Fix direction:** one sentence in §3.2 or §4.4, so it does not read as an oversight to the next
reviewer.

---

```yaml
verdict: revise
doc_version: design-v1.md
findings:
  - id: repo-fit-1
    severity: blocking
    section: "6.3 Worker lifecycle / 8.1 F5+F11 / 8.2 GF-2"
    finding: >
      A hard-killed sweep always leaves `_state/sweep.lock` behind (the `finally` never runs), and
      §6.3's orphan-sweep rule refuses to auto-clear a lock whose recorded pid is dead. GF-2's
      specified command sequence (`SM`; `SM --unlock`; `SM`) therefore cannot reach its stated
      observation, because `snakemake --unlock` clears `.snakemake/locks/`, not `_state/sweep.lock`.
      F5's recovery path lands directly in F11's refusal.
    rationale: >
      GF-2 is the only gate for G2 ("resume is measured, not asserted"), the milestone's headline
      claim; as specified it is unexecutable. Observably, the third command fails on the stale lock and
      no member runs. A user hard-killed once has no documented exit: §6.3 says "the message names the
      recovery command" and the design never names one. Compounds with repo-fit-14: the contradiction
      is with F5's general hard-kill path, and it becomes reachable in GF-2 specifically once that
      gate's non-cascading `Stop-Process` injection is corrected.
    suggested_fix: >
      Name the lock-clearing recovery command and add it to GF-2, and/or record process creation time
      alongside `pid` so a dead-or-recycled holder can be auto-cleared safely — pid alone is a weak
      liveness test on Windows.

  - id: repo-fit-2
    severity: major
    section: "4.3 Stage 3 — Sweep (rule 3.08 `threads:`)"
    finding: >
      `threads: workflow.cores` is evaluated at parse time and `workflow.cores` raises when cores are
      unset (`snakemake/workflow.py:583-593`; `cli.py:1942-1948` leaves cores None for the default
      local executor). Probe-verified on the pinned Snakemake 9.6.2: a one-rule Snakefile with that
      directive fails BOTH `snakemake --unlock -s …` and `snakemake --dry-run -s …` when `-c` is
      omitted.
    rationale: >
      `AGENTS.md` § Key Commands documents `snakemake --unlock -s <Snakefile> --configfile <cfg>` with
      no `-c`, and that is exactly the command F5/GF-2 rely on after a crash — so the recovery path
      breaks. The Snakefile already guards this hazard at `:486-489`, so the design reintroduces a trap
      the repo has already paid for.
    suggested_fix: >
      Reuse the existing guarded `_cores` binding (or a callable `threads=`), degrading to 1 rather
      than raising when cores are unset.

  - id: repo-fit-3
    severity: major
    section: "4.3 Stage 3 — Sweep (rule 3.08 `input:`)"
    finding: >
      `staticmaps = ancient({basin_dir}/staticmaps.nc)` is a declared input with no producer in wf3.
      `ancient()` suppresses the mtime trigger, not the existence requirement, and
      `tests/test_cli.py:64-70` stages only `staticgeoms/region.geojson` and the wf1 config snapshot.
    rationale: >
      `test_snakefile_cli_climate_experiment` (`tests/test_cli.py:214-230`) asserts returncode 0 and
      runs on a bare checkout, so `MissingInputException` turns both CI legs red
      (`.github/workflows/ci.yml` runs `pixi run pytest tests/`), and the design's own per-step
      falsifier `pytest tests/test_cli.py` fails at step 4.
    suggested_fix: >
      Drop the input — §5.1 already carries `staticmaps_digest` as a `params:` value on the
      `file_digest_or_absent` pattern, which is what actually carries the freshness signal. If the edge
      is kept, name the fixture extension in §13.

  - id: repo-fit-4
    severity: major
    section: "6.5 Logging and benchmark capture"
    finding: >
      §6.5 writes both `_parts/3.08_run_sweep.log` and `_parts/3.08_run_sweep/<member>.log` and claims
      the parts merge "with no change to merge_logs". `merge_logs._members`
      (`blueearth_cst/shared/merge_logs.py:106-108`) tests the flat `<label>.log` first and returns
      early, so a label can have a flat log OR a part-dir, never both. No existing label has both.
    rationale: >
      Every per-member log is silently dropped from `wf3_climate_experiment.log`, and because those
      paths never enter `merged`, `_remove_parts` never deletes them — the documented "one file in
      logs/ after a clean run" invariant breaks and `_parts/3.08_run_sweep/` grows across runs. That is
      a silent loss of precisely the per-member visibility G4 exists to deliver. (merge_benchmarks is
      unaffected — recursive glob at `:55-59`.)
    suggested_fix: >
      Put the orchestrator log inside the part-dir (`3.08_run_sweep/_orchestrator.log`) so the label
      has one shape; alternatives are two labels or a change to shared `_members` with its own test.

  - id: repo-fit-5
    severity: major
    section: "6.6 Forcing lifecycle (step 3) / 4.3 rule 3.07 / 10 WG-5"
    finding: >
      `downscale_climate_forcing.py` reads the `snakemake` global at module top level with no function
      and no guard (`:11-25`, stated in its own comment) and wraps the body in
      `tee_to_log(snakemake.log[0])`, so "downscale_climate_forcing.py's body, in-slot" is not callable
      without an extraction that §2.5 and §13 never assign. Same class: §10 calls WG-5 "verbatim, only
      the producer's input: set changes", but `prepare_climate_data_catalog.py:132-133` derives its
      entries from `sm.input.cst_nc`/`rlz_nc`, so a manifest-derived entry list is a script change.
    rationale: >
      The milestone's core step carries an unscoped refactor of a hydromt-touching module, and §9.6's
      "Downscale — Identical, same script body" is asserted about a body that does not yet exist in
      callable form, so that parity leg has nothing to run against until the extraction lands.
    suggested_fix: >
      Add the extraction as an explicit, separately-verifiable sub-step (R5 did exactly this for
      `prepare_weagen_config.py` — copy that shape) and name `prepare_climate_data_catalog.py` in
      §13 step 5.

  - id: repo-fit-6
    severity: major
    section: "9.4 OQ-4 — reduce with holes / 4.4 Stage 4"
    finding: >
      Under the default `aggregate_rlz: True` the reduce cannot express a hole while "keeping its
      body": the loop runs `range(st_num)` and selects
      `csv_fns_i = [x for x in csv_fns if x.endswith("cst_<i+1>.csv")]`
      (`export_wflow_results.py:153,161-162`), so a missing member makes `pd.concat([])` at `:167`
      raise; and `df_out_mean`/`df_out_basavg` are pre-allocated `np.zeros((st_num, …))`
      (`:103-107,137-141`), so a hole yields a zero row rather than an absent one.
    rationale: >
      GF-7 is an in-scope gate (OQ-4 is settled as fail-loud + `allow_partial`) and cannot pass; the
      naive implementation's failure mode is a silently-zero `basin.csv` row for an unrun stress-test
      cell — exactly the distorted response surface §9.4 exists to prevent. It also contradicts §4.4's
      "keeps its body" and §9.6's "Reduce — Identical".
    suggested_fix: >
      Specify the reduce change (size the frames from the ledger's succeeded set, skip empty groups)
      and give `allow_partial` its own falsifier, keeping C-10 a full-grid byte-identity check.

  - id: repo-fit-7
    severity: major
    section: "4.1 rule 3.01 (guard fusion) / 10b + 13 step 9 (baseline slice)"
    finding: >
      Two CI-running tests are invalidated and named nowhere. `tests/test_guard_invalidation.py`
      targets the sentinel path `experiments/<exp>/.project_consistency_ok` (`:95`) and executes the
      guard rule against it (`:104-115`), so the sentinel replacement and the 3.00b→3.01 fusion
      invalidate the whole file. `tests/test_check_baseline_scope.py:86-95` pins the exact tag
      cardinality `{model_creation: 5, climate_projections: 6, climate_experiment: 3}` and `:147`/`:180`
      assert `len(targets) == 14`; adding `response_long.csv` makes those 4 and 15.
    rationale: >
      Both run on a bare checkout, so both CI legs go red at the step that lands the change, and
      C-15's "guard failure modes are unchanged" is not verifiable by the single test file it cites.
    suggested_fix: >
      Name both files in §13 (steps 1 and 9), and widen C-15 to `test_guard_invalidation.py` while
      distinguishing its contract assertions (verdict + message) from its plumbing assertions (the
      sentinel path).

  - id: repo-fit-8
    severity: major
    section: "6.1 Process topology"
    finding: >
      Snakemake does not import a `script:` module: it writes preamble+source to a generated temp file
      under `.snakemake/scripts/` and runs it as a subprocess (`snakemake/script/__init__.py:634-645`),
      with the preamble rebinding `__file__` to the real module path (`:778-786`). `multiprocessing`
      spawn therefore re-executes `run_sweep.py` top level in every one of the `p` children via
      `_fixup_main_from_path`. The design never addresses this.
    rationale: >
      Every module-level import in `run_sweep.py` is paid `p` times, which directly contradicts §6.1's
      "the orchestrator never imports hydromt" cost model unless the module is deliberately kept
      import-cheap; and correctness depends on the guarded
      `if __name__ == "__main__": if "snakemake" in globals():` form
      (`check_project_consistency.py:219-231`) while the sibling module in the same package does the
      opposite (repo-fit-5), so the wrong local pattern is the more available one. H4/C-5 test pool
      stability, not this.
    suggested_fix: >
      State the invariant (no module-level side effects, guarded entry, slot body in a separate
      importable module) — or make 3.08 a `shell:` rule through `run_logged.py` exactly as
      `Snakefile_climate_experiment:546` already does for a long-lived Julia child, which sidesteps
      `__main__` entirely and gives the orchestrator log the repo's standard tee handling (`:21-25`).
      Import-cheapness also lets §13 step 4's Julia-free unit tests avoid `sys.modules.setdefault`
      stubs and the collection-order pollution in `dev/followups.md` § R3+.

  - id: repo-fit-9
    severity: minor
    section: "7.5 --dry-run honesty / 2.5 delegated ownership"
    finding: >
      `sweep_status.py` is placed in `dev/scripts/` while being described as the user-facing
      replacement for lost `--dry-run` visibility. AGENTS.md's three-homes split assigns `dev/scripts/`
      to things that inspect or maintain the repository and are never part of a run, and `scripts/` to
      what a user runs. (`prune_experiment_orphans.py` in `dev/scripts/` is correct — it mirrors
      `prune_series_cache.py`.)
    rationale: >
      Misfiling the one artifact that compensates for the removed DAG visibility makes it less
      discoverable to the audience it exists for, and blurs a split AGENTS.md states explicitly (O-23).
    suggested_fix: "Move to `scripts/sweep_status.py`, or state why the exception is taken."

  - id: repo-fit-10
    severity: minor
    section: "4.2 Seed derivation / 9.5 OQ-5 / 7.6"
    finding: >
      `master_seed` is taken from `generateWeatherSeries.seed` in the tracked repo template
      `config/templates/weathergen_config.yml:17`, yet §7.6 treats it as a user-facing invalidation
      lever. Changing it is a repo edit, not a project edit, and two projects on one checkout cannot
      differ.
    rationale: >
      A reproducibility-critical, per-experiment input has no home in the R01 sectioned config, so
      exercising the documented lever means editing tracked, shared repo state.
    suggested_fix: >
      Add `workflows.climate_experiment.master_seed` on the `get_config` optional contract, defaulting
      to the template value, and record it in the manifest from there.

  - id: repo-fit-11
    severity: minor
    section: "4.5 Config keys retired / 9.1 branch (b)"
    finding: >
      "Rejected with a named migration message" has no mechanism: `get_config`
      (`snake_utils.py:122-154`) has only present/optional/required semantics, and no code anywhere in
      the repo rejects a retired key — including the R01 migration. The only parse-time key validator
      is the local `_positive_batch_key` (`Snakefile_climate_experiment:501-508`).
    rationale: >
      Without a stated mechanism and a pinning test the intended behaviour is likely to land as a
      silent ignore, which is the exact failure the section is written to prevent.
    suggested_fix: >
      Specify a small parse-time helper mirroring `_positive_batch_key` plus a unit test, and note
      that a parse-time raise also blocks `--unlock` until the config is edited.

  - id: repo-fit-12
    severity: minor
    section: "4.4 response_long.csv / 12 C-11"
    finding: >
      `response_long.value` is typed float while `Qstats.csv` is an all-string table: the frames are
      built `dtype="str"` and filled by `np.concatenate([["mean"], cst_stat, df.values.round(2)])`
      (`export_wflow_results.py:103-119, 205-239`), so every cell is numpy's stringification of a
      rounded float.
    rationale: >
      C-11's "cell-for-cell" re-pivot check then depends on repr formatting (trailing zeros, exponent
      forms) rather than on values, making the acceptance test brittle in a way that will read as a
      real regression when it fires.
    suggested_fix: >
      State C-11 as parsed-value equality at the declared rounding, or declare the string formatting
      itself part of the HM-7 contract.

  - id: repo-fit-13
    severity: minor
    section: "13 step 6 — Contracts, validators, tooling, docs"
    finding: >
      The step-6 inventory misses five items the design changes or invalidates:
      `dev/scripts/estimate_batch_makespan.py` + `tests/test_estimate_batch_makespan.py` (P3-3 tooling
      for a deleted lever, cited in §6.4 but never dispositioned); `dev/conventions/naming.md:77-84`
      (the `st_num` paragraph names three rules the design deletes);
      `dev/scripts/semantic_tree_diff.py:201` (a now-dead allowlist entry for
      `.project_consistency_ok`, plus its `:381` comment);
      `tests/test_workflow_climate_experiment.py:9,28` (docstring pins "12 Wflow runs" / "56 jobs
      under --forceall" against §4.5's 13); and §9.1 itself, whose *activate* recommendation was
      superseded at G1 by the DEFERRED ruling.
    rationale: >
      The §9.1 item matters most: an implementer reading the accepted body will take the activate
      recommendation as authority and make a value-changing call-site edit the gate explicitly
      deferred. The rest is stale documentation that the milestone is the natural moment to fix.
    suggested_fix: "Extend §13 step 6's list with all five, and rewrite §9.1's recommendation in place."

  - id: repo-fit-14
    severity: minor
    section: "5.3 Atomicity / 8.2 GF-2"
    finding: >
      Two Windows-specific semantics are assumed away. (1) `os.replace` raises `PermissionError` when
      another process holds the target open — and §7.5 makes `sweep_status.py` a first-class concurrent
      reader of `members.json` / `ledger_final.csv` / `sweep_completeness.csv`. (2) GF-2's
      `Stop-Process -Id <snakemake pid> -Force` does not cascade: the orchestrator is a child process
      (`script/__init__.py:857+`) and Windows has no process groups, so the slots and Julia workers
      survive the "hard kill".
    rationale: >
      (1) makes finalization intermittently fail on the dev platform in exactly the situation the
      status command is meant for; (2) means GF-2 does not produce the state it is written to produce,
      so a green GF-2 would not evidence what it claims.
    suggested_fix: >
      Bounded retry with a named error on the whole-file writes; specify GF-2's injection as a
      process-tree kill (`taskkill /T /F`, or target the orchestrator's own pid).

  - id: repo-fit-15
    severity: minor
    section: "5.1 Manifest schema — member_hash digests"
    finding: >
      `file_digest_or_absent` (`snake_utils.py:177-181`) slurps the whole file with `f.read()` and runs
      at Snakefile parse time, on every invocation including `--dry-run` and `--unlock`. Today's uses
      are small YAML snapshots; §5.1 extends the pattern to `staticmaps.nc`.
    rationale: >
      Scale-dependent and invisible on the 152 KB fixture, but a real basin's staticmaps makes every
      wf3 parse pay a full read plus whole-file memory.
    suggested_fix: >
      Use a chunked digest helper, or key on the `wflow_sbm.toml` digest plus grid size+mtime, keeping
      the invalidation semantics unchanged.

  - id: repo-fit-16
    severity: minor
    section: "3.2 ownership split / 4.4 Stage 4"
    finding: >
      The reduce's per-member CSV reads become undeclared when `rlz_csv_fns` is replaced by
      `ledger_final`. §3.2 and R-6 justify only the undeclared *writes*. R07 B6 was the opposite
      correction, and its rationale is still in the tree at
      `Snakefile_climate_experiment:553-557`.
    rationale: >
      The reason declaration is now impossible (no rule produces those CSVs, so declaring them raises
      MissingInputException) is sound but unstated, so it reads as an oversight to the next reviewer of
      a convention the repo deliberately tightened.
    suggested_fix: "One sentence in §3.2 or §4.4 stating the MissingInputException constraint."

  - id: repo-fit-17
    severity: minor
    section: "6.2 Orchestrator ↔ Julia worker line protocol"
    finding: >
      The protocol pins one-line messages and explicit flushing but never states an encoding. Julia
      writes UTF-8; Python text-mode pipes default to the locale codec (cp1252 on the dev box).
      `.github/workflows/ci.yml` names cp1252/CRLF/file-locking as the Windows defect class this repo
      owns, and `Snakefile_climate_experiment:21-25` records that `run_logged.py` exists partly to do
      "UTF-8/exit-code handling" for these same R/Julia children. (CRLF itself is benign — `json.loads`
      tolerates a trailing `\r`.)
    rationale: >
      A Wflow error string with a non-cp1252 character raises `UnicodeDecodeError` in the
      orchestrator's reader, so the decode fails on the very message the failure path exists to carry
      and the member is recorded `class=worker` with a decode traceback instead of the real error.
    suggested_fix: >
      Pin `encoding="utf-8"` and an explicit `errors=` policy on the worker pipes in §6.2's rules, and
      state the same for the per-member `Rscript` capture.
```
