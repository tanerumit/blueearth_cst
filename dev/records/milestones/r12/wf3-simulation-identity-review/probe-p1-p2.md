# Framework-feasibility probes P1, P2 — wf3-simulation-identity

Run: wf3-simulation-identity | probed 2026-09-06 | commit `d50427e4`

All Snakemake invocations against the real workflow are `--dryrun`. The standalone
probes in `.tmp/scratchpad/2026-09-06_probe/` are throwaway Snakefiles with `run:`
bodies that only `write_text`; two of those were executed for real to observe
multi-invocation behaviour. No real workflow run was executed.

## P1 — scenario table at DAG-construction time

**Question** (verbatim from the intake) — *Can the scenario table be read at
DAG-construction time from a config-derived pure function and, alternatively, from
a supplied file, without a checkpoint?*

**Method**

Trace first, then five executed experiments in `.tmp/scratchpad/2026-09-06_probe/p1/`.

Trace of today's config-derived path:

- `run_stress_test.smk:187` — `_, _, ST_NUM = stress_test_grid(stress_test_cfg)`,
  module scope, pure function of `my_cfg["stress_test"]`.
- `blueearth_cst/shared/snake_utils.py:2034-2068` — `stress_test_grid` reads only
  the mapping; no I/O.
- `run_stress_test.smk:180, 205, 218-219, 233` — `RLZ_NUM`, `ST_START`
  (`0 if run_hist else 1`), `ST_WIDTH`/`RLZ_WIDTH` via `index_width`, `ST_BASELINE`.
- `run_stress_test.smk:978-990` (3.11) — output is a **static Python list**,
  `temp([f"{wg_dir}/output/rlz_{rlz_ix(n)}_st_{ST_BASELINE}.nc" for n in ...])`,
  zero wildcards.
- `run_stress_test.smk:1120-1121` — `_k_members` flat list; `:1179-1180` slices it
  into `_batches`; `:1247` — `expand(...)` in 3.16's `input:` over `rlz_num`/`st_num`.

So: config → `stress_test_grid` → module-scope ints → `expand()` / static lists.
No file is read to learn the id set today.

Commands, all `pixi run snakemake -s <file> -c1 --dryrun`, exit code captured
without a pipe:

| case | Snakefile | table |
|---|---|---|
| (a) present at parse time | `Snakefile_present` | `table.csv`, 3 rows, `csv.DictReader` at module scope |
| (b1) absent, unguarded read | `Snakefile_absent_unguarded` | `missing_table.csv` |
| (b2) absent, guarded read → `[]` | `Snakefile_absent_guarded` | same, `if os.path.isfile(...) else []` |
| (c) table is a rule output in the same Snakefile, clean tree | `Snakefile_selfproduced` | `gen/table.csv`, guarded read |
| (c′) same, but via `checkpoint` | `Snakefile_checkpoint` | `genc/table.csv` |

**Result**

- **(a) works.** `[parse] ids read = ['001', '002', '003']`, then
  `make 3 / all 1 / total 4`, exit 0. `expand()` over CSV rows at parse time needs
  no checkpoint.
- **(b1) loud failure**, exit **1**:
  ```
  FileNotFoundError in file ".../Snakefile_absent_unguarded", line 5:
  [Errno 2] No such file or directory: 'missing_table.csv'
  ```
- **(b2) SILENT OMISSION**, exit **0**:
  ```
  [parse] ids read = []
  rule all:
      jobid: 0
      reason: Rules with neither input nor output files are always executed.
  Job stats: all 1 / total 1
  ```
  Every scenario job is absent from the DAG and nothing reports it.
- **(c) two invocations required, the first silently incomplete.** Real run 1 on a
  clean tree: `[parse] ids read = []`, `build_table 1 / all 1 / total 2`, **exit 0**
  — the table was written and *zero* scenario jobs ran, with no warning. Dry-run 2,
  table now on disk: `[parse] ids read = ['001', '002']`, `make 2 / all 1 / total 3`.
- **(c′) a checkpoint resolves (c) in one invocation.** `outc/001.txt` and
  `outc/002.txt` both produced from a clean tree, exit 0.

Repo precedent, checked rather than asserted: `analyze_projections.smk:467` reads a
YAML **unguarded** at module scope (`yaml.safe_load(Path(DATA_SOURCES).read_text(...))`)
and `:468-471` reads a JSON **guarded** (`if os.path.isfile(STORE_INDEX) else None`);
`COMBINATIONS` at `:489` is the parse-time `expand()` source. The other three `.smk`
files, `run_stress_test.smk` included, contain no parse-time file read.

