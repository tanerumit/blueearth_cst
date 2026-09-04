# Intake — WF3 in three stages: scenario space, simulation, metrics

> **Stage-0 intake. No design exists yet.** This is the scope authority a
> `design-review-loop` run would work under: what was declared *before* any
> drafting — the scope gaps, the owner constraints, the decision criteria, the
> non-goals, the evidence register, the feasibility probes, the
> gate-materialization check and the derived-artifact register.
>
> **Revision 2, 2026-09-04** — same day as revision 1, before any design run
> opened. Revision 1 proposed a single registry table carrying provenance *and*
> bundling. The owner replaced that with a three-stage decomposition in which no
> one table solves everything; the reasoning review's blocking finding (RR-1)
> dissolved as a result. Once a design run opens, this file stops being edited.
>
> **Revision 1 is readable at commit `2d7dbeed`, and it matters** — the reasoning
> review (RR-1 .. RR-7 below) was filed against *that* framing, not this one. Its
> dispositions here describe what revision 1 proposed, so a reader judging whether
> a disposition is fair needs the text it disposed of:
>
> ```
> git show 2d7dbeed:dev/milestones/r12/simulation-identity-intake.md
> ```
>
> Specifically, revision 1's registry carried a single `group_id` column and its
> scope gap 4 asked how pooled rows were keyed. E9 is why that failed. This is the
> same reason `sealed-records.yml` exists — a superseded position is only
> checkable while it is still legible — with the difference that a pre-design
> intake revision is cheap enough to leave in history rather than in the tree.

Stage 0 of a prospective `design-review-loop` run, slug `wf3-simulation-identity`.
Driver-authored; **no design content here**.

## The change request

Assembled from one conversation, 2026-09-04. The final framing is the owner's
three-stage decomposition:

> I think that we need to separate the process in several phases..
>
> 1. forcings (N scenarios) -> 2) simulated impacts (response variables for N
>    scenarios) -> 3) metrics (may be for a reduced set, e.g., bundled scenarios,
>    depending on the nature of the metric/user preference).
>
> - Lets try to divide the problem: we do not need a single table/shape to solve
>   everything.
> - We first need to map scenario space. Then tell the simulator (in this case
>   wflow) how to loop over scenarios and spit out the results.
> - Once the results are out, we then need to compute metrics.

and, on what the simulator is entitled to know:

> If the user is bringing their own scenarios, or perhaps, scenarios are
> downscaled from GCM time-series, the scenario file should be supplied to the
> simulator (wflow).
>
> Simulator only needs to know: -> calibrated model -> scenario table (different
> forcings, or later on, model configurations). It can then enumerate over the
> rows of the table and produce outputs. The output file names carries
> scenario_ids, not specific columns (e.g., rlz_1_st_2).

The motivating requirement, stated earlier in the same conversation, is to be able
to admit other scenario families later — user-supplied series, or scenarios
downscaled from GCM time series — which have no realization index and no
perturbation-grid point. **Building that family is not in scope here** (see
Non-goals); not precluding it is.

## Problem

WF3 fuses the three stages, and the fusion is expressed as a **composite run
identity**: the ordered pair `(rlz, st_id)`. That pair presumes the scenario set
is the factorial expansion of a sampled axis and a designed axis. Four costs
follow.

1. **A non-factorial scenario set cannot be expressed.** A user-supplied or
   GCM-downscaled scenario set is a flat, ragged list. There is no assignment of
   such a set into `(rlz, st)` that is not a lie.
2. **Identity is recovered by parsing a filename.** `export_wflow_results.py:79`
   holds `_MEMBER_IN_STEM = re.compile(r"^rlz_(\d+)_st_(\d+)$")`;
   `member_from_run_csv` raises `ValueError` on any stem that does not match. The
   post-processor's contract with the simulator is a **string spelling**. This one
   function is the concrete reason another family cannot be admitted.
3. **Bundling is inferred from the identity, and the identity can only express one
   bundling.** The reduction pools by "same `st_id`, all `rlz`" because that is
   what the composite id makes reachable. But two bundlings already coexist in the
   same output — Class A is per realization, Classes B and C pool across them — so
   bundling is a property of the *metric*, not of the scenario set. The identity
   cannot carry that, and neither could a single grouping column.
