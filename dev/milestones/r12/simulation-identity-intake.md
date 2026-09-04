# Intake — WF3 simulation identity: one `sim_id` at the model seam

> **Stage-0 intake, authored 2026-09-04. No design exists yet.** This is the
> scope authority a `design-review-loop` run would work under: what was declared
> *before* any drafting — the scope gaps, the owner constraints, the decision
> criteria, the non-goals, the evidence register, the feasibility probes, the
> gate-materialization check and the derived-artifact register.
>
> It is kept unedited once a design run starts. Its value is that it predates the
> design, so a later reader can see which premises were checked up front and
> which were carried as hypotheses.

Stage 0 of a prospective `design-review-loop` run, slug `wf3-simulation-identity`.
Driver-authored; **no design content here**.

## The change request, verbatim

> The direction I want to move towards is to create a single simulation id
> column, which is currently represented through st_id x rlz_id. This way, I can
> also input other types of scenarios in the future, for instance top-down
> downscaled GCM scenarios. In that case, the simulator (e.g., wflow model) will
> only loop through the run id set instead of st_id and rlz_id which won't be
> available.

and, narrowing the seam after the first framing conflated identity with pooling:

> What `export_wflow_results.py` does it post-processing. I first need a clear
> id/indexing column for each combination of climatic conditions (e.g.,
> stochastic realization x climate perturbations) inputted into the model
> (wflow), and what is outputted from there... The outputs are post-processed,
> e.g., pooled to calculate certain metrics later on.

The second message is the load-bearing one. It places the id at the **model I/O
boundary** — one climate series in, one model output out — and puts pooling
firmly downstream of it, as an operation over table columns rather than a
property the identity must encode.

## Problem

WF3's run identity is the ordered pair `(rlz, st_id)`, and that pair is a
**cross-product**: it presumes the scenario set is the factorial expansion of a
sampled axis and a designed axis. Three costs follow.

1. **A non-factorial scenario family cannot be expressed at all.** A top-down
   downscaled GCM scenario set is a flat, ragged list — `(model, scenario,
   horizon)`, with no realization index and no design point. There is no
   assignment of such a set into `(rlz, st)` that is not a lie.
2. **Identity is recovered by parsing a filename.** `export_wflow_results.py:79`
   holds `_MEMBER_IN_STEM = re.compile(r"^rlz_(\d+)_st_(\d+)$")`, and
   `member_from_run_csv` raises `ValueError` on any stem that does not match. The
   post-processor's contract with the simulator is a **string spelling**, not a
   column. This one function is the concrete reason another family cannot be
   admitted — not the pooling, not the surface.
3. **The identity scheme is already leaking.** `indicator_tables.py:136` carries
   `POOLED_REALIZATION = 0`, a numeric sentinel written into the numeric `rlz_id`
   key column, with its own comment recording the fragility: *"safe ONLY because
   no metric emits both grains; if that ever changes it must become a string, or
   `groupby("rlz_id")` folds pooled rows in as another realization."* A key column
   that must carry an out-of-band value to express a derived grain is a key column
   doing two jobs.

The execution layer has already flattened itself and has no word for what it
iterates. Rule 3.15 (`run_stress_test.smk:1216-1241`) is a generated rule per
batch with **no wildcards at all**; it slices a flat Python list
(`_k_members`, `:1120`) and keys its log and benchmark by batch id. `(r, c)`
survives inside it only to spell four filenames.

## Scope — what this design must close

Nine gaps: seven derived from reading the request against the tree, plus gaps 4–6
sharpened or added by the intake reasoning review (below). None re-opens an owner
ruling; three require *superseding* prior accepted change requests, which is
itself in scope (see Constraints).

