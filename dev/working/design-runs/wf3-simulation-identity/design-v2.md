# WF3 in three stages — scenario space, simulation, metrics: Design

> **design-v2**, run `wf3-simulation-identity`, milestone R12. Genre:
> **workflow-spec**. Scope authority:
> `dev/milestones/r12/simulation-identity-intake.md` (frozen). Measurements this
> document is bound by: `dev/working/design-runs/wf3-simulation-identity/probe-p1-p2.md`.
> Owner rulings this revision implements: R-1 .. R-6 (`status.md` § G1). The E18
> precondition (R-6) is discharged in
> `dev/working/design-runs/wf3-simulation-identity/candidate-family-schema.md`,
> which is part of this design's evidence and is cited as **CFS** below.
>
> **Epistemic labelling — four labels, and the taxonomy applies to itself.**
> Every substantive claim below is marked **[measured]** (an executed
> observation, with the command or the probe row that produced it), **[cited]**
> (verified by reading a named file at a named line; reproducible by opening the
> file, but nothing was run), **[argued]** (a conclusion drawn from cited code or
> contract text), or **[assumed]** (a premise this design leans on that nothing
> in the repository establishes). An unlabelled sentence is ordinary connective
> prose and carries no claim.
>
> **`[cited]` exists because v1 did not have it** (`risk-9`). v1 labelled roughly
> a dozen code reads `[measured — read the function]`, which is its own definition
> of `[argued]` wearing the stronger word. The labels are how a reader allocates
> scrutiny — separating "P2 ran six mechanisms twice" from "someone read line 79"
> is the whole function of the scheme — so the relabel is not cosmetic. After it,
> **`[measured]` appears only on P1/P2 rows and on commands actually run**, and the
> count falls by roughly two thirds, which is the point.

## 1. Problem statement

WF3's run identity is the ordered pair `(rlz, st_id)`, and that pair is not a
label on the experiment — it *is* the experiment's data model. Four consequences,
each with a code site.

**1. Identity is recovered by parsing a filename.** `export_wflow_results.py:79`
holds `_MEMBER_IN_STEM = re.compile(r"^rlz_(\d+)_st_(\d+)$")`, and
`member_from_run_csv` (`export_wflow_results.py:82-92`) raises `ValueError` on any
stem that does not match. The reduction's contract with the simulator is therefore
a **string spelling**, not a declared interface. [cited — read the function]

**2. The scenario set is structurally required to be a full factorial.** The run
set is built as a cross-product at `run_stress_test.smk:1120`
(`_k_members = [(int(r), int(c)) for r in range(1, RLZ_NUM + 1) for c in
range(ST_START, ST_NUM + 1)]`) and again as an `expand()` over two independent
wildcard lists at `:1247`. A flat, ragged scenario list — a user-supplied set, or
one downscaled from GCM series — has no assignment into `(rlz, st)` that is not an
invention.

**E18 is no longer a bare hypothesis, and its argument has changed.** The intake
records E18 as *"HYPOTHESIS — asserted, no artifact exists"* and argues it from
**raggedness**. Raggedness is the weak half: a critic answers "pad it", and a
GCM-downscaled set of 6 GCMs × 3 SSPs × 2 horizons *is* numerically factorial, so
the raggedness argument does not reach the motivating case at all. CFS §3 settles
it on stronger ground and **confirms E18**:

- **`st_id` is a foreign key, not a free integer.** Every `st_id` names a row of
  monthly perturbation multipliers in `stress_test_lookup.csv`, and `validate_hm7`
  refuses an emitted `st_id` the lookup does not define
  (`interchange_contracts.py:1030-1038`). A `(ssp245, 2050)` pair has no such row,
  and minting one means computing change factors inside WF3 — WF2's business,
  forbidden here by `AGENTS.md` § Background. [cited — the validator block]
- **`rlz` is a common-random-numbers index, not a label.** Two rows sharing an
  `rlz` are two perturbations of one baseline draw
  (`run_stress_test.smk:1020`); two rows sharing a GCM are two downscalings. Under
  R-3 that pairing is a declared property, so spelling a GCM as `rlz` asserts
  something false about the surface's interpretation. [cited — the rule input]

So a set that *does* factor still cannot be expressed as `(rlz, st)` without
either a dangling foreign key or a false pairing claim. [argued, from CFS §3]
**This design no longer rests E18 on raggedness**, and §7 records the residual
risk accordingly.

**3. Bundling is inferred from the identity, and the identity can express only one
bundling.** Two bundlings already coexist in one output file: Class A metrics are
emitted per realization (`export_wflow_results.py:384-401`), while the Class-B GEV
fits (`:405-426`) and the Class-C month-selecting means (`:431-441`) pool across
realizations at one design point. Bundling is thus a property of the **metric**,
not of the scenario set — and a composite run identity has no place to record
that. [cited — read the three emit blocks]

**4. The scheme is already leaking through a sentinel.**
`shared/indicator_tables.py:136` carries `POOLED_REALIZATION = 0`, an out-of-band
value written into the numeric `rlz_id` key column, with its own comment recording
the fragility: *"safe ONLY because no metric emits both grains; if that ever
changes it must become a string, or `groupby("rlz_id")` folds pooled rows in as
another realization."* [cited — read the constant]

Meanwhile the execution layer has already flattened and has no word for what it
iterates: rule 3.15 (`run_stress_test.smk:1216-1241`) is generated per batch with
**no wildcards**, slices the flat `_k_members` list, and keys its log and benchmark
by batch id. `(r, c)` survives inside it only to spell filenames. [cited — read the rule]

**The problem this design solves** is therefore not "rename some files". It is:
WF3 fuses scenario construction, simulation and reduction into one identity, and
that fusion prevents three separable concerns from being stated separately — what
scenarios exist, what the simulator is entitled to know, and at what grain each
metric is defined.

## 2. Goals / Non-goals

### 2.1 Goals

1. **Make the simulator family-agnostic.** Stage 2 learns the run list and the
   built model, and nothing about what produced the forcing. Admitting a second
   scenario family must require **adding** a producer rule, never **editing** an
   existing stage-2 rule, and no stage-2 rule may branch on a family.

   **This wording is a correction, and CFS is why.** v1 said "no edit to stage 2",
   which is false of any design at all: a forcing series that arrives from outside
   WF3 needs something that puts it where rule 3.14 expects it, and that something
   is a rule. CFS §4 names the exact cost — one core column (`forcing_uri`) and one
   rule (3.11b `stage_supplied_forcing`) — and establishes that rules 3.14, 3.15
   and 3.16 are untouched by it, because they see `run_<id>.nc` and cannot tell
   which of three producers wrote it. Goal 1 is met on the second reading and was
   never meetable on the first.
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
| S2 | **The simulator knows only the built model and the run list.** It enumerates rows and writes outputs named by the run id, never by family-specific columns | Owner, 2026-09-04 | §5.2's seam core is three family-blind columns; §5.3 specifies stage 2 against those columns only |
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
| D3 | **The DESIGN must be stable under set growth; the index need not be.** Narrowed by W4: `st_id` and its properties live in the lookup and stay put; the sequential index may renumber, provided a changed lookup is *detectable* rather than silent | §5.5.3a — jointly by the experiment freeze this repository already has and by the narrower digest guard |
| D4 | **Grain is declared, never a sentinel.** Nothing may reuse a key column to mean two things | §5.4.1–§5.4.3 — `POOLED_REALIZATION` is deleted |
| D5 | **Store the finest grain, derive every summary.** Stage 2's raw output is the finest grain; every metric is a declared derivation over it. The exception is real and stated: for a pooled estimator the finest grain that *exists* is the bundle | §5.4.1, §5.4.1a (Class C moves to the finest grain under R-2, so the exception narrows to Class B alone), and §5.4.4 for the estimator precondition that makes the exception principled rather than convenient |
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
writes a **scenario table** whose rows are runs: a family-blind core of three
columns plus a labelled, family-specific block. The **1→2 seam** is a view of that
table restricted to the core — it is what makes stage 2 family-blind, and it needs
three columns, not the two the intake specifies (§5.2.2, from P2). Stage 2
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

**Universal core — three columns, in this order, present for every family:**

| column | type | nullable | meaning |
|---|---|---|---|
| `run_id` | text, zero-padded, width `W` (§5.5.2) | no | This run's identity. Unique within the table. The **only** thing that appears in a stage-2 filename |
| `derived_from` | text, a `run_id` from this same table | **yes** | This run's climate forcing is produced by transforming the run named here. Empty means the forcing is produced *ab initio* inside WF3. A **dependency edge**, not a family concept (§5.2.2) |
| `evaluated` | `true` / `false`, lowercase | no | Whether this run's *simulated* output is required. `false` marks a row that exists only as a forcing ancestor (§5.1.5) |

**`forcing_uri` is REMOVED from the core, and this is a decision rather than a
retreat** (`risk-2`, `arch-2`). v1 declared it a required seam column whose stage-2
use was "the forcing path for a supplied family", and then specified no producer
for such a row, no consumer in §5.2.3's exhaustive derived-object list, no rule in
§5.6, no migration row in §8.1 and no falsifier in §9. Worse, §5.6's `ROOT_IDS`
definition excluded exactly those rows from rule 3.11's outputs, so a row carrying
a `forcing_uri` had **no producer at all** for its `run_<id>.nc`
(`arch-2`) — a contract promising a capability that fails with a
`MissingInputException` on first use.

The two available fixes were: implement it (a staging rule 3.11b, a WG-4 producer
clause, a validator and a gate), or remove it. **Implementing it ships an ingest
path for a family the intake's non-goal forbids building.** So it is removed, and
CFS §4 is what makes the removal accountable: it names precisely what re-admitting
the column costs — one core column, one rule 3.11b `stage_supplied_forcing`, one
WG-4 clause, one falsifier — and establishes that the column is **family-blind**
when it returns ("where this run's series comes from" means the same thing for
every family and evaluates to empty for one that generates its own), so the seam
contract survives its addition. Recorded as Q8 in §10.

**Consequence for the exclusivity rule.** v1's mutual-exclusivity rule between
`derived_from` and `forcing_uri` goes with the column. What remains is simpler and
still checkable: `derived_from` is either empty (produced *ab initio* by rule 3.11)
or names a row in this table (produced by transformation, rule 3.12). There are
exactly two producers in this milestone, and §5.2.3's `ROOT_IDS`/`DERIVED_FROM`
partition is total over the table.

**One table, one family (normative).** `scenario_family` MUST carry exactly one
distinct value in a scenario table. **CFS §4 is why this sentence exists**, and
nothing in the review panel names it: a table holding two families would need the
union of their blocks with blanks — `gcm` empty on every stochastic row, `st_id`
empty on every downscaled row — which is the denormalisation defect C28 was
written to contain, arriving from the other direction. Admitting a second family
concurrently is the per-family file split this design already says it makes cheap,
and the split is a *file* split precisely because the core is family-blind.

**Row order (normative)** (`risk-7`). v1 minted run ids "in scenario-table order"
and never defined that order, so two natural readings — rlz-major (today's
`_k_members`, `run_stress_test.smk:1120-1121`) and st-major — produce different
`run_id ↔ (rlz, st_id)` mappings for the same config, and the digest cannot detect
the difference because it is computed over whichever order was minted. The order
is therefore a normative property of the table, not an implementation detail:
**rlz-major, and within a realization the baseline row first**, matching
`_k_members`'s existing iteration exactly. [cited — the comprehension at `:1120-1121`]
Two things depend on it: six filenames the baseline manifest fingerprints, so an
unpinned order is baseline churn on any refactor of `scenario_table()`; and the
`(rlz, st_id) → run_id` crosswalk that GF-9's comparison instrument is built from
(§9), which cannot be written against an unspecified order.

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