4. **The identity scheme is already leaking.** `indicator_tables.py:136` carries
   `POOLED_REALIZATION = 0`, an out-of-band value written into the numeric
   `rlz_id` key column, with its own comment recording the fragility: *"safe ONLY
   because no metric emits both grains; if that ever changes it must become a
   string, or `groupby("rlz_id")` folds pooled rows in as another realization."*

Meanwhile the execution layer has already flattened itself and has no word for
what it iterates. Rule 3.15 (`run_stress_test.smk:1216-1241`) is a generated rule
per batch with **no wildcards**; it slices a flat Python list (`_k_members`,
`:1120`) and keys its log and benchmark by batch id. `(r, c)` survives inside it
only to spell filenames.

## The three stages, and what each owns

| stage | produces | knows about |
|---|---|---|
| **1 — scenario space** | the scenario table: what scenarios exist and what each one *is* | the scenario family and its own columns. The only place family-specific columns live |
| **1→2 seam** | the run list the simulator enumerates: `scenario_id` + its forcing | nothing about the family. Two columns |
| **2 — simulation** | one raw output per `scenario_id`, named by it | the built model and the run list. Nothing about what produced the forcing |
| **3 — metrics** | indicator tables, at each metric's own grain | the raw outputs, the scenario table (for labels), and each metric's declared grain |

The 1→2 seam is a **view** of stage 1, not necessarily a separate file. It is named
because it is the contract that makes the simulator family-blind: it is what
guarantees stage 2 cannot acquire a dependency on `rlz` or `st_id`.

**One row is one run.** If model configuration later becomes columns of the same
table (owner, 2026-09-04), a row is still exactly one simulation, so the identity
holds without redefinition.

**Grain lives in stage 3.** Whether a metric is computed per run or over a bundle
is a property of the metric, declared there — not a column of the scenario table
and not a consequence of which loop the code happens to sit in.

## Artifacts at issue

Everything spelled `rlz_<r>_st_<m>` on the run path today:

| stage | artifact | producer |
|---|---|---|
| climate series (baseline) | `{wg_dir}/output/rlz_<r>_st_0.nc` | 3.11 `generate_weather_realizations` |
| climate series (perturbed) | `{wg_dir}/output/rlz_<r>_st_<m>.nc`, `m ≥ 1` | 3.12 `perturb_climate_realization` |
| model forcing | `{runs_dir}/forcing/inmaps_rlz_<r>_st_<m>.nc` | 3.14 `downscale_climate_realization` |
| model config | `{runs_dir}/config/rlz_<r>_st_<m>.toml` | 3.14 |
| per-member catalog (WG-5) | `{runs_dir}/config/rlz_<r>_st_<m>.yml` | 3.14 |
| **model output** | `{runs_dir}/output/rlz_<r>_st_<m>.csv` | 3.15 `run_wflow_batch_<b>` |

## Scope — what this design must close

Eight gaps. None re-opens an owner ruling; three require *superseding* prior
accepted change requests, which is itself in scope.