| # | Gap | Why it blocks implementation |
|---|---|---|
| 1 | **The seam is undefined.** Which artifacts carry `sim_id`, where the id is minted, and what crosses the boundary in each direction | Everything else is downstream of this |
| 2 | **`sim_id`'s form is unruled.** It must be stable under set growth (C24 reason 2), which excludes a sequential integer; opaque-vs-self-describing is genuinely open and C25 already rejected content-hashed ids once, on different grounds | The id appears in filenames, catalog keys and a tree inventory; its form is not cosmetic |
| 3 | **The registry has no schema, producer, or home.** Supertype/subtype (a core table plus per-family sidecars) versus one wide nullable table is undecided, as is whether it is parse-time-derivable | C26's chicken-and-egg is live: Snakemake needs the id set at DAG-construction time, before any rule has written a file |
| 4 | **Pooled rows have no key under a `sim_id` table, and this is the sharpest gap.** Class B (GEV return levels) and Class C (fixed-month means) are pooled *across* realizations at a design point and written with `st_id` + the sentinel `POOLED_REALIZATION`. Their value belongs to a **group**, not to a simulation. A table keyed only by `sim_id` has no row shape for them | Raised as a blocking finding by the intake reasoning review. Either the table keeps a group key — so it does not narrow to `sim_id` — or a synthetic `sim_id` is minted for a group, which breaks the one stated contract. Neither is chosen; the design must choose |
| 5 | **The baseline relation is family-specific and currently implicit.** `st_0` is a *stochastic-family* concept treated as universal: `_category_month` fixes the wet/dry month once from `runs[0]` and evaluates every member against it. A GCM-derived run's indicator is comparable only against *its own* historical run, not against `st_0` | Raised by the review. The registry as sketched has no `baseline_sim_id`, so a second family cannot say what it is a delta from — which is the thing the surface actually plots |
| 6 | **Record length is an unstated estimator precondition.** The Class B GEV is fitted on `RLZ_NUM × N` blocks *because* a fit over one short realization is ill-conditioned (the module's own docstring). A 30-year GCM horizon supplies ~30 blocks against several hundred for a surface cell, under the same metric name in the same table, with no column recording the difference | Raised by the review. Not a bug today — it becomes one the moment a second family shares the table |
| 7 | **Two seam contracts change.** WG-2 pins `rlz_<n>_st_<m>.nc` as a **DAG-globbed naming pattern** in its *pinned surface*; WG-5 pins one catalog entry per `rlz_<n>_st_<m>`; HM-7 pins the five indicator columns | A contract document here is normative, not descriptive |
| 8 | **C24, C25 and C28 must be superseded, not edited.** `wf3-change-requests.md` is in `dev/reference/sealed-records.yml`; `tests/test_sealed_records.py` fails any edit. C25 is in scope because it rejected content-hashed ids as "opaque and unsortable" — an objection a hash-shaped `sim_id` re-incurs | The mechanism is a new decision record, and it must argue reason-by-reason |
| 9 | **Migration and tree shape.** Four artifact families are renamed; `naming.md` §7 requires a migration note; `semantic_tree_diff.py`'s inventory and the full baseline manifest move with them | A tree-shape change the fixture-dependent test layer cannot catch in a worktree |

## The four artifacts at issue

Everything spelled `rlz_<r>_st_<m>` on the run path today:

| stage | artifact | producer |
|---|---|---|
| climate series (baseline) | `{wg_dir}/output/rlz_<r>_st_0.nc` | 3.11 `generate_weather_realizations` |
| climate series (perturbed) | `{wg_dir}/output/rlz_<r>_st_<m>.nc`, `m ≥ 1` | 3.12 `perturb_climate_realization` |
| model forcing | `{runs_dir}/forcing/inmaps_rlz_<r>_st_<m>.nc` | 3.14 `downscale_climate_realization` |
| model config | `{runs_dir}/config/rlz_<r>_st_<m>.toml` | 3.14 |
| per-member catalog (WG-5) | `{runs_dir}/config/rlz_<r>_st_<m>.yml` | 3.14 |
| **model output** | `{runs_dir}/output/rlz_<r>_st_<m>.csv` | 3.15 `run_wflow_batch_<b>` |

The id is minted where a climate series becomes addressable (3.11/3.12 output,
crossing the WG-2 seam) and consumed where the model output is reduced (HM-7).

## Constraints — settled, not open for review

| Constraint | Source |
|---|---|
| **The id sits at the model I/O boundary.** One climate series in, one model output CSV out. That is its entire contract | Owner, 2026-09-04 (second message) |
| **Pooling is downstream and does not constrain the id.** Metrics group by registry columns after a join; nothing parses `sim_id` | Owner, 2026-09-04 |
| **The direction is a wf3 split** — scenario/climate generation on one side, impact simulation on the other. This design is the seam that makes the split possible, not the split itself | Owner, 2026-09-04 (first message) |
| **Admitting other scenario families is the motivating requirement**, downscaled GCM scenarios named specifically. A design that only tidies the current two-factor scheme does not satisfy the request | Owner, 2026-09-04 |
| **Stress-test scenarios come from the stochastic weather generator; the experiment workflow is never coupled to CMIP scenarios.** The perturbation grid stays scenario-neutral | `AGENTS.md` § Background |
| **CMIP6 output is a plausibility overlay only.** It never drives a stress-test run | `AGENTS.md` § Background |
| Repo-wide: this is the workflow engine only; hydromt / wflow conventions used verbatim, never re-engineered | `AGENTS.md` § Hard Constraints |

**The scenario-neutrality constraint is the one a reviewer must price explicitly.**
The proposal admits non-stochastic runs into wf3's *simulation* half. The argument
offered is that the constraint forbids CMIP **driving** the stress test — the
perturbation grid must remain scenario-neutral — and does not require the
*simulator* to know what produced its forcing; and that GCM-derived runs would
land as overlay **points**, never as surface **cells**, which is wf2's existing
role. That argument is stated here so it is reviewed rather than assumed.

## Decision criteria

1. **The simulator must be family-agnostic.** If admitting a second family
   requires editing the simulator or the reducer's identity handling, the design
   has not drawn the seam.
2. **No identity recoverable by string parsing.** A spelling is not a contract;
   the replacement is a column and a join.
3. **The id must be stable under set growth** — adding realizations, resizing the
   grid, or admitting a family must not renumber existing runs. This is C24
   reason 2, which survives.
4. **Grain is a column, not a sentinel.** Whatever replaces `POOLED_REALIZATION`
   must not reuse a key column to mean two things.
5. **Parse-time derivability is preferred over a checkpoint.** A Snakemake
   checkpoint is a large complexity jump; the stochastic family's registry should
   stay a pure function of config, as `stress_test_grid()` is today (C26).
6. **The migration is one atomic rename plus a shape change**, with every live
   reference updated in the same commit (`AGENTS.md` § Conventions), and a
   documented rollback.
7. **Gate-ability.** Every claimed runtime property needs an observation that
   would falsify it.

## Success criteria

- All seven scope gaps closed in normative text, not sketch.
- A superseding decision record under `dev/decisions/` that argues C24
  reason-by-reason and states C28's trigger, without editing the sealed record.
- Replacement contract text for WG-2, WG-5 and HM-7, droppable into the two seam
  documents.
- A migration note satisfying `naming.md` §7.
- A claim → falsifier table handed to `task-brief`.
- A stated position on whether this subsumes the dropped `t2608082036`, and on
  what happens to `member_hash` (design-v4's identity) under a minted `sim_id` —
  the two may be the same object arriving from opposite directions.

## Non-goals

- **The wf3 split itself.** This design makes it possible; it does not perform it.
  No workflow file is added or removed.
- **Admitting a GCM family.** No `sim_gcm` producer, no downscaling path, no
  config surface for it. The registry must *accommodate* one; building one is a
  separate milestone. A design that ships a speculative second family has
  overreached.
- **The response-surface plotting change.** That a surface becomes
  family-conditional follows from the schema; specifying the plot does not.
- **R12's execution model** — manifest, ledger, resumable sweeps, epochs,
  quarantine, atomic publication. Related and possibly reordered by this, but not
  authored here.
- **Fixing `st_0`'s comparability** — `t2608151154`, `origin: R12`, untouched.
- **Re-opening the perturbation grid's scenario-neutrality.** Out of bounds.
- Any change to CST-API, CST-frontend, or `csthelpers`.

## Evidence register

Empirical premises the design leans on. Falsity of any row changes a decision.

| # | Premise | Source | Exact observation | Reproduction | Confidence |
|---|---|---|---|---|---|
| E1 | Post-processing recovers run identity by regex over the output CSV's filename stem | `export_wflow_results.py:79-92` | `_MEMBER_IN_STEM = re.compile(r"^rlz_(\d+)_st_(\d+)$")`; `member_from_run_csv` raises `ValueError` on a non-matching stem | Read the function | **Verified** 2026-09-04 |
| E2 | The batch rule carries no wildcards and iterates a flat member list | `run_stress_test.smk:1120, 1216-1241` | `_k_members` is a flat list comprehension; `rule: name: f"run_wflow_batch_{_b}"` builds `input`/`output` as static Python lists; log and benchmark are keyed `batch_{_b}` | Read the rule | **Verified** 2026-09-04 |
| E3 | C24 ruled explicitly against a single id, on four reasons | `dev/milestones/r09/wf3-change-requests.md:640-646` | "two id spaces, not one… Run identity stays `(rlz, st)`", with pooling, renumbering, batching-by-wildcard and log-legibility given as reasons | Read the section | **Verified** 2026-09-04 |
| E4 | C24 reason 3 has expired | E2 above vs `wf3-change-requests.md:645` | The reason names "the P3-3 batching work groups by realization via wildcard patterns"; the landed batch rule has no wildcards | Compare the two | **Verified** 2026-09-04 |
| E5 | C24 reason 4 has expired | `run_stress_test.smk:1238-1240` | Logs are already keyed by batch id, not by rlz/st; the member span is a console banner string, not the log's identity | Read the rule | **Verified** 2026-09-04 |
| E6 | The indicator table is five columns and carries both member indices | `blueearth_cst/shared/indicator_tables.py:126-132` | `INDICATOR_COLUMNS = ("metric", "location", "st_id", "rlz_id", "value")` | Read the constant | **Verified** 2026-09-04 |
| E7 | A derived grain is expressed as a sentinel inside a key column | `indicator_tables.py:133-136` | `POOLED_REALIZATION = 0`, with an inline comment stating it is safe only while no metric emits both grains | Read the constant | **Verified** 2026-09-04 |
| E8 | The reduction pools *within* realization deliberately, for a stated methodological reason | `export_wflow_results.py:40-46, 233-234` | Annual minima are extracted within each realization and the blocks pooled, because a synthetic continuous index across realizations manufactured 7-day flows that occurred in no realization | Read the docstring and the function | **Verified** 2026-09-04 |
| E9 | WG-2 pins the member naming pattern as part of its *pinned surface* | `dev/reference/contracts/weather-generator-seam.md:238-245` | "naming pattern: `rlz_<n>_st_<m>.nc` — a DAG-globbed pattern"; listed again under "pinned surface" | Read WG-2 | **Verified** 2026-09-04 |
| E10 | WG-5 pins one catalog entry per member, including `st_0` | `weather-generator-seam.md:260-277` | "one entry per `rlz_<n>_st_<m>` (**including `st_0`**)", one catalog per member, `temp()` | Read WG-5 | **Verified** 2026-09-04 |
| E11 | C28 kept `st_id` denormalized *provisionally*, with a named revisit trigger | `wf3-change-requests.md` § C28 | Ruled 2026-08-05 "at this stage", against the recommendation, with "an explicit revisit when a third dimension arrives" | Read the section | **Verified** 2026-09-04 |
| E12 | `t2608082036` (the WF3 v2 re-derivation) was dropped, and eight references survive it | `dev/LOG.md:47` | Dropped 2026-08-18 by owner ruling; the row names all eight surviving references and states that the *item* was dropped, not the work declared abandoned | Read the row | **Verified** 2026-09-04 |
| E13 | A sequential `sim_id` renumbers the set when `RLZ_NUM` or the grid changes | C24 reason 2, `wf3-change-requests.md:643` | Argued, not measured — but it is arithmetic over a cross-product, so the failure is structural | Construct two configs differing only in `realizations_num` | **HYPOTHESIS — structural, not executed** |
| E14 | A downscaled GCM scenario set is not expressible as `(rlz, st)` | The change request | Argued from the shape of `(model, scenario, horizon)`; no such set exists in this repo to test against | — | **HYPOTHESIS — asserted, no artifact exists.** Recorded so a reviewer prices it rather than inherits it |
| E15 | `member_hash` (design-v4 §5.1) and a minted `sim_id` may be the same object | `design-v4.md:987` at tag `archive/wf3-experiment-v2` | `member_hash` is a stable-under-growth identity over the member tuple; whether it can *serve* as `sim_id`, or must stay a separate freshness column, is undetermined | `git show archive/wf3-experiment-v2:dev/working/design-runs/wf3-experiment-v2/design-v4.md` | **OPEN QUESTION — not a premise** |
| E16 | Two of the three grain classes are keyed by design point, not by simulation | `export_wflow_results.py:384, 405-426, 431-441` | Class A is per realization; Class B (GEV return levels) and Class C (fixed-month means) are emitted as `(st_id, POOLED_REALIZATION)` rows. Their value has no owning run | Read the three emit blocks | **Verified** 2026-09-04 — this is what makes gap 4 blocking |
| E17 | The Class-C month is fixed once from `st_0` and applied to every member | `export_wflow_results.py:356-365` | `if q_locations and 0 in runs:` … `_category_month(baseline, "wet"/"dry")`, with the Q5 comment "pick from st_0, then evaluate that month for every member" | Read the block | **Verified** 2026-09-04 — this is what makes gap 5 concrete |
| E18 | The GEV fit's precision is a function of realization count, stated as the reason for the pooling | `export_wflow_results.py:27-35` | "a GEV fit over one short realization is ill-conditioned; pooling multiplies the block sample by" the realization count | Read the docstring | **Verified** 2026-09-04 |
| E19 | Plotting a GCM-derived run on the T × P plane requires computing its (ΔT, ΔP) | Review argument, not code | No such run exists; the position is not a model output and would have to be derived from the GCM series — which is wf2's change-factor computation | — | **HYPOTHESIS — argued at intake.** Load-bearing for the scenario-neutrality question; recorded so a reviewer prices it |

## Framework-feasibility probes

Mechanisms whose feasibility depends on Snakemake execution semantics. Each needs
a probe with a recorded result, **not a paragraph of prose**.

| Probe | Question | Why prose cannot settle it |
|---|---|---|
| P1 | Can the registry be read at DAG-construction time from a config-derived pure function *and* from an externally supplied file, without a checkpoint? | C26's chicken-and-egg is the reason the design table exists in its current form; the external-file path is new and is the whole point of the change |
| P2 | Does collapsing `rlz_<r>_st_<m>` to `sim_<id>` disturb rule 3.12's `wildcard_constraints`, which exist to stop a `CyclicGraphException` between 3.11's and 3.12's output patterns? | 3.12's constraint (`st_num ≥ 1`, `:1005-1018`) is load-bearing for DAG construction and is expressed over a token this change removes |
| P3 | Does 3.14's per-member WG-5 catalog still resolve when its key is `sim_<id>`, given hydromt reads the catalog by key? | The catalog is an upstream schema we emit into; a key-shape change is exactly where a pinned-as-reliance surface bites |
| P4 | Does `pixi run tree-check` classify the renamed tree, and does `build_project_tree_rules` need extending in the same commit? | The inventory is code, not a snapshot; a stale entry reports undeclared on every future run |

## Gate materialization

| Gate | Verdict | Detail |
|---|---|---|
| `pytest tests/test_export_wflow_results.py`, `test_interchange_contracts.py`, `test_indicator_tables.py` | **Runnable** | The narrow tier; these own the changed surfaces |
| `pytest tests/test_cli.py` | **Runnable, required** | Rules' declared inputs and outputs change shape |
| `pixi run test-full` | **Runnable, required at merge** | Touches a Snakefile, a `script:` signature *and* `shared/` — the `workflow_contract` and `process_isolation` tiers |
| `pixi run tree-check` | **Runnable, needs a code change with the design** | Four artifact families move; `semantic_tree_diff.py`'s `build_project_tree_rules` must land in the same commit. `build_r09_path_map` stays frozen |
| `pytest tests/test_sealed_records.py` | **Runnable, and it is a constraint not a check here** | It will fail any attempt to edit C24/C28 in place. The design must supersede, not edit |
| `check_baseline.py check` | **NEEDS A PRE-CHANGE RE-RECORD** | Every wf3 target path moves, so the gate fails by construction. A re-record must land **before the first implementation commit**, from `snake_config_baseline.yml`, in the primary checkout, `--notemp` on WF1, no other session live. A comparison gate cannot be applied retrospectively — the R12 lookup design's R1, and it applies verbatim here |
| `validate_wg2` / `validate_wg5_catalog_grid` / `validate_hm7` | **Change with the design** | Part of the deliverable, not independent checks. All three assert the `rlz_<n>_st_<m>` shape |
| The fixture-dependent test layer | **Cannot run in a worktree** | It skips rather than fails, and this is a tree-shape change — the case `AGENTS.md` records as surviving every gate a branch can run. Implementation gating must happen in the primary checkout, on a seeded fixture |

## Derived-artifact register

Artifacts that derive from this design and go stale the moment review changes it.
**Author spawns are barred from touching them**; each is regenerated from the
accepted version after G2.

| Artifact | Regenerated by |
|---|---|
| `dev/decisions/00NN-*.md` (new) | Author from the accepted design — the C24/C28 supersession |
| `dev/reference/contracts/weather-generator-seam.md` (WG-2, WG-5) | Replace the naming-pattern and catalog-key clauses from the accepted design |
| `dev/reference/contracts/hydrological-model-seam.md` (HM-7) | Replace the column contract |
| `dev/reference/naming.md` §4 (member token) and §7 (migration record) | Author from the accepted design |
| `dev/reference/workflows/rule-index.md` | Regenerate the 3.11 / 3.12 / 3.14 / 3.15 / 3.16 rows |
| `dev/scripts/semantic_tree_diff.py` `build_project_tree_rules` | Extend with the new tree; `build_r09_path_map` frozen |
| `dev/baseline/manifest.json` | Re-record before the first implementation commit, then again after |
| `dev/roadmap.md` § R12 | Rewrite — this changes what R12 is, and E12's eight dangling references need repointing or an explicit abandonment |
| `dev/tasks/` — a new board item; `t2608151154` if `st_0`'s treatment moves | Board rewrite from the accepted design |
| The `task-brief` for implementation | Stage 7 handoff, with the claim → falsifier table |

## Reasoning review at intake — findings

A method-layer review of the change request's reasoning was dispatched before
stage 1 (Fable 5.1, `critical-thinker`, 2026-09-04). It was asked to critique the
*science and method*, not the mechanics. Verdict: **the seam is drawn in the right
place; the table on the far side of it is wrong as sketched.** Its three verified
tree-reads agree with E1–E3 above, with one correction carried into the record:
"the batch rule has no wildcards" is true of **rule 3.15 only** — rules 3.12 and
3.14 still carry `{rlz_num}` / `{st_num}` (`run_stress_test.smk:1004-1069`). That
is the seam's own location, so the argument holds, but the claim must be stated
with its scope.

| # | Finding | Class | Disposition |
|---|---|---|---|
| RR-1 | Pooled Class B/C values are keyed by group, not by run, and have no row shape under a `sim_id`-only table | **Structural error** | **Accepted** — became scope gap 4; the design must choose between a retained group key and a minted group id, and neither is pre-ruled |
| RR-2 | Baseline comparability crosses the seam: `st_0` is a stochastic-family concept used as universal, and a GCM run's delta is against its own historical run | **Method** | **Accepted** — became scope gap 5 |
| RR-3 | Record length is an unstated estimator precondition; a 30-year horizon and a multi-realization cell share a metric name with no column recording precision | **Method** | **Accepted** — became scope gap 6 |
| RR-4 | The composite identity carried a *structural guarantee* of a full factorial (common random numbers across design points); a column carries the information but not the guarantee | **Method, partly pre-existing** | **Accepted as a decision criterion** — the registry writer must assert rectangularity for the stochastic family. Noted honestly: the batch rule already degraded per-member completeness, so this cost predates the change |
| RR-5 | Plotting a GCM run as an overlay point still requires its (ΔT, ΔP), which is wf2's change-factor computation re-entering wf3 | **Method — bears on a hard constraint** | **Accepted as E19 and an open question.** The premise survives only if the surface reduction is explicitly family-gated and the overlay is a separate product |
| RR-6 | "Nothing parses it" (a consumer contract) and "semantically empty" (a string property) are different choices, conflated in the request. A readable unparsed composite satisfies every raised constraint and keeps the outputs folder sortable | **Taste, with a real regression** | **Accepted into scope gap 2**, and it is why C25 joined the supersession set (gap 8) |
| RR-7 | The motivating family does not exist, so the registry schema is underdetermined and risks being frozen wrong | **Process** | **Accepted as a non-goal boundary plus a requirement**: ship a schema-versioning rule and a family-gated surface reducer, not a "clean seam" that is clean only because one side is empty |

**The strongest fair statement of the case against**, recorded so the design
answers it rather than inherits it: *the composite identity is the experimental
design expressed in the type system; the proposal moves the design into data, for
the benefit of a family whose comparability semantics nobody has written down.*

**Five questions the design must answer.** RR-1 and RR-2 are the gating pair —
the review's closing judgement is that if those two are answered the proposal is
sound, and if they are not, the seam is right but the table is wrong.

1. Where do Class B/C values live under a `sim_id` table, and what is the group
   key for a family that pools differently?
2. What is the baseline relation per family — does `st_0` stay reserved, or become
   `baseline_sim_id` in the registry?
3. Does the registry writer assert rectangularity for the stochastic family, and
   what happens to a pooled metric when a run is missing?
4. Is a GCM-derived run's (ΔT, ΔP) computed inside wf3, and how is that reconciled
   with "never couple wf3 to CMIP scenarios"?
5. Why an opaque id rather than a readable unparsed composite — and does the
   answer also dispose of C25?

## Genre mapping

`workflow-spec` — it specifies artifacts, a rule boundary and three data
contracts inside one workflow. It carries a **method component**: whether a
hydrological simulator is legitimately indifferent to the provenance of its
forcing, and what that indifference costs at the reduction. That component is why
the run needs a method-literate reviewer and not only a repo-fit one.

## Seeding

No prior note to seed from. Stage 1 authors from this intake, the four artifacts
table above, and two external inputs:

- `dev/milestones/r12/wf3-experiment-v2-design-review-record.md` — the surviving
  architecture list, and `member_hash` in particular (E15).
- `design-v4.md` §3.1 and §5.1 at tag `archive/wf3-experiment-v2` — the four-stage
  shape and the member-identity scheme, as **input, not starting point**, on the
  same terms the roadmap sets for R12.

The method component's reasoning review is complete and its findings are recorded
above (RR-1 .. RR-7); stage 1 authors against the revised nine-gap scope, not the
original seven.
