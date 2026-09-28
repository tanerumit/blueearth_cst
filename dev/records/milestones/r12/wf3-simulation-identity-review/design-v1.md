# WF3 in three stages — scenario space, simulation, metrics: Design

> **design-v1**, run `wf3-simulation-identity`, milestone R12. Genre:
> **workflow-spec**. Scope authority:
> `dev/milestones/r12/simulation-identity-intake.md` (frozen). Measurements this
> document is bound by: `dev/working/design-runs/wf3-simulation-identity/probe-p1-p2.md`.
>
> **Epistemic labelling.** Every substantive claim below is marked
> **[measured]** (an executed observation, with the command or the probe row that
> produced it), **[argued]** (a conclusion from cited code or contract text, not
> executed), or **[assumed]** (a premise this design leans on that nothing in the
> repository establishes). An unlabelled sentence is ordinary connective prose and
> carries no claim.

## 1. Problem statement

WF3's run identity is the ordered pair `(rlz, st_id)`, and that pair is not a
label on the experiment — it *is* the experiment's data model. Four consequences,
each with a code site.

**1. Identity is recovered by parsing a filename.** `export_wflow_results.py:79`
holds `_MEMBER_IN_STEM = re.compile(r"^rlz_(\d+)_st_(\d+)$")`, and
`member_from_run_csv` (`export_wflow_results.py:82-92`) raises `ValueError` on any
stem that does not match. The reduction's contract with the simulator is therefore
a **string spelling**, not a declared interface. [measured — read the function]

**2. The scenario set is structurally required to be a full factorial.** The run
set is built as a cross-product at `run_stress_test.smk:1120`
(`_k_members = [(int(r), int(c)) for r in range(1, RLZ_NUM + 1) for c in
range(ST_START, ST_NUM + 1)]`) and again as an `expand()` over two independent
wildcard lists at `:1247`. A flat, ragged scenario list — a user-supplied set, or
one downscaled from GCM series — has no assignment into `(rlz, st)` that is not an
invention. [argued from the two sites; **E18 is a HYPOTHESIS** — no such set exists
in this repository to test against, and this design does not treat it as measured]

**3. Bundling is inferred from the identity, and the identity can express only one
bundling.** Two bundlings already coexist in one output file: Class A metrics are
emitted per realization (`export_wflow_results.py:384-401`), while the Class-B GEV
fits (`:405-426`) and the Class-C month-selecting means (`:431-441`) pool across
realizations at one design point. Bundling is thus a property of the **metric**,
not of the scenario set — and a composite run identity has no place to record
that. [measured — read the three emit blocks]

**4. The scheme is already leaking through a sentinel.**
`shared/indicator_tables.py:136` carries `POOLED_REALIZATION = 0`, an out-of-band
value written into the numeric `rlz_id` key column, with its own comment recording
the fragility: *"safe ONLY because no metric emits both grains; if that ever
changes it must become a string, or `groupby("rlz_id")` folds pooled rows in as
another realization."* [measured — read the constant]

Meanwhile the execution layer has already flattened and has no word for what it
iterates: rule 3.15 (`run_stress_test.smk:1216-1241`) is generated per batch with
**no wildcards**, slices the flat `_k_members` list, and keys its log and benchmark
by batch id. `(r, c)` survives inside it only to spell filenames. [measured]

**The problem this design solves** is therefore not "rename some files". It is:
WF3 fuses scenario construction, simulation and reduction into one identity, and
that fusion prevents three separable concerns from being stated separately — what
scenarios exist, what the simulator is entitled to know, and at what grain each
metric is defined.

## 2. Goals / Non-goals

### 2.1 Goals

1. **Make the simulator family-agnostic.** Stage 2 learns the run list and the
   built model, and nothing about what produced the forcing. Admitting a second
   scenario family must require no edit to stage 2.
2. **Remove string-parsed identity.** No consumer recovers what a run *is* by
   matching a regex against a path.
3. **Make each metric's grain a declared property**, and remove the
   `POOLED_REALIZATION` sentinel by making the results file's key column carry one
   kind of thing.
4. **Keep the stochastic family's scenario set parse-time derivable**, so no
   checkpoint enters WF3 (decision criterion 6, and P1 case (c) is the trap).
5. **Label the scenario table's family-specific columns as such**, so a later
   split into per-family tables is a file split rather than a redesign.
6. **Execute the rename atomically**, with a migration note, a rollback, and a
   falsifier for every runtime property claimed.

### 2.2 Non-goals (binding, from the intake)

- **Building a second scenario family.** No GCM producer, no downscaling path, no
  config surface for one. This design must *accommodate* one; shipping one is a
  separate milestone.
- **Model configuration as a scenario column.** One row stays one run, so the
  extension is not precluded; no such column is added now.
- **A user-facing config surface for metric grain.** Grain becomes an explicit,
  named property of each metric **in code**. Promoting it to configuration is a
  later decision.
- **Splitting the WF3 `.smk` file.** The three stages become *separable* — three
  contracts and a family-blind seam — not *separated*. WF3 stays one file; no
  workflow entry point is added or removed.
- **R12's execution model** — manifest, ledger, resumable sweeps, epochs,
  quarantine, atomic publication. Related and possibly reordered by this design;
  not authored here. See §5.5.4 on `member_hash` and §10.
- **Fixing `st_0`'s comparability with the surface** (`t2608151154`). Untouched;
  §5.3.5 states the one thing this design owes it.
- **Re-opening the perturbation grid's scenario-neutrality.** Out of bounds.
- Any change to CST-API, CST-frontend, or `csthelpers`.

## 3. Settled framing — carried forward, not re-opened

The intake's constraints table is ruled and closed. It is restated here because
the design's structure is a consequence of it, and a reader must be able to check
that consequence without a second document.

| # | Constraint | Source | Where this design honours it |
|---|---|---|---|
| S1 | **Three stages, three contracts. No single table solves everything** | Owner, 2026-09-04 | §5.1 (scenario table), §5.2 (seam view), §5.4 (index table + results) are three artifacts with three schemas |
| S2 | **The simulator knows only the built model and the run list.** It enumerates rows and writes outputs named by the run id, never by family-specific columns | Owner, 2026-09-04 | §5.2's seam core is four family-blind columns; §5.3 specifies stage 2 against those columns only |
| S3 | **Bundling is a property of the metric, resolved at stage 3** — not a column of the scenario table | Owner, 2026-09-04 | §5.4.1 puts grain in the metric declaration; the scenario table has no grain column |
| S4 | **Build for the current bottom-up assessment; do not define every possible scenario family up front** | Owner, 2026-09-04 | §5.1.3 defines exactly one family block (`stochastic`) and a registry that names it; §6 A5 records the rejected general-registry shape |
| S5 | **Stress-test scenarios come from the stochastic weather generator; the experiment workflow is never coupled to CMIP scenarios.** The perturbation grid stays scenario-neutral | `AGENTS.md` § Background | §5.4.5: overlay coordinates are stage-1 **columns**, never a WF3 derivation; the surface reduction is family-gated |
| S6 | **CMIP6 output is a plausibility overlay only.** It never drives a stress-test run | `AGENTS.md` § Background | No stage reads a WF2 artifact; §5.4.5 |
| S7 | **No local calibration.** The model instance is what WF1 built from global data | `AGENTS.md` § Background | Stage 2 takes "the built model" as given; §5.3 |
| S8 | Repo-wide: this is the workflow engine only; hydromt / wflow conventions used verbatim, never re-engineered | `AGENTS.md` § Hard Constraints | §5.8 changes only the **keys** of our emitted catalog, never the hydromt catalog schema |

**One row is one run.** If model configuration later becomes columns of the same
table, a row is still exactly one simulation, so the identity holds without
redefinition. This is the property that lets §5.1's schema grow by columns rather
than by a second key.

**Grain lives in stage 3.** Whether a metric is computed per run or over a bundle
is declared where the metric is defined — not as a column of the scenario table
and not as a consequence of which loop the code sits in.

## 4. Decision criteria

The intake's eight criteria, restated with the section that discharges each.

| # | Criterion | Discharged by |
|---|---|---|
| D1 | **The simulator must be family-agnostic.** If admitting a second family requires editing stage 2, the seam is in the wrong place | §5.2.2 (the `derived_from` argument), §5.3 |
| D2 | **No identity recoverable by string parsing.** A spelling is not a contract | §5.3.4 — `member_from_run_csv` is deleted and its replacement specified |
| D3 | **The DESIGN must be stable under set growth; the index need not be.** Narrowed by W4: `st_id` and its properties live in the lookup and stay put; the sequential index may renumber, provided a changed lookup is *detectable* rather than silent | §5.5.3 (the stale-lookup digest guard) |
| D4 | **Grain is declared, never a sentinel.** Nothing may reuse a key column to mean two things | §5.4.1–§5.4.3 — `POOLED_REALIZATION` is deleted |
| D5 | **Store the finest grain, derive every summary.** Stage 2's raw output is the finest grain; every metric is a declared derivation over it. The exception is real and stated: for a pooled estimator the finest grain that *exists* is the bundle | §5.4.1, and §5.4.4 for the estimator precondition that makes the exception principled rather than convenient |
| D6 | **Parse-time derivability over a checkpoint.** The stochastic family's scenario table stays a pure function of config | §5.1.4, bound by P1 |
| D7 | **The migration is one atomic rename plus a shape change**, every live reference updated in the same commit, with a documented rollback | §8 |
| D8 | **Gate-ability.** Every claimed runtime property needs an observation that would falsify it | §9 |

**Two criteria are in tension, and the design resolves rather than balances them.**
D1 says stage 2 must hold no family-specific knowledge. P2 measured that *every*
mechanism which builds a DAG under a single opaque id requires stage 2 to know
which ids are baselines, at parse time — and `ruleorder`, the one mechanism that
needs no such knowledge, **fails**. §5.2.2 resolves this by changing what stage 2
is told: not *which ids are baselines* (a family concept) but *which row's output
each row's forcing derives from* (a dependency edge, true of any family). If that
resolution is wrong, D1 is unsatisfiable at this seam and the seam must move.

## 5. Selected approach

**The shape in one paragraph.** Stage 1 mints a flat namespace of *units* and
writes a **scenario table** whose rows are runs: a family-blind core of four
columns plus a labelled, family-specific block. The **1→2 seam** is a view of that
table restricted to the core — it is what makes stage 2 family-blind, and it needs
four columns, not the two the intake specifies (§5.2.2, from P2). Stage 2
enumerates the seam and writes one raw output per run, named by the run id and by
nothing else. Stage 3 declares each metric's **grain**, resolves grains into
*bundles*, writes a **unit index** explaining every id in its results, and emits
four-column results tables. One sequence numbers runs and bundles; the index table
is what tells them apart.

**What is genuinely new**, as against a rename: the seam's `derived_from` edge
(§5.2.2), the unit index (§5.4.3), each metric's declared grain and estimator
precondition (§5.4.1, §5.4.4), and the scenario-table digest guard (§5.5.3).
Everything else is the consequence of applying those four to the existing rules.

### 5.1 Stage 1 — the scenario table

#### 5.1.1 What stage 1 owns

Stage 1 answers **what scenarios exist and what each one is**. It is the only
place family-specific columns live, and the only place a scenario's provenance is
recorded. It does not know what a metric is, and it does not know how the
simulator is invoked.

#### 5.1.2 Schema — normative

**Artifact.** `<exp>/config/scenario_table.csv`. One row per run. UTF-8, LF, comma
separated, header present, no index column. Every id column is **text** and every
consumer MUST read it as text (`pd.read_csv(..., dtype={"run_id": str,
"derived_from": str})`; R `colClasses = c(run_id = "character")`). The
zero-padding is meaningless the moment a reader coerces to int, and the failure is
a silent join miss — the same trap WG-2 already documents for `st_id`.

**Universal core — four columns, in this order, present for every family:**