**Verdict** — **feasible with stated conditions.** Both a
supplied file read at parse time (a) and a config-derived pure function build the
DAG. A checkpoint is required **only** if the table is produced by a rule of the
same workflow invocation (case c).

**What this constrains in the design**

1. The scenario table must be **outside the DAG** — supplied by the user, or
   generated/committed ahead of the run — or WF3 needs a checkpoint. The
   family-blind seam is compatible with the no-checkpoint route only if stage 1's
   table is *not* a stage-1 rule output that stage 2 reads at parse time.
2. If the design keeps rule 3.09 (`prepare_stress_test_grid`) writing
   `stress_test_lookup.csv` **and** makes the id set come from that file, it lands
   squarely in case (c). Today it does not: 3.09's output is consumed as a rule
   `input:` (3.12, `:1026`), never at parse time.
3. **The guarded read is the dangerous branch.** (b2) and (c) both exit 0 with the
   scenario runs missing. Any parse-time read of a supplied table must be
   **unguarded, or guarded with an explicit raise** — never an `else []` fallback.
4. The repo's existing bootstrap for "a generated file read at parse time" is to
   **track the generated file**: `config/catalogs/cmip6_data.yml` and
   `cmip6_store_index.json` are both in `git ls-files`. A supplied scenario table
   needs the same story, or a documented pre-run generation step.

## P2 — the 3.11 / 3.12 producer ambiguity under a single id

**Question** (verbatim from the intake) — *Does renaming `rlz_<r>_st_<m>` to a
single id disturb rule 3.12's `wildcard_constraints`, which exist to stop a
`CyclicGraphException` between 3.11's and 3.12's output patterns?*

**Method**

1. **Control** — unmodified dry-run.
   `pixi run snakemake all -c 1 -s run_stress_test.smk --configfile test_case/snake_config_rapid.yml --dry-run`
   failed with `MissingInputException in rule check_project_consistency` (this
   worktree has no seeded `test_case/test_rapid`), so the control was re-run with
   `--configfile test_case/snake_config_baseline.yml` against the seeded
   `test_case/test_local`: **exit 0**, `perturb_climate_realization 12`, total 43.
   (`realizations_num: 2`, `run_historical: true` → `ST_START = 0`, so `st_0` *is*
   in the DAG and the ambiguity is reachable.)
2. **Mutation** — `run_stress_test.smk` rule 3.12's
   `st_num=member_index_regex(ST_WIDTH)` (`:1018`) replaced by the loosened
   `st_num=rf"[0-9]{{{ST_WIDTH}}}"`, which admits the baseline. Same baseline
   dry-run, then `pixi run pytest tests/test_guard_invalidation.py -x -q`.
   Restored with `git checkout -- run_stress_test.smk`.