| # | Gap | Why it blocks implementation |
|---|---|---|
| 1 | **The three artifacts have no schemas.** The scenario table, the seam view, and what stage 2's raw output is keyed by | Everything else is downstream |
| 2 | **`scenario_id`'s form is unruled.** It must be stable under set growth — adding realizations or resizing the grid must not renumber existing runs (C24 reason 2, which survives). That excludes a sequential integer. Opaque-vs-readable is genuinely open, and C25 already rejected content-hashed ids once as "opaque and unsortable" | The id appears in six filenames, a catalog key and a tree inventory; renaming it later is a second migration with a second baseline re-record |
| 3 | **Where the scenario table is written, and by what.** For the stochastic family it should be computable from config before the DAG is built, as `stress_test_grid()` is today; an externally supplied family would provide it as a file | C26's chicken-and-egg is live: Snakemake needs the id set at DAG-construction time, before any rule has written a file. Getting this wrong reaches for a checkpoint, which is a large complexity jump |
| 4 | **Each metric's grain must become explicit**, and the index table that explains it must be specified. Today grain is emergent — a metric is pooled because of which loop it sits inside. Class A is per realization; Classes B and C pool across them and are written with `st_id` + the `POOLED_REALIZATION` sentinel | The indicator table carries two grains permanently: a return level is not the mean of per-run return levels, so for that metric the finest grain that exists *is* the bundle. W2 sets the direction — one index column, meaning explained elsewhere — and leaves the design to specify the index table, the mixed namespace's validation, and each metric's declared grain |
| 5 | **The baseline relation is implicit and family-specific.** `st_0` is a stochastic-family concept used as universal: `_category_month` fixes the wet and dry month once from `runs[0]` and evaluates every member against it | **DEFERRED by owner ruling (W3)** until a second scenario family exists to test against. Kept as a gap, not dropped, because the design must not settle it by accident — a `scenario_id` scheme that hardcodes a reserved baseline id forecloses the question. **Correction to revision 2:** deferral is cheaper than stated there — the scenario table is *not* among the seven baseline targets (`q_indicators.csv` is; its predecessor `stress_test_design.csv` never was, per the R11 ruling), so adding a baseline column later costs a contract and validator change, not a re-record |
| 6 | **Record length is an unstated estimator precondition.** The Class B GEV is fitted on `RLZ_NUM × N` blocks *because* a fit over one short realization is ill-conditioned | Not a defect today. It becomes one the moment a second family shares the table under the same metric name |
| 7 | **Three contract clauses change.** WG-2 pins `rlz_<n>_st_<m>.nc` as a **DAG-globbed naming pattern** in its *pinned surface*; WG-5 pins one catalog entry per `rlz_<n>_st_<m>`; HM-7 pins the five indicator columns | A contract document here is normative, not descriptive |
| 8 | **C24, C25 and C28 must be superseded, not edited**, and the migration executed atomically. `wf3-change-requests.md` is in `dev/reference/sealed-records.yml`; `tests/test_sealed_records.py` fails any edit. Six artifact paths move, `naming.md` §7 requires a migration note, and `semantic_tree_diff.py`'s inventory moves with them | The mechanism is a new decision record arguing reason-by-reason. A tree-shape change the fixture-dependent test layer cannot catch in a worktree |

## Constraints — settled, not open for review

| Constraint | Source |
|---|---|
| **Three stages, three contracts. No single table solves everything** | Owner, 2026-09-04 |
| **The simulator knows only the built model and the run list.** It enumerates rows and writes outputs named by `scenario_id`, never by family-specific columns | Owner, 2026-09-04 |
| **Bundling is a property of the metric, resolved at stage 3** — not a column of the scenario table | Owner, 2026-09-04 |
| **Build for the current bottom-up assessment; do not define every possible scenario family up front** | Owner, 2026-09-04 |
| **Stress-test scenarios come from the stochastic weather generator; the experiment workflow is never coupled to CMIP scenarios.** The perturbation grid stays scenario-neutral | `AGENTS.md` § Background |
| **CMIP6 output is a plausibility overlay only.** It never drives a stress-test run | `AGENTS.md` § Background |
| **No local calibration.** The model instance is what WF1 built from global data; "the built model", not a calibrated one | `AGENTS.md` § Background |
| Repo-wide: this is the workflow engine only; hydromt / wflow conventions used verbatim, never re-engineered | `AGENTS.md` § Hard Constraints |

**The scenario-neutrality constraint still needs pricing.** The decomposition makes
stage 2 family-blind, which is the point. But a future GCM-derived run plotted
against the response surface needs a position on the temperature/precipitation
plane, and that position is a change-factor computation. The intended answer is
that such coordinates are *columns supplied by stage 1*, computed by whatever
produced the scenarios, so stage 3 reads them rather than deriving them — keeping
CMIP logic out of WF3 entirely. That answer is recorded here so it is reviewed
rather than assumed; it is not yet ruled.

## Working direction — initial, NOT settled

**Read this section differently from the one above it.** The constraints table is
ruled and closed. What follows is the owner's stated *initial direction*, given
2026-09-04 with the explicit qualifier: *"these are not definite decisions. These
are my initial thoughts. We shall solidify along the way."* A design run may test
these, argue against them, and bring back a different answer — which is exactly
what it is for. It may **not** silently ignore them.