| column | type | nullable | meaning |
|---|---|---|---|
| `run_id` | text, zero-padded, width `W` (§5.5.2) | no | This run's identity. Unique within the table. The **only** thing that appears in a stage-2 filename |
| `derived_from` | text, a `run_id` from this same table | **yes** | This run's climate forcing is produced by transforming the run named here. Empty means the forcing is produced *ab initio* — generated inside WF3, or supplied. A **dependency edge**, not a family concept (§5.2.2) |
| `forcing_uri` | text, a path or URI | **yes** | Where this run's forcing series comes from when it is supplied from outside WF3. Empty means WF3 produces it |
| `evaluated` | `true` / `false`, lowercase | no | Whether this run's *simulated* output is required. `false` marks a row that exists only as a forcing ancestor (§5.1.5) |

**Exclusivity rule (normative).** `derived_from` and `forcing_uri` are **mutually
exclusive**: at most one may be non-empty on a row. Both empty means "produced
ab initio inside WF3" (the stochastic baseline). Both non-empty is malformed and
the validator refuses it. This is what stops a supplied series and a derivation
rule from silently disagreeing about the same run.

**Acyclicity rule (normative).** The `derived_from` edges form a forest: no cycles,
and every non-empty `derived_from` names a `run_id` present in the same table.
Refused at write time and at parse time. (A cycle here becomes a
`CyclicGraphException` deep inside Snakemake, which is exactly the diagnosis this
design exists to stop shipping.)

**Family block — labelled, not universal.** After the core, a family block whose
column names are enumerated in code, in
`blueearth_cst/shared/scenario_families.py`:

```python
FAMILY_COLUMNS = {
    "stochastic": ("rlz", "st_id"),
}
```

That registry **is** the label. It is what makes the columns' family-specificity a
checkable fact rather than a convention, and it is what makes a later split into
per-family tables a file split: the core is already family-blind, and the block is
already a named set. A `scenario_family` column carrying the family name is the
first column of the block, so a table is self-describing when it leaves the tree.

For the `stochastic` family the block is:

| column | type | meaning |
|---|---|---|
| `scenario_family` | text | Literal `stochastic` |
| `rlz` | integer text, zero-padded to `index_width(RLZ_NUM)` | The realization draw. The *sampled* axis |
| `st_id` | integer text, zero-padded to `index_width(ST_NUM)`, or empty for the baseline row | The design point, joining `stress_test_lookup.csv`. The *designed* axis |

`st_id` is **empty on the baseline row**, not zero. WG-2's `st_0`-has-no-row rule
(`weather-generator-seam.md:166-180`) already establishes that the baseline is not
a surface member; carrying an empty `st_id` rather than a reserved `0` keeps that
property expressed as absence, in the one place absence is cheap to express.
[argued from the WG-2 text]

**Completeness (RR-4, decision criterion D8).** The composite identity carried a
*structural* guarantee that the run set was a full factorial. A column carries the
information but not the guarantee, so the guarantee becomes a **declared
predicate** on the family: `scenario_families.completeness("stochastic")` asserts
that the non-baseline rows are exactly the cross-product `rlz × st_id` over the
observed values, and that exactly one baseline row exists per `rlz`. A family that
declares no predicate gets none, and the validator says so rather than passing
silently. This is the intake's answer to question 3, and it is strictly stronger
than today: `_member_span` at `run_stress_test.smk:1195-1212` already has to print
`(partial)` because the batch rule degraded per-member completeness, so the cost
predates this change and is now at least detectable. [argued]

#### 5.1.3 What is deliberately absent

- **No grain column.** S3.
- **No bundle rows.** The table's rows are runs. Bundles are stage 3's (§5.4.3).
- **No model-configuration column.** Non-goal; the row-is-a-run property leaves
  room for one.
- **No baseline flag.** `derived_from` and `evaluated` carry everything the DAG
  needs without the word (§5.2.2, §5.1.5). Scope gap 5 stays open by construction.

#### 5.1.4 Where it is written, and by what (scope gap 3)

**Bound by P1.** A parse-time read of a scenario table works; a table *produced by
a rule of the same invocation* and read at parse time is the one shape that
requires a checkpoint (P1 case (c) — measured: the first invocation on a clean
tree exited 0 with zero scenario jobs and no warning).

The design therefore separates **deriving** the table from **recording** it:

1. **`scenario_table(cfg)` is a pure function**, in
   `blueearth_cst/shared/scenario_index.py`, called at Snakefile module scope. For
   the `stochastic` family it reads only `my_cfg` — `realizations_num`,
   `run_historical`, and `stress_test_grid(stress_test_cfg)` — exactly as
   `run_stress_test.smk:179-205` does today, and does no I/O. **This is the
   source of the id set for the DAG.** [argued from the existing sites; the
   config-derived parse-time path is measured feasible by P1 case (a)]
2. **Rule 3.09 writes the same object to disk** as a `rule all` target, from the
   *same function*, so the enumeration that expands the DAG and the enumeration
   that describes it cannot disagree (C26, preserved verbatim one level up). The
   written file is a **record of what ran**; nothing reads it at parse time. This
   is precisely today's arrangement for `stress_test_lookup.csv` — rule 3.09's
   output is consumed as a rule `input:` at `run_stress_test.smk:1026`, never at
   parse time — so the design stays out of P1 case (c) by keeping a property the
   workflow already has, not by acquiring a new one.
3. **A supplied family reads its table at parse time from a config path**, and
   that read is **unguarded** — or guarded with an explicit `raise`. Never
   `if os.path.isfile(...) else []`. P1 case (b2) measured that the guarded form
   exits **0** with every scenario job absent from the DAG and nothing reported.
   That is an `AGENTS.md` "no silent caps" violation of the most expensive kind:
   a run that looks successful and computed nothing. The repository already has
   the correct precedent — `analyze_projections.smk:467` reads a YAML unguarded at
   module scope — and the correct bootstrap for a generated file read at parse
   time, which is to **track** it (`config/catalogs/cmip6_data.yml` and
   `cmip6_store_index.json` are both in `git ls-files`). A supplied scenario table
   needs the same story or a documented pre-run generation step. [measured, P1]