3. **Standalone model** — `.tmp/scratchpad/2026-09-06_probe/p2/`. Faithful to the
   real shape: `A_plural` mirrors 3.11 (one job, **static output list**, zero
   wildcards) producing `out/scenario_{001,004}.nc`; `B_wildcard` mirrors 3.12
   (`output: "out/scenario_{sid}.nc"`, input = one of A's outputs via a dict).
   Ids `001..006`, baselines at `001` and `004` — deliberately **not** partitionable
   by pattern, which is what a plain sequential id gives with two realizations.
   Six mechanisms, each run twice: once with A's subtree resolvable, once with A
   carrying a missing external input (`seed_missing.txt`).
4. **Scaling check on the recommended mechanism** — `common_big.py`, 500 ids with
   10 **scattered** baselines (`001, 051, 101, …`), so the alternation constraint
   is 490 alternatives and no prefix partition exists. Timed against the same
   Snakefile with a loose `[0-9]{3}` constraint, and re-run with A unresolvable.

**Result**

*Mutation of the real workflow.* The loosened dry-run on the **seeded** tree was
**clean — exit 0, total 43, no exception.** The in-file comment at `:1005-1018` (the claim itself at `:1015`)
("Probed — removing it still yields CyclicGraphException") did **not** reproduce
under a plain dry-run. It reproduces under `tests/test_guard_invalidation.py`,
which builds a fresh project:

```
CyclicGraphException in rule perturb_climate_realization in file
".../run_stress_test.smk", line 1003:
Cyclic dependency on rule perturb_climate_realization.
```

(`test_2c_fresh_project_missing_wf1_snapshot` failed asserting
`MissingInputException`; `1 failed, 1 passed in 39.69s`.) The constraint is
load-bearing, and **a clean dry-run is a false negative for it** — exactly what
`member_index_regex`'s docstring (`snake_utils.py:2163-2176`) predicts.

*Standalone model.* The trigger was isolated: the cycle appears **only when the
plural rule's own subtree is unresolvable.** With A resolvable, Snakemake prefers
the zero-wildcard rule and every shape below builds. With A's input missing, it
falls back to the wildcard rule, whose input for a baseline id is its own output.

| # | mechanism | A resolvable | A's input missing |
|---|---|---|---|
| 0 | naive, no constraint (input fn raises `KeyError` on baseline ids) | builds (`A 1 / B 4`), prints `InputFunctionException` tracebacks, exit 0 | **`CyclicGraphException`** |
| 0b | naive, total input fn (`DERIVED.get(sid,'001')`) | builds (`A 1 / B 4`) | **`CyclicGraphException`** |
| i | `wildcard_constraints: sid=r"00[3-6]"` — id-regex partition; requires baselines to be a contiguous prefix block | builds | clean `MissingInputException` — works |
| i-c | `wildcard_constraints: sid="\|".join(derived_ids)` — explicit alternation, **no partitionability needed** | builds | clean `MissingInputException` — works |
| ii | `ruleorder: A_plural > B_wildcard` | builds | **`CyclicGraphException`** — fails |
| iii | separate directories (`base/` vs `pert/`) | builds | clean `MissingInputException` — works |
| iv | one rule, branching `input:` function (`[]` for baselines) | builds (`make_scenario 6`) | clean `MissingInputException` — works |

*Scaling.* The alternation constraint does **not** blow up DAG construction at
realistic size — it is cheaper than the loose one, because it prunes candidate
producers rather than enumerating them:

| Snakefile, 500 ids | wall (incl. pixi startup) | outcome |
|---|---|---|
| `Snakefile_big_alt` (490-alternative constraint) | **2.7 s** | exit 0, `A_plural 1 / B_wildcard 490 / total 492` |
| `Snakefile_big_loose` (`[0-9]{3}`) | **9.5 s** | exit 0, but 490 `InputFunctionException` tracebacks printed |
| `Snakefile_big_alt_miss` (alternation, A unresolvable) | 3.6 s | exit 1, clean `MissingInputException` |

**The measured collision with the intake's seam spec.** Every mechanism that
constructs — (i), (i-c), (iii), (iv) — requires stage 2 to know **which ids are
baselines, at parse time**: (i) needs the block bounds, (i-c) needs
`"|".join(non_baseline_ids)`, (iii) needs to route each id to `base/` or `pert/`,
(iv)'s branching function tests `w.sid in BASE_IDS`. The only two mechanisms that
need no such knowledge — 0 and `ruleorder` — are the two that fail. So the intake's
1→2 seam spec, *"`scenario_id` + its forcing. Two columns"*, is **insufficient under
every mechanism measured to work.**

**Verdict** — **feasible with stated conditions. The single-id scheme does not
force a structural change to the 3.11/3.12 boundary, but it does force an explicit
replacement mechanism.** The constraint cannot survive as written:
`member_index_regex(ST_WIDTH)` is a statement about the `st_num` token, and that
token is gone. `ruleorder` is **not** a valid replacement — measured failure.

The verdict is about the **rule boundary**; the cost lands on the **seam contract**.
3.11 and 3.12 can stay two rules, but the two-column seam cannot stay two columns.

Minimal changes, in increasing structural cost:

- **(i-c) explicit alternation constraint** — cheapest, and the only regex form that
  works for an *arbitrary* baseline id set. It is parse-time-derived
  (`"|".join(non_baseline_ids)`), so it needs the id set at parse time, which P1
  confirms is available. **No structural change.**
- **(i) reserved low block** — constrain 3.12's id to exclude ids `0..RLZ_NUM-1`.
  Cheap, but it **hardcodes a reserved baseline id range into the DAG**, which is
  precisely what scope gap 5 / W3 says must not be foreclosed. With RLZ_NUM > 1 a
  single reserved id does not suffice, so this collapses into (i) plus a numbering
  convention. Not recommended.
- **(iii) separate directories** — `{wg_dir}/output/baseline/` vs `perturbed/`.
  Robust and self-documenting, but a seventh path move, and it re-introduces a
  family-specific concept ("baseline") into a directory name at the stage-2 seam.
- **(iv) one rule** — collapses 3.11 and 3.12 into one rule whose input function
  returns `[]` for a baseline id. Structurally cleanest under a family-blind seam,
  and the only option in which stage 2 has no baseline/perturbed distinction at all.
  But 3.11 is an R weathergenr call producing all realizations in **one** job and
  3.12 is a per-member R call, so this is a workflow restructure, not a rename.

**NOT PROBED — the shape that keeps the seam family-blind.** A third seam column,
nullable `derived_from` (`scenario_id`, forcing, `derived_from`). Stage 2's input
function then reads "this row's forcing derives from that row's output, or from
nothing" — a **dependency edge**, not a baseline concept — so stage 2 acquires no
family-specific knowledge and W3 is not foreclosed. Mechanically it is mechanism
(iv) with the branch driven by data rather than by a `BASE_IDS` set, and (iv) was
measured to work; but the `derived_from` form itself **was not run**, and it is the
shape the design should evaluate first.

**What this constrains in the design**

1. The design must **name its replacement mechanism explicitly** and gate it. Not
   naming one means silently taking mechanism 0, which fails on a fresh project —
   i.e. on a first run, which is exactly when a new scheme is first exercised.
2. **`ruleorder` is measured not to work.** Remove it from the option set.
3. The gate must be a **fresh-project** DAG build, not a dry-run on a seeded tree.
   `tests/test_guard_invalidation.py` is the observation that falsifies the claim;
   `--dry-run` on `test_local` is not.
4. (i)/(i-b) buy cheapness by hardcoding a reserved baseline id range — a direct
   collision with W3. (i-c) expresses the same partition as **data** rather than as
   a reserved range, which is better, but it is still stage 2 holding a
   family-specific distinction; it does not exempt (i-c) from decision criterion 1.
5. **The 1→2 seam needs a third column, or an equivalent.** Two columns cannot
   express what every working mechanism needs. `derived_from` is the candidate that
   pays this without naming a baseline; it is unmeasured.

## Incidental findings

- **Snakemake's parser rejects multi-line parenthesised expressions inside a rule
  directive**: `input: (expand(...)\n + expand(...))` raised
  `SyntaxError: Expecting rule keyword, comment or docstrings inside a rule
  definition`, and a multi-line `if/else` inside a directive raised
  `Unexpected keyword else in rule definition`. Both had to be hoisted to
  module-scope helpers. Relevant if a design sketch shows multi-line `input:` blocks.
- **The default target is the first rule in the file.** A `checkpoint` declared
  above `rule all` silently became the target: the run reported
  `1 of 1 steps (100%) done`, produced nothing else, exit 0; the next invocation
  said `Nothing to be done`. Another silent-success shape.
- **Snakemake 9.6.2 tolerates a raising input function during DAG construction.**
  Mechanism 0 printed six `InputFunctionException` / `KeyError` tracebacks and still
  exited 0 with a correct DAG, suggesting `--strict-dag-evaluation` in the message.
  A design relying on an input function raising to disqualify a rule is relying on
  non-strict mode.
- `test_case/test_rapid` is **not seeded in this worktree**, so no WF3 dry-run under
  `snake_config_rapid.yml` reaches rules 3.11/3.12. The seeded tree here is
  `test_case/test_local` (baseline config). An implementation gate for this milestone
  specified as "rapid" will not run in a fresh worktree.
- `config/catalogs/cmip6_data.yml` and `cmip6_store_index.json` are **generated and
  tracked** (`git ls-files`), which is how `analyze_projections.smk`'s unguarded
  parse-time read bootstraps. A live precedent for P1's supplied-file path.

## Environment

- pixi 0.70.2; Snakemake 9.6.2; Python 3.12.13 (conda-forge), win-64.
- `profiles/default/config.yaml` auto-loaded (`quiet: reason`) for the real-workflow
  invocations; not for the standalone scratch Snakefiles, which were run from the
  scratch directory.
- Configs: `test_case/snake_config_rapid.yml` attempted first (recorded above);
  `test_case/snake_config_baseline.yml` used for the P2 control and mutation because
  `test_case/test_rapid` is unseeded in this worktree.
- Scratch: `.tmp/scratchpad/2026-09-06_probe/{p1,p2}/` in the worktree
  `.worktrees/blueearth_cst/session-3` (gitignored).
- Git status at finish: `?? dev/working/design-runs/` only — **no modifications to
  tracked files**. `run_stress_test.smk` was mutated for the P2 reproduction and
  restored with `git checkout -- run_stress_test.smk`.