| # | Direction | Why it is provisional |
|---|---|---|
| W1 | **Pooled and per-run values share one results file.** No split into two tables | Confirmed by the owner as fine; the alternative was offered and declined. Low risk of reversal |
| W2 | **The results file carries the results plus ONE index column, and nothing else.** What an index *means* — a single run, or a bundle of runs — is explained in a separate table. `metric, location, scenario_id, value`, four columns, no blanks and no grain column | The strongest of the four, and it improved on the driver's own preference. Held provisional because it constrains a baseline-covered artifact and the id namespace at once (below) |
| W3 | **`st_0` and the baseline relation stay OPEN**, deliberately, until there is a second scenario family to test against | The owner's ruling is to defer, not to decide either way. Recorded as deferred so a design run does not treat silence as licence to settle it |

**W2's consequence, which the design must confirm rather than inherit.** One index
column holding both run ids and bundle ids means a **single mixed namespace**. That
is only safe if:

- every id in the results file resolves in the index table, checked by the HM-7
  validator rather than assumed;
- run ids and bundle ids are distinguishable *on sight*, which argues for readable
  prefixed strings and against an opaque or numeric id — so W2 and scope gap 2 are
  one decision, not two;
- nothing downstream `groupby`s the index column directly. The join comes first,
  the grouping second.

The driver's own preference had been two columns (`scenario_id` + `group_id`, blank
when pooled). It is recorded here as the rejected alternative, with its stated
objection to W2 — *"the key is polymorphic"* — noted as **withdrawn**: the
polymorphism is resolved in one explicit artifact rather than smuggled into the
results file, which is a materially different thing.

## Decision criteria

1. **The simulator must be family-agnostic.** If admitting a second family requires
   editing stage 2, the seam is in the wrong place.
2. **No identity recoverable by string parsing.** A spelling is not a contract.
3. **The id must be stable under set growth.** Adding realizations, resizing the
   grid, or admitting a family must not renumber existing runs.
4. **Grain is declared, never a sentinel.** Nothing may reuse a key column to mean
   two things.
5. **Store the finest grain, derive every summary** — the principle the accepted
   lookup-table design established, applied one level up. Stage 2's raw output is
   the finest grain; every metric is a declared derivation over it. The exception
   is real and must be stated: for a pooled estimator the finest grain that exists
   is the bundle.
6. **Parse-time derivability over a checkpoint.** The stochastic family's scenario
   table stays a pure function of config.
7. **The migration is one atomic rename plus a shape change**, every live reference
   updated in the same commit, with a documented rollback.
8. **Gate-ability.** Every claimed runtime property needs an observation that would
   falsify it.

## Success criteria

- All eight scope gaps closed in normative text, not sketch.
- Schemas for the three artifacts, with the family-specific columns of the
  scenario table explicitly labelled as such — so a later split into per-family
  tables is a file split, not a redesign.
- A superseding decision record under `dev/decisions/` arguing C24 reason-by-reason
  and stating C25's and C28's triggers, without editing the sealed record.