**The `else []` hazard generalizes, and the design states the rule once:**
`scenario_index` **raises `EmptyScenarioSetError` on a zero-row scenario table**,
wherever the table came from. An empty run set is never a valid WF3 configuration,
and the whole class of silent-success shapes P1 found (b2, c, and the
first-rule-is-the-default-target case in P1's incidental findings) is closed by
refusing at the minter rather than by hoping each reader guards correctly.

#### 5.1.5 `run_historical`, without a baseline concept

`run_stress_test.smk:205` sets `ST_START = 0 if run_hist else 1`, and that value
reaches both the batch member list (`:1120`) and rule 3.16's `expand()` (`:1247`).
With `run_historical: false` the baseline *series* must still exist — rule 3.12
perturbs it (`:1023`) — but its wflow run is not wanted.

Under the new schema this needs no flag and no baseline word:

- The baseline row is **always** in the scenario table, with `derived_from` and
  `forcing_uri` both empty.
- `evaluated` is `run_historical` for that row and `true` for every perturbed row.
- Stage 2's *target* set is the `evaluated` rows. Because Snakemake is pull-based,
  `<runs>/output/run_<id>.csv` is simply never requested for an unevaluated row,
  while `<wg>/output/run_<id>.nc` is still built because rule 3.12 declares it as
  an input. This reproduces today's behaviour exactly, through a column instead of
  through an integer start offset. [argued — the mechanism is the same pull
  semantics `ST_START` already relies on at `:1247`; the falsifier is GF-4 in §9]

`evaluated` is family-blind: any family may have rows that exist only as forcing
ancestors. It says nothing about baselines, and stage 3 is free to declare units
over an unevaluated run's descendants without ever naming it.

**No silent cap.** When any row has `evaluated: false`, the run header MUST report
the count (`N scenarios, M simulated`). A row dropped from the simulation set is
exactly the kind of self-imposed bound `AGENTS.md` requires a tool to announce.

### 5.2 The 1→2 seam view

#### 5.2.1 What it is

The seam is the **projection of the scenario table onto its universal core** —
`run_id, derived_from, forcing_uri, evaluated`. It is a *view*, not necessarily a
separate file: for the stochastic family it is the same in-memory object stage 1
minted, sliced to four columns. It is named because it is the contract that
guarantees stage 2 cannot acquire a dependency on `rlz` or `st_id`.

**Normative rule.** Stage 2 code MUST NOT reference any column outside the core.
This is checkable: the family block's column names are enumerated in
`FAMILY_COLUMNS`, so a test can assert that no module under the stage-2 boundary
mentions one. That test is what makes S2 a contract rather than an intention.

#### 5.2.2 Why the seam is four columns and not two — the P2 correction

**The intake's seam spec is wrong as written, and the probe is why.** The intake's
stage table states the seam is *"`scenario_id` + its forcing. Two columns"*
(`simulation-identity-intake.md:105`). P2 measured six mechanisms for keeping
rules 3.11 and 3.12 as two producers under a single flat id, each run twice (with
the plural rule's subtree resolvable, and with it unresolvable):

| mechanism | with A's subtree unresolvable | needs stage 2 to know… |
|---|---|---|
| naive, no constraint | **`CyclicGraphException`** | nothing |
| `ruleorder: A_plural > B_wildcard` | **`CyclicGraphException`** | nothing |
| id-regex partition (`00[3-6]`) | clean `MissingInputException` | the baseline block bounds |
| explicit alternation (`"\|".join(derived_ids)`) | clean `MissingInputException` | the derived-id set |
| separate directories | clean `MissingInputException` | which id goes in which directory |
| one rule, branching `input:` function | clean `MissingInputException` | which ids have no ancestor |

[measured — P2 standalone model, six mechanisms × two states]

Every mechanism that constructs needs stage 2 to distinguish two kinds of id at
parse time. Two of the four working ones do it by **hardcoding a reserved id
range**, which is exactly what scope gap 5 / W3 forbids foreclosing. And
`ruleorder` — the cheap escape that would need no such knowledge — **fails**, so it
is out of the option set. So two columns cannot express what any working mechanism
requires.

**The resolution: change what stage 2 is told, not how much.** `derived_from` says
*"this row's forcing is produced by transforming that row's output"*. That is a
**dependency edge**. It is a true statement about any scenario family — a
supplied family has all-empty edges; a downscaling family might have a chain two
deep — and it names no baseline, reserves no id, and constrains no numbering. D1
is satisfied not because stage 2 knows less, but because what it knows is
family-blind.

**The probe's own objection, answered head-on.** P2's constraint note 4 warns that
the data-driven alternation is *"still stage 2 holding a family-specific
distinction"*. It is not, and the distinction is testable rather than rhetorical:
a family-specific fact is one whose *meaning* changes with the family. "Which ids
are baselines" does — `st_0` means something in the stochastic family and nothing
in a GCM-downscaled one. "Which rows have a forcing ancestor" does not; it means
the same thing for every family, and evaluates to the empty set for a family that
supplies all its forcing. The falsifier for that argument is a paper exercise
against a second family's schema, because **E18 is a hypothesis and no second
family exists to test against** — this design does not pretend otherwise, and §10
records it as the open question it is.

**`derived_from` pays for itself twice**, which is the strongest practical
argument for it over any alternative in §6. Under a flat id, rule 3.12 cannot
*compute* which series it perturbs: today the input is
`rlz_{rlz_num}_st_{ST_BASELINE}.nc` (`run_stress_test.smk:1020`), derived from the
member's own realization index. With a flat opaque id that derivation is
impossible, so a lookup is required for the **input** regardless of what the
wildcard constraint does. `derived_from` is that lookup. A design that solved only
the constraint problem — a reserved id block, say — would still need this column.

**Status: [argued], not measured.** The `derived_from` *form* was explicitly not
run (P2, "NOT PROBED"). What was measured is that its two mechanical
ingredients work: the data-derived alternation constraint (mechanism i-c) and the
data-driven branching input (mechanism iv), each clean under both states, and the
alternation scaling to 500 ids with 10 scattered baselines in **2.7 s** — cheaper
than the loose `[0-9]{3}` constraint's 9.5 s, because it prunes candidate producers
rather than enumerating them. The gate that would falsify the composition is
GF-1 in §9, and it MUST be a **fresh-project DAG build**: P2 measured that the
in-file claim at `run_stress_test.smk:1015` is a **false negative on a seeded
dry-run**, and that the `CyclicGraphException` reproduces only through
`tests/test_guard_invalidation.py`.

#### 5.2.3 Seam schema — normative

| column | required | stage 2 uses it for |
|---|---|---|
| `run_id` | yes | the wildcard value; every output filename |
| `derived_from` | yes (nullable) | rule 3.12's `input:` (which series to transform) and its `wildcard_constraints` alternation |
| `forcing_uri` | yes (nullable) | the forcing path for a supplied family |
| `evaluated` | yes | which run CSVs are targets |

Stage 2 derives exactly three parse-time objects from the seam, all pure:

```python
RUN_IDS        = [r["run_id"] for r in SEAM]
DERIVED_FROM   = {r["run_id"]: r["derived_from"] for r in SEAM if r["derived_from"]}
EVALUATED_IDS  = [r["run_id"] for r in SEAM if r["evaluated"]]
```

and the alternation constraint is `"|".join(DERIVED_FROM)`. If `DERIVED_FROM` is
empty — a family that supplies every series — rule 3.12 is unreachable and its
constraint is the empty alternation, which Snakemake treats as matching nothing.
That is the correct outcome and MUST be asserted rather than assumed (GF-2, §9):
an empty alternation that silently matched *everything* would put us back in
mechanism 0.

### 5.3 Stage 2 — the simulator

#### 5.3.1 What stage 2 owns

Stage 2 answers **what each scenario does to the system**. It takes the built
model (S7 — what WF1 built, not a calibrated one) and the seam view, enumerates
the run list, and writes one raw output per evaluated run. It has no concept of a
realization, a design point, a grid, a baseline, or a family.

#### 5.3.2 Raw-output key — normative (scope gap 1, third artifact)

**One raw output per run, keyed by `run_id` and by nothing else.**

| artifact | path |
|---|---|
| climate series | `<exp>/climate/weathergenr/output/run_<run_id>.nc` |
| model forcing | `<exp>/hydrology/wflow/forcing/inmaps_run_<run_id>.nc` |
| run config | `<exp>/hydrology/wflow/config/run_<run_id>.toml` |
| per-run catalog | `<exp>/hydrology/wflow/config/run_<run_id>.yml` |
| **model output** | `<exp>/hydrology/wflow/output/run_<run_id>.csv` |
| warm state | `<exp>/hydrology/wflow/output/outstates_run_<run_id>.nc` |

**`run_` is a token, not a feature.** W4 forbids embedding *features* in the id;
it does not require a bare integer filename. `run_007.nc` sorts, greps and reads
as a run; `007.nc` reads as nothing. The token is fixed text, identical on every
row, so it carries zero information about the scenario and nothing can parse it
for meaning. This follows `naming.md` §4's existing practice of a stable token
plus a zero-padded index (`rlz_`, `st_`), and answers RR-6's real regression — an
unsortable, unreadable outputs folder — without embedding anything.

The `run_id` is minted, zero-padded to the namespace width `W` (§5.5.2), and
**textually identical** in the filename and in every table. One token, one
spelling, everywhere.

#### 5.3.3 What stage 2 must not do

- It must not derive one run's path from another's (that is `derived_from`'s job).
- It must not parse a path to recover anything.
- It must not read the scenario table's family block, or `stress_test_lookup.csv`
  for any purpose other than passing the design parameters through to the
  generator, which is stage 1's artifact travelling as an opaque payload
  (§5.6, rule 3.12).

#### 5.3.4 Deleting `member_from_run_csv` — the replacement, specified (D2)

`export_wflow_results.py:79-92` is deleted. The replacement must not reintroduce
an implicit contract in the form of list ordering.

Rule 3.16's `input:` today is an `expand()` over two wildcard lists
(`run_stress_test.smk:1247`). It becomes a **static list plus an explicit map**,
following rule 3.15's existing precedent of passing a member list through
`params:` (`:1234`):

```python
RUN_CSV_BY_ID = {rid: f"{runs_dir}/output/run_{rid}.csv" for rid in EVALUATED_IDS}

rule derive_wflow_indicators:
    input:
        run_csvs = list(RUN_CSV_BY_ID.values()),
    params:
        run_csv_by_id = RUN_CSV_BY_ID,
        scenario_table = SCENARIO_TABLE,     # rows, not a path
```

The script addresses runs through `snakemake.params.run_csv_by_id`, a dict keyed
by `run_id`. **Order-independence is the point**: a zip of `input.run_csvs` with a
parallel id list would be a positional contract, which is the same class of defect
as the filename regex — an unstated invariant that fails silently when one side is
reordered. The dict makes the association explicit and makes a missing key a
`KeyError` naming the run.

The scenario table travels as `params:` **rows**, not as a path, so the reduction
never re-reads and re-parses stage 1's file and cannot disagree with the DAG about
what ran. This also gives rule 3.16 a real rerun trigger on the scenario set,
which today it lacks: `:1248-1252` records that the rule reads **no** parameter
artifact at all.

#### 5.3.5 Not foreclosing scope gap 5 — the one concrete site

Scope gap 5 is **deferred by W3**, and this design keeps it deferred. Two things
are required for "deferred" to be true rather than nominal:

1. **No reserved baseline id.** The minted `run_id` reserves nothing; the baseline
   is an ordinary row distinguished only by an empty `derived_from`. Two of P2's
   four working mechanisms (the id-regex partition, and its reserved-low-block
   variant) would have hardcoded a baseline range into the DAG; both are rejected
   in §6 for exactly this reason.
2. **The one code site that *does* hardcode the baseline relation must be made
   indirect.** `export_wflow_results.py:362` reads
   `if q_locations and 0 in runs:` — the Class-C wet/dry month is fixed once from
   run index **literal `0`** and then evaluated for every member
   (`:356-365`). Under a flat id that literal is meaningless, so it must change
   anyway. It becomes a lookup of a **declared reference unit** on the metric
   (§5.4.1's `reference` field): the mechanism becomes explicit and family-blind,
   while *which* unit a family nominates — and whether the relation is even
   well-defined for a family that has no unperturbed member — stays open under W3.
   Specifying the mechanism and leaving the semantics open is exactly the
   obligation the intake gives this design: not to settle gap 5 by accident, in
   either direction.

### 5.4 Stage 3 — metrics, grain, and the index table

#### 5.4.1 Grain becomes a declared property of the metric (scope gap 4)

Today grain is **emergent**: a metric is pooled because of which loop it sits
inside. Class A is emitted inside `for rlz, sim in per_rlz.items()`
(`export_wflow_results.py:384-401`); Classes B and C are emitted outside it with
`POOLED_REALIZATION` in the `rlz_id` column (`:405-426`, `:431-441`). Nothing
declares this; a reader recovers it from indentation.

**Normative.** Every metric carries a **grain declaration** in
`blueearth_cst/shared/indicator_tables.py`, beside the metric's name and suffix,
as a structured record:

| field | values | meaning |
|---|---|---|
| `grain` | `"run"` \| `"bundle"` | Whether the metric's value is defined per run or only over a set of runs |
| `bundle_by` | a **grouping key**, required iff `grain == "bundle"` | Which runs share a value. A named function of a scenario-table row, not a column name |
| `reference` | a grouping key, or `None` | The unit whose value fixes a shared parameter for every other unit (Class C's month). `None` for metrics that need none |
| `min_blocks` | integer, or `None` | The estimator's record-length precondition (§5.4.4) |

For the current metric set this makes the existing three classes explicit and
changes no number:

| class | metrics | `grain` | `bundle_by` | `min_blocks` |
|---|---|---|---|---|
| A — linear in years | `mean_annual_*`, `*_p95`, `Q7day_*` means, `BaseFlowIndex`, and every per-subcatchment variable | `run` | — | `None` |
| B — non-linear fit | `return_level_max`, `return_level_7day_min` | `bundle` | `same_design_point` | `RLZ_NUM × N` blocks; see §5.4.4 |
| C — selects a category | `wetmonth_mean`, `drymonth_mean` | `bundle` | `same_design_point` | `None` |

**`bundle_by` is a named function, not a column.** `same_design_point` is
registered in `scenario_families.py` beside the family whose rows it can group —
for `stochastic` it is "equal `st_id`, any `rlz`". This is the one place where a
family-specific fact legitimately enters stage 3, and it enters as a *registered
grouping* rather than as a column reference scattered through the reducer. A
family that declares no such grouping cannot use a `bundle`-grained metric, and
the validator says so by name instead of pooling over the wrong thing. [argued]

Class A stays per-run for the reason `export_wflow_results.py:344-350` already
gives, and that reason is the D5 principle in the concrete: these are "annual
statistic, then mean over years" over equal-length realizations, so per-run values
average back to the pooled value exactly and nothing is lost by storing the finer
grain. `aggregate_rlz` existed only to choose between grains that are not
different, which is why R11 retired it.

**D5's stated exception, and why it is principled.** For Classes B and C the
finest grain that *exists* is the bundle, and the reason is methodological, not
convenient. The GEV is fitted on pooled blocks because a fit over one short
realization is ill-conditioned (`export_wflow_results.py:27-35`); the pooling is
of the **sample**, never a spliced series, because splicing manufactured 7-day
flows occurring in no realization (`:40-46`). Class C pools because `idxmax()`
selects one month and different realizations select different ones. A per-run
Class-B value would not be a finer measurement of the same quantity — it would be
a *different, worse* estimator. Declaring `grain` makes that a statement the code
carries rather than a fact a reader must reconstruct. [measured — the two
docstrings state it; argued that declaring it changes nothing numerically]

#### 5.4.2 Results file — normative (W2)

**Artifact.** `<exp>/results/<token>_indicators.csv`, one per variable in
`workflows.build_model.wflow_outvars`, unchanged from HM-7's current path rule.

**Header, exactly and in order — four columns:**

    metric, location, unit_id, value

- `metric` — composite `<token>_<statistic>`, unchanged. The table is
  self-contained once it leaves the tree and needs no `variable` column;
  `validate_hm7` asserts the metric agrees with the table it sits in.
- `location` — the bare id, unchanged (`130000086`, not `Q_130000086`). `basin`
  stays reserved and unemitted for the Q11 reason.
- `unit_id` — the evaluation unit this value is about: **a run id or a bundle id**,
  drawn from one sequence (§5.5.2). Text, zero-padded, width `W`.
- `value` — `float32`, unrounded, unchanged.

**What is deleted:** `st_id`, `rlz_id` and `POOLED_REALIZATION`
(`shared/indicator_tables.py:125-136`). The sentinel goes with the column that
carried it. This is D4 discharged: no key column means two things, because the one
key column means exactly one thing — an evaluation unit — and the index table says
which kind each is.

**Nothing downstream may `groupby` the index column directly.** The join to the
index table comes first, the grouping second. This is stated in HM-7 (§5.9) so an
out-of-repo consumer reads it, because the consumers that draw a surface are
out-of-repo and re-implement from the contract text.

#### 5.4.3 The unit index — normative (W2's separate table)

**Artifact.** `<exp>/results/unit_index.csv`. A `rule all` target, produced by
rule 3.16 alongside the indicator tables.

**Why `results/` and not `config/` — settled, not left open.** `config/` would pair
it with `scenario_table.csv`, which is the other defensible reading. `results/`
wins because the index is produced by the reduce, is meaningless without the tables
beside it, and must travel with them when a results set leaves the project tree.
The cost is that it becomes a baseline-fingerprinted `rule all` target — which is
free **now**, because §8 re-records the manifest either way, and a re-record later.
Settling it here rather than carrying it as an open question is deliberate: an
unresolved path for a baseline-covered artifact is a migration item, not a
question.

**Header, exactly and in order — three columns, LONG shape:**

    unit_id, grain, member_run_id

| row kind | shape |
|---|---|
| a **run** unit | exactly one row: `grain = run`, `member_run_id = unit_id` |
| a **bundle** unit | *k* rows, one per member run: `grain = bundle`, `member_run_id` = that run's `run_id` |

Long rather than a delimited list, for one reason: it joins. A consumer asking
"which runs is this number over?" performs a join, not a string split, and a
consumer asking "which units mention run 048?" performs the same join in the other
direction. A delimited-list column can answer neither without parsing, which is
the class of contract this design exists to remove.

**Bundle meaning is recovered by joining, not by a column.** The index deliberately
carries **no** `bundle_key` or label column. A bundle's meaning is "the set of runs
it contains", and what those runs have in common is answered by joining
`member_run_id` back to the scenario table's family block. A label column would be
family-specific text inside a family-blind artifact, and it would be a
denormalised copy — the exact defect C28's obligation 1 was written to contain.

**Invariants (asserted by `validate_hm7`, §5.9):**

1. Every `unit_id` in every indicator table **resolves** in `unit_index.csv`.
   This is W2's safety condition, checked rather than assumed.
2. Every `member_run_id` resolves in `scenario_table.csv`.
3. No `unit_id` appears with two different `grain` values.
4. A `grain = run` unit has exactly one row, and its `member_run_id` equals its
   `unit_id`.
5. Every metric's declared grain matches the grain of every unit it is emitted
   against. A `bundle`-grained metric emitted against a run unit is refused, and
   so is the reverse.
6. The `unit_id` set of the index equals the minter's **evaluated** namespace for
   this configuration — every `evaluated: true` run, plus every bundle over them —
   completeness, so a truncated reduce is a failure rather than a shorter table.
   It is deliberately **not** the minter's whole run slice: under
   `run_historical: false` an unevaluated ancestor row exists in the scenario
   table and has no unit, which is correct and must not be read as a hole (§5.5.2).

Invariant 5 is the one that replaces the sentinel's implicit guarantee. The
`POOLED_REALIZATION` comment says the scheme is *"safe ONLY because no metric emits
both grains"*; invariant 5 makes that a checked property instead of a standing
condition nobody re-checks when a metric is added.

#### 5.4.4 Record length as a declared estimator precondition (scope gap 6, RR-3)

**The finding.** `export_wflow_results.py:27-35` states that the Class-B GEV is
fitted on `RLZ_NUM × N` blocks *because* a fit over one short realization is
ill-conditioned. That is a precondition on the estimator, and nothing records it.
The same docstring names the unstated assumption behind it: both pooling methods
give `RLZ_NUM × N` blocks *only if* every realization is a whole number of years
on the same calendar boundary, "and nothing checks that". [measured — the
docstring]

It is not a defect today, because one family with one record length produces every
row. It becomes one the moment a second family shares the table under the same
metric name: a 30-year GCM-downscaled run and a multi-realization stochastic
bundle would carry `q_return_level_max` in the same column with materially
different estimator precision, and nothing would say so.

**Normative.** `min_blocks` on the metric declaration is a **precondition, not a
diagnostic**. At reduction time, for each bundle a `bundle`-grained metric is
computed over, the reducer counts the blocks actually available and:

- if the count is below `min_blocks`, it **refuses** — raising, naming the metric,
  the unit, the required and the actual block count — rather than fitting;
- it never silently degrades to a smaller sample, and never emits a row it could
  not compute to the declared precision.

**`min_blocks` is a constant integer floor per metric, not a function of config.**
That is the whole point: a threshold derived from `RLZ_NUM × N` would equal the
sample the run happens to produce and could never fire, which is documentation
wearing a check's clothes. It is an absolute statement about the estimator — *this
GEV is not defined below this many blocks* — and it therefore **can** refuse a
configuration.

**Its value for this milestone is set to the block count the shipped baseline
config produces, and no higher.** That keeps the change output-neutral on every
shipped config (§9 GF-9) while leaving the mechanism real: a config with fewer
realizations or a shorter run than the baseline **will** refuse, which is the
intended behaviour and must be documented as a user-visible consequence.

**Raising it to a literature-defensible floor is a separate decision and is
deliberately not taken here** (§10, Q7). Choosing a number from extreme-value
practice rather than from the fixture is a methodological change that would refuse
existing configurations, and a precondition introduced alongside a rename must not
move a number or refuse a run that used to work — otherwise the migration's
baseline evidence becomes unreadable (§8). This design ships the mechanism and the
declaration site; the threshold's scientific calibration is named as owed.

**Why refuse rather than record.** The alternative — a `n_blocks` column beside
each value — was considered and rejected in §6 (A7). It re-couples the results
header to an estimator detail, it makes every consumer responsible for a check it
will not perform, and it answers a *comparability* question with a number rather
than with a decision. Refusing states the toolbox's position: this metric is
defined at this precision or it is not emitted. This is the same shape as
`prepare_cst_parameters.refuse_out_of_domain_multipliers`
(`prepare_cst_parameters.py:82-120`), which refuses a configuration whose
arithmetic the WG-2 bound cannot cover rather than emitting a caveat.

#### 5.4.5 Overlay coordinates and scenario-neutrality (RR-5 / E19)

The intake records an unruled position; this design rules it.

**Ruling.** A family's response-surface coordinates are **columns supplied by
stage 1**, computed by whatever produced the scenarios. Stage 3 *reads* them; WF3
never *derives* them.

For the `stochastic` family the coordinates are already a derivation from
`stress_test_lookup.csv` at reporting time — the axis is a declared triple
`{variable, months, statistic}` evaluated over the lookup, specified completely in
HM-7 and implemented for reference in `shared/surface_axes.py`. That derivation is
family-specific and stays where it is; it is reached through the scenario table's
`st_id` column, which is in the family block. A future GCM-derived family would
carry its `(ΔT, ΔP)` as its own family-block columns, produced by whatever
downscaled it.

**Why this satisfies S5/S6.** A change-factor computation is WF2's business. If
WF3 derived overlay coordinates it would have to import that computation, and the
experiment workflow would acquire a CMIP dependency — precisely what `AGENTS.md`
§ Background forbids. Supplying them as data keeps the boundary: WF3 plots a point
it was handed and computes no projection quantity. [argued]

**Consequence, stated rather than left to be found.** The surface reduction becomes
**family-gated**: it draws a surface only for a family that declares surface-axis
columns, and reports (never silently omits) that it drew none for a family that
does not. Specifying the plotting change is a non-goal; specifying the gate is
not, because without it a second family silently produces an empty or nonsensical
surface. **E19 is a HYPOTHESIS** — that plotting a GCM-derived run requires its
`(ΔT, ΔP)` is argued from the shape of a response surface, not measured — and if
it is false, this ruling costs nothing (the columns are simply unused).

### 5.5 The identity: column name, sequence, stale-lookup guard

W4 directs the *form* — a plain zero-padded sequential number, nothing embedded,
width from `index_width` (C27). Three things were left open. This section settles
all three.

#### 5.5.1 The column name — settled: two names, one namespace

**Decision.** `run_id` in the scenario table and the seam view; `unit_id` in the
results tables and the unit index. Identical value space, identical spelling,
identical width: a run's `unit_id` *is* its `run_id`, character for character.

**This is a type declaration, not two namespaces.** A column's name states what it
may contain:

- `run_id` may contain **only** run ids. That is what lets the seam's contract be
  stated at all, and what lets a validator refuse a bundle id appearing in a
  stage-1 or stage-2 artifact.
- `unit_id` may contain **a run id or a bundle id**. That is what W2 asks for, and
  naming it `scenario_id` would assert something false about half its values —
  the intake's own objection, that *"calling a bundle a 'scenario' reads oddly"*.

W2 constrains the **results file's** index column and says nothing about the
scenario table's key, so this refines W4's open point rather than departing from
it. The single-name alternative is recorded in §6 (A1) with the reason it lost.

**`scenario_id` is not used as a column name anywhere.** The word survives in prose
and in the family block's `scenario_family`, where it is accurate.

#### 5.5.2 One sequence, one width, and where it is minted

**Decision, following W4.** Run ids and bundle ids draw from **one sequence** at
**one width**. `048` is a run, `061` is a bundle, and `unit_index.csv` is what
distinguishes them. No prefix, no embedded type, no reserved range.

**The minter.** `blueearth_cst/shared/scenario_index.py` holds one pure function
that mints the whole namespace:

```python
def mint(scenario_rows, grain_declarations) -> Namespace: ...
```

- `W = index_width(len(runs) + len(bundles))` — one width for the whole namespace.
- Run ids are minted first, in scenario-table order, from `1`.
- Bundle ids continue the same counter, in a **deterministic** order: sorted by
  `(bundle_by name, grouping key)`, so the same configuration always mints the
  same namespace.
- It **raises** on an empty run set (§5.1.4).

**The run slice and the evaluated namespace are different sets, and the minter
returns both.** Ids are minted for **every** scenario-table row, including rows
with `evaluated: false` — an id is a name, and a forcing ancestor needs one
(rule 3.12 addresses it). Units are declared over the **evaluated** rows only. So
under `run_historical: false` the baseline row holds a `run_id`, appears in no
`unit_index.csv` row, and that is the correct state rather than a hole — which is
why §5.4.3's invariant 6 is stated against the evaluated namespace and not against
the run slice.

**Why the minter is shared rather than owned by a stage.** This is C26's *"one
enumeration, two consumers"* applied one level up. Stage 1 consumes the run slice
and writes the scenario table; stage 3 consumes the whole namespace and writes the
unit index. Neither stage owns the other's concept, and the two cannot disagree
about a width or an id, because there is only one place either is computed.

**Pre-empting the obvious objection.** Minting run ids requires the *count* of
declared bundles, so the minter reads the grain declarations. That does **not**
put grain in the scenario table (no grain column exists), does not make grain a
stage-1 decision (stage 1 never evaluates a grouping), and does not let stage 1
name a bundle. It reads one integer to size a field. S3 holds.

**The residual coupling, stated honestly.** Because `W` is sized over the whole
namespace, introducing a metric with a **new grouping** changes the bundle count,
which can change `W`, which renames every stage-2 file. Three things bound it:

1. It fires only when a *new grouping* is introduced. Adding a metric that reuses
   an existing `bundle_by` adds no bundle and cannot move `W`.
2. It fires only when the count crosses a power of ten.
3. It is **loud**: the digest guard (§5.5.3) refuses the run rather than mixing
   two widths in one tree.

The alternative that decouples fully — a per-artifact width, `W_run` for
run-scoped artifacts and `W_total` for unit-scoped, with the index table as
crosswalk — is rejected in §6 (A2) because it gives one run **two spellings**, and
the absence of a second spelling is precisely the property whose loss produced E1.
One width, one spelling, one stated cost.

#### 5.5.3 The stale-lookup guard — settled

**The hazard.** A sequential id means nothing except relative to the table that
defines it. Re-running a *changed* scenario set into an existing experiment folder
silently relabels yesterday's outputs: `run_007.csv` from the old set and `007` in
the new scenario table are different scenarios wearing one name. C25's
experiment-scoping ruling contains the **cross-experiment** case; the **in-place**
case needs the table to be identifiable.

**Decision.** A canonical digest of the scenario table is written beside the run
outputs and checked at parse time.

- **`scenario_table_sha256`** = SHA-256 over the canonical serialization of the
  scenario table: rows sorted by `run_id`, columns in schema order, values as the
  CSV text the writer emits, LF-joined, UTF-8. Canonical because a digest over the
  file's bytes would fire on a line ending or a column reorder that changed no
  scenario.
- **Written** by rule 3.09 to `<exp>/config/.scenario_table.sha256`, and carried
  into `<exp>/results/run_metadata.json` by rule 3.16b, which already exists for
  exactly this class of fact and already takes the indicator tables as *input*
  rather than writing into them, so that recording a digest cannot falsify the
  baseline.
- **Checked at parse time.** If `<exp>/config/.scenario_table.sha256` exists and
  disagrees with the digest of the table just derived, WF3 **refuses**, naming
  both digests and the experiment, and telling the user the two resolutions: run
  into a new experiment (C25's mechanism, still the right answer), or delete the
  experiment's run outputs deliberately.
- The refusal is **not** silenceable by a flag. A flag here would be a
  configuration surface for corrupting a results file.

**This is what makes D3's narrowing safe.** W4 narrows "the id must be stable
under set growth" to "the *design* must be stable; the index may renumber,
provided a changed lookup is detectable rather than silent". The digest is the
detector. Without it, W4's narrowing is not a narrowing but a removal.

#### 5.5.4 `member_hash` under a minted id — E20 resolved, and what survives

**They are not the same object and must not be merged.** `member_hash`
(`design-v4.md:987` at tag `archive/wf3-experiment-v2`) is a SHA-256 over the
canonical JSON of a member tuple plus its result-affecting inputs — a **machine
freshness boundary**. A minted `run_id` is a **human-and-join handle**. Merging
them produces an id that is opaque *and* unsortable, which is the exact objection
C25 raised against content-hashed ids.

**What survives, and what does not, in this design:**

- The *idea* survives as §5.5.3's `scenario_table_sha256` — but at **table** grain,
  not member grain. A table digest is the minimal object that detects a stale
  lookup, which is the only freshness question this design has.
- Per-**run** content digests do **not** enter here. Their purpose is selective
  reuse — "this member's inputs are unchanged, skip it" — which is R12's execution
  model and an explicit non-goal (§2.2). Adding them now would ship half a
  resumability mechanism with no ledger to make it correct, and design-v4 records
  in detail how a member-freshness predicate that inspects the wrong terms
  publishes a response surface computed against superseded realizations while the
  manifest records the new ones.
- When the execution model is authored, `member_hash` attaches to the `run_id`
  as a **column of a ledger**, not as a replacement for it. That is the correct
  relationship and this design does not foreclose it.

#### 5.5.5 Does this subsume `t2608082036`?

**Partially, and the boundary is exact.** `t2608082036` ("re-derive the WF3 v2
execution design against the post-R11 tree") was dropped 2026-08-18 by owner
ruling, and `dev/LOG.md:47` records that **eight references survive it**, the row
itself being what they now resolve to.

- **Subsumed:** everything those references assign to *identity and stage
  boundaries* — what a member is, how it is named, how the reduce keys its rows,
  and the WG/HM clauses that pin those. Three of the eight references
  (`stress-test-lookup-design.md` ×3) assign WF3 execution mechanics — rule shape,
  rerun triggers, log and benchmark parts — and the identity half of that is
  settled here (§5.6).
- **Not subsumed:** the manifest, the ledger, resumable sweeps, epochs and
  transition legality, quarantine, checked atomic publication, and the
  counterbalanced timing protocol. Those are what the `wf3-experiment-v2` record
  lists as *surviving* architecture, and they are this milestone's declared
  non-goal.

**Recommendation to the roadmap** (specified here, executed after G2 — see §8's
authority note): repoint the identity-flavoured references at this design, and
mark the execution-model references as still open under a successor item. The LOG
row already states the requirement: *"If the work is genuinely abandoned,
`roadmap.md` and the two milestone docs need saying so; if it returns under a new
ID, they need repointing."* This design answers "it returns, in two halves".

### 5.6 Rule-level changes

Enough to implement, and no more — the owner's emphasis puts depth in §§5.1–5.5,
and this section is the mechanical consequence of them. Every rule keeps its
number: `naming.md` §8b forbids renumbering to insert a rule, and none is inserted.

| rule | change |
|---|---|
| **3.09** `prepare_stress_test_grid` | Gains a **second output**, `<exp>/config/scenario_table.csv`, written from `scenario_index.scenario_table(cfg)` — the same object the Snakefile minted at parse time (§5.1.4). Also writes `<exp>/config/.scenario_table.sha256`. `stress_test_lookup.csv` is unchanged in shape and content. One rule and one enumeration, per C26 |
| **3.11** `generate_weather_realizations` | Output list becomes `[f"{wg_dir}/output/run_{rid}.nc" for rid in ROOT_IDS]`, where `ROOT_IDS` are the run ids with empty `derived_from` **and** empty `forcing_uri`. Still one job, still a static Python list, still zero wildcards — unchanged in shape from `run_stress_test.smk:978-990`. The R receives the concrete output paths it must write, as it does today via the width params |
| **3.12** `perturb_climate_realization` | `wildcard_constraints` becomes `run_id = "\|".join(DERIVED_FROM)` — the measured mechanism (i-c), data-derived, replacing `st_num=member_index_regex(ST_WIDTH)` at `:1018`, whose token no longer exists. `input.rlz_nc` becomes `lambda w: f"{wg_dir}/output/run_{DERIVED_FROM[w.run_id]}.nc"`. `lookup_csv` stays a constant input (`:1026`) and the design-point argument becomes the row's `st_id` from the scenario table, passed via `params:` rather than parsed from the wildcard |
| **3.14** `downscale_climate_realization` | Wildcard `{run_id}` replaces `{rlz_num}`/`{st_num}`; `wildcard_constraints: run_id=rf"[0-9]{{{W}}}"` keeps the digits-only guard that stops a path splitting across a `/` boundary. Output paths per §5.3.2 |
| **3.15** `run_wflow_batch_<b>` | `_k_members` becomes a flat list of `run_id` strings — it is *already* a flat list (`:1120`), so this is a substitution, not a restructure. `params.members` carries run ids; `_member_span`'s two-range banner is replaced by a first–last id span, since a flat list has no rectangle to describe and the `(partial)` caveat at `:1210-1213` becomes vacuous |
| **3.16** `derive_wflow_indicators` | `input:` becomes the static list of §5.3.4; `params:` gains `run_csv_by_id` and the scenario-table rows. Gains a **second output**, `<exp>/results/unit_index.csv`. `params.st_num` / `params.st_start` (`:1266`, `:1271`) are deleted — run coverage is now checked against the minted namespace |
| **3.16b** `write_run_metadata` | Gains `scenario_table_sha256`. Unchanged otherwise, and still takes the indicator tables as `input:` so the digest never lands inside a baseline-fingerprinted file |

**Rerun triggers, and the trap this workflow already has.** P4 asks whether the
stage-3 metric spec re-fires the reduce when it changes; rule 3.09's own comment
(`run_stress_test.smk:882-887`) records the shape of the hazard — both its config
inputs are `ancient()`, so `params.stress_test_cfg` is its **only** rerun trigger,
and without it a grid edit would leave a stale table in place. Rule 3.16 today
reads **no** parameter artifact at all (`:1248-1252`), so a grain declaration
change would not re-fire it. Passing the scenario-table rows and the grain
declarations through `params:` (§5.3.4) gives it one. **P4 is not yet executed**
and this design does not claim it is; GF-6 in §9 is its gate.

**Parse-time refusals, all in one place.** The empty scenario set (§5.1.4), the
`derived_from`/`forcing_uri` exclusivity and acyclicity rules (§5.1.2), and the
digest mismatch (§5.5.3) are all raised by `scenario_index` before the DAG is
built, in the same position as `refuse_out_of_domain_multipliers` today. A refusal
that lands after the DAG is a refusal that has already cost a run.

### 5.7 WG-2 replacement text

WG-2 pins `<exp>/config/stress_test_lookup.csv` — the monthly perturbation grid.
**It is not the artifact that carries the member naming pattern**; that is WG-4
(§5.7b), and the intake's E13 and scope gap 7 attribute it to WG-2 in error. WG-2's
shape, semantics, precision and multiplier domain are **entirely unchanged** by this
design. Three clauses change, all about how the table is *reached*.

**Replacement clauses (the rest of WG-2 stands verbatim):**

- **`st_id`:** the design-point id, **zero-padded** to a width derived from
  `ST_NUM` (C27), **textually identical to the `st_id` column of the
  `stochastic` family block in `<exp>/config/scenario_table.csv`**, so the two are
  ONE token and the two tables join without a crosswalk. It is **no longer**
  identical to any filename token — filenames carry `run_id` (§5.3.2), which is a
  different namespace at a different width. **Read it as a string**; every
  `st_id` in one table has the same width; a table mixing widths is malformed.

- **`st_0` has NO row, and the reason is now stated once rather than twice.** The
  table covers design points `1..ST_NUM`. The unperturbed baseline has no design
  parameters, so it has no row here, and in `scenario_table.csv` it is the row
  with an **empty `st_id`** and an empty `derived_from`. Its absence from this
  table remains load-bearing: an all-zero row would be indistinguishable from an
  identity design point while denoting a differently-processed climate.

- **consumer:** rule 3.12 `perturb_climate_realization`, passed in as `lookup_csv`
  — a **constant** input. The design-point id arrives as a `params:` value taken
  from the scenario table's family block, **not** parsed from a wildcard or a
  filename. It is not an `input:` on rule 3.16; the reduction reaches the design
  parameters through the scenario table.

- **pinned surface** gains one clause: **`st_id` joins `scenario_table.csv`'s
  family block for the `stochastic` family, and that join is total in one
  direction** — every non-baseline scenario row's `st_id` appears in this table.
  The reverse need not hold (a design point with no realization is a config the
  grid can express and the run set need not contain).

### 5.7b WG-4 and WG-6 — the clauses the intake did not count

**Finding, reported here because the intake is frozen.** The intake's scope gap 7
says *"Three contract clauses change"* and names WG-2, WG-5 and HM-7. That
undercounts. The `rlz_<n>_st_<m>` spelling is pinned in **nine** clauses across two
contract documents:

| clause | site | what it pins |
|---|---|---|
| WG-2 | `weather-generator-seam.md:166-180` | `st_id` as the filename token; `st_0` absent |
| **WG-4** | `:238-244` | **`naming pattern: rlz_<n>_st_<m>.nc` — a DAG-globbed pattern**, repeated under *pinned surface*. **This is the clause E13 attributes to WG-2** |
| WG-5 | `:260-284` | one catalog entry per `rlz_<n>_st_<m>`, including `st_0`; the entry-key grid |
| **WG-6** | `:311` | `naming pattern: forcing/inmaps_rlz_<n>_st_<m>.nc` |
| HM-2 (wf3 twin) | `hydrological-model-seam.md:75` | the wf3 forcing twin path |
| HM-4 | `:169` | `config/rlz_<n>_st_<m>.toml` |
| HM-5 | `:214` | `output/rlz_<n>_st_<m>.csv` |
| HM-6b | `:277, :286` | `output/outstates_rlz_<n>_st_<m>.nc` |
| HM-7 | `:300-319` | the results columns |

[measured — `grep -n` over both contract files]

**Replacement, WG-4:**

- **path pattern:** `<exp>/climate/weathergenr/output/run_<run_id>.nc`, for every
  run in the scenario table, whether its series is generated *ab initio* (rule
  3.11) or by transformation (rule 3.12). The path does not distinguish the two —
  which is the point: the producer is determined by the scenario table's
  `derived_from`, not by the filename.
- **naming pattern:** `run_<run_id>.nc` — `run_` is a fixed token carrying no
  information; `run_id` is a zero-padded sequential index at the namespace width
  `W`. **The pattern is DAG-globbed** (rule 3.14 wildcards; rules 3.11/3.12
  enumerate), and **nothing parses it**: a consumer that needs to know what a run
  *is* joins `scenario_table.csv`.
- Everything else in WG-4 — the `(time, lat, lon)` raster shape, the minimal
  `{precip, temp}` variable set, the `spatial_ref` CRS descriptor, the `temp()`
  lifecycle, the asserted-if-present `crs`/`category` rule — is **unchanged**.

**Replacement, WG-6:** `naming pattern: forcing/inmaps_run_<run_id>.nc`. Nothing
else in WG-6 changes.

**HM-2 / HM-4 / HM-5 / HM-6b** take the corresponding path substitutions from
§5.3.2 and change in no other respect. They are listed here so the migration's
"every live reference in the same commit" obligation (D7) has a complete target
list, and so the validator-index rows at `hydrological-model-seam.md:744-763` and
`:792-795` are updated with them.

### 5.8 WG-5 replacement text

WG-5 pins the per-run hydromt data catalog. **S8 binds here**: the catalog *schema*
is hydromt's and is used verbatim; only the **entry key** — a name we choose —
changes.

**Replacement clauses:**

- **path pattern:** `<exp>/hydrology/wflow/config/run_<run_id>.yml` — ONE per run,
  `temp()`, beside that run's TOML. One catalog per run, not one aggregate naming
  every run: the entries differ only in `uri`, so an aggregate forces its producer
  to fan in over the whole sweep.
- **shape (pinned-as-reliance — hydromt data-catalog schema, OUR emitted
  subset):** one entry keyed **`run_<run_id>`**, carrying
  `{uri, driver.name = raster_xarray, driver.options.preprocess = harmonise_dims,
  driver.options.lock = false, metadata.crs = 4326, metadata.category = meteo,
  data_type = RasterDataset}`. The key is the same token as the file's own
  basename, so a reader never has to know two spellings.
- **cross-artifact invariant:** the **entry-key set equals the run set** — every
  `run_id` in the scenario table with `evaluated: true`, and every root run whose
  series a perturbed run derives from. Previously stated as "the realization × cst
  grid"; that phrasing embedded the factorial assumption in the contract and is
  replaced by a set equality against a table, which is checkable for any family.
  Checked by the relational validator `validate_wg5_catalog_grid`, which is
  renamed **`validate_wg5_catalog_runs`** — "grid" is now a false description of
  what it checks. (`naming.md` §7 covers this: it is a test-facing identifier, so
  the rename rides in the same migration note.)
- **The "including `st_0`" clause is deleted**, not reworded. It named a
  family-specific member. Its content is preserved by the set equality above,
  which covers the baseline because the baseline is an ordinary run.
- **temp() lifecycle, pinned surface, deliberately unpinned, validators:**
  unchanged in substance; `validate_wg5` (per-entry schema) is untouched, since no
  per-entry field changes.

**P3 is unexecuted and this design does not claim otherwise.** The probe asks
whether hydromt still resolves the catalog when its key is the new id. The
mechanism is a dict key in a YAML file that our own code writes and our own code
names in the `-d` argument, so nothing upstream is being asked to parse it —
[argued] — but "argued" is not "measured", and GF-7 in §9 is its gate.

### 5.9 HM-7 replacement text

**Finding first, because it is independent of this design.** The HM-7 contract
document is **already stale against its own validator**.
`hydrological-model-seam.md:310-319` pins *"exactly seven columns, in this order:
`metric, location, st_id, rlz_id, temp_change, precip_change, value`"*, while
`shared/indicator_tables.py:125-131` defines five columns and
`shared/interchange_contracts.py:842` asserts five, its docstring explaining that
the axis columns were removed and *"the counts in that sentence are the historical
ones and are not a typo"*. So the validator and the module agree with each other
and disagree with the contract text a re-implementer reads. [measured — three
sites]. This design's replacement fixes it; it would need fixing regardless.

**Replacement HM-7:**

- **path pattern:** `<exp>/results/<token>_indicators.csv`, one per variable in
  `workflows.build_model.wflow_outvars`. Unchanged.
- **producer:** rule 3.16 `derive_wflow_indicators`
  (`blueearth_cst/experiment/export_wflow_results.py`). Unchanged.
- **consumer:** CST-API / GUI (terminal in-repo). Unchanged.
- **pinned surface — every table carries exactly four columns, in this order:**

      metric, location, unit_id, value

  The header does not grow with the gauge count (locations are rows) and no longer
  grows with the stress dimension count either. `metric` is a composite
  `<token>_<statistic>`, so a table is self-contained once it leaves the project
  tree; `validate_hm7` asserts the metric agrees with the table it sits in.
  `value` is `float32` and unrounded.

- **`unit_id` — the evaluation unit, and the rule for reading it.** Zero-padded
  **text** at the namespace width. It names **a run or a bundle of runs**, and
  **which** is stated in `<exp>/results/unit_index.csv`, never inferred. Two
  normative consequences for consumers:

  1. **Join before you group.** Nothing may `groupby` this column directly. A
     bundle row and a run row are not two observations of one thing, and grouping
     them together silently averages a return level into a mean.
  2. **Resolve, or fail.** Every `unit_id` here appears in `unit_index.csv`. A
     consumer that cannot resolve one has a truncated or mismatched pair of files
     and must stop rather than drop the row.

  `rlz_id`, `st_id` and the `POOLED_REALIZATION` sentinel are **gone**. A pooled
  value is a bundle unit, stated in the index; a per-realization value is a run
  unit. The sentinel's standing precondition — *"safe ONLY because no metric emits
  both grains"* — is discharged rather than restated, because the two grains now
  have two kinds of id instead of one column with an out-of-band value.

- **`unit_index.csv` is part of this contract**, with the schema and six
  invariants of §5.4.3. It is a `rule all` target and persists.

- **`location`:** unchanged — the bare id; `basin` reserved and unemitted (Q11).

- **variable tokens:** unchanged (`q`, `precip`, `aet`, `gwr`, `overland_flow`,
  `snow`), with the minting rule and the glossary cross-reference as written.

- **The response-surface axis derivation** is unchanged in substance and moves one
  join further out: it is reached through `scenario_table.csv`'s `stochastic`
  family block (`st_id`) rather than assumed of every row, and it applies **only**
  to rows whose units resolve to runs of a family declaring surface-axis columns
  (§5.4.5). `shared/surface_axes.py` stays the reference implementation. The
  clause that *"there is no `st_0` row"* in the lookup stands, and its consequence
  — the baseline is reported as an annotated reference value beside the surface,
  never placed on it — is unchanged and still `t2608151154`'s business, not this
  design's.

- **`validate_hm7` asserts**, in addition to the header, the vocabulary and the
  metric/table agreement it asserts today: the six `unit_index` invariants of
  §5.4.3, and each metric's emitted grain against its declaration. Its `rlz_num`
  and `lookup` optional arguments are replaced by `unit_index` and
  `scenario_table`.

### 5.10 The superseding decision record — C24, C28, and why not C25

**Mechanism.** `dev/milestones/r09/wf3-change-requests.md` is in
`dev/reference/sealed-records.yml` and `tests/test_sealed_records.py` fails any
edit to it. So the record is **superseded, never edited**, by a new ADR under
`dev/decisions/` — the next free number is **0009** (`dev/decisions/` currently
runs 0001–0008), filed as
`dev/decisions/0009-one-run-identity-with-declared-grain.md` and indexed in
`dev/decisions/index.md`.

**This section specifies that record's content. Writing it is a post-G2 act**
(§8's authority note).

#### 5.10.1 C24 — superseded, reason by reason

C24 (`wf3-change-requests.md:640-646`) ruled *"two id spaces, not one… Run
identity stays `(rlz, st)`"* on four reasons. Each is answered separately, because
a supersession that argues the conclusion rather than the reasons is an assertion.

| # | C24's reason, as written | Disposition |
|---|---|---|
| 1 | *"C10 pools over realization but not design, and one opaque id cannot express that"* | **Superseded, and the premise was already false when written.** The claim is that pooling is a property of the id space. E9 shows two bundlings coexist in one output today (`export_wflow_results.py:384`, `:405-426`, `:431-441`), and the composite id cannot express *that* either — it expresses one, and the second is smuggled in as `POOLED_REALIZATION` (`indicator_tables.py:136`). The replacement does not make one id express pooling; it moves pooling out of the id entirely, into a declared metric property with an explicit index (§5.4). What C24 asked the id to do, no id can do |
| 2 | *"adding realizations would otherwise renumber the design"* | **Premise removed by W4, not disputed.** It was written when the id was the only handle on a design point. Under this design `st_id` survives as a **lookup column** in the scenario table's family block and in `stress_test_lookup.csv`, so adding realizations renumbers the opaque handle and leaves the design untouched: grid point 3 is still grid point 3, in a table a reader consults anyway. Decision criterion D3 is narrowed accordingly — what must be stable is the *design's* identity, not the index — and the narrowing is made safe by the digest guard (§5.5.3), which is the part C24 could not have anticipated because it had no reason to |
| 3 | *"the P3-3 batching work groups by realization via wildcard patterns"* | **Expired, measured.** The landed batch rule has no wildcards: `run_stress_test.smk:1216-1241` generates one rule per batch with static Python input/output lists sliced from the flat `_k_members` (`:1120`). Nothing groups by realization via a wildcard pattern anywhere in WF3 (E5) |
| 4 | *"a failing run's log should name what broke"* | **Expired, measured — and improved.** Logs are keyed by batch id (`:1238-1240`); the member span is a console banner string, not the log's identity (E6). Under this design a failing run is named by its `run_id`, which resolves in one join to a table row stating everything the run is — strictly more than `rlz 2 / st 7` conveyed, and it does not degrade when the batch spans a ragged slice, which `_member_span`'s `(partial)` caveat (`:1210-1213`) exists to admit |

**Net:** two reasons expired against the tree; one rests on a premise W4 removed;
one asks the identity to do something it demonstrably never did. C24 is superseded
in full.

#### 5.10.2 C28 — superseded, with its own trigger stated

C28 (`wf3-change-requests.md:659-690`) ruled **"at this stage"**, explicitly
against the recommendation, that the results tables carry `st_id` *alongside* the
perturbation columns, with **"an explicit revisit when a third dimension
arrives"** (E15). It carried two obligations: a consistency check in
`validate_hm7`, and a hard stop when a third stress dimension appears.

**Its trigger fired, and not the one it named.** C28's own text records the
position plainly: *"alongside re-couples the results header to the stress
dimension count, which is exactly what CR-2 removed on the location axis. That is
tolerable at two dimensions and is not a permanent position."* The named revisit
condition was a third axis. What actually arrived was different and stronger:

1. **Half of C28 was already undone.** R11 removed `temp_change` and
   `precip_change` from the results because a month-length-weighted annual mean
   misreports a seasonal design (`indicator_tables.py:116-124`;
   `interchange_contracts.py:844-857`). The seven-column shape C28 ruled has not
   existed since — only the contract document still describes it (§5.9's finding).
   So C28's *"plottable without a join"* benefit, which was the whole reason the
   owner chose `alongside` over `replace`, is already gone: a consumer already
   joins the lookup to get an axis.
2. **`st_id` is now family-specific.** C28 was a normalisation trade inside one
   family. Under a family-blind results file it is also a **correctness** problem:
   `st_id` is undefined for a family that has no design grid, so a column that is
   sometimes meaningful is a column that is sometimes blank, which W2 rules out.

**Disposition:** C28 is superseded. The results file carries `unit_id` and no
family column; the join C28 avoided is now a join to `unit_index.csv`, which is
required anyway for a reason C28 did not have — the mixed run/bundle namespace.
C28's obligation 1 (a consistency check on a denormalised copy) is discharged by
there being no denormalised copy. Obligation 2 (a hard stop at a third dimension)
**survives and moves**: `prepare_cst_parameters._KNOWN_AXES` still refuses an
unrecognised axis at write time, and the refusal message must now cite ADR 0009
rather than C28.

#### 5.10.3 Why C25 is **not** superseded

C25 (`wf3-change-requests.md:647-651`) ruled that ids are **experiment-scoped** —
the table lives in `experiments/<id>/` beside the config snapshot — and rejected
content-hashed ids as *"stable but opaque and unsortable"* and positional ids as
growing a segment per dimension.

**W4 satisfies C25 rather than overturning it, on both halves.**

- **The objection was to ids that are opaque *and* unsortable.** A zero-padded
  sequential number is neither: it sorts lexically (that is what `index_width`,
  C27, exists for) and it is not opaque in the sense C25 meant — a content hash is
  opaque *and* has no order; a sequential index has a total order and a table that
  explains it. C25's rejected alternatives are still rejected here: §5.5.4 keeps
  `member_hash` out of the id for exactly C25's reason, and no positional scheme
  is proposed.
- **The experiment-scoping ruling is load-bearing and is *relied on*.** It is what
  contains the cross-experiment case of the stale-lookup hazard: because ids are
  scoped to an experiment folder, `007` in experiment A and `007` in experiment B
  never collide, and the guard §5.5.3 has to cover only the in-place case. Remove
  C25 and the digest guard becomes insufficient rather than merely narrower.

**Disposition: C25 stands, unamended.** ADR 0009 must say so explicitly and say
why — a supersession record that lists two of three neighbouring rulings and is
silent on the third invites a future reader to assume the omission was an
oversight.

## 6. Alternatives considered

Each row is a shape that was genuinely on the table, with what it would have cost.
A1, A2 and A3 are the three the reviewer should press hardest.

### A1 — One column name everywhere (`unit_id`, or `id`, or `index`)

**Shape.** A single key column name in the scenario table, the seam, the index and
the results, since all four draw from one sequence.

**Motivation.** The intake's own instruction: *"Settle it once; renaming a key
column later costs a baseline re-record."* One name is one thing to learn, and
`scenario_id` was rejected only because *"calling a bundle a 'scenario' reads
oddly"* — a naming problem a neutral word solves.

**Rejected because a column's name is the only place its admissible contents can
be declared.** Under one name, nothing states that a bundle id may never appear in
a stage-2 filename or a seam row, so nothing can check it — and that is the class
of unstated invariant (E1's filename regex, C28's unchecked denormalised copy)
this design exists to remove. Two names cost one sentence of explanation and buy a
validator rule. **What would change the decision:** a demonstration that a
validator can state the same restriction without the name — e.g. a per-artifact
declared id domain in the contract text alone. That is possible but weaker: it
puts the restriction where only a reader of the contract sees it, rather than in
the artifact a consumer opens.

### A2 — Two widths (`W_run` for run artifacts, `W_total` for unit artifacts)

**Shape.** Size run ids from the run count alone; size the unit namespace from the
total; let `unit_index.csv` be the crosswalk between `048` and `0048`.

**Motivation.** It fully removes §5.5.2's residual coupling: adding a metric with
a new grouping could never change a stage-2 filename.

**Rejected because it gives one run two spellings.** A run would be `048` in the
scenario table and its filename, and `0048` in the results — and the crosswalk
would be mandatory for a join that is otherwise trivial. The absence of a second
spelling is exactly the property whose loss produced E1, and re-introducing it to
buy insurance against a rare, loud event is the wrong trade. **What would change
the decision:** evidence that new groupings are introduced often enough for the
width to move in practice — say, two grain-introducing changes in a milestone.

### A3 — Two sequences (runs `1..n`, bundles from a separate counter)

**Shape.** Keep the mixed column, but mint bundle ids from an independent
sequence, distinguished by a prefix or by a reserved high block.

**Rejected because W4 rules against it** (*"One mixed number space, not two…
No prefix, no embedded type"*) and because the design does not need it: the
coupling A2 attacks is bounded and detected, and a prefix would make the id
self-describing, which is the property W4 removed on purpose. Recorded because it
is the obvious reading of §5.5.2's stated cost, and a reviewer should see that it
was weighed rather than missed.

### A4 — `ruleorder: generate > perturb` instead of a data-driven constraint

**Rejected: measured to fail.** P2 ran it in both states; with the plural rule's
subtree unresolvable it raises `CyclicGraphException`. It is out of the option set,
not merely disfavoured. Recorded because it is the cheapest-looking answer and the
one an implementer would reach for first.

### A5 — A reserved baseline id range (P2 mechanisms i / i-b)

**Shape.** Constrain rule 3.12's id to exclude ids `1..RLZ_NUM`, making the low
block a reserved baseline range.

**Rejected on two counts.** It **forecloses scope gap 5** by hardcoding a
family-specific concept into the DAG's regex, which W3 explicitly forbids; and it
requires the baselines to be a contiguous prefix block, so with `RLZ_NUM > 1` it
collapses into a numbering convention that the scenario table would then have to
honour — a constraint flowing backwards from stage 2 into stage 1. P2 records the
same verdict from the mechanical side ("Not recommended").

### A6 — Separate directories (`output/baseline/` vs `output/perturbed/`)

**Rejected.** Measured to work (P2 mechanism iii), robust and self-documenting,
but it re-introduces the word "baseline" into a *path* at the stage-2 seam — a
family-specific concept in the one place this design is trying to keep
family-blind — and it is a seventh path move for no gain over `derived_from`.

### A7 — A `n_blocks` (or `record_length`) column beside each value

**Shape.** Answer scope gap 6 by recording the estimator's sample size per row
rather than refusing below a precondition.

**Rejected.** It re-couples the results header to an estimator detail (the defect
CR-2 removed on the location axis and C28 re-incurred on the stress axis), it
makes every out-of-repo consumer responsible for a comparability check none will
perform, and it answers a decision question with a number. §5.4.4's refusal states
the toolbox's position instead. **What would change the decision:** a consumer
requirement to compare metrics across families *with* differing precision rather
than to be prevented from doing so — i.e. a use case for a caveated value.

### A8 — A `baseline` boolean column on the scenario table

**Shape.** The simplest way to give stage 2 what P2 says it needs.

**Rejected.** It is the family-specific distinction stated as data, which is what
P2's constraint note 4 warns against, and it settles scope gap 5 by accident: once
a column named `baseline` exists, the baseline *relation* has been defined as "this
row versus the rows flagged true", which is precisely the question W3 defers.
`derived_from` carries the same DAG information with none of the semantics.

### A9 — A checkpoint for the scenario table

**Rejected.** P1 measured that a checkpoint does resolve the self-produced-table
case in one invocation, so it works — but D6 prefers parse-time derivability, and
§5.1.4 shows the workflow already has it and keeps it. A checkpoint would be a
large complexity jump bought to solve a problem the design does not create.

### A10 — Keep `(rlz, st)` and fix only the sentinel

**Shape.** The minimal change: leave identity alone, make `rlz_id` a string, add a
grain column. This is the strongest form of "do nothing", and RR's summary of the
case against this whole change is its argument: *the composite identity is the
experimental design expressed in the type system; the proposal moves the design
into data, for the benefit of a family whose comparability semantics nobody has
written down.*

**Rejected, and the rejection is qualified.** It fixes leak 4 and nothing else:
identity is still recovered by regex (leak 1), the set is still structurally
factorial (leak 2), and grain still cannot be declared per metric without a second
grouping column that E9 shows one column cannot carry (leak 3). But the case
against is **not eliminated** by the three-stage split, only narrowed: stage 2 is
family-blind on its own merits and stage 3's grain becomes explicit whether or not
a second family ever arrives, which is why this design is worth doing *today*
rather than when E18 acquires an artifact. A reviewer who thinks the narrowing is
insufficient is disagreeing with the change request, not with this document.

## 7. Consequences and risks

| # | Consequence | Class | Handling |
|---|---|---|---|
| C-1 | **Every WF3 output path moves.** Seven artifact paths (§5.3.2), plus per-run log and benchmark part names under `3.12_*/`, `3.14_*/` | Certain | §8; the baseline manifest is re-recorded **before** the first implementation commit |
| C-2 | **`check_baseline.py check` fails by construction** until re-recorded. A comparison gate cannot be applied retrospectively | Certain | §8 step 0, verbatim from the R12 lookup design's R1 |
| C-3 | **The fixture-dependent test layer cannot gate this in a worktree** — it skips rather than fails, and this is a tree-shape change | Certain | Implementation gating happens in the primary checkout on a seeded fixture; §9 marks which gates are worktree-runnable |
| C-4 | A **new grouping** introduced later can change `W` and rename every stage-2 file | Low likelihood, bounded | §5.5.2; detected loudly by the digest guard, never silent. A2 is the standing alternative if it proves common |
| C-5 | **`derived_from` is argued, not measured.** The composition of P2's (i-c) and (iv) was not run | Open until GF-1 | GF-1 is a **fresh-project** DAG build. A seeded dry-run is a measured false negative here |
| C-6 | **Reading `run_id` as an integer silently breaks every join** — the same trap WG-2 documents for `st_id` | Recurring | Stated in §5.1.2 and in each replacement contract clause; `validate_*` reads as text and asserts the width |
| C-7 | Out-of-repo consumers (CST-API, frontend, `csthelpers`, `docs/notebooks/Climate Stress Test.ipynb`) re-implement HM-7 from its text and **will break** on the four-column shape | Certain, out of scope to fix | HM-7's replacement is written to be implementable standalone; the change is announced in the migration note. Per the standing ruling, no decision here is gated on whether they consume an artifact by path or name |
| C-8 | **`_member_span`'s banner loses its rectangle.** A flat run list has no `rlz a-b \| st c-d` to print | Cosmetic | §5.6; a first–last id span replaces it and the `(partial)` caveat becomes vacuous |
| C-9 | The refusal in §5.4.4 could, on a future config, stop a run that previously produced a (poor) number | Intended | Set to today's guaranteed value, so unreachable under any shipped config; output-neutral on the fixture |
| C-10 | **Nine contract clauses change, not three.** The intake undercounts (§5.7b) | Certain | The complete list is §5.7b's table; D7's atomicity obligation covers all nine |

**The risk this design is least able to retire.** E18 — that a user-supplied or
GCM-downscaled set is not expressible as `(rlz, st)` — is a **hypothesis with no
artifact to test against**, and it is the motivating premise. If it is false, the
benefit shrinks to the three defects that are measured (E1's regex, E9's two
coexisting bundlings, E8's sentinel), which A10 argues are worth fixing anyway but
which would not on their own justify a nine-clause contract change. This is stated
as the design's own weakest point rather than left for a reviewer to find.

## 8. Migration plan

**Satisfies `dev/reference/naming.md` §7**, which requires a
`dev/<milestone>/migration_<topic>.md` note for a rename touching `rule all`
output filenames, column labels in `rule all` output tables, hydromt catalog
source names, and fixture paths read by `check_baseline.py` — this change touches
all four.

**Note to be written:** `dev/milestones/r12/migration_scenario-identity.md`.
No user-facing `docs/migration-*.md` guide is required: production `project_dir`
outputs are regenerated, not migrated, and no config key a user writes changes
name. (If a user is holding a WF3 results file for an external consumer, the
announcement belongs in the release notes, not in a migration guide.)

**Authority note.** This section *specifies* the migration note, ADR 0009, the
contract edits, the `naming.md` §4/§7 entries, the `rule-index.md` rows, the
`semantic_tree_diff.build_project_tree_rules` extension, the baseline re-record,
the roadmap rewrite and the board item. **None of them is written by this design
stage.** Each is a derived artifact, regenerated from the accepted design after G2.

### 8.1 Old → new mapping

| # | old | new |
|---|---|---|
| 1 | `<exp>/climate/weathergenr/output/rlz_<r>_st_0.nc` | `<exp>/climate/weathergenr/output/run_<run_id>.nc` |
| 2 | `<exp>/climate/weathergenr/output/rlz_<r>_st_<m>.nc` | same as 1 — **the two collapse into one pattern**, which is the point |
| 3 | `<exp>/hydrology/wflow/forcing/inmaps_rlz_<r>_st_<m>.nc` | `.../forcing/inmaps_run_<run_id>.nc` |
| 4 | `<exp>/hydrology/wflow/config/rlz_<r>_st_<m>.toml` | `.../config/run_<run_id>.toml` |
| 5 | `<exp>/hydrology/wflow/config/rlz_<r>_st_<m>.yml` | `.../config/run_<run_id>.yml` (and its catalog **entry key**) |
| 6 | `<exp>/hydrology/wflow/output/rlz_<r>_st_<m>.csv` | `.../output/run_<run_id>.csv` |
| 7 | `<exp>/hydrology/wflow/output/outstates_rlz_<r>_st_<m>.nc` | `.../output/outstates_run_<run_id>.nc` |
| 8 | `logs/_parts/<exp>/3.12_*/rlz_<r>_st_<m>.log`, `3.14_*/…` (and the benchmark twins) | `…/run_<run_id>.log` / `.tsv` |
| — | *(new)* | `<exp>/config/scenario_table.csv`, `<exp>/config/.scenario_table.sha256`, `<exp>/results/unit_index.csv` |

**Column labels** (`naming.md` §7, second class): `st_id, rlz_id` → `unit_id` in
every `<token>_indicators.csv`; `temp_change, precip_change` already gone.
**Identifier renames:** `validate_wg5_catalog_grid` → `validate_wg5_catalog_runs`;
`member_from_run_csv` deleted; `POOLED_REALIZATION` deleted; `ST_BASELINE`,
`ST_START`, `ST_WIDTH`, `RLZ_WIDTH`, `rlz_ix`, `st_ix`, `_k_members`,
`_member_span` all change or go (`run_stress_test.smk:205-233`, `:1120`,
`:1184-1214`).

### 8.2 Sequence — one atomic rename plus a shape change (D7)

| step | action | why it is where it is |
|---|---|---|
| **0** | **Re-record `dev/baseline/manifest.json`** from `test_case/snake_config_baseline.yml`, in the **primary checkout**, `--notemp` on WF1, no other session live | Every WF3 target path moves, so the gate fails by construction afterwards. A comparison gate cannot be applied retrospectively. `--notemp` because rule 1.14 declares `run_default/output.csv` as `temp()` and that file is the manifest's wf1 discharge target |
| **1** | **One commit** landing: `shared/scenario_index.py`, `shared/scenario_families.py`, the six rule edits, the reducer rewrite, `interchange_contracts` (WG-2/4/5/6, HM-2/4/5/6b/7), the four contract documents, `naming.md` §4 + §7, `rule-index.md`, `semantic_tree_diff.build_project_tree_rules`, ADR 0009, the migration note, and every test | `naming.md` §7's atomicity and `AGENTS.md`'s *"grep the old spelling and fix every live reference in the same commit"*. A tree-shape change split across commits leaves the repo in a state where `tree-check` reports undeclared paths on every run |
| **2** | **`build_r09_path_map` stays frozen** — it is a historical map, not a live inventory | Stated in the gate-materialization table and preserved here so the implementer does not "helpfully" extend it |
| **3** | **Re-record the baseline again** after the change, from the same config and checkout | The manifest's targets are the new paths; the numbers must be unchanged (§9, GF-9) |

### 8.3 Rollback

**One commit, so one revert.** The rollback is `git revert` of step 1 plus
`git checkout <pre-change-sha> -- dev/baseline/manifest.json`, restoring step 0's
recording. Nothing else is required, because:

- **No run output is tracked.** Outputs live under `project_dir`, which is outside
  the repository tree (the untracked `test_case/test_local` being a dev-only
  exemption), so a revert leaves a project folder holding new-scheme files that
  the reverted code will not recognise. **The documented remedy is to delete the
  experiment folder's `climate/`, `hydrology/` and `results/` subtrees and re-run**
  — not to rename files back. A half-renamed tree is the one state neither scheme
  can read, and a scripted un-rename would be a second migration to test.
- **The sealed record is untouched**, so no revert can violate
  `tests/test_sealed_records.py`. ADR 0009 is reverted with the commit; the index
  entry goes with it.
- **The digest guard makes the failure mode of a partial rollback loud**: an old
  `.scenario_table.sha256` beside a new table refuses at parse time rather than
  mislabelling.

**Rollback window.** Step 3's re-record is the point of no cheap return: after it,
reverting also means restoring the manifest, which is why step 0's recording must
be preserved on a branch and not overwritten in place.

## 9. Validation plan — claim → falsifier (D8)

Every runtime property this design claims, the observation that would falsify it,
and the command that produces it. **`fresh-project` means a DAG built against a
project directory with no WF3 artifacts** — P2 measured that a dry-run on a seeded
tree is a **false negative** for the 3.11/3.12 ambiguity, so a seeded dry-run is
not an acceptable substitute anywhere it is named.

| # | Claim | Status now | Falsifier | Command |
|---|---|---|---|---|
| **GF-1** | The `derived_from`-driven alternation constraint keeps 3.11/3.12 unambiguous **on a fresh project** | **[argued]** — its two ingredients are measured (P2 i-c, iv); the composition is not | A `CyclicGraphException` in `perturb_climate_realization`, or any exception other than a clean `MissingInputException` when an upstream input is absent | `pixi run pytest tests/test_guard_invalidation.py -x -q` (fresh-project builder), extended with a case asserting the constraint's alternation set equals `DERIVED_FROM`'s keys |
| **GF-2** | An **empty** `DERIVED_FROM` yields an alternation matching **nothing**, not everything | [assumed] — Snakemake's empty-alternation semantics are not measured | Rule 3.12 becoming eligible for a root run's output on a family with no derived rows | A unit test building a two-rule Snakefile with `wildcard_constraints: run_id=""` and asserting `MissingRuleException`, plus a refusal in `scenario_index` if `DERIVED_FROM` is empty *and* rule 3.12 is reachable |
| **GF-3** | The scenario table is derivable at parse time with **no checkpoint** | **[measured]** — P1 (a) and the config-derived trace | Any WF3 invocation requiring two passes to build a complete DAG, or a `checkpoint` appearing in `run_stress_test.smk` | `pixi run snakemake all -c1 -s run_stress_test.smk --configfile test_case/snake_config_baseline.yml --dry-run` on a fresh project; job count equals `len(EVALUATED_IDS)`-derived expectation, exit 0, one invocation |
| **GF-4** | `run_historical: false` omits the baseline's **wflow run** while still building its **series** | [argued] — the pull semantics `ST_START` already relies on at `:1247` | `run_<baseline>.csv` appearing as a job under `run_historical: false`, or `run_<baseline>.nc` **not** appearing | Two fresh-project dry-runs differing only in `run_historical`; diff the job lists |
| **GF-5** | An empty scenario set **refuses**; a guarded read never silently empties the DAG | [argued] — the hazard is **measured** (P1 b2: exit 0, zero jobs) | Any WF3 invocation exiting 0 with zero scenario jobs | A test invoking `scenario_index.mint` with a zero-row table and asserting `EmptyScenarioSetError`; plus a static gate asserting that no parse-time table read in any `.smk` is guarded by a fallback yielding an **empty id set**. Narrowly worded on purpose: `analyze_projections.smk:468-471` guards a parse-time JSON read with `else None` and its consumer handles `None` explicitly, which is correct and must not be flagged — the defect is the silent empty, not the guard |
| **GF-6** | Editing a **grain declaration** re-fires rule 3.16 | [assumed] — **P4 is unexecuted**, and the `ancient()`/no-`params:` trap is live in this workflow (rule 3.09's own comment records it) | A grain edit leaving `q_indicators.csv` untouched on the next invocation | Run WF3 to completion on `test_rapid`; edit a `bundle_by`; `snakemake --dry-run` and assert 3.16 is scheduled |
| **GF-7** | hydromt resolves the per-run catalog under the new entry key | [argued] — **P3 is unexecuted** | Rule 3.14 failing to find its source, or reading the wrong entry | One real rule-3.14 execution on `test_rapid` |
| **GF-8** | `pixi run tree-check` classifies the renamed tree with no undeclared paths | [assumed] — **P5 is unexecuted**; the inventory is code, not a snapshot | `tree-check` reporting undeclared paths after a complete run | `pixi run tree-check` against a completed `test_local` run, post-change |
| **GF-9** | The rename is **output-neutral**: no number moves | [argued] — nothing in §§5.1–5.6 changes an arithmetic path; §5.4.4's precondition is set to today's guaranteed value | Any `check_baseline.py check` difference beyond a path rename | `python dev/scripts/check_baseline.py check` after step 3's re-record, against step 0's values |
| **GF-10** | Every `unit_id` in every results table resolves in `unit_index.csv`, and no unit carries two grains | [argued] — it is the validator's own assertion | A results row whose `unit_id` is absent from the index, or a `unit_id` with two `grain` values | `pixi run pytest tests/test_interchange_contracts.py -k hm7`, plus synthetic pass/fail pairs as the existing validators use |
| **GF-11** | Stage 2 references **no** family-block column | [argued] | Any module on the stage-2 path naming `rlz`, `st_id` or `scenario_family` outside a `params:` passthrough | A static test asserting no stage-2 module mentions a name in `FAMILY_COLUMNS` |
| **GF-12** | A changed scenario table re-run in place **refuses** | [argued] | A second run with a different table completing and overwriting outputs | Run WF3 on `test_rapid`; change `realizations_num`; re-run into the same experiment; assert a parse-time refusal naming both digests |

**Gate ladder for implementation** (matching `AGENTS.md`'s validation ladder to
this change's blast radius): `pytest tests/test_cli.py` on every rule edit — the
only place a malformed `config/defaults/*.yml` surfaces; `pixi run test-full`
before merge, because this touches a Snakefile, a `script:` signature **and**
`shared/`, which is the `workflow_contract` and `process_isolation` case;
`pixi run tree-check` and `check_baseline.py check` before the milestone seal.
Redirect each gate to a file rather than piping it through `tail`.

## 10. Open questions

| # | Question | Why it is open, and what would close it |
|---|---|---|
| **Q1** | Is `derived_from` genuinely family-blind, or is it the baseline distinction in disguise? | The argument (§5.2.2) is that a dependency edge means the same thing for every family while "is a baseline" does not. **E18 is a hypothesis**, so there is no second family to test it against. Closed by a paper schema for one candidate family — enough to show the column evaluates to something meaningful, or to empty — plus GF-1 |
| **Q2** | Two column names or one (§5.5.1, A1)? | Settled here as two, on a type-declaration argument. Reversible at zero cost **only before implementation**; afterwards it is a baseline re-record. Flagged because it is the one place this design refines W4's "settle it once" rather than following it literally |
| **Q3** | Does the width coupling (§5.5.2 / C-4) matter in practice? | Needs a frequency observation this repository cannot yet supply: how often a *new grouping* is introduced. If it turns out to be common, A2 is the prepared answer |
| **Q4** | Scope gap 5 — the baseline relation | **Deferred by W3.** This design keeps it open (§5.3.5) and specifies only the mechanism that replaces the hardcoded `0`. Closed when a second family exists to test comparability against |
| **Q5** | Do the eight surviving `t2608082036` references get repointed or abandoned? | §5.5.5 recommends splitting them: identity references here, execution-model references to a successor item. Needs an owner ruling, and it is a roadmap edit, which is a derived artifact |
| **Q6** | Does the intake's undercount of contract clauses (three vs nine, §5.7b) change the milestone's size estimate? | Six of the nine are one-line path substitutions; the substantive ones are WG-2, WG-5 and HM-7, which the intake did identify. Raised for the gate rather than resolved here |
| **Q7** | What is the scientifically defensible value of `min_blocks` for the two GEV return levels? | Set for this milestone to the shipped baseline config's block count, so the rename stays output-neutral (§5.4.4). A literature-derived floor is the right long-run answer and would refuse some existing configurations, which is why it is not taken alongside a rename. Closed by a methodological ruling, not by a measurement in this repository |

**Two things in the input set that a reviewer should know are contradictory**, both
reported to the driver rather than fixed here, since the artifacts are frozen or
derived: the intake's **E13** attributes the member naming pattern to WG-2 when it
is WG-4 (§5.7b), and the **HM-7 contract document is stale against its own
validator** — seven columns pinned, five asserted (§5.9).

## 11. Revision log

| version | date | author | change |
|---|---|---|---|
| v1 | 2026-09-07 | author (stage 1, `design-review-loop` run `wf3-simulation-identity`) | First draft. Authored from the frozen intake (revision 2), the executed P1/P2 probe results, the `wf3-experiment-v2` review record, and `design-v4.md` §3.1/§5.1 at tag `archive/wf3-experiment-v2`. Departures from the working direction, and findings against the input set, are listed below |

**Departures from W1–W4, stated once and in one place:**

| direction | disposition |
|---|---|
| **W1** — pooled and per-run values share one results file | **Followed.** One `<token>_indicators.csv` per variable carries both grains, distinguished by `unit_id` and explained by `unit_index.csv` |
| **W2** — the results file carries results plus ONE index column, four columns, no blanks and no grain column | **Followed exactly**, at `metric, location, unit_id, value`. W2's three safety conditions are discharged in §5.4.2, §5.4.3 (invariant 1) and §5.9 ("join before you group") |
| **W3** — the baseline relation stays open | **Followed.** §5.3.5 keeps it open on both required counts: no reserved baseline id, and the one hardcoded site is made indirect without settling its semantics. Two of P2's four working mechanisms are rejected in §6 specifically because they would have foreclosed it |
| **W4** — a plain zero-padded sequential number, nothing embedded; one mixed number space; the column NAME and the stale-lookup guard left open | **Followed on form and on the single sequence** (§5.5.2). **Refined on the column name** (§5.5.1): two names, `run_id` and `unit_id`, over one namespace and one value space, rather than one name everywhere. This is a refinement rather than a departure — W2 constrains only the results file's index column and W4's open point is exactly this — but it is the one place the design does not do the literal simplest thing, so it is marked. The alternative is A1 |

**Findings against the input set** (reported, not fixed — the artifacts are frozen
or derived):

1. **The intake's 1→2 seam spec is insufficient**, measured. Two columns cannot
   express what any mechanism P2 measured to work requires (§5.2.2).
2. **E13 mis-attributes the naming-pattern clause** to WG-2; it is WG-4:238-244.
3. **Scope gap 7 undercounts the affected contract clauses** — nine, not three
   (§5.7b).
4. **The HM-7 contract document is stale against its own validator** — seven
   columns pinned at `hydrological-model-seam.md:310-319`, five asserted at
   `interchange_contracts.py:842` (§5.9). Independent of this design.
5. **Probes P3, P4 and P5 are unexecuted.** GF-6, GF-7 and GF-8 are their gates,
   and the corresponding claims are labelled `[assumed]` rather than argued.