#: R-3. Whether contrasts BETWEEN design points of this family are paired.
PAIRING = {
    "stochastic": "paired_across_design_points",
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

**The empty `st_id` IS a grouping key (normative)** (`risk-5`). This sentence is
load-bearing and v1 did not have it. §5.4.1 declares `bundle_by =
same_design_point` as "equal `st_id`, any `rlz`", and today's reducer emits Class-B
return levels **for the baseline design point** whenever `run_historical` is set —
`for st in members` runs over `members` including `st = 0`
(`export_wflow_results.py:373-427`). [cited] Under the new schema the baseline's
bundle is keyed by the **empty string**, and the concrete failure of leaving that
unstated is quiet: `pandas.groupby` drops null keys by default, so a conforming
implementation silently emits no baseline return-level rows, on the shipped
baseline config, into a `rule all` artifact the manifest fingerprints. Therefore,
normatively:

- the empty `st_id` is a grouping key like any other;
- a grouping MUST NOT drop null or empty keys — `dropna=False` is not an option
  the implementer chooses, it is the contract;
- the minter mints a bundle for it, so it is in the unit namespace and
  §5.4.3 invariant 6 can see its absence.

GF-13 (§9) is its falsifier. Note that v1's own instruments would not have caught
this: `domain-5` establishes that GF-9's comparator fails structurally on the
column change *before* comparing any number, and invariant 6 checks the emitted
unit set against the minter's namespace — so if the minter never mints the
empty-key bundle, the namespace is short in the same way the table is and the two
agree about a hole.

**Completeness (RR-4, decision criterion D8).** The composite identity carried a
*structural* guarantee that the run set was a full factorial. A column carries the
information but not the guarantee, so the guarantee becomes a **declared
predicate** on the family: `scenario_families.completeness("stochastic")`.

**Asserted against the CONFIGURED axes, not the observed values** (`domain-9`). v1
asserted the cross-product "over the observed values", which detects raggedness
and misses uniform truncation: a table missing an entire realization, or an entire
design point, has a smaller observed value set and passes. That is exactly
backwards for the case RR-4 and D8 exist for. The predicate therefore asserts the
non-baseline rows are exactly `{1..RLZ_NUM} × {1..ST_NUM}` — both available at the
minter for the stochastic family, since the table is a pure function of config
(§5.1.4) — plus exactly one baseline row per `rlz`.

**A family that declares no cardinality is reported as UNCHECKABLE, not passed.**
The honest limit of this mechanism, stated because `domain-9` is right that the
predicate as v1 wrote it "holds only where the question does not arise": for the
stochastic family completeness is nearly free, because a pure function of config
cannot be truncated; for a supplied family — the case that motivates the check —
the expected cardinality is not derivable and the family MUST declare it or be
reported uncheckable by name. Silence is not a pass. This is strictly stronger
than today: `_member_span` at `run_stress_test.smk:1195-1212` already prints
`(partial)` because the batch rule degraded per-member completeness, so the cost
predates this change and is now at least named. [argued]

**Pairing is declared, and the declaration is checked (R-3).** `derived_from` is
presented in §5.2.2 as a DAG dependency edge, and for the stochastic family it is
also the carrier of a methodological property: rule 3.12's input is
`rlz_{rlz_num}_st_{ST_BASELINE}.nc` (`run_stress_test.smk:1020`), so every design
point at realization *r* is perturbed from **that same realization's** baseline
draw. [cited] That is common random numbers across design points, and it is what
makes a surface difference between two design points a **paired contrast** rather
than a difference between two independent samples. RR-4 named it, the intake
accepted it, and v1 answered only the completeness half.

- `PAIRING[family]` is a required registry field taking
  `paired_across_design_points` / `independent` / `none`.
- Stage 3 **records it beside the surface**, so a family whose `derived_from`
  column is uniformly empty produces a surface *marked unpaired* rather than one
  that silently reads like the stochastic one. Two families sharing a metric name
  and a surface, one supporting paired inference and one not, with nothing in any
  artifact recording the difference, is the same defect class as the unstated
  record-length precondition §5.4.4 fixes.
- **Consistency refusal, which R-3 does not state and CFS §4 exposes:** a family
  declaring `paired_across_design_points` whose `derived_from` column is empty on
  every row is **refused at parse time**. A declared pairing is only true if the
  edges exist, and without this clause the field is a claim with nothing behind it
  — the shape of defect this design exists to remove, reintroduced by its own fix.

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

- The baseline row is **always** in the scenario table, with `derived_from` empty.
- `evaluated` is `run_historical` for that row and `true` for every perturbed row.
- **Stage 2's target set is the `evaluated` rows, and the exclusion is a FILTER on
  the batch member list — not pull semantics** (`arch-5`).

**v1's mechanism sentence was wrong, and this is the correction.** v1 argued that
"because Snakemake is pull-based, `<runs>/output/run_<id>.csv` is simply never
requested for an unevaluated row", citing `run_stress_test.smk:1247` as the
precedent. That citation licenses a claim about a different rule. Rule 3.16's
`expand()` at `:1247` *is* pull-based; **rule 3.15 is not.** It is loop-generated
per batch with static Python output lists sliced from `_k_members` —
`csvs = [f"{runs_dir}/output/rlz_{rlz_ix(r)}_st_{st_ix(c)}.csv" for (r, c) in
_members]` (`run_stress_test.smk:1226-1231`) — so **every member of `_k_members`
is an unconditional declared output of its batch rule**, requested or not. [cited
— the generated rule body; this is intake E2, which v1 recorded in §1 and then
failed to connect to §5.1.5] What excludes the baseline today is `ST_START`
filtering `_k_members` at `:1120`, and nothing else.

The consequence of leaving v1's sentence standing would have landed in numbers,
not in prose: §5.5.2 mints ids for **every** scenario-table row, and §5.6's
rule-3.15 row said only that `_k_members` "becomes a flat list of `run_id`
strings". Read literally, the unevaluated baseline re-enters the batch rule and is
simulated, adding `run_<baseline>.csv` to a GF-9-covered reduce — so the
output-neutrality claim would fail on exactly the `run_historical: false`
configuration, and the design's stated mechanism would not explain why.

**Normative, therefore:** `_k_members` is built from `EVALUATED_IDS`, never from
`RUN_IDS` (§5.6's rule-3.15 row says so explicitly). The `.nc` series for an
unevaluated ancestor is still built, because rule 3.12 declares it as an `input:`
— that half of the pull argument is correct and survives. GF-4's falsifier is
strengthened accordingly: it asserts the baseline's CSV is absent from the **batch
rule's declared outputs**, not merely absent from the job list, because on a static
output list those are different questions.

`evaluated` is family-blind: any family may have rows that exist only as forcing
ancestors. It says nothing about baselines, and stage 3 is free to declare units
over an unevaluated run's descendants without ever naming it.

**No silent cap.** When any row has `evaluated: false`, the run header MUST report
the count (`N scenarios, M simulated`). A row dropped from the simulation set is
exactly the kind of self-imposed bound `AGENTS.md` requires a tool to announce.

### 5.2 The 1→2 seam view

#### 5.2.1 What it is

The seam is the **projection of the scenario table onto its universal core** —
`run_id, derived_from, evaluated`. It is a *view*, not necessarily a separate
file: for the stochastic family it is the same in-memory object stage 1 minted,
sliced to three columns. It is named because it is the contract that guarantees
stage 2 cannot acquire a dependency on `rlz` or `st_id`.

#### 5.2.1a The family-blindness rule — ONE statement, one exception, one instrument

**This subsection replaces three divergent statements of the same rule**
(`arch-1`). v1 stated it at `:340` with no exception ("Stage 2 code MUST NOT
reference any column outside the core"), again in §5.3.3 with one exception
("...other than passing the design parameters through to the generator"), and
again in GF-11 with a *different* exception ("outside a `params:` passthrough") —
and then §5.6's rule-3.12 row required exactly the excepted thing, so the
strictest statement was false of the design's own specification. A reader could
not tell which sentence was the contract. This is the design's load-bearing rule;
three scopes is three rules.

**The rule, stated once and normatively:**

> **A stage-2 rule MUST NOT branch on, filter by, compare, or derive a path or an
> id from any family-block column. A family-block value may travel through a
> stage-2 rule as an OPAQUE `params:` payload — obtained only from
> `scenario_families.family_payload(row)`, passed through unread, and interpreted
> only by the family-specific script at the far end.**

Every other statement of it in this document is deleted. §5.3.3 and GF-11 now
*cite* this rule rather than restating it at a new scope.

**The exception is real, it is stated once, and here is what it costs.** The rule
cannot be stated without an exception, and pretending otherwise is what produced
v1's three versions. Rule 3.12 must hand the weather generator the design point's
monthly multipliers, and those are family-specific by construction — a design
grid is what `stochastic` *is*. The honest formulation is not "stage 2 knows
nothing family-specific" but **"stage 2 makes no decision on anything
family-specific"**: it may carry a sealed envelope, and it may not open it.

The cost of the exception, stated rather than minimised:

1. **The envelope is a hole in the checkable surface.** Whatever
   `family_payload(row)` returns reaches a script, and no static test can prove
   the script does not branch on it. The containment is that the *addressing* is
   family-blind — rule 3.12 selects its payload by `run_id`, never by `st_id` —
   so a family with a different payload shape needs a different generator script,
   not a different rule.
2. **A family with no payload must be expressible.** `family_payload` returns an
   empty mapping for a family declaring no block columns beyond
   `scenario_family`, and rule 3.12 must not require a non-empty one. Both CFS
   variants exercise this.
3. **It is the single point where a family-shaped fact crosses the seam**, so it
   is the single place a future family-admission review must look.

**The instrument, respecified so that it has a referent** (`arch-1`). GF-11's v1
instrument was "a static test asserting no stage-2 module mentions a name in
`FAMILY_COLUMNS`". There is no such module: §2.2 makes splitting the WF3 `.smk`
a **binding non-goal**, so rules 3.11/3.12/3.14/3.15 (stage 2), the stage-1
minting call and rule 3.16 (stage 3) all live in `run_stress_test.smk`, and "no
module under the stage-2 boundary" names nothing in a single-file workflow. The
replacement has two parts, both constructible today:

- **`family_payload(row)` in `scenario_families.py` is the ONLY permitted reader
  of a family-block column outside stage 1 and stage 3.** It is a named function,
  so "who reads the block" becomes a question about call sites rather than about
  file boundaries.
- **Stage membership is declared per rule, and the test is an AST test over the
  named rule bodies.** A module-level `STAGE = {"3.11": 2, "3.12": 2, "3.14": 2,
  "3.15": 2, "3.09": 1, "3.16": 3}` mapping in the Snakefile makes the boundary a
  declaration rather than a file layout; the test parses `run_stress_test.smk`,
  walks the body of each rule declared stage 2, and asserts that no bare name in
  `FAMILY_COLUMNS[*]` appears in it, `family_payload(...)` excepted. That is
  GF-11's new command in §9.

This works precisely *because* the file is not split, and it keeps working if it
later is.

#### 5.2.2 Why the seam is three columns and not two — the P2 correction

> **Count change from v1**, which said four. `forcing_uri` left the core
> (§5.1.2), so the core is `run_id, derived_from, evaluated`. The argument below
> is unaffected: it is about `derived_from`, and the intake's two-column seam is
> still measured insufficient.

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

**`derived_from` carries a methodological property as well as a DAG edge (R-3).**
Stated here because v1 presented it as *purely* an edge, and the pairing half is
what a family-blind seam costs at the reduction. For any family that populates the
column, `derived_from` is the record of which runs share a random draw; for
`stochastic` that is common random numbers across design points
(`run_stress_test.smk:1020`). The property is declared in `PAIRING` and recorded
beside the surface (§5.1.2), and a family declaring it with an empty column is
refused. That is the intake's "price the scenario-neutrality constraint" answered
concretely: the price is that pairing must be *declared*, because the seam can no
longer *guarantee* it structurally.

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

**And it is measured BEFORE the migration commits — probe P2b** (`risk-3`). In v1
this claim's only gate was GF-1, which runs against the implemented workflow and
therefore cannot execute until §8.2 step 1 has landed two shared modules, six rule
edits, the reducer rewrite, nine contract clauses, ADR 0009 and every test. That
is the wrong ordering for the design's **single highest-consequence unmeasured
claim**: §4 states in this design's own words that if the `derived_from` resolution
is wrong, *"D1 is unsatisfiable at this seam and the seam must move"*. A failed
GF-1 after step 1 is not a revert, it is a redesign, and §8.3's rollback story is
written for a defect rather than a structural refutation.

**P2b, normative as a milestone precondition:**

- **What.** Add a seventh mechanism to P2's existing standalone model — input
  function *and* alternation constraint both driven by a `derived_from` table,
  i.e. the composition of (i-c) and (iv) that P2 records as **NOT PROBED**.
- **Run it in three states**, not two: the plural rule's subtree resolvable; the
  subtree unresolvable (the `CyclicGraphException` case); and **`DERIVED_FROM`
  empty**, which also settles GF-2's currently `[assumed]` empty-alternation
  semantics and is the CFS-variant case.
- **Where.** The scratch harness P2 already built
  (`.tmp/scratchpad/2026-09-06_probe/p2/`), six mechanisms × two states plus a
  500-id scaling Snakefile. Adding a seventh is scratch work of the same size as
  what has already been run.
- **When.** Before §8.2 step 1. GF-1 remains the in-workflow gate; it must not be
  the first observation.

This is **not** CFS's question. CFS §3 settles E18 (whether a second family is
expressible); P2b settles the mechanical composition, which needs no second family
to test.

#### 5.2.3 Seam schema — normative

| column | required | stage 2 uses it for |
|---|---|---|
| `run_id` | yes | the wildcard value; every output filename |
| `derived_from` | yes (nullable) | rule 3.12's `input:` (which series to transform) and its `wildcard_constraints` alternation |
| `evaluated` | yes | which run CSVs are targets |

**Three columns, and the derived-object list below is exhaustive.** v1's table
carried a fourth (`forcing_uri`) that the derived-object list omitted and no rule
read — the mismatch `arch-2`'s identifier trace calls "break 1". The seam table
and the derived-object list are now the same set, which is the property that makes
either of them checkable.

Stage 2 derives exactly three parse-time objects from the seam, all pure:

```python
RUN_IDS        = [r["run_id"] for r in SEAM]
DERIVED_FROM   = {r["run_id"]: r["derived_from"] for r in SEAM if r["derived_from"]}
EVALUATED_IDS  = [r["run_id"] for r in SEAM if r["evaluated"]]
```

and the alternation constraint is `"|".join(DERIVED_FROM)`. If `DERIVED_FROM` is
empty — a family that supplies every series — rule 3.12 is unreachable and its
constraint is the empty alternation, which Snakemake treats as matching nothing.
That is the correct outcome and **must be measured rather than assumed** — it is
P2b's third state and GF-2 in §9, promoted out of `[assumed]` by this revision. An
empty alternation that silently matched *everything* would put us back in
mechanism 0, and both CFS candidate families have an empty `derived_from`, so this
is the first thing a second family would meet.

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
- **The family-blindness rule is §5.2.1a's, cited and not restated.** v1 restated
  it here at a third scope, which is the `arch-1` defect. Rule 3.12's handling of
  the design parameters is the single stated exception, and §5.2.1a is where it is
  stated: the payload is obtained from `family_payload(row)`, travels sealed, and
  is opened only by the generator script.

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

Today grain is **emergent in the reducer and declared, weakly, in one constant.**
Both halves matter and v1 stated only the first.

- **Emergent where it is computed.** Class A is emitted inside
  `for rlz, sim in per_rlz.items()` (`export_wflow_results.py:384-401`); Classes B
  and C are emitted outside it with `POOLED_REALIZATION` in the `rlz_id` column
  (`:405-426`, `:431-441`). A reader recovers the grain from indentation. [cited]
- **But a declaration already exists, and v1 missed it.** `Q_METRIC_SUFFIXES`
  carries a class letter per metric (`indicator_tables.py:198-215`),
  `METRIC_CLASSES = {"A": "per-realization", "B": "pooled", "C": "pooled"}` at
  `:245`, and `metric_grain(token, metric)` at `:274-296` returns the grain by
  name — and `validate_hm7` already calls it (`interchange_contracts.py:940`).
  [cited — five sites]

**This changes the framing of the whole subsection, and nothing in the 31 findings
names it.** What follows is therefore a **refinement of an existing declared
surface**, not a new mechanism: the vocabulary gains structure (a record instead
of a letter), gains three fields the letter cannot carry, and — under R-2 —
changes what it returns for Class C. It also puts `METRIC_CLASSES`,
`Q_METRIC_SUFFIXES`, `metric_grain` and `dev/reference/indicator-glossary.md` in
the migration inventory as *semantic* changes rather than spelling ones (§8.2).

**Normative.** Every metric carries a **grain declaration** in
`blueearth_cst/shared/indicator_tables.py`, beside the metric's name and suffix,
as a structured record replacing the bare class letter:

| field | values | meaning |
|---|---|---|
| `grain` | `"run"` \| `"bundle"` | Whether the metric's value is defined per run or only over a set of runs |
| `bundle_by` | a **grouping key**, required iff `grain == "bundle"` | Which runs share a value. A named function of a scenario-table row, not a column name |
| `reference` | a grouping key, or `None` | The unit whose series fixes a shared parameter for every other unit (Class C's month). **Required** for Class C under R-1 |
| `blocks_per_return_period` | float, or `None` | The estimator's extrapolation precondition, per return-period year (§5.4.4) |

**`bundle_by` and `reference` are two different ideas, and v1 conflated them.**
`bundle_by` means *"this value is only defined over a set of runs"*. `reference`
means *"this value depends on a parameter fixed from another unit"*. **Sharing a
reference is not pooling.** That distinction is what R-2 turns on, and stating it
is the correction `domain-1` asked for.

For the current metric set the declaration is:

| class | metrics | `grain` | `bundle_by` | `reference` | `blocks_per_return_period` |
|---|---|---|---|---|---|
| A — linear in years | `mean_annual_*`, `*_p95`, `Q7day_*` means, `BaseFlowIndex`, and every per-subcatchment variable | `run` | — | `None` | `None` |
| B — non-linear fit | `return_level_max`, `return_level_7day_min` | `bundle` | `same_design_point` | `None` | `1.0` (§5.4.4) |
| **C — evaluates a fixed category** | `wetmonth_mean`, `drymonth_mean` | **`run`** | — | **required** | `None` |

#### 5.4.1a Class C is `grain: run` with a required `reference` — R-1 and R-2

**v1 declared Class C `grain: bundle` on a premise the code refutes, and this is
the correction.** The blocking finding `domain-1` is accepted in full; the owner
ruled it at G1 as R-2, after ruling the underlying semantics as R-1.

**What v1 got wrong, precisely.** It wrote that *"Class C pools because `idxmax()`
selects one month and different realizations select different ones"*. That
mechanism **is not in the code**. `_category_month` is called **once, globally**,
outside the member loop, from the `st_0` baseline
(`export_wflow_results.py:361-364`: `if q_locations and 0 in runs:` →
`_category_month(baseline, "wet"/"dry")`). [cited] And the Class-C value is
`_month_mean(pooled, month, anchor)` = `frame[frame.index.month == month]
.resample(anchor).mean().mean()` (`:173-175`) — filter to the month, mean per
water year, mean over years. That is the **identical** "annual statistic, then
mean over years" structure the code cites at `:384-385` to keep Class A per-run.
For equal-length realizations on one calendar the pooled Class-C value is exactly
the mean of the per-realization values, so **a per-run grain both exists and is
finer**.

**R-1 (owner, semantics).** *"wetmonth shall be the same across all realizations
(needs to be selected in advance). We shall not pool different calendar months
together for this metric."* So the behaviour in the code today is correct and
intended; a per-realization month selection is now a **design error**, not an
unchosen alternative, and this design records it as one. `reference` is therefore
**required** for Class C — it is what guarantees the one shared month — and a
family registering no reference grouping may not carry a Class-C metric.

**R-2 (owner, storage).** Class C is `grain: run`. Per-run values are well-defined
and average back exactly, so storing the finer grain loses nothing and preserves
**per-realization spread**: a reader can see whether the wet-month response at a
design point is consistent across realizations or driven by one outlier draw.
Under `grain: bundle` that information is destroyed at write time and is not
recoverable from the results file. This is D5 applied exactly as v1 applies it to
Class A one paragraph earlier — which is why v1's Class-C row violated its own
decision criterion.

**Accepted cost, taken deliberately at the gate.** The results file **gains rows**
for these two metrics: `RLZ_NUM` rows per design point per location instead of
one. So HM-7's pinned surface changes in row count as well as column set, and the
baseline moves. §9's GF-9 instrument is built to see exactly this (the Class-C
crosswalk case), and §8.2's re-record covers it.

**Two further clauses on `reference`, both stated because v1's specification was
incomplete in ways that reach behaviour:**

1. **The reference parameter is resolved ONCE PER TABLE, not per location**
   (`domain-8`). `_category_month` collapses over locations as well as over units:
   it sums monthly flow across gauges, takes `idxmax()`, and returns
   `int(chosen.iloc[0])` — the **first** gauge column
   (`export_wflow_results.py:159-170`), documented there as preserving pre-R11
   behaviour under ruling Q5. [cited] So one gauge's wettest month is applied to
   every gauge in the basin. A re-implementer working from v1's normative text
   ("the unit whose value fixes a shared parameter") would reasonably compute it
   per location — a behaviour change smuggled in under a migration whose headline
   claim is output-neutrality. Q5 is cited as the authority, and the collapse is
   normative text rather than an artefact of the implementation.
2. **A declared `reference` unit MUST be `evaluated: true`, refused at parse
   time** (`domain-6`). §5.1.5 sets `evaluated = run_historical` for the baseline
   row; §5.3.5 makes the Class-C month a lookup of the declared reference unit,
   which needs that unit's simulated series; §5.4.3 invariant 6 requires the unit
   index to cover every evaluated run. Under `run_historical: false` those three
   clauses cannot all hold. Today's code resolves the same tension **silently**:
   `if q_locations and 0 in runs:` (`:362`) leaves `wet_month`/`dry_month` as
   `None`, and the Class-C rows are simply never emitted — no log line, no
   failure, **two configured metrics gone from the deliverable unannounced**.
   [cited] That is a live `AGENTS.md` "no silent caps" violation in the exact
   configuration to which §5.1.5 adds no-silent-cap language. The refusal joins
   the parse-time refusals of §5.6, and its message names the metric, the
   reference grouping, and `run_historical` as the setting to change. GF-14 is its
   falsifier.

#### 5.4.1b Bundling, and the one remaining bundle-grained class

**`bundle_by` is a named function, not a column.** `same_design_point` is
registered in `scenario_families.py` beside the family whose rows it can group —
for `stochastic` it is "equal `st_id`, any `rlz`". This is the one place where a
family-specific fact legitimately enters stage 3, and it enters as a *registered
grouping* rather than as a column reference scattered through the reducer. A
family that declares no such grouping cannot use a `bundle`-grained metric, and
the validator says so by name instead of pooling over the wrong thing. [argued]

**A grouping MUST NOT drop empty keys.** Restated here from §5.1.2 because this is
where it bites: after R-2 the only `bundle`-grained metrics are the two Class-B
return levels, and the baseline design point's bundle is keyed by the **empty
`st_id`**. The default `pandas.groupby` behaviour silently drops it. See §5.1.2
and GF-13.

Class A stays per-run for the reason `export_wflow_results.py:344-350` already
gives, and that reason is the D5 principle in the concrete: these are "annual
statistic, then mean over years" over equal-length realizations, so per-run values
average back to the pooled value exactly and nothing is lost by storing the finer
grain. `aggregate_rlz` existed only to choose between grains that are not
different, which is why R11 retired it.

**D5's stated exception, now narrowed to Class B alone, and why it is principled.**
For Class B the finest grain that *exists* is the bundle, and the reason is
methodological, not convenient. The GEV is fitted on pooled blocks because a fit
over one short realization is ill-conditioned (`export_wflow_results.py:27-35`);
the pooling is of the **sample**, never a spliced series, because splicing
manufactured 7-day flows occurring in no realization (`:40-46`). A per-run Class-B
value would not be a finer measurement of the same quantity — it would be a
*different, worse* estimator. **Class C is no longer part of this exception**, and
v1's extension of the argument to it is the error R-2 corrects: pooling a
non-linear fit and evaluating a fixed calendar month over pooled years are not the
same operation, and only the first destroys information by being computed finer.
[cited — the two docstrings state it for Class B; argued that declaring it changes
no Class-B number]

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

**Row count changes under R-2, and the change is stated here rather than
discovered.** With Class C at `grain: run`, `q_wettest_month_mean` and
`q_driest_month_mean` each emit `RLZ_NUM` rows per design point per location where
they previously emitted one. On the shipped baseline config (`RLZ_NUM = 2`,
`test_case/snake_config_baseline_run_stress_test.yml`) that is a doubling for
those two metrics. The migration is therefore **not** output-neutral in the naive
sense v1 claimed: every Class-A and Class-B *value* is unchanged, and Class C
gains rows whose mean over `rlz` reproduces the old pooled value exactly. §9's
GF-9 instrument checks precisely that decomposition — it is the one place the
"nothing moves" claim becomes three separate, checkable claims instead of one
unfalsifiable one.

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

   **The asymmetry, stated once and referenced from the other place it applies**
   (`risk-4`): an unevaluated forcing ancestor has a **`.nc`** (rule 3.11 builds
   it because rule 3.12 declares it as an input), and **no catalog entry, no run
   CSV and no unit**. WG-5's cross-artifact invariant (§5.8) and this invariant
   both rest on it, and v1 had it right here and wrong there.

7. **The baseline design point's bundle exists** whenever `run_historical: true` —
   the unit keyed by the empty `st_id` (§5.1.2). A namespace missing it is short,
   not smaller. Added because `risk-5` establishes that invariant 6 alone cannot
   see this: if the minter never mints the empty-key bundle, the namespace and the
   table agree about the hole.

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
on the same calendar boundary, "and nothing checks that". [cited — the
docstring]

It is not a defect today, because one family with one record length produces every
row. It becomes one the moment a second family shares the table under the same
metric name: a 30-year GCM-downscaled run and a multi-realization stochastic
bundle would carry `q_return_level_max` in the same column with materially
different estimator precision, and nothing would say so.

**The precondition's SHAPE changes under R-4, and its value is picked here.** v1
declared an absolute integer `min_blocks`, argued it as "an absolute statement
about the estimator", and then set it to the block count the shipped fixture
happens to produce. `domain-3` filed that as self-refuting in two independent
ways, and both are accepted:

- **The value's provenance was the fixture.** A threshold read off the fixture is
  the "documentation wearing a check's clothes" the same paragraph accused the
  alternative of being, and it guaranteed the check could never fire on any
  shipped config — so the mechanism would ship untested against its own purpose.
- **The shape omitted the extrapolation.** What governs whether a GEV return level
  is defensible is the block sample size **relative to the return period being
  extrapolated**. An absolute floor cannot distinguish a 20-year level from a
  200-year level fitted on the same sample. Both periods are already in scope —
  `RETURN_PERIOD_PEAK_YR = 10` and `RETURN_PERIOD_LOW_YR = 2`
  (`indicator_tables.py:186-187`), imported by the reduction module at
  `export_wflow_results.py:62-63`. [cited] No new input is needed.

**Normative, replacing `min_blocks`.** The metric declares
`blocks_per_return_period`, a float. At reduction time, for each bundle a
`bundle`-grained metric is computed over, the reducer computes

    required = max( ceil(blocks_per_return_period × T),  GEV_IDENTIFIABILITY_FLOOR )

where `T` is the metric's declared return period, counts the blocks actually
available, and:

- if the count is below `required`, it **refuses** — raising, naming the metric,
  the unit, the return period, the required and the actual block count — rather
  than fitting;
- it never silently degrades to a smaller sample, and never emits a row it could
  not compute to the declared precision.

**The ratio is picked, and here is the argument for the number.** R-4 makes this a
milestone precondition rather than Q7's follow-on, so it is settled here:

> **`blocks_per_return_period = 1.0`** for both return-level metrics — the block
> sample must be at least as long as the return period being estimated.

This is a statement about extrapolation with standing independent of this
repository: a return level at period `T` estimated from fewer than `T` blocks is
extrapolated beyond the sample that informs it, and the fitted shape parameter,
not the data, is carrying the answer. It is deliberately the *permissive* end of
defensible practice — stricter readings (do not extrapolate beyond half the
record, i.e. a ratio of 2) exist and are considered below — because a precondition
introduced alongside a rename must not silently redefine which configurations are
legal.

**`GEV_IDENTIFIABILITY_FLOOR = 10` blocks**, and it needs its own provenance
rather than riding on the ratio. The ratio alone would demand **2 blocks** for
`return_level_7day_min` (`T = 2`), which is below the three parameters a GEV has;
the fit is not merely imprecise but unidentified. Ten is the conventional minimum
record length below which at-site frequency analysis is not attempted at all — a
standing position in hydrological practice rather than an arithmetic gesture — and
it leaves a three-parameter fit meaningful residual degrees of freedom. It is a
floor, not a target: it is not a claim that ten blocks give a good fit.

**Two honest statements about these two constants, because a reader would
otherwise mis-read which is doing the work.**

1. **The ratio's discriminating power is LATENT today.** With `T = 10` and
   `T = 2`, `required` evaluates to 10 for *both* metrics, so the declaration's
   value is uniform across everything in the shipped set and no configuration
   distinguishes a 10-year level from a 2-year one. R-4's purpose — a precondition
   that separates a 20-year level from a 200-year one on the same sample — is
   satisfied **structurally**, and first *fires* at `T > 10`. That is a real
   improvement over v1's absolute floor, which could never acquire the property at
   any `T`; it is not a claim that the ratio changes any behaviour now.
2. **The floor is the binding term and carries the weaker argument of the two.**
   `blocks_per_return_period = 1.0` is an estimator statement about
   extrapolation; the floor is a practice convention. Since the floor is what
   actually decides every shipped config, that asymmetry is stated rather than
   left for a reviewer to notice. **What would raise it:** adopting a stricter
   published minimum for stable L-moment shape estimation (commonly 15–20 blocks),
   or a sensitivity study in this repository showing the fitted shape parameter's
   variance across realizations at the baseline block count. Either is a
   methodological change that refuses shipped configs, so it belongs with A12's
   ratio question and not inside a rename — Q7.

**What this refuses, stated plainly, including the fact that it refuses no shipped
config today.**

| config | blocks | `return_level_max` (T=10) requires | `return_level_7day_min` (T=2) requires | verdict |
|---|---|---|---|---|
| `snake_config_baseline` (2 rlz × 16 yr) | 32 | 10 | 10 | passes |
| `snake_config_rapid` (2 rlz × 9 yr) | 18 | 10 | 10 | passes |
| 1 rlz × 9 yr | 9 | 10 | 10 | **refuses** |

**The floor binds for both shipped return periods; the ratio binds from `T > 10`
upward.** That is stated rather than hidden — a reader who assumes the ratio is
doing the work today would be wrong. What the ratio buys is the property
`domain-3` asked for: the declaration now distinguishes a 20-year level from a
200-year level fitted on the same sample, so a user who raises `T` gets a
proportionally raised requirement instead of a constant that was calibrated for a
different question.

**The alternative ratio, and why it was not taken.** `blocks_per_return_period =
2.0` — the "do not extrapolate beyond half the record" reading — would require 20
blocks for the peak return level and therefore **refuses `snake_config_rapid`**, a
shipped smoke config, dropping two of its eleven q metrics. That is a
methodological tightening arriving as a side effect of a rename, which §8 argues
against on its own terms: it would make the migration's baseline evidence
unreadable, because a value that vanished and a value that moved look the same in
a comparison. Raising the ratio is a clean, separable later decision now that the
*shape* is right, and §10's Q7 is rewritten to say exactly that rather than to
defer the whole mechanism.

**The refusal is falsifiable, which v1's was not** (`domain-4`). v1 shipped the
design's one genuinely new scientific mechanism with **no GF row exercising a
refusal**, in a document whose eighth decision criterion is that every claimed
runtime property have a falsifier — and with GF-9 asserting the opposite (that no
number moves, and by C-9 that the refusal is unreachable). GF-15 in §9 is its
falsifier: a unit test invoking the reducer on a synthetic bundle whose block
count is one below `required`, asserting the refusal and the five facts its
message must name. It is a synthetic test on purpose, because reachability on a
shipped config is not something this design claims.

**Why refuse rather than record.** The alternative — a `n_blocks` column beside
each value — was considered and rejected in §6 (A7). It re-couples the results
header to an estimator detail, it makes every consumer responsible for a check it
will not perform, and it answers a *comparability* question with a number rather
than with a decision. Refusing states the toolbox's position: this metric is
defined at this precision or it is not emitted. This is the same shape as
`prepare_cst_parameters.refuse_out_of_domain_multipliers`
(`prepare_cst_parameters.py:82-120`), which refuses a configuration whose
arithmetic the WG-2 bound cannot cover rather than emitting a caveat.

#### 5.4.4a Fit uncertainty — the position, argued as a position (`domain-7`)

**Stated because v1 did not state it.** v1 argued admissibility against A7's
`n_blocks` column, which is a different question from whether uncertainty crosses
the seam at all. The finding is right that it does not, and that the four-column
header forecloses carrying it.

**The position, ruled here.** *The toolbox reports **admissible point estimates**
and carries no fit uncertainty across the stage-2 → stage-3 seam.* A value is
emitted at declared precision or it is refused; there is no third state in which a
caveated number travels.

**Where uncertainty survives, and where it does not — after R-2 the residual is
Class B alone.**

- **Class A and Class C carry per-run rows**, so ensemble spread across
  realizations is recoverable from the results file by the reader. R-2 moved Class
  C into this half; under v1 it was in the other.
- **Class B carries nothing.** `return_level_max` and `return_level_7day_min` are
  GEV quantiles fitted on a pooled block sample
  (`_return_level_from_blocks`, `export_wflow_results.py:225-253`) and are written
  as a bare `value`. [cited] Neither an interval nor the sample size travels.

**The honest cost.** In a bottom-up stress test the surface is read for where it
crosses a performance threshold, and a return level fitted on a pooled block
sample carries sampling uncertainty that can be comparable to the
perturbation-induced differences the surface is drawn to show. Under this position
a reader cannot tell whether a gradient between two design points exceeds the
estimator's own noise. `blocks_per_return_period` is an **admissibility gate, not
an interval**, and substituting one for the other is a choice rather than a
solution.

**Why take it anyway, for this milestone.** Growing the four-column header is
ruled out by W2 and would re-incur the CR-2 defect on a third axis. The route that
stays open is the one W2 already permits: `metric` is a free vocabulary, so a
companion metric name (`q_return_level_10yr_max_ci95_lo` / `_hi`) can admit an
interval later **without any schema change** — a metric declaration and a reducer
change, no contract migration. That is recorded as Q9 in §10, and it is why this
position is a deferral of a capability rather than a foreclosure of one.

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
- Run ids are minted first, in the scenario table's **normative row order**
  (§5.1.2: rlz-major, baseline row first within a realization), from `1`. v1 said
  "in scenario-table order" and left that order undefined, which `risk-7` filed:
  rlz-major and st-major produce different `run_id ↔ (rlz, st_id)` mappings for
  the same config, the digest cannot tell them apart because it is computed over
  whichever was minted, and the crosswalk GF-9's instrument needs cannot be
  written against an unspecified order.
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

**The coupling, stated accurately — v1 understated it** (`risk-6`, `arch-7`). v1
wrote that the minter "reads one integer to size a field" and that stage 1 "never
evaluates a grouping". **The second half is false of v1's own specification**:
bundle ids are ordered by `(bundle_by name, grouping key)`, and a grouping key is
the *value* a grouping function returns for a row — so the minter must **evaluate
stage-3 grouping functions over stage-1 rows**. The accurate statement is:

> Minting requires the **number** of bundles and their **deterministic order**, so
> the minter imports the grain declarations and evaluates each `bundle_by`
> grouping over the scenario table's rows. The `run_id` strings in
> `scenario_table.csv` — and therefore the file, and therefore its digest — are a
> function of the declared metric set.

**S3 still holds, on a narrower reading than v1 gave it.** No grain column exists,
stage 1 takes no grain decision, and stage 1 cannot name a bundle. What is true and
was hidden is that a **stage-1 artifact's content depends on a stage-3
declaration**, which is a real cost against S1 ("three stages, three contracts") —
the settled constraint §3 restates. It is priced in §7 (C-4, C-11), and it is
the cost A3 pays off, which is why §6's A3 entry is now argued rather than
deferred.

**Three things bound the width coupling:**

1. It fires only when a *new grouping* is introduced. Adding a metric that reuses
   an existing `bundle_by` adds no bundle and cannot move `W`.
2. It fires only when the count crosses a power of ten.
3. It is loud — but **v1's account of the loudness was wrong**, and this is the
   `arch-7` correction. v1 said the digest guard "refuses the run rather than
   mixing two widths in one tree", and presented that as a benefit. What the guard
   would actually report is a **changed scenario set** when the scenario set is
   byte-identical, because the digest moved for a width reason: a diagnosis
   pointing the user at the wrong artifact, and one whose remedy costs the whole
   stage-2 sweep. §5.5.3 therefore separates the two terms.

**Rule 3.09 gains a rerun trigger for the grain declarations** (`arch-7`). Since
3.09's output content now demonstrably depends on the declarations, and 3.09's
config inputs are `ancient()` so `params.stress_test_cfg` is its **only** rerun
trigger (`run_stress_test.smk:882-887`, whose own comment records the trap)
[cited], rule 3.09's `params:` gains the grain-declaration digest, matching what
§5.3.4 does for rule 3.16. v1 asked this question of 3.16 (P4 / GF-6) and never of
3.09. GF-16 in §9 is its falsifier.

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

##### 5.5.3a The guard this repository already has, and why v1 did not see it

**`risk-1` is accepted as close to a framing finding, and this subsection is the
reconciliation it asked for.** v1 analysed the in-place hazard without citing the
guard that already covers most of it, then designed a new guard in a shape this
repository explicitly rejected.

**What exists.** `experiment.yml` records the resolved `workflows.run_stress_test`
section, and `check_not_frozen` refuses any change to it once the experiment has
produced results (`blueearth_cst/experiment/write_experiment_config.py:113-140`;
`_frozen_differences` at `:63`, `has_run_successfully` at `:55`, raising
`ExperimentConfigFrozenError`). [cited — note the review's `:191-239` citation
points at the `__main__` block; the function is at `:113-140`] `realizations_num`
**and** the perturbation grid are both inside that section (`my_cfg =
config["workflows"]["run_stress_test"]` at `run_stress_test.smk:94`,
`stress_test_cfg = my_cfg["stress_test"]` at `:186`), and the comparison is by
value over the nested mapping. It is written by rule 3.07, early in WF3. So **for
the only scenario family that exists, changing the scenario set in place is
already refused.**

**What the freeze deliberately permits, and v1's guard would have broken.** The
freeze keys on `has_run_successfully` — the merged workflow log, written by the
last rule in WF3 — and its module docstring states the reasoning in terms:
*"Freezing at creation would be a different and worse feature — it would forbid
the legal case to make the illegal one easy"* (`:13-17`). [cited] A run that dies
at rule 3.12 leaves no marker, so editing the config and re-running is the
**legal** case. v1's digest is written by rule 3.09 and checked at parse time, so
it would be on disk after that failed run and would refuse the user's legitimate
fix — with a refusal v1 declares "not silenceable by a flag". That is a false
positive on the one case the repository went out of its way to allow.

**Three corrections follow.**

1. **The digest check is keyed to the same success marker as the freeze.** It does
   not fire unless `has_run_successfully(run_marker)` is true. The two guards then
   have the same activation condition and cannot disagree about whether an
   experiment is settled.
2. **Precedence is stated.** The freeze is checked first, at rule 3.07, and its
   message is the one a user of the stochastic family sees for a config edit. The
   digest is the narrower, later check. A user never meets both messages for one
   cause.
3. **The justification is narrowed to the coverage the freeze genuinely does not
   give.** v1 claimed that without the digest "W4's narrowing is not a narrowing
   but a removal". That is too strong and `risk-1` is right to reject it. The
   honest statement is:

   > For the stochastic family the freeze already contains the in-place hazard,
   > because the scenario table is a pure function of a config section the freeze
   > compares by value. The digest covers the case the freeze **cannot see**: a
   > scenario table that is not derived from that config section — a **supplied**
   > table, changing on disk under an unchanged config — and, secondarily, a
   > change to `scenario_table()`'s own logic, which moves the table without
   > moving the config.

   That is a real gap and worth one sidecar file. It is not the load-bearing
   support for D3's narrowing that v1 made it, and §5.10.1's C24-reason-2
   disposition is adjusted accordingly: the narrowing is made safe **jointly** by
   the experiment freeze (existing, load-bearing) and the digest (new, narrower).

**A second false positive, removed by construction** (`risk-1` (c)). v1's
canonical serialization spans the family block, whose membership comes from
`FAMILY_COLUMNS` in code — so editing the registry moves the digest with no
scenario changed. Combined with `arch-7`'s width term, the v1 digest fired on at
least three causes and named one. **The digest is therefore taken over the
scenario table's *semantic content only*: the family block's values and the
`derived_from` edges, keyed by `(scenario_family, family-block values)`, with
`run_id` spellings, column order and the registry's column *names* excluded.** A
width change and a registry rename then move no digest, and the guard reports the
one cause it is named for.

**Decision.** A canonical digest of the scenario table's semantic content is
written beside the run outputs and checked at parse time.

- **`scenario_table_sha256`** = SHA-256 over the canonical serialization of the
  scenario table's **semantic content**: for each row, `scenario_family` and the
  family-block values, plus the `derived_from` edge expressed as the *ancestor's
  family-block values* rather than as a `run_id` string; rows sorted by that
  tuple; LF-joined, UTF-8. Canonical, and deliberately **blind to `run_id`
  spellings, column order, width `W`, and the registry's column names** — a digest
  that moved on any of those would fire on the causes `arch-7` and `risk-1` (c)
  identify and would then name the wrong one.
- **Written** by rule 3.09 to `<exp>/config/.scenario_table.sha256`, and carried
  into `<exp>/results/run_metadata.json` by rule 3.16b, which already exists for
  exactly this class of fact and already takes the indicator tables as *input*
  rather than writing into them, so that recording a digest cannot falsify the
  baseline. **The sidecar is authoritative; `run_metadata.json`'s copy is a
  record** — v1 wrote it to two places and said which was read nowhere
  (`arch-8`). Only the sidecar is read.
- **Checked at parse time, and only on a settled experiment.** The check is
  skipped unless `has_run_successfully(run_marker)` is true (§5.5.3a correction
  1). If the sidecar exists, the experiment has run successfully, and the sidecar
  disagrees with the digest of the table just derived, WF3 **refuses**, naming
  both digests and the experiment, and telling the user the two resolutions: run
  into a new experiment (C25's mechanism, still the right answer), or delete the
  experiment's run outputs **and the sidecar** deliberately.
- **The remedy must actually clear the refusal** (`arch-8`). v1's remedy named
  `climate/`, `hydrology/` and `results/`; the sidecar lives under `config/`,
  which no list included, so a user following the instruction met the same refusal
  again with nothing left to try — at exactly the moment the design intends to be
  maximally clear, and with no flag to silence it. `<exp>/config/.scenario_table.sha256`
  is added to the refusal message and to §8.3's deletion list, in both places.
- The refusal is **not** silenceable by a flag. A flag here would be a
  configuration surface for corrupting a results file.

**What this does for D3's narrowing — restated, because v1 overclaimed it.** W4
narrows "the id must be stable under set growth" to "the *design* must be stable;
the index may renumber, provided a changed lookup is detectable rather than
silent". The detection is **joint**: for the stochastic family the experiment
freeze (`check_not_frozen`) already refuses the config edit that would renumber
the set, and the digest covers the supplied-table and changed-minter-logic cases
the freeze cannot see (§5.5.3a). v1's sentence — *"without it, W4's narrowing is
not a narrowing but a removal"* — is withdrawn as unsupported.

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
| **3.09** `prepare_stress_test_grid` | Gains a **second output**, `<exp>/config/scenario_table.csv`, written from `scenario_index.scenario_table(cfg)` — the same object the Snakefile minted at parse time (§5.1.4). Also writes `<exp>/config/.scenario_table.sha256`. `stress_test_lookup.csv` is unchanged in shape and content. One rule and one enumeration, per C26. **`params:` gains the grain-declaration digest** (`arch-7`): 3.09's output content depends on the declarations through `W` and the bundle count (§5.5.2), its config inputs are `ancient()`, and `params.stress_test_cfg` is otherwise its only rerun trigger (`:882-887`). Falsifier GF-16 |
| **3.11** `generate_weather_realizations` | Output list becomes `temp([f"{wg_dir}/output/run_{rid}.nc" for rid in ROOT_IDS])`, where `ROOT_IDS` are the run ids with empty `derived_from`. **`temp()` restored** (`arch-9`): v1's row gave a bare comprehension while §5.7b said the `temp()` lifecycle is unchanged and the live rule wraps it (`run_stress_test.smk:990`) — an implementer following v1 literally would stop the baseline NCs being temporary, which `AGENTS.md` names as the change that explodes disk usage on large sweeps. Still one job, still a static Python list, still zero wildcards — unchanged in shape from `:978-990` |
| **3.12** `perturb_climate_realization` | `wildcard_constraints` becomes `run_id = "\|".join(DERIVED_FROM)` — the measured mechanism (i-c), data-derived, replacing `st_num=member_index_regex(ST_WIDTH)` at `:1018`, whose token no longer exists. `input.rlz_nc` becomes `lambda w: f"{wg_dir}/output/run_{DERIVED_FROM[w.run_id]}.nc"`. `lookup_csv` stays a constant input (`:1026`) and the design parameters travel as `params: payload = family_payload(row)` — a sealed mapping obtained from the single permitted accessor and passed through unread, per §5.2.1a's one stated exception. The rule does not name `st_id` |
| **3.14** `downscale_climate_realization` | Wildcard `{run_id}` replaces `{rlz_num}`/`{st_num}`; `wildcard_constraints: run_id=rf"[0-9]{{{W}}}"` keeps the digits-only guard that stops a path splitting across a `/` boundary. Output paths per §5.3.2 |
| **3.15** `run_wflow_batch_<b>` | **`_k_members` is built from `EVALUATED_IDS`, never from `RUN_IDS`** (`arch-5`) — the batch rule's outputs are STATIC Python lists (`:1226-1231`), so every member of `_k_members` is an unconditional output and no pull semantics exclude anything; the exclusion is this filter, exactly as `ST_START` is today. v1's row was silent on it, and read literally the unevaluated baseline would have been simulated. It is *already* a flat list (`:1120`), so this is a substitution, not a restructure. `params.members` carries run ids; `_member_span`'s two-range banner is replaced by a first–last id span, since a flat list has no rectangle to describe and the `(partial)` caveat at `:1210-1213` becomes vacuous |
| **3.16** `derive_wflow_indicators` | `input:` becomes the static list of §5.3.4; `params:` gains `run_csv_by_id`, the scenario-table rows, the grain declarations and the **grouping-registry digest** (`risk-8`). Gains a **second output**, `<exp>/results/unit_index.csv`. `params.st_num` / `params.st_start` (`:1266`, `:1271`) are deleted — run coverage is now checked against the minted namespace |
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

**The `params:` trigger covers half the change space, and the other half is closed
explicitly** (`risk-8`). v1 claimed a rerun trigger on "a grain change" without
distinguishing two kinds:

| change | what travels through `params:` | re-fires? |
|---|---|---|
| a metric names a **different** `bundle_by` | the name string changes | **yes** — a string comparison sees it |
| `same_design_point`'s **body** changes what it computes | the name string is unchanged | **no** under v1 |

The second is not hypothetical: `bundle_by` is specified as *"a named function,
not a column"*, so the function body is code and the param is a label for it.
GF-6's v1 falsifier ("edit a `bundle_by`") does not distinguish the two and could
pass while the hazard it was written for is live. **Rule 3.16's `params:`
therefore carries a digest of the grouping registry's source** alongside the
declarations, so a body change moves a param value. GF-6 is worded in §9 as two
cases, and states which one each mechanism closes. The same treatment is applied
to rule 3.09 (`arch-7`), for the same reason.

**Parse-time refusals, all in one place.** The empty scenario set (§5.1.4); the
acyclicity rule and the one-table-one-family rule (§5.1.2); the pairing-consistency
refusal (§5.1.2); the reference-unit-must-be-evaluated refusal (§5.4.1a); and the
digest mismatch on a settled experiment (§5.5.3) are all raised by `scenario_index`
before the DAG is built, in the same position as `refuse_out_of_domain_multipliers` today. A refusal
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

[cited — `grep -n` over both contract files]

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

**Replacement text for HM-2, HM-4, HM-5 and HM-6b — written out, not derived**
(`risk-10`). v1 gave an *instruction* ("take the corresponding path substitutions
from §5.3.2 and change in no other respect") where the intake's success criterion
is "closed in normative text, not sketch", and where §8.2 step 1 requires every
live reference fixed in one commit. Four of nine targets reached the implementer
as a derivation. They are clauses now:

- **HM-2 (wf3 forcing twin), replacing `hydrological-model-seam.md:75`:**
  *path pattern:* `<exp>/hydrology/wflow/forcing/inmaps_run_<run_id>.nc` — one per
  run in the scenario table, the wf3 twin of the wf1 forcing. `run_id` is
  zero-padded text at the namespace width; nothing parses the name. Every other
  clause of HM-2 — variable set, raster shape, CRS descriptor, lifecycle —
  unchanged.
- **HM-4 (run config), replacing `:169`:**
  *path pattern:* `<exp>/hydrology/wflow/config/run_<run_id>.toml` — one per
  evaluated run, written by rule 3.14. The TOML's own contents, the pinned
  key subset and the hydromt/wflow conventions it follows are unchanged.
- **HM-5 (model output), replacing `:214`:**
  *path pattern:* `<exp>/hydrology/wflow/output/run_<run_id>.csv` — one per
  evaluated run, written by rule 3.15's batch. It is the **finest-grain artifact
  of the whole workflow** (D5) and the only stage-2 output stage 3 reads. Columns,
  time axis and units unchanged.
- **HM-6b (warm state), replacing `:277` and `:286`:**
  *path pattern:* `<exp>/hydrology/wflow/output/outstates_run_<run_id>.nc` — one
  per evaluated run, `temp()`, lifecycle and content unchanged.

**Validator-index rows** at `hydrological-model-seam.md:744-763` and `:792-795`
are targets of the same commit, with `rlz_<n>_st_<m>` replaced by `run_<run_id>`
in each row's artifact column and `validate_wg5_catalog_grid` respelled
`validate_wg5_catalog_runs` (§5.8).

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
- **cross-artifact invariant:** the **entry-key set equals the `evaluated: true`
  run set**, full stop. Previously stated as "the realization × cst grid"; that
  phrasing embedded the factorial assumption in the contract and is replaced by a
  set equality against a table, which is checkable for any family. Checked by the
  relational validator `validate_wg5_catalog_grid`, which is renamed
  **`validate_wg5_catalog_runs`** — "grid" is now a false description of what it
  checks. (`naming.md` §7 covers this: it is a test-facing identifier, so the
  rename rides in the same migration note.)

  **v1's second clause is DELETED, because it was unsatisfiable** (`risk-4`). v1
  added "*and every root run whose series a perturbed run derives from*". The
  per-run catalog is written by rule 3.14 as a `temp()` output beside that run's
  TOML (`run_stress_test.smk:1085-1088`), and 3.14 is pull-scheduled from rule
  3.15's demand for that run's forcing. [cited] Under `run_historical: false` the
  root run is `evaluated: false` (§5.1.5), so no 3.15 job requests it, no 3.14 job
  fires, and no catalog entry exists — while v1's invariant demanded one. A
  relational validator that fails on a supported config option is worse than the
  phrasing it replaces, and it would have landed in a contract document
  out-of-repo readers re-implement from.

  **The asymmetry it exposes is real, and is stated once here and once in §5.4.3.**
  An unevaluated forcing ancestor has a `.nc` (rule 3.11) and **no catalog and no
  unit**. That is correct, not a hole: a catalog entry describes a forcing handed
  to a wflow run, and there is no wflow run.

  **A latent defect is removed rather than inherited.** The existing validator
  bakes the same assumption in differently — `interchange_contracts.py:1327-1331`
  builds its expected key set as `m in range(0, st_num + 1)` unconditionally, i.e.
  assuming `ST_START = 0`. [cited] v1 would have pinned that assumption as
  normative text; the replacement removes it, and the migration is the moment to
  do so because the validator is being rewritten anyway.
- **The "including `st_0`" clause is deleted**, not reworded. It named a
  family-specific member. Its content is preserved by the set equality above,
  which covers the baseline because the baseline is an ordinary run.
- **temp() lifecycle, pinned surface, deliberately unpinned:** unchanged in
  substance.

- **`validate_wg5` changes, and v1's claim that it does not was false against the
  code** (`arch-3`). v1 wrote *"`validate_wg5` (per-entry schema) is untouched,
  since no per-entry field changes"*. The validator does not merely validate
  fields — it **selects** the entries by key prefix and fails when there are none
  (`blueearth_cst/shared/interchange_contracts.py:554-560`):
  `entries = {k: v for k, v in cfg.items() if isinstance(k, str) and
  k.startswith("rlz_")}`, then `if not entries: diffs.append(f"{label}: no
  'rlz_<n>_st_<m>' entries in catalog")`, with the key pattern also carried in its
  docstring at `:525` and `:536-537`. [cited — I read the function] Under this
  design's own replacement the sole entry key becomes `run_<run_id>`, so
  `validate_wg5` would find **zero entries and report a contract violation on
  every well-formed catalog**.

  This is the purest form of the defect class this design exists to attack — a
  contract text positively asserting that a validator is unaffected by a change
  that breaks it — and it propagates: §8.2's atomic commit lists
  `interchange_contracts` as a target while §5.8's rationale told the implementer
  the WG-5 per-entry validator needed no edit, so D7's one-commit obligation was
  briefed against an incomplete target.

  **Replacement:** `validate_wg5`'s **entry selector** moves from the `rlz_`
  prefix to `run_`, its no-entries diagnostic moves with it (`no 'run_<run_id>'
  entries in catalog`), and its docstring's key pattern moves with both. **Per-entry
  FIELD validation is what is unchanged** — that is the true statement v1 meant and
  did not write.

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
and disagree with the contract text a re-implementer reads. [cited — three
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
  **text**. **Every `unit_id` in one results set shares one width; the width is
  DISCOVERED from `unit_index.csv`, never computed; a set mixing widths is
  malformed.** This is the same formulation WG-2 already uses for `st_id`, and it
  replaces v1's "at the namespace width" (`arch-10`), which pinned a value the
  contract does not define: §5.5.2 makes the width a function of the declared
  bundle count in `shared/indicator_tables.py` — a repository-internal,
  version-dependent quantity an out-of-repo re-implementer cannot compute, while
  C-7 requires HM-7 to be implementable standalone. It names **a run or a bundle
  of runs**, and
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

- **`unit_index.csv` is part of this contract**, with the schema and seven
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

- **`validate_hm7` asserts — the complete list, including the assertions v1
  silently dropped** (`arch-4`). v1 enumerated what the validator would assert and
  omitted two things it asserts today. Contract-replacement text is what a
  re-implementer and the migration commit both work from, so an omission here
  converts a loud failure into a silently shorter results file — the same "no
  silent caps" defect this design attacks elsewhere, and one that would be
  attributed to this migration rather than to the omission.

  1. **The header, the metric vocabulary, and metric/table agreement** — as today.
  2. **The seven `unit_index` invariants of §5.4.3.**
  3. **Each metric's emitted grain against its declaration** — the replacement for
     the `POOLED_REALIZATION` standing precondition.
  4. **The id-domain check, re-pointed** — replacing today's `allowed =
     {POOLED_REALIZATION} | set(range(1, int(rlz_num) + 1))`
     (`interchange_contracts.py:947-953`) [cited]. Its successor is: every
     `unit_id` resolves in `unit_index.csv`, and every `member_run_id` resolves in
     `scenario_table.csv`'s `run_id` column. v1 left this to be inferred from the
     argument swap; it is stated.
  5. **Design-point completeness, re-expressed over the new join path** —
     replacing today's two-directional lookup check and `st_0` partition
     (`:995-1038`) [cited]: every lookup `st_id` produced rows, and no emitted
     `st_id` is unknown to the lookup.

     **The baseline half must be restated in terms of the EMPTY key, not a
     baseline token, or it is unimplementable.** Today's validator computes
     `baseline_token = "0".zfill(width)` and asserts it is present in the tables
     and absent from the lookup. Under §5.1.2 the baseline row's `st_id` is
     **empty**, not a zero-padded token, so the assertion has no token to look
     for. Re-expressed: **at least one unit resolves, through the join, to a
     scenario row whose `st_id` is empty**; and the "absent from the lookup" half
     is discharged by construction rather than checked, because an empty string is
     never a lookup key. Stating this in the token's language would have shipped
     an assertion that cannot be written — the same defect class `arch-3` filed
     against the WG-5 clause, arriving through the fix for `arch-4`. The existing
     check's *purpose* is preserved exactly: it exists because two of eleven q
     metrics are derived from the baseline and a missing baseline silently removed
     180 rows with the validator green. That case is now covered twice — here, and
     by invariant 7 / GF-13 (`risk-5`).

     The join is now
     `unit_id → unit_index.member_run_id → scenario_table.st_id →
     stress_test_lookup.st_id`, and it applies **only to families declaring an
     `st_id` block column** — which is what makes it family-blind machinery
     rather than a stochastic assumption in a universal contract. This is not the
     same property as §5.4.3's invariant 6: invariant 6 checks the emitted unit
     set against the **minter's namespace**, and this checks it against the
     **configured design**. Without it the guarantee is *weaker than today's* for
     the stochastic family, which is the opposite of what the migration claims.
     The existing diagnostic text — *"a member that never ran is not a smaller
     table — it is a response surface with holes in it"* — is preserved verbatim,
     because it says why.

  Its `rlz_num` and `lookup` optional arguments are replaced by `unit_index`,
  `scenario_table` and `lookup`.

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
| 2 | *"adding realizations would otherwise renumber the design"* | **Premise removed by W4, not disputed.** It was written when the id was the only handle on a design point. Under this design `st_id` survives as a **lookup column** in the scenario table's family block and in `stress_test_lookup.csv`, so adding realizations renumbers the opaque handle and leaves the design untouched: grid point 3 is still grid point 3, in a table a reader consults anyway. Decision criterion D3 is narrowed accordingly — what must be stable is the *design's* identity, not the index — and the narrowing is made safe **jointly** by the experiment freeze (`check_not_frozen`, `write_experiment_config.py:113-140`, which already refuses the in-place config edit that would renumber the set) and by the digest guard for the cases the freeze cannot see (§5.5.3a). v1 attributed the safety to the digest alone; `risk-1` is right that this overstates a new mechanism and understates one the repository already had, and a supersession record that mis-attributes its own safety argument is exactly what a future reader would re-check |
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
sequence, distinguished by a prefix (`b_012`) or by a reserved high block.

**v1 rejected this by deference, and that rejection is withdrawn.** v1 wrote
*"Rejected because W4 rules against it… and because the design does not need it"*.
Under **R-5** W4 is a *direction*, not a ruling: it sits under the intake's
`## Working direction — initial, NOT settled` heading, whose own text says a
design run *"may test these, argue against them, and bring back a different
answer"*; and "one mixed number space, not two" is the driver's inference
("Applying W4 consistently"), not owner text. The deference was also internally
inconsistent — §5.5.1 openly *refines* W4 on the column name and argues the
refinement on merits, so a criterion argued against in one section and treated as
dispositive in another was doing no work. `risk-6` is accepted on all three
counts.

**A3's real case is stronger than v1 let it look, and it must be stated before it
can be rejected.** Three arguments for it:

1. **It is what W2 asks for.** W2's own safety conditions include *"run ids and
   bundle ids are distinguishable **on sight**, which argues for readable prefixed
   strings and against an opaque or numeric id"*. A prefix delivers exactly that.
   Rejecting A3 while citing W2 elsewhere means answering this clause, not
   omitting it — which v1 did.
2. **It pays off the coupling §5.5.2 has to apologise for.** With two sequences,
   run ids are sized from the run count alone, so the minter no longer needs the
   bundle count to mint a `run_id`. And it goes further than A2: it removes the
   *ordering* requirement too, so the minter would not need to **evaluate stage-3
   grouping functions over stage-1 rows** at all. That evaluation is a real cost
   against S1 ("three stages, three contracts"), now stated accurately in §5.5.2.
3. **It removes the width-change hazard entirely**, which is C-4 and which
   `arch-7` shows produces a misdiagnosing refusal in its current form.

**Rejected, on merits, for two reasons that outweigh those three.**

- **A prefixed id is a parsed id, and this design's second decision criterion is
  that nothing recovers identity by parsing.** `b_012` tells a consumer what kind
  of thing it is holding *from the string*, and the moment that is true, some
  consumer will branch on it — `if unit_id.startswith("b_")` is the same shape of
  contract as `_MEMBER_IN_STEM`, arriving one level up. The whole point of
  `unit_index.csv` is that kind is answered by a **join**, and a self-describing
  id makes the index optional in practice while it remains mandatory in the
  contract. That is how the `POOLED_REALIZATION` sentinel came to exist: a key
  column that told you something extra, until it didn't.
- **A reserved high block is worse than a prefix, not better.** It reintroduces a
  reserved range in the id space, and §6's A5 rejects a reserved range for the
  baseline on the grounds that reserved ranges leak into the code that has to
  respect them. The objection does not become sound because the reserved thing is
  a bundle rather than a baseline.

**What would change the decision** (stated because a rejection without one is an
assertion): evidence that new groupings are introduced often enough that the width
churn is a recurring operational cost — the same trigger as A2, which A3 also
satisfies and more cheaply. If that evidence appears, A3 is preferred over A2,
because two sequences beat two widths: A2's defect is that one run gets two
spellings, and A3 gives each object exactly one.

**And the coupling A3 would have paid off is now priced rather than hidden.**
§5.5.2 states that the minter evaluates stage-3 groupings over stage-1 rows, §7
carries it as C-11, and §5.5.3 no longer digests the `run_id` spelling — so a
width change is no longer a misdiagnosed refusal. That is the mitigation that
makes carrying A3's cost tolerable; without it the balance would be closer.

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

### A11 — Implement `forcing_uri` fully instead of removing it

**Shape.** Keep the column in the universal core and add what v1 omitted: a rule
3.11b `stage_supplied_forcing` whose input is the row's `forcing_uri` and whose
output is `run_<run_id>.nc`, the same data-derived alternation treatment as 3.12
so three producers stay unambiguous, a WG-4 producer clause, a migration row and a
falsifier. This is `arch-2`'s option (a) and `risk-2`'s option (b).

**Motivation.** It makes the design's motivating capability real rather than
accommodated, and it would let CFS's Variant B actually run.

**Rejected because it ships an ingest path for a family the intake forbids
building.** "Building a second scenario family. No GCM producer, no downscaling
path, no config surface for one" is a binding non-goal, and a staging rule that
reads a user-supplied series is the ingest half of exactly that. The design's
obligation is to *accommodate*, and CFS §4 discharges it by demonstrating that the
column returns without breaking the seam: it is family-blind, its addition is
additive rather than a redesign, and rules 3.14/3.15/3.16 never learn of it.
**What would change the decision:** the second-family milestone opening, at which
point A11 is the specification to implement and CFS §4 is its scope.

### A12 — `blocks_per_return_period = 2.0`

**Shape.** The stricter extrapolation reading — do not extrapolate beyond half the
block sample — requiring 20 blocks for the 10-year peak return level.

**Rejected because it refuses a shipped config** (`snake_config_rapid`, 18
blocks), dropping two of its eleven q metrics as a side effect of a rename. A
methodological tightening must arrive as its own decision, where its cost is the
subject rather than a footnote: in a migration, a value that vanished and a value
that moved look identical in a comparison, so the tightening would also damage the
migration's own evidence. **What would change the decision:** taking it as a
separate change once the shape is in place, which §10 Q7 now names as the live
form of that question.

## 7. Consequences and risks

| # | Consequence | Class | Handling |
|---|---|---|---|
| C-1 | **Every WF3 output path moves.** Seven artifact paths (§5.3.2), plus per-run log and benchmark part names under `3.12_*/`, `3.14_*/` | Certain | §8; the baseline manifest is re-recorded **before** the first implementation commit |
| C-2 | **`check_baseline.py check` fails by construction** until re-recorded. A comparison gate cannot be applied retrospectively | Certain | §8 step 0, verbatim from the R12 lookup design's R1 |
| C-3 | **The fixture-dependent test layer cannot gate this in a worktree** — it skips rather than fails, and this is a tree-shape change | Certain | Implementation gating happens in the primary checkout on a seeded fixture; §9 marks which gates are worktree-runnable |
| C-4 | A **new grouping** introduced later can change `W` and rename every stage-2 file | Low likelihood, bounded | §5.5.2; detected loudly by the digest guard, never silent. A2 is the standing alternative if it proves common |
| C-5 | **`derived_from` is argued, not measured.** The composition of P2's (i-c) and (iv) was not run | Open until **P2b**, then GF-1 | v1 gated this only after the migration's point of no cheap return, which `risk-3` filed: a failed GF-1 after step 1 is a redesign, not a revert (§4 — "the seam must move"). **P2b** (§5.2.2) measures the composition on P2's existing standalone harness, in three states, **before** §8.2 step 1. GF-1 stays the in-workflow gate and is a **fresh-project** DAG build; a seeded dry-run is a measured false negative here |
| C-6 | **Reading `run_id` as an integer silently breaks every join** — the same trap WG-2 documents for `st_id` | Recurring | Stated in §5.1.2 and in each replacement contract clause; `validate_*` reads as text and asserts the width |
| C-7 | Out-of-repo consumers (CST-API, frontend, `csthelpers`, `docs/notebooks/Climate Stress Test.ipynb`) re-implement HM-7 from its text and **will break** on the four-column shape | Certain, out of scope to fix | HM-7's replacement is written to be implementable standalone; the change is announced in the migration note. Per the standing ruling, no decision here is gated on whether they consume an artifact by path or name |
| C-8 | **`_member_span`'s banner loses its rectangle.** A flat run list has no `rlz a-b \| st c-d` to print | Cosmetic | §5.6; a first–last id span replaces it and the `(partial)` caveat becomes vacuous |
| C-9 | The refusal in §5.4.4 could, on a future config, stop a run that previously produced a (poor) number | Intended, and **reachable** | `blocks_per_return_period = 1.0` with a 10-block identifiability floor refuses no shipped config (§5.4.4's table states this plainly rather than claiming reachability the design does not have) but **does** refuse a 1-realization 9-year config, which is one edit from `snake_config_rapid`. Documented as a user-visible consequence; falsified synthetically by GF-15, not by reachability |
| C-10 | **Nine contract clauses change, not three.** The intake undercounts (§5.7b) | Certain | The complete list is §5.7b's table; D7's atomicity obligation covers all nine |

| C-11 | **A stage-1 artifact's content depends on a stage-3 declaration.** The minter evaluates the declared groupings over scenario rows to order and count bundles, so `scenario_table.csv`'s `run_id` strings are a function of the metric set | Certain, structural | Stated accurately in §5.5.2 rather than minimised as v1 did; rule 3.09 gains a rerun trigger for it (`arch-7`); the digest no longer covers `run_id` spellings so it cannot misdiagnose the resulting refusal; A3 is the standing alternative that removes it |
| C-12 | **Class C gains rows.** R-2 stores per-realization values for `q_wettest_month_mean` / `q_driest_month_mean`, so the results file changes row count as well as column set | Certain, ruled | §5.4.2; GF-9's instrument checks the three cases separately, and the Class-C case checks that the mean over `rlz` reproduces the old pooled value |
| C-13 | **Admitting a second family requires ADDING a producer rule**, not editing one. Goal 1's v1 wording ("no edit to stage 2") was unachievable by any design | Certain | §2.1 Goal 1 reworded; CFS §4 prices it — one core column, one rule, one WG-4 clause, one falsifier |
| C-14 | **Two refusals can address one experiment.** The experiment freeze and the digest guard | Low | §5.5.3a states the precedence and gives them one activation condition; a user meets one message per cause |

**The risk this design is least able to retire — and it is smaller than v1 said.**
E18 was the motivating premise and v1 carried it as *"a hypothesis with no artifact
to test against"*, naming it the design's weakest point. **R-6 required it settled
before G2, and CFS settles it: E18 is CONFIRMED** (CFS §3), on the join-semantics
and pairing grounds rather than on raggedness. What remains open is narrower and
should be read as such:

- **Confirmed:** a GCM-downscaled or user-supplied set is not expressible as
  `(rlz, st)` without a dangling `st_id` foreign key or a false pairing claim.
  Cheap to check, and checked.
- **Still hypothetical:** that anyone will *build* such a family. CFS takes no
  position on it and the intake makes it a non-goal. If nobody ever does, the
  benefit reduces to the three measured defects (E1's regex, E9's two coexisting
  bundlings, E8's sentinel) plus the two this revision adds to the list — the
  Class-C grain error R-2 corrects and the silent Class-C drop under
  `run_historical: false` (`domain-6`) — which A10 argues are worth fixing anyway.
  That is a materially better floor than v1's, because two of the five are wrong
  behaviour rather than wrong structure.

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
| **1** | **One reference-atomic change** landing everything in § 8.2a's inventory | `naming.md` §7 and `AGENTS.md`'s *"grep the old spelling and fix every live reference in the same commit"*. A tree-shape change that leaves a live document naming a dead path is the state neither scheme can read |
| **2** | **`build_r09_path_map` stays frozen** — it is a historical map, not a live inventory | Stated in the gate-materialization table and preserved here so the implementer does not "helpfully" extend it |
| **3** | **Re-record `dev/baseline/manifest.json`** after the change, from the same config and checkout, **and run the §9 crosswalk comparator once against step 0's recording before re-recording** | The manifest's targets are the new paths. `check_baseline.py check` cannot bridge this discontinuity — its comparator fails structurally on the column-set and row-count change (`domain-5`) — so the crosswalk is what carries GF-9's three claims across it, and it must run while step 0's recording is still the reference |

### 8.2a The commit inventory — complete, and what v1 left out

**`arch-6` is accepted: v1's inventory was short, and an atomic-rename plan with a
short inventory lands broken** — the implementer discovers the missing entries one
gate at a time, on a commit that was supposed to be self-consistent.

**Carried from v1:** `shared/scenario_index.py` (new), `shared/scenario_families.py`
(new), the six rule edits in `run_stress_test.smk`, the reducer rewrite
(`experiment/export_wflow_results.py`), `shared/interchange_contracts.py`
(WG-2/4/5/6, HM-2/4/5/6b/7 **and `validate_wg5`'s entry selector** — §5.8),
`dev/reference/contracts/weather-generator-seam.md`,
`dev/reference/contracts/hydrological-model-seam.md`, `dev/reference/naming.md`
§4 + §7, `dev/reference/workflows/rule-index.md`,
`dev/scripts/semantic_tree_diff.py` (`build_project_tree_rules`), ADR 0009, the
migration note, and every affected test.

**Added by this revision:**

| target | what changes | why v1 missed it |
|---|---|---|
| `blueearth_cst/shared/indicator_tables.py` | `Q_METRIC_SUFFIXES`' class letters become grain records; `METRIC_CLASSES` (`:245`) and `metric_grain` (`:274-296`) change **semantically** for Class C under R-2 | v1 treated the grain declaration as new; it refines an existing surface (§5.4.1) |
| `dev/reference/indicator-glossary.md` | documents per-metric grain as `rlz_id = 0` (`:101-104`) and the two key columns (`:154-155`); **pinned row-for-row against the code by `tests/test_indicator_glossary.py`** | `arch-6` |
| `blueearth_cst/shared/surface_axes.py` | `read_indicators` reads an indicator table with `dtype={"st_id": str}` (`:295-305`) — a function that cannot survive the four-column header, though §5.9 calls the module "the reference implementation" | `arch-6` |
| `dev/scripts/check_baseline.py` | `TARGETS` is a **hardcoded** list (`:237`); `_indicator_key_columns` (`:788`) and the `st_id`-is-text note (`:771`) encode the old header; and GF-9's comparison instrument lands here (§9) | `arch-6` + `domain-5` |
| `dev/baseline/indicator_ref/74ed83c06b2e7e6c.csv` | a **tracked** reference table carrying the old columns; regenerated | `arch-6` |
| `docs/notebooks/Climate Stress Test.ipynb` | **in-repo**, so C-7's "out-of-repo consumers are out of scope" disposition does not cover it | `arch-6` |

**One v1 claim corrected.** §5.4.3 said `unit_index.csv` becoming a
baseline-fingerprinted `rule all` target is "free **now**". It is not: the
manifest's target set is seven explicitly declared paths and `TARGETS` is
hardcoded, so covering the new file **requires adding one row to
`check_baseline.TARGETS`**. Cheap, but an edit rather than a consequence of
re-recording.

### 8.2b "Atomic" is two requirements, and only one of them forces one commit

**`risk-11` is accepted.** v1 presented single-commit granularity as forced by D7
and then derived its rollback story from it. The two requirements are different:

- **Reference atomicity** — no state in which a live document names a path that no
  longer exists. This is what `naming.md` §7 and `AGENTS.md` require, and it is
  satisfied by a **branch squashed at merge**, or by any sequence in which each
  commit is internally consistent. It does not require one commit.
- **Tree-shape atomicity** — `tree-check` reporting undeclared paths on every run
  between the rename and the inventory update. Also satisfied by the above.

**Decision:** the requirement is **reference atomicity**, and the change may land
as a branch squashed at merge. That buys reviewability and bisectability on the
largest change in the milestone — the reducer rewrite, the rule edits and the
contract text can be reviewed separately — at no cost to either obligation. §8.2
step 1 is one *landing*, not necessarily one *commit*.

### 8.3 Rollback

**Two different things are being rolled back, and v1 presented one revert as the
whole story** (`risk-11`).

1. **The code.** `git revert` of the squashed landing, plus
   `git checkout <pre-change-sha> -- dev/baseline/manifest.json` restoring step
   0's recording. This part is genuinely one operation.
2. **The project tree.** A revert restores no project tree, and no revert can:
   see the deletion remedy below.
3. **A structural refutation is not revertible in this sense at all.** If GF-1
   fails after the landing, §4 says the seam must move — that is a redesign, and
   the rollback machinery here is written for a defect. **P2b (§5.2.2) exists to
   make this branch unreachable**, by measuring the composition before the
   landing rather than after it.

- **No run output is tracked.** Outputs live under `project_dir`, which is outside
  the repository tree (the untracked `test_case/test_local` being a dev-only
  exemption), so a revert leaves a project folder holding new-scheme files that
  the reverted code will not recognise. **The documented remedy is to delete the
  experiment folder's `climate/`, `hydrology/` and `results/` subtrees AND
  `config/.scenario_table.sha256`, then re-run** — not to rename files back. A
  half-renamed tree is the one state neither scheme can read, and a scripted
  un-rename would be a second migration to test. **The sidecar is in this list
  because `arch-8` found it missing from both v1 lists**, which left the
  documented remedy unable to clear the refusal it was documented for.
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
| **GF-1** | The `derived_from`-driven alternation constraint keeps 3.11/3.12 unambiguous **on a fresh project** | **[argued]** — its two ingredients are measured (P2 i-c, iv); the composition is measured by **P2b before the landing** (§5.2.2), and GF-1 is the in-workflow confirmation, never the first observation | A `CyclicGraphException` in `perturb_climate_realization`, or any exception other than a clean `MissingInputException` when an upstream input is absent | `pixi run pytest tests/test_guard_invalidation.py -x -q` (fresh-project builder), extended with a case asserting the constraint's alternation set equals `DERIVED_FROM`'s keys |
| **GF-2** | An **empty** `DERIVED_FROM` yields an alternation matching **nothing**, not everything | **[measured by P2b]** — this is P2b's third state (§5.2.2), promoted out of `[assumed]` because it is also the CFS-variant case: both candidate families have an empty `derived_from` column | Rule 3.12 becoming eligible for a root run's output on a family with no derived rows | A unit test building a two-rule Snakefile with `wildcard_constraints: run_id=""` and asserting `MissingRuleException`, plus a refusal in `scenario_index` if `DERIVED_FROM` is empty *and* rule 3.12 is reachable |
| **GF-3** | The scenario table is derivable at parse time with **no checkpoint** | **[measured]** — P1 (a) and the config-derived trace | Any WF3 invocation requiring two passes to build a complete DAG, or a `checkpoint` appearing in `run_stress_test.smk` | `pixi run snakemake all -c1 -s run_stress_test.smk --configfile test_case/snake_config_baseline.yml --dry-run` on a fresh project; job count equals `len(EVALUATED_IDS)`-derived expectation, exit 0, one invocation |
| **GF-4** | `run_historical: false` omits the baseline's **wflow run** while still building its **series** | [argued] — **the mechanism is a filter on `_k_members`, not pull semantics** (`arch-5`, §5.1.5); rule 3.15's outputs are static lists (`:1226-1231`) | `run_<baseline>.csv` appearing in **any batch rule's declared outputs** under `run_historical: false` — not merely in the job list, which is the weaker check v1 specified — or `run_<baseline>.nc` **not** appearing | Two fresh-project dry-runs differing only in `run_historical`; diff the job lists **and** assert over each generated batch rule's `output.csvs` |
| **GF-5** | An empty scenario set **refuses**; a guarded read never silently empties the DAG | [argued] — the hazard is **measured** (P1 b2: exit 0, zero jobs) | Any WF3 invocation exiting 0 with zero scenario jobs | A test invoking `scenario_index.mint` with a zero-row table and asserting `EmptyScenarioSetError`; plus a static gate asserting that no parse-time table read in any `.smk` is guarded by a fallback yielding an **empty id set**. Narrowly worded on purpose: `analyze_projections.smk:468-471` guards a parse-time JSON read with `else None` and its consumer handles `None` explicitly, which is correct and must not be flagged — the defect is the silent empty, not the guard |
| **GF-6** | Editing a grain declaration re-fires rule 3.16 — **two cases, stated separately** (`risk-8`): (a) a metric names a different `bundle_by`; (b) a grouping function's BODY changes what it computes | [assumed] — **P4 is unexecuted**, and the `ancient()`/no-`params:` trap is live here (rule 3.09's own comment records it). Case (a) is closed by the declaration travelling through `params:`; case (b) is closed by the **grouping-registry source digest** in the same `params:`, and v1 closed only (a) while wording the gate so it could not tell them apart | Either case leaving `q_indicators.csv` untouched on the next invocation | Run WF3 to completion on `test_rapid`; **(a)** repoint a metric's `bundle_by` and assert 3.16 is scheduled; **(b)** change `same_design_point`'s body without renaming it and assert 3.16 is scheduled |
| **GF-7** | hydromt resolves the per-run catalog under the new entry key | [argued] — **P3 is unexecuted** | Rule 3.14 failing to find its source, or reading the wrong entry | One real rule-3.14 execution on `test_rapid` |
| **GF-8** | `pixi run tree-check` classifies the renamed tree with no undeclared paths | [assumed] — **P5 is unexecuted**; the inventory is code, not a snapshot | `tree-check` reporting undeclared paths after a complete run | `pixi run tree-check` against a completed `test_local` run, post-change |
| **GF-9** | **Three separate claims, not one** (see § GF-9's instrument below): (a) every Class-A and Class-B value is unchanged; (b) Class C's new per-run values average, over `rlz`, to the old pooled value; (c) no row is lost | [argued] — nothing in §§5.1–5.6 changes an arithmetic path, and R-2's per-run decomposition is exact for equal-length realizations | Any (a) value differing beyond `INDICATOR_RTOL`; any (b) realization-mean differing beyond it; any (c) old row with no new counterpart | The crosswalk comparator specified below, run once against step 0's recording. **`check_baseline.py check` alone cannot execute this** and must not be cited as if it could |
| **GF-10** | Every `unit_id` in every results table resolves in `unit_index.csv`, and no unit carries two grains | [argued] — it is the validator's own assertion | A results row whose `unit_id` is absent from the index, or a `unit_id` with two `grain` values | `pixi run pytest tests/test_interchange_contracts.py -k hm7`, plus synthetic pass/fail pairs as the existing validators use |
| **GF-11** | Stage-2 rules make **no decision** on a family-block column (§5.2.1a's single normative rule) | [argued] | Any rule declared `STAGE == 2` whose body names a `FAMILY_COLUMNS` member outside a `family_payload(...)` call | **An AST test over named rule bodies**, not over modules: parse `run_stress_test.smk`, take the rules the module-level `STAGE` mapping declares stage 2, and assert no bare `FAMILY_COLUMNS[*]` name appears in each body. v1's instrument — "no stage-2 module mentions one" — **had no referent**, because §2.2 makes splitting the `.smk` a binding non-goal, so every stage lives in one file (`arch-1`) |
| **GF-12** | A changed scenario table re-run in place is **refused by SOMETHING**, and the design knows which | [argued] | A second run with a different table completing and overwriting outputs | **v1's falsifier could not show the digest was load-bearing** (`risk-1`): "change `realizations_num`, assert a refusal" is satisfied by a tree in which `check_not_frozen` would have refused anyway. Two cases now: **(a)** change `realizations_num` after a successful run and assert the **experiment freeze** refuses, with its message — the stochastic family's real guard; **(b)** hold the config fixed, edit a **supplied** scenario table on disk after a successful run, and assert the **digest** refuses. (b) is the digest's only novel coverage and is the one that must pass for §5.5.3 to be worth shipping |
| **GF-13** | The baseline design point carries `return_level_*` rows under `run_historical: true` — the empty `st_id` is a grouping key and nothing drops it (`risk-5`) | [argued] — the normative clause is §5.1.2's; the hazard is `pandas.groupby`'s default null-key drop | A results table with no `return_level_max` row for the baseline design point's unit, or a unit index with no bundle for the empty key | A unit test grouping a synthetic scenario table containing an empty-`st_id` row and asserting the bundle is minted **and** carries rows; plus a `test_rapid` run asserting both return-level metrics resolve to a baseline unit |
| **GF-14** | A metric declaring a `reference` whose unit is `evaluated: false` **refuses at parse time**, and no metric is silently dropped (`domain-6`) | [argued] — today's behaviour is a measured silent drop (`export_wflow_results.py:362`, two metrics vanish under `run_historical: false` with no log line) | A `run_historical: false` invocation completing with `q_wettest_month_mean` absent from the tables and no refusal | Build the DAG on `test_rapid` with `run_historical: false` and assert `scenario_index` raises, naming the metric, the reference grouping and the setting |
| **GF-15** | The estimator precondition **refuses** below `required` blocks, naming five facts (`domain-4`) | [argued] — v1 shipped this mechanism with no falsifier at all, in a design whose D8 requires one | The reducer fitting, or emitting a row, on a bundle with `required - 1` blocks; or a message omitting metric, unit, return period, required or actual | A unit test invoking the reducer on a synthetic bundle one block below `required`, asserting the refusal and each of the five named facts. **Synthetic on purpose:** §5.4.4's table states that no shipped config reaches the threshold, so reachability is not claimed |
| **GF-16** | Editing a grain declaration re-fires rule **3.09** (`arch-7`) | [assumed] — same `ancient()` trap as GF-6, never asked of 3.09 in v1 | A declaration edit that changes the bundle count leaving `scenario_table.csv` untouched on the next invocation | Run WF3 on `test_rapid`; add a metric with a new `bundle_by`; `--dry-run` and assert 3.09 is scheduled |
| **GF-17** | The digest guard does **not** fire on a failed run, on a width change, or on a `FAMILY_COLUMNS` rename (`risk-1`, `arch-7`) | [argued] — the guard is keyed to `has_run_successfully` and digests semantic content only (§5.5.3) | A refusal after a run that died before the merged log was written; or a refusal whose cause is a width or a registry rename | Three cases on `test_rapid`: kill WF3 at 3.12 and re-run with an edited config (must proceed, or be refused by the **freeze** with the freeze's message, never by the digest); add a grouping that crosses a power of ten (must not refuse); rename a family-block column (must not refuse) |
| **GF-18** | A family declaring `paired_across_design_points` with an all-empty `derived_from` is refused (§5.1.2, from CFS §4) | [argued] | Such a table building a DAG | A unit test over `scenario_index` with a synthetic registry entry |

### GF-9's instrument — the crosswalk comparator (`domain-5`)

**v1's GF-9 was not executable, and this is the replacement.** `domain-5` is
accepted in full, and the risk lens independently re-derived it. The comparator
`check_baseline.py` uses keys each row on **every non-value column**
(`_indicator_key_columns`, `dev/scripts/check_baseline.py:788`) and issues a
**structural FAIL** on a column-set or column-order mismatch and on an unequal
row-key set *before any numeric comparison* (`:790-797`, `:861-874`). [cited — I
read both functions] This design changes the columns from
`metric, location, st_id, rlz_id, value` to `metric, location, unit_id, value`
and, under R-2, changes the row count as well — so the comparator returns a
structural failure **unconditionally**. It cannot report "a difference beyond a
path rename" because it cannot compare the two tables at all. §8.2's step 3 then
re-records from the post-change code, leaving the only surviving comparison as the
new recording against itself.

**So the migration's central safety claim had no working instrument, and the
design used that claim to justify both a single landing and (in v1) a
fixture-derived threshold.** Honest statement of the situation: **this change
cannot be gated by `check_baseline.py check` in its current form.** What replaces
it is a one-off comparison written for this migration, run once, and discarded:

**`dev/scripts/` one-off — `compare_indicators_across_rename.py`** (dev-only,
never on a run path, deleted after the milestone seals):

1. **Build the crosswalk.** From the post-change `scenario_table.csv` join
   `unit_index.csv`: `(rlz, st_id) → run_id → unit_id`. This is well-defined
   **only because §5.1.2 pins the row order** (`risk-7`); against an unspecified
   order the crosswalk cannot be written, which is why the two findings are one
   piece of work.
2. **Case A — per-run metrics (Class A).** Old key `(metric, location, st_id,
   rlz_id)` maps 1:1 onto new `(metric, location, unit_id)` through the crosswalk.
   Compare `value` under `INDICATOR_RTOL` with the existing group-relative ATOL.
   **Expect exact equality of the key sets.**
3. **Case B — pooled metrics (Class B).** Old key `(metric, location, st_id,
   POOLED_REALIZATION)` maps 1:1 onto the **bundle** unit for that design point.
   Same tolerance. The baseline design point's bundle is keyed by the empty
   `st_id` and must be present (GF-13).
4. **Case C — the metrics R-2 moved.** Old pooled value vs the **mean over `rlz`
   of the new per-run values** at the same design point and location. This is a
   real check rather than a tautology: R-1/R-2's entire justification is that the
   per-run values average back to the pooled value exactly for equal-length
   realizations on one calendar, so a failure here falsifies the ruling's premise,
   not just the implementation.
5. **Case D — coverage.** Every old row is accounted for by exactly one of A, B or
   C, and every new row has an old counterpart or is a Class-C sibling. A dropped
   row is a failure, not a shorter table.

**Where this leaves the standing gate.** `check_baseline.py` is still re-recorded
at §8.2 steps 0 and 3 and remains the gate for *subsequent* changes; the crosswalk
is what bridges the one discontinuity this migration creates. `TARGETS`,
`_indicator_key_columns` and the `st_id`-is-text note change with the header
(§8.2a). **§8.2 must say this**, rather than carrying a claim its cited command
cannot evaluate.

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
| **Q1** | ~~Is `derived_from` genuinely family-blind?~~ **CLOSED** by CFS | The paper schema v1 named as the closing instrument was written (R-6). Both candidate variants populate `derived_from` as the empty set, which is what §5.2.2 predicts for a family that supplies its own forcing, and neither needs a baseline concept to do it. The mechanical half is P2b + GF-1. What CFS did **not** close is whether such a family is ever built, which is a milestone question, not a design one |
| **Q2** | Two column names or one (§5.5.1, A1)? | Settled here as two, on a type-declaration argument. Reversible at zero cost **only before implementation**; afterwards it is a baseline re-record. Flagged because it is the one place this design refines W4's "settle it once" rather than following it literally |
| **Q3** | Does the width coupling (§5.5.2 / C-4) matter in practice? | Needs a frequency observation this repository cannot yet supply: how often a *new grouping* is introduced. If it turns out to be common, A2 is the prepared answer |
| **Q4** | Scope gap 5 — the baseline relation | **Deferred by W3.** This design keeps it open (§5.3.5) and specifies only the mechanism that replaces the hardcoded `0`. Closed when a second family exists to test comparability against |
| **Q5** | Do the eight surviving `t2608082036` references get repointed or abandoned? | §5.5.5 recommends splitting them: identity references here, execution-model references to a successor item. Needs an owner ruling, and it is a roadmap edit, which is a derived artifact |
| **Q6** | Does the intake's undercount of contract clauses (three vs nine, §5.7b) change the milestone's size estimate? | Six of the nine are one-line path substitutions; the substantive ones are WG-2, WG-5 and HM-7, which the intake did identify. Raised for the gate rather than resolved here |
| **Q7** | Should `blocks_per_return_period` be raised from `1.0` toward the stricter `2.0` reading? | **The shape and a value are settled here, not deferred** — R-4 made that a milestone precondition, and §5.4.4 picks `1.0` with a 10-block identifiability floor and states exactly which configs each refuses. What remains is a *tightening*, which is a clean separate decision now that the declaration references the return period: A12 records that `2.0` refuses `snake_config_rapid` and why that cost should not ride on a rename. Closed by a methodological ruling |
| **Q8** | When `forcing_uri` returns to the core, is A11's shape right? | §5.1.2 removes it; CFS §4 prices its return at one core column, one rule 3.11b, one WG-4 clause and one falsifier, and argues it is family-blind so the seam survives. Closed by the second-family milestone, which A11 specifies |
| **Q9** | Should Class-B fit uncertainty be admitted as companion metrics? | §5.4.4a rules the position — admissible point estimates, no interval — and records that W2's free `metric` vocabulary leaves the route open at no schema cost. Closed by a decision that a surface reader needs the interval, which is a use-case question this repository cannot answer |

**Two things in the input set that a reviewer should know are contradictory**, both
reported to the driver rather than fixed here, since the artifacts are frozen or
derived: the intake's **E13** attributes the member naming pattern to WG-2 when it
is WG-4 (§5.7b), and the **HM-7 contract document is stale against its own
validator** — seven columns pinned, five asserted (§5.9).

## 11. Revision log

| version | date | author | change |
|---|---|---|---|
| v1 | 2026-09-07 | author (stage 1, `design-review-loop` run `wf3-simulation-identity`) | First draft. Authored from the frozen intake (revision 2), the executed P1/P2 probe results, the `wf3-experiment-v2` review record, and `design-v4.md` §3.1/§5.1 at tag `archive/wf3-experiment-v2`. Departures from the working direction, and findings against the input set, are listed below |
| **v2** | **2026-09-07** | author (stage 3, revision r1) | **Revision against 31 internal findings across three lenses (1 blocking, 19 major, 11 minor) and owner rulings R-1 .. R-6.** Every finding is dispositioned in `ledger.md`. Summary below |

**What changed between v1 and v2, and why.** Grouped by what moved rather than by
finding id; the per-id record is `ledger.md`.

| # | Change | Driver | Why it mattered |
|---|---|---|---|
| 1 | **Class C becomes `grain: run` with a required `reference`** (§5.4.1a) | R-1, R-2 / `domain-1` (blocking) | v1's justification for pooling it described a mechanism absent from the code: the month is fixed once, globally, from the baseline (`export_wflow_results.py:361-364`), and the value is linear in years, so a per-run grain exists and is finer. v1 would have pinned a false estimator claim into HM-7's normative surface and destroyed per-realization spread for two metrics permanently |
| 2 | **The paired-sampling property is declared and checked** (§5.1.2, §5.2.2) | R-3 / `domain-2` | `derived_from` carries common random numbers, so contrasts between design points are paired. A family-blind seam admits an unpaired family; without a declared marker two surfaces would look alike and support different inference. CFS added the consistency refusal R-3 does not state |
| 3 | **`min_blocks` becomes `blocks_per_return_period`, and the ratio is PICKED** (§5.4.4) | R-4 / `domain-3`, `domain-4` | v1's floor was absolute in shape (so blind to the extrapolation) and fixture-derived in value (so unable to fire). `1.0` with a 10-block identifiability floor, with the refused/passed configs tabulated and A12 recording the stricter reading's cost. GF-15 is the falsifier v1 had none of |
| 4 | **GF-9 gets a working instrument** (§9) | `domain-5` | The baseline comparator keys rows on every non-value column and fails structurally on a column-set change, so "no number moves" was unfalsifiable — and R-2 made it worse by changing the row count too. Replaced by a three-case crosswalk comparison, with the Class-C case checking R-2's own averaging premise |
| 5 | **The family-blindness rule is stated ONCE, with one exception, and gets a constructible instrument** (§5.2.1a) | `arch-1` | Three statements at three scopes, the strictest falsified by the design's own rule table, and a falsifier with no referent in a single-file workflow. Now: one sentence, `family_payload()` as the only permitted reader, and an AST test over rules declared stage 2 |
| 6 | **`forcing_uri` is removed from the core** (§5.1.2) | `arch-2`, `risk-2` | A normative seam column with no producer, consumer, migration row or gate. Implementing it would ship an ingest path the non-goal forbids; CFS §4 prices its return so the removal is accountable |
| 7 | **The WG-5 replacement is fixed in both halves** (§5.8) | `arch-3`, `risk-4` | `validate_wg5` **selects** entries by `k.startswith("rlz_")` and errors when there are none (`interchange_contracts.py:554-560`), so v1's "untouched" claim was false; and the cross-artifact invariant was unsatisfiable under `run_historical: false`. Both, per the index's "both or neither" |
| 8 | **The stale-lookup guard is reconciled with the one already here** (§5.5.3a) | `risk-1`, `arch-8` | `check_not_frozen` (`write_experiment_config.py:113-140`) already refuses an in-place config change once results exist. The digest is keyed to the same success marker, its justification narrowed to the supplied-table case, its digest narrowed to semantic content, and the sidecar added to both deletion lists |
| 9 | **`evaluated`'s mechanism is corrected** (§5.1.5, §5.6) | `arch-5` | Rule 3.15's outputs are static lists, so pull semantics exclude nothing; `_k_members` is built from `EVALUATED_IDS`. Read literally, v1 would have simulated the unevaluated baseline and broken output-neutrality on the one config it claimed to preserve |
| 10 | **A3 is re-argued on merits** (§6) | R-5 / `risk-6` | W4 is direction, not a ruling, and v1 deferred to it in §6 while refining it in §5.5.1. A3 is rejected on the parsed-id and reserved-range arguments, with W2's own "distinguishable on sight" clause answered rather than omitted |
| 11 | **The design's central unmeasured claim is measured BEFORE the landing** (P2b, §5.2.2) | `risk-3` | GF-1 could only run after the migration's point of no cheap return, and a failure there is a redesign, not a revert |
| 12 | **E18 is settled** (CFS, §1, §7) | R-6 / `domain-10`, `risk-3` | Confirmed, on join-semantics and pairing grounds rather than raggedness — which is a stronger argument than the intake's and reaches the factorial GCM case the intake's does not |
| 13 | **Epistemic labels are honest** (front matter) | `risk-9` | ~12 code reads were labelled `[measured]`. A fourth label, `[cited]`, and the relabel |
| 14 | Rule 3.09 gains a rerun trigger; the width/grain coupling is stated accurately; the digest stops misdiagnosing it | `arch-7` | A stage-3 edit silently invalidating a stage-1 artifact, then reported as a changed scenario set |
| 15 | HM-7 regains its dropped assertions; `unit_id`'s width is discovered, not computed | `arch-4`, `arch-10` | A dropped design-point completeness check turns a loud failure into a shorter table; a contract cannot pin a value it does not define |
| 16 | Four HM clauses written out; the commit inventory extended by six targets; "atomic" resolved to reference atomicity | `risk-10`, `arch-6`, `risk-11` | Sketch where the success criterion says normative text; an inventory short by six live references; and one conflated requirement forcing an unreviewably large single commit |
| 17 | Row order pinned; completeness asserted against configured axes; the empty `st_id` declared a valid grouping key; the `reference` unit's evaluation precondition and per-table resolution stated; `temp()` restored on 3.11; GF-6 split into two cases | `risk-7`, `domain-9`, `risk-5`, `domain-6`, `domain-8`, `arch-9`, `risk-8` | The remaining specification gaps, two of which (`risk-5`, `domain-6`) reach wrong or missing rows rather than wrong prose |
| 18 | The fit-uncertainty position is argued as a position | `domain-7` | v1 answered a comparability question with an admissibility gate without saying it was doing so |

**One finding is DEFERRED rather than fixed**, and it is marked as such in the
ledger rather than dressed as an acceptance. `domain-7` — no fit uncertainty
crosses the stage-2 → stage-3 seam for the pooled GEV — is **correct and is not
closed here.** §5.4.4a states the position and shows the route that stays open
(companion metric names, no schema change), which is what the finding's own
suggested fix offers as an alternative; but the substantive gap the finding names
— a surface reader cannot tell whether a gradient exceeds the estimator's noise —
remains open. Trigger: a stated requirement to read the surface for threshold
crossings *with* the interval, at which point Q9 becomes a metric-declaration and
reducer change and no contract migration.

**Departures from W1–W4, stated once and in one place:**

| direction | disposition |
|---|---|
| **W1** — pooled and per-run values share one results file | **Followed.** One `<token>_indicators.csv` per variable carries both grains, distinguished by `unit_id` and explained by `unit_index.csv` |
| **W2** — the results file carries results plus ONE index column, four columns, no blanks and no grain column | **Followed exactly**, at `metric, location, unit_id, value`. W2's three safety conditions are discharged in §5.4.2, §5.4.3 (invariant 1) and §5.9 ("join before you group") |
| **W3** — the baseline relation stays open | **Followed, and R-1 PARAMETERIZES it rather than settling it.** §5.3.5 keeps it open on both required counts: no reserved baseline id, and the one hardcoded site made indirect without settling its semantics. R-1 makes Class C's `reference` required and keeps it a **per-family registered grouping**, so the baseline concept lives in `scenario_families.py` and stays a family's own declaration. Two of P2's four working mechanisms are rejected in §6 specifically because they would have foreclosed it |
| **W4** — a plain zero-padded sequential number, nothing embedded; one mixed number space; the column NAME and the stale-lookup guard left open | **Followed on form and on the single sequence** (§5.5.2), **refined on the column name** (§5.5.1), and — under **R-5** — no longer *deferred to*. W4 is direction, not a ruling. v1 refined it in §5.5.1 while treating it as dispositive in §6's A3 rejection, which was incoherent whichever reading of W4 won; §6's A3 entry is now argued on merits and reaches the same conclusion for different reasons. The stale-lookup guard is settled jointly with the guard already in the repository (§5.5.3a). The alternatives are A1 (one name) and A3 (two sequences) |

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
   and the corresponding claims are labelled `[assumed]` rather than argued. **P2b
   is added by this revision** (§5.2.2) and is a milestone precondition rather
   than a gate.
6. **The intake argues E18 from raggedness, which does not reach the motivating
   case.** A GCM-downscaled set can be numerically factorial; E18 survives on the
   `st_id`-foreign-key and pairing grounds instead (CFS §3, §1). Reported because
   the intake is frozen; the design no longer inherits the weaker argument.
7. **Grain was already a declared surface, and v1 did not say so.** `METRIC_CLASSES`
   (`indicator_tables.py:245`), the class letters in `Q_METRIC_SUFFIXES`
   (`:198-215`) and `metric_grain` (`:274-296`) already declare per-metric grain,
   and `validate_hm7` already calls it (`interchange_contracts.py:940`). §5.4.1 is
   a refinement of that surface, not a new mechanism — which also puts three more
   targets in the migration inventory. **Not filed by any of the 31 findings**;
   found while checking `domain-1` against the code.
8. **`validate_wg5_catalog_grid` bakes `ST_START = 0` into its expected key set**
   (`interchange_contracts.py:1327-1331`), so it is latently wrong under
   `run_historical: false` today. v1 would have pinned the assumption as normative
   text; §5.8 removes it instead. Pre-existing, and independent of this design.