- Replacement contract text for WG-2, WG-5 and HM-7.
- A migration note satisfying `naming.md` §7.
- A claim → falsifier table handed to `task-brief`.
- A stated position on whether this subsumes the dropped `t2608082036`, and on what
  happens to `member_hash` (design-v4's identity) under a minted `scenario_id` —
  the two may be the same object arriving from opposite directions.

## Non-goals

- **Building a second scenario family.** No GCM producer, no downscaling path, no
  config surface for one. The design must *accommodate* a second family; shipping
  one is a separate milestone. A design that ships a speculative family has
  overreached.
- **Model configuration as a scenario column.** Named by the owner as a later
  extension. The design must not preclude it — one row stays one run — but it adds
  no such column now.
- **A user-facing config surface for metric grain.** The minimum is that grain
  becomes an explicit, named property of each metric *in code*. Promoting it to
  configuration is a separate, later decision.
- **The wf3 file split itself.** The three stages are the *motivating* framing, and
  this design makes them **separable** — three contracts, a family-blind seam, no
  stage reaching into another's columns. It does not **separate** them: WF3 stays
  one `.smk` file, no workflow entry point is added or removed, and the stage
  boundaries are contracts rather than files. Splitting the file is a later
  milestone that this one makes cheap.
- **The response-surface plotting change.** That a surface becomes family-gated
  follows from the schema; specifying the plot does not.
- **R12's execution model** — manifest, ledger, resumable sweeps, epochs,
  quarantine, atomic publication. Related, possibly reordered by this, not authored
  here.
- **Fixing `st_0`'s comparability** — `t2608151154`, `origin: R12`, untouched.
- **Re-opening the perturbation grid's scenario-neutrality.** Out of bounds.
- Any change to CST-API, CST-frontend, or `csthelpers`.

## Evidence register

Empirical premises the design leans on. Falsity of any row changes a decision.

| # | Premise | Source | Exact observation | Reproduction | Confidence |
|---|---|---|---|---|---|
| E1 | Post-processing recovers run identity by regex over the output CSV's filename stem | `export_wflow_results.py:79-92` | `_MEMBER_IN_STEM = re.compile(r"^rlz_(\d+)_st_(\d+)$")`; `member_from_run_csv` raises `ValueError` on a non-matching stem | Read the function | **Verified** 2026-09-04 |
| E2 | The batch rule carries no wildcards and iterates a flat member list | `run_stress_test.smk:1120, 1216-1241` | `_k_members` is a flat list comprehension; the generated rule builds `input`/`output` as static Python lists; log and benchmark keyed `batch_{_b}` | Read the rule | **Verified** 2026-09-04 |
| E3 | Rules 3.12 and 3.14 still carry `{rlz_num}` / `{st_num}` wildcards | `run_stress_test.smk:1004-1069` | The flattening is true of the simulator rule only — which is where the seam is drawn, so the argument holds with its scope stated | Read both rules | **Verified** 2026-09-04 (reasoning review correction) |
| E4 | C24 ruled explicitly against a single id, on four reasons | `wf3-change-requests.md:640-646` | "two id spaces, not one… Run identity stays `(rlz, st)`", citing pooling, renumbering, batching-by-wildcard, log legibility | Read the section | **Verified** 2026-09-04 |
| E5 | C24 reason 3 has expired | E2 vs `wf3-change-requests.md:645` | The reason names "the P3-3 batching work groups by realization via wildcard patterns"; the landed batch rule has none | Compare | **Verified** 2026-09-04 |
| E6 | C24 reason 4 has expired | `run_stress_test.smk:1238-1240` | Logs are keyed by batch id; the member span is a console banner string, not the log's identity | Read the rule | **Verified** 2026-09-04 |
| E7 | The indicator table is five columns and carries both member indices | `indicator_tables.py:126-132` | `INDICATOR_COLUMNS = ("metric", "location", "st_id", "rlz_id", "value")` | Read the constant | **Verified** 2026-09-04 |
| E8 | A derived grain is expressed as a sentinel inside a key column | `indicator_tables.py:133-136` | `POOLED_REALIZATION = 0`, with an inline comment stating it is safe only while no metric emits both grains | Read the constant | **Verified** 2026-09-04 |
| E9 | **Two bundlings already coexist in one output.** Class A is per realization; Classes B and C pool across realizations at one design point | `export_wflow_results.py:384, 405-426, 431-441` | Class A emits per-`rlz` rows; B and C emit `(st_id, POOLED_REALIZATION)` rows | Read the three emit blocks | **Verified** 2026-09-04 — this is why grain cannot be one column of the scenario table |
| E10 | The reduction pools *within* realization deliberately, for a stated methodological reason | `export_wflow_results.py:40-46, 233-234` | Annual minima are extracted within each realization and the blocks pooled, because a synthetic continuous index across realizations manufactured 7-day flows occurring in no realization | Read the docstring and function | **Verified** 2026-09-04 |
| E11 | The Class-C month is fixed once from `st_0` and applied to every member | `export_wflow_results.py:356-365` | `if q_locations and 0 in runs:` … `_category_month(baseline, "wet"/"dry")`, with the Q5 comment "pick from st_0, then evaluate that month for every member" | Read the block | **Verified** 2026-09-04 |
| E12 | The GEV fit's precision is a function of realization count, and that is the stated reason for pooling | `export_wflow_results.py:27-35` | "a GEV fit over one short realization is ill-conditioned; pooling multiplies the block sample by" the realization count | Read the docstring | **Verified** 2026-09-04 |
| E13 | WG-2 pins the member naming pattern as part of its *pinned surface* | `weather-generator-seam.md:238-245` | "naming pattern: `rlz_<n>_st_<m>.nc` — a DAG-globbed pattern"; repeated under "pinned surface" | Read WG-2 | **Verified** 2026-09-04 |
| E14 | WG-5 pins one catalog entry per member, including `st_0` | `weather-generator-seam.md:260-277` | "one entry per `rlz_<n>_st_<m>` (**including `st_0`**)", one catalog per member, `temp()` | Read WG-5 | **Verified** 2026-09-04 |
| E15 | C28 kept `st_id` denormalized *provisionally*, with a named revisit trigger | `wf3-change-requests.md` § C28 | Ruled 2026-08-05 "at this stage", against the recommendation, with "an explicit revisit when a third dimension arrives" | Read the section | **Verified** 2026-09-04 |
| E16 | `t2608082036` (the WF3 v2 re-derivation) was dropped, and eight references survive it | `dev/LOG.md:47` | Dropped 2026-08-18 by owner ruling; the row names all eight and states the *item* was dropped, not the work abandoned | Read the row | **Verified** 2026-09-04 |
| E17 | A sequential id renumbers the set when `RLZ_NUM` or the grid changes | C24 reason 2, `wf3-change-requests.md:643` | Argued, not measured — but it is arithmetic over a cross-product, so the failure is structural | Construct two configs differing only in `realizations_num` | **HYPOTHESIS — structural, not executed** |
| E18 | A user-supplied or GCM-downscaled scenario set is not expressible as `(rlz, st)` | The change request | Argued from the shape of such a set; no such set exists in this repo to test against | — | **HYPOTHESIS — asserted, no artifact exists.** Recorded so a reviewer prices it rather than inherits it |
| E19 | Plotting a GCM-derived run on the T × P plane requires its (ΔT, ΔP) | Reasoning review argument, not code | Not a model output; it would have to be derived from the GCM series, which is WF2's change-factor computation. The intended answer is that stage 1 supplies it as columns | — | **HYPOTHESIS — argued at intake.** Load-bearing for the scenario-neutrality question |
| E20 | `member_hash` (design-v4 §5.1) and a minted `scenario_id` may be the same object | `design-v4.md:987` at tag `archive/wf3-experiment-v2` | `member_hash` is a stable-under-growth identity over the member tuple; whether it can *serve* as the id, or must stay a separate freshness column, is undetermined | `git show archive/wf3-experiment-v2:dev/working/design-runs/wf3-experiment-v2/design-v4.md` | **OPEN QUESTION — not a premise** |

## Reasoning review at intake — findings

A method-layer review of the change request's reasoning was dispatched before
stage 1 (Fable 5.1, `critical-thinker`, 2026-09-04), asked to critique the science
and method rather than the mechanics. It reviewed **revision 1's** single-registry
framing. Verdict then: *the seam is drawn in the right place; the table on the far
side of it is wrong as sketched.*

The three-stage decomposition that followed **dissolves its blocking finding**
rather than answering it. The dispositions below are stated against the current
framing.

| # | Finding | Class | Disposition under the three-stage framing |
|---|---|---|---|
| RR-1 | Pooled Class B/C values are keyed by group, not by run, and have no row shape under an id-only table | **Structural error in revision 1** | **Dissolved.** Revision 1 put one `group_id` in the registry, which cannot express two coexisting bundlings (E9). Moving grain to stage 3 as a declared property of each metric removes the conflict. What survives is gap 4: the indicator table still carries two grains permanently, and must key both without a sentinel |
| RR-2 | Baseline comparability crosses the seam: `st_0` is a stochastic-family concept used as universal | **Method** | **Accepted as scope gap 5, then DEFERRED by owner ruling (W3)** — the finding stands and is not disputed; settling it waits for a second family to test against. The design's obligation narrows to not foreclosing it |
| RR-3 | Record length is an unstated estimator precondition; a 30-year horizon and a multi-realization cell share a metric name with no column recording precision | **Method** | **Accepted** — scope gap 6 |
| RR-4 | The composite identity carried a *structural guarantee* of a full factorial (common random numbers across design points); a column carries the information but not the guarantee | **Method, partly pre-existing** | **Accepted as decision criterion 8 and a stage-1 obligation** — the scenario table must make an incomplete set detectable. Noted honestly: the batch rule already degraded per-member completeness, so the cost predates this change |
| RR-5 | Plotting a GCM run as an overlay point still requires its (ΔT, ΔP), which is WF2's change-factor computation re-entering WF3 | **Method — bears on a hard constraint** | **Accepted as E19 and an unruled position.** The intended answer is that stage 1 supplies the coordinates as columns; the design must rule it, and family-gate the surface reduction |
| RR-6 | "Nothing parses it" (a consumer contract) and "semantically empty" (a string property) are different choices, conflated in the request. A readable unparsed composite satisfies every raised constraint and keeps the outputs folder sortable | **Taste, with a real regression** | **Accepted into scope gap 2**, and why C25 joined the supersession set |
| RR-7 | The motivating family does not exist, so a general registry schema is underdetermined and risks being frozen wrong | **Process** | **Largely answered by the owner's scoping ruling** — build for the current assessment, do not define every family up front. What remains is the success criterion that family-specific columns be *labelled*, so a later split is a file split rather than a redesign |

**The strongest fair statement of the case against**, recorded so the design answers
it rather than inherits it: *the composite identity is the experimental design
expressed in the type system; the proposal moves the design into data, for the
benefit of a family whose comparability semantics nobody has written down.* The
three-stage split narrows this — stage 2 is family-blind on its own merits, and
stage 3's grain becomes explicit whether or not a second family ever arrives — but
it does not eliminate it.

**Questions the design must answer.**

1. **Direction given (W2), specification open.** One index column, meaning explained
   in a separate table. What is that table's schema, how is the mixed run/bundle
   namespace validated, and how does each metric declare its grain?
2. **Deferred (W3).** The baseline relation and `st_0`'s status wait for a second
   scenario family. The design's obligation is only to *not foreclose* it.
3. How does stage 1 make an incomplete scenario set detectable?
4. Are a future family's overlay coordinates supplied by stage 1, and does that
   satisfy "never couple WF3 to CMIP scenarios"?
5. Opaque id or readable unparsed composite — and does the answer dispose of C25?

## Framework-feasibility probes

Mechanisms whose feasibility depends on Snakemake execution semantics. Each needs a
probe with a recorded result, **not a paragraph of prose**.

| Probe | Question | Why prose cannot settle it |
|---|---|---|
| P1 | Can the scenario table be read at DAG-construction time from a config-derived pure function *and*, alternatively, from a supplied file, without a checkpoint? | C26's chicken-and-egg is why the current design table exists in its form; the supplied-file path is new and is the whole point of the change |
| P2 | Does renaming `rlz_<r>_st_<m>` to a single id disturb rule 3.12's `wildcard_constraints`, which exist to stop a `CyclicGraphException` between 3.11's and 3.12's output patterns? | The constraint (`st_num ≥ 1`, `:1005-1018`) is load-bearing for DAG construction and is expressed over a token this change removes |
| P3 | Does 3.14's per-member WG-5 catalog still resolve when its key is the new id, given hydromt reads the catalog by key? | The catalog is an upstream schema we emit into; a key-shape change is where a pinned-as-reliance surface bites |
| P4 | Does the stage-3 metric spec re-fire the reduce when it changes? | The `ancient()`/no-`params:` trap is live in this workflow (rule 3.09 is deaf to `stress_test` edits) and a new declared input inherits the same hazard |
| P5 | Does `pixi run tree-check` classify the renamed tree, and does `build_project_tree_rules` need extending in the same commit? | The inventory is code, not a snapshot; a stale entry reports undeclared on every future run |

## Gate materialization

| Gate | Verdict | Detail |
|---|---|---|
| `pytest tests/test_export_wflow_results.py`, `test_interchange_contracts.py`, `test_indicator_tables.py` | **Runnable** | The narrow tier; these own the changed surfaces |
| `pytest tests/test_cli.py` | **Runnable, required** | Rules' declared inputs and outputs change shape |
| `pixi run test-full` | **Runnable, required at merge** | Touches a Snakefile, a `script:` signature *and* `shared/` — the `workflow_contract` and `process_isolation` tiers |
| `pixi run tree-check` | **Runnable, needs a code change with the design** | Six artifact paths move; `build_project_tree_rules` must land in the same commit. `build_r09_path_map` stays frozen |
| `pytest tests/test_sealed_records.py` | **Runnable, and a constraint rather than a check** | It fails any attempt to edit C24/C25/C28 in place. The design must supersede, not edit |
| `check_baseline.py check` | **NEEDS A PRE-CHANGE RE-RECORD** | Every WF3 target path moves, so the gate fails by construction. A re-record must land **before the first implementation commit**, from `snake_config_baseline.yml`, in the primary checkout, `--notemp` on WF1, no other session live. A comparison gate cannot be applied retrospectively — the R12 lookup design's R1, verbatim |
| `validate_wg2` / `validate_wg5_catalog_grid` / `validate_hm7` | **Change with the design** | Part of the deliverable, not independent checks. All three assert the `rlz_<n>_st_<m>` shape |
| The fixture-dependent test layer | **Cannot run in a worktree** | It skips rather than fails, and this is a tree-shape change — the case `AGENTS.md` records as surviving every gate a branch can run. Implementation gating must happen in the primary checkout, on a seeded fixture |

## Derived-artifact register

Artifacts that derive from this design and go stale the moment review changes it.
**Author spawns are barred from touching them**; each is regenerated from the
accepted version after G2.

| Artifact | Regenerated by |
|---|---|
| `dev/decisions/00NN-*.md` (new) | Author from the accepted design — the C24 / C25 / C28 supersession |
| `dev/reference/contracts/weather-generator-seam.md` (WG-2, WG-5) | Replace the naming-pattern and catalog-key clauses |
| `dev/reference/contracts/hydrological-model-seam.md` (HM-7) | Replace the column contract |
| `dev/reference/naming.md` §4 (member token) and §7 (migration record) | Author from the accepted design |
| `dev/reference/workflows/rule-index.md` | Regenerate the 3.11 / 3.12 / 3.14 / 3.15 / 3.16 rows |
| `dev/scripts/semantic_tree_diff.py` `build_project_tree_rules` | Extend with the new tree; `build_r09_path_map` frozen |
| `dev/baseline/manifest.json` | Re-record before the first implementation commit, then again after |
| `dev/roadmap.md` § R12 | Rewrite — this changes what R12 is, and E16's eight dangling references need repointing or an explicit abandonment |
| `dev/tasks/` — a new board item; `t2608151154` if `st_0`'s treatment moves | Board rewrite from the accepted design |
| The `task-brief` for implementation | Stage 7 handoff, with the claim → falsifier table |

## Genre mapping

`workflow-spec` — it specifies artifacts, stage boundaries and three data contracts
inside one workflow. It carries a **method component**: whether a hydrological
simulator is legitimately indifferent to the provenance of its forcing, and what
that indifference costs at the reduction. That component is why the run needs a
method-literate reviewer and not only a repo-fit one.

## Seeding

No prior note to seed from. Stage 1 authors from this intake, the stage table and
artifact table above, and two external inputs:

- `dev/milestones/r12/wf3-experiment-v2-design-review-record.md` — the surviving
  architecture list, and `member_hash` in particular (E20).
- `design-v4.md` §3.1 and §5.1 at tag `archive/wf3-experiment-v2` — its four-stage
  shape (prepare / generate / sweep / reduce) is the owner's 1-2-3 arrived at
  independently, with prepare folded in. Treated as **input, not starting point**,
  on the terms the roadmap sets for R12.

The method component's reasoning review is complete and recorded above
(RR-1 .. RR-7). Stage 1 authors against the eight-gap scope, and against the five
questions closing that section.
