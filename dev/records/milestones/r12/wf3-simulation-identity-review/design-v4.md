# Scenario generation and system behavior simulation: WF3 successor design

> **design-v4 — proposed revision; not reviewer-approved.** Run `wf3-simulation-identity`, milestone
> R12. Genre: software-system workflow specification with methodological
> decisions. Date: **2026-09-09**. Code baseline:
> `4e26c2394dd002f7dfb61b1943e002866c6ca4bf`.
> Revision source checkout recorded by the v3 domain reviewer:
> `7e4f5031ea2354b523b64fec5648072fe517e3dd`; this is provenance for the
> authoring/review state and does not replace the source-code baseline.
>
> **Scope authority.** The frozen
> `dev/milestones/r12/simulation-identity-intake.md`; owner rulings R-1 through
> R-6 in `status.md`; and approved addendum v2 in
> `scope-expansion-2026-09-09.md`; and the G1-v3 correction ruling dated
> 2026-09-09. This revision supersedes `design-v3.md` as the proposed design.
> It does not alter the intake, v1/v2/v3, reviews, ledger history,
> probes, or status record.
>
> **Review state.** Author self-review is complete.
> The Astra domain review of v3 required revision; it did not review or approve
> v4. Scientific evaluation and clean-room external review of this revision are
> still pending. No implementation or scientific run has been performed for v4.
>
> **Lifecycle.** Temporary while the design-review run is open. If accepted, the
> maintained-current destination is
> `dev/milestones/r12/wf3-simulation-identity-design.md`; its revision history is
> append-only. Prior versions and review artifacts remain historical evidence.
>
> **Normative-body budget.** Comparable accepted designs range from 1,041 lines
> (`r14/config-shape-design.md`) through 1,640 (`r05/climate-experiment-design.md`)
> to 2,946 (`r12/stress-test-lookup-design.md`). This revision targets
> **1,200–2,100 lines**. V4 uses the upper end because the G1-v3 package adds
> scientific validation and provenance contracts that must remain self-contained.
> It retains schemas, invariants, formulas, migration
> mappings, and falsifiers while leaving round-by-round argument in v2 and the
> review ledger.

Four evidence labels are used where they affect a decision:

- **[measured]** — an executed probe recorded in P1/P2 or P3/P4/P5;
- **[cited]** — verified by reading the named repository artifact at the code
  baseline above;
- **[argued]** — a conclusion from cited or measured evidence;
- **[proposed, untested]** — new design content that implementation has not yet
  exercised.

Unlabelled text is normative connective text. Proposed APIs and filenames in
this document do not exist yet.

## 1. Problem and request type

**Request type: improve.** The current WF3 combines three different contracts
inside `run_stress_test.smk`:

1. define and generate the climate scenario set;
2. prepare Wflow forcing and simulate one response per scenario; and
3. reduce retained responses into metrics for one case or a metric bundle.

The fusion is expressed through `(rlz, st_id)` in paths. The reducer reconstructs
those fields by applying `_MEMBER_IN_STEM` to each Wflow CSV filename, so a
spelling acts as an undeclared interface. Class A, B, and C metrics then use
different grains, with pooled rows represented by `POOLED_REALIZATION = 0` in a
column otherwise holding a realization id. [cited: `export_wflow_results.py`,
`indicator_tables.py`]

E18, the premise that a second scenario type cannot honestly use `(rlz, st)`,
is confirmed by `candidate-family-schema.md`. A numerically rectangular GCM set
still fails semantically: `st_id` is a foreign key to the stochastic perturbation
lookup and `rlz` asserts common-random-number pairing that a GCM label does not
carry. This design does not build that scenario type; the paper schema only establishes
that a neutral run identity is warranted.

The approved destination is now **two independently runnable workflows and
three logical stages**:

```text
generate_scenarios.smk                         simulate_system.smk
┌───────────────────────────────┐             ┌──────────────────────────────┐
│ Stage 1                       │             │ Stage 2                      │
│ enumerate + generate forcing │──collection─▶│ prepare + simulate + expose │
└───────────────────────────────┘             │ responses                    │
                                              └──────────────┬───────────────┘
                                                             │ retained response view
                                              ┌──────────────▼───────────────┐
                                              │ Stage 3                      │
                                              │ metrics at declared grain    │
                                              └──────────────────────────────┘
```

`generate_scenarios.smk` produces a durable, immutable scenario collection.
`simulate_system.smk` consumes a ready collection without invoking its producer.
Its user-facing name is **Simulate system behavior**: it simulates long-term
system behavior under perturbed climate scenarios, with terminology that also
accommodates future non-climate scenarios. This naming does not expand the
production backends or scenario types authorized by this design.
Its `metrics` target can recompute metrics from retained responses without
invoking Wflow. These names are selected proposals and are migration surfaces,
not descriptions of current files.

The split must preserve the current bottom-up method. Stochastic perturbations
from `weathergenr` remain the stress-test forcing. Projection products remain a
terminal plausibility overlay and have no dependency edge into either new
workflow. No projection product selects, constrains, or drives a scenario run.

## 2. Goals, constraints, and non-goals

### 2.1 Goals

1. Replace filename-parsed `(rlz, st)` with sequential `run_id` handles scoped
   to an immutable scenario collection.
2. Make the system simulator independent of scenario type: it consumes an identified forcing
   record, a built model, and result-affecting settings, without receiving
   `rlz`, `st_id`, unperturbed-case flags, or a scenario type payload.
3. Retain `run_id` for runs and `unit_id` for run-or-bundle metric units, with
   one mixed sequence, one width, and an explicit index that gives every unit's
   membership.
4. Make scenario generation independent of a built Wflow model, and make system simulation consume a completed collection without calling the generator.
5. Expose a simulator-independent response-series interface sufficient for the
   current metrics, without requiring a second normalized persistence copy.
6. Make metric grain, required responses, reference semantics, and estimator
   preconditions explicit and machine-checkable.
7. Allow metrics-only recomputation from retained responses. Missing required
   response variables cause a clear refusal; they never trigger simulation or
   fabricated defaults.
8. Separate freshness by cause: scenario collection, forcing artifact, model,
   simulator settings, response inventory, and metric definition.
9. Preserve deterministic ordering, complete accounting, and the one-off
   numerical comparison for the intentional R-2 Class-C grain migration.
10. Establish and test the logical adapters inside current WF3 first, then
    extract the two entry points.

### 2.2 Settled method and repository constraints

| ID | Constraint | Consequence here |
|---|---|---|
| S1 | Three stages and three contracts; no one table solves all three | Scenario table, response inventory, and unit index remain distinct |
| S2 | Simulator sees the built model and run list, never scenario type columns | The collection consumer view excludes the scenario type block and derivation edges |
| S3 | Bundling belongs to metrics | Bundle declarations and membership exist only in stage 3 |
| S4 | Build for the current bottom-up assessment | Only the stochastic scenario type is implemented in production |
| S5 | Perturbations are scenario-neutral stochastic forcing | `weathergenr` remains the production generator |
| S6 | CMIP6 is a terminal plausibility overlay | `analyze_projections` has no outgoing edge into generation or simulation |
| S7 | No local calibration | Stage 2 consumes the model WF1 built from global data |
| S8 | HydroMT, hydromt_wflow, and Wflow conventions are used verbatim | The adapter wraps their public inputs/outputs; it does not reimplement them |
| R-1 | Class C uses one month selected once and shared across realizations | The reference resolver runs once per metric set, before per-run reduction |
| R-2 | Class C is stored at `grain: run` | Each realization retains its own Class-C value |
| R-3 | Pairing is declared and evidenced | `paired_across_design_points` requires supporting `derived_from` edges |
| R-4 | Return-level minimum-sample screening is expressed per return period | The provisional formula, separate fit-validity refusal, and bounded scientific validation criterion in §7.5 remain binding; a passing count is not precision or identifiability evidence |
| R-5 | W4 was direction; the single mixed sequence stands on merits | The sequence is retained but its old width mechanism is replaced in §8 |
| R-6 | E18 is settled before further review | The confirmed paper-schema result is carried, not reopened |

R14 is a later current-tree fact and therefore supersedes v2's live-config
premises: `run_historical` is retired and `st_0` is always simulated. The
stochastic table consequently marks every row `evaluated: true`. The general
interface retains `evaluated` for a future forcing-only ancestor, and its
reference refusal is tested with a synthetic fixture rather than by reviving the
retired config key. [cited: `config_composition.py`, `run_stress_test.smk`]

### 2.3 Non-goals

- No production scenario provider beyond `weathergenr` and no production
  simulator beyond Wflow.
- No plugin discovery, dynamic loading, version negotiation, or third-party
  backend API.
- No third metrics workflow. Stage 3 is an independently targetable operation
  inside `simulate_system.smk`.
- No GCM/downscaled/user-supplied scenario producer. The synthetic provider and
  dummy simulator exist only as fixtures.
- No CMIP-to-stress-test forcing link and no change to WF2's projection method.
- No local model calibration or alternative hydrological engine.
- No model-configuration scenario columns in this milestone.
- No user-facing metric-grain configuration.
- No change to `st_0` comparability or to the perturbation method.
- No general manifest, namespace-claim, fencing-token, attempt, quarantine, or
  resume platform. The bounded ready-marker, immutability, retention, and stale
  consumption rules in §§5–6 are required by the split and stop there.
- No implementation, code edit, regression-baseline re-record, or scientific experiment in
  this design stage.

### 2.4 Terminology

| term | meaning in this design |
|---|---|
| scenario | One fully specified forcing case, including its realization and perturbation for the stochastic scenario type; not just a design point. Today's generated scenarios are climate scenarios. |
| scenario type / `scenario_type` | Classification that selects scenario construction and interpretation rules; currently `stochastic`. Each collection contains exactly one scenario type. |
| scenario collection | The durable set of scenario records, forcing artifacts, and provenance published by stage 1. |
| design point | One prescribed perturbation combination, shared across stochastic realizations. |
| realization | One stochastic weather draw; its perturbed descendants retain that draw's identity and pairing. |
| run / `run_id` | A collection-scoped case handle assigned before simulation, including to a forcing-only ancestor. It does not identify an execution attempt. The existing `grain: run` spelling denotes a metric for one evaluated case. |
| simulation / `simulation_id` | The collection-wide stage-2 object identified by the collection, model, simulator, settings, and response request. |
| execution attempt | An actual invocation or retry; no attempt-tracking platform is added here. |
| response series | A simulated time series exposed through the response interface, before metric calculation. |
| metric bundle | The declared group of evaluated cases supplying a bundle-grain metric. Membership is distinct from pooling, which is an estimator operation on those members' data. |
| metric unit / `unit_id` | The single evaluated case or metric bundle to which a metric value belongs. Bare `unit` in index contracts abbreviates metric unit; physical units describe response quantities. |
| metric / indicator value | A metric is a declared calculation; an indicator value is its reported result. Existing `<token>_indicators.csv` filenames retain this meaning. |
| unperturbed | Generated forcing with no imposed climate perturbation. |
| historical | The historical forcing period or WF1 simulation. |
| reference | The explicitly selected comparator or metric-reference group. |
| baseline | Always qualified: code baseline for the inspected revision, regression baseline for the numerical fixture/manifest. Use unperturbed or reference for scientific cases according to their role. |

An unperturbed generated series is not thereby equivalent to the historical
simulation. The existing `st_0` comparability question remains out of scope.
`run_id` and `unit_id` retain their approved identities and sequence rules;
`simulation_id` names the distinct collection-wide identity. The conceptual
chain is scenario collection → simulations → response series → metrics.

## 3. Capability-slot mapping and validation ownership

All revisions below are immutable. Repository bindings use the code-baseline
commit; method rulings use the frozen intake commit or the dated owner record.
This is a software-system ownership table, not an agent-process design.

| capability slot | binding and immutable revision | implementation owner | validation authority |
|---|---|---|---|
| `decision_framing` | frozen intake at `d50427e4`; R-1..R-6 dated 2026-09-07; scope addendum v2 dated 2026-09-09 | CST architecture | owner gate for framing; model validator for method consequences |
| `data_adapter` | HydroMT/hydromt_wflow surfaces as used at `4e26c239…` | model builder; geospatial analyst for forcing metadata | model validator for forcing compatibility; existing interchange validators for schema |
| `ensemble_generator` | `weathergenr` binding and current WF3 integration at `4e26c239…` | model builder | model validator for generated-forcing plausibility and completeness |
| `simulation_engine` | Wflow binding and current batch driver at `4e26c239…` | model builder | model validator for execution completeness and hydrological plausibility |
| `system_model_validation` | current model-reference/model-digest contract at `4e26c239…` | model validator | model validator |
| `impact_model` | `not_applicable` — declared outputs are hydrological response variables and metrics, with no separate impact model | — | — |
| `performance_analysis` | current indicator vocabulary plus R-1..R-4, revised by this design | stress-test analyst | model validator for metric inputs and estimator acceptance; crosswalk comparator for migration |
| `robustness_evaluation` | `not_applicable` — no option×scenario matrix or robustness ranking is added | — | — |
| `projection_overlay` | `not_applicable` to both new execution DAGs — WF2 remains an independent terminal plausibility product at `4e26c239…` | stress-test analyst | model validator for overlay plausibility; no authority to select a run |
| `orchestrator` | Snakemake and runner bindings at `4e26c239…` | CST architecture; rules implemented by Python engineering | DAG/config contract tests and fresh-project execution probes |

Every modeling handoff has an acceptance gate before integration:

- Stage 1 → validation: scenario cardinality, pairing evidence, climate variable
  names/units/calendar/timestep/coverage, per-file digest, and collection
  completeness.
- Stage 2 → validation: forcing compatibility, model digest, settings digest,
  one successful response inventory entry for every requested run-variable-
  location combination, and Wflow log review.
- Stage 3 → validation: declared response requirements, bundle membership,
  record-length preconditions, unit-index invariants, and the R-2 numerical
  migration comparison.

No production run is being orchestrated by this document, so a run-control
conformance level and namespace claim are **not applicable at authoring time**.
The implementation must not label a project root managed or a run `ready` under
the wider CST run-control protocol unless a separate design supplies validated
intent and a won namespace claim.

## 4. Selected architecture

### 4.1 Workflow and target boundaries

| entry point | top-level target | responsibility | may depend on |
|---|---|---|---|
| `generate_scenarios.smk` | `all` | enumerate, generate, perturb, validate, and publish one scenario collection | project/basin/climate config, shared region and historical climate store, weathergenr environment |
| `simulate_system.smk` | `all`, with `operation: simulate-and-metrics` | validate a ready collection and model, prepare Wflow inputs, execute, retain native responses, derive metrics | ready scenario collection; WF1 model leaves and model digest |
| `simulate_system.smk` | `metrics` or a metric-set filename, with `operation: metrics-only` | validate retained response inventory and derive metrics only | ready scenario collection; retained response inventory/native response files; metric declarations |

Scenario generation has **no** edge to the Wflow TOML, `.outputs_configured`,
WF1 snapshot, model digest, Wflow executable, or simulation experiment directory.
System simulation has **no** generation rule and cannot satisfy a missing
collection by executing one. Its collection path is a required external leaf at
that entry-point boundary.

The operation and requested target form one fail-closed selection. The only
supported top-level pairs are `simulate-and-metrics` + `all` and
`metrics-only` + `metrics`; the latter also admits a direct filename inside the
selected metric-set directory. Mixed pairs, a Wflow filename in metrics-only
mode, multiple targets spanning both stages, and an unrecognized target refuse
at parse time and name the supported pairs. A bare default invocation is exactly
`simulate-and-metrics` + `all`; it never infers metrics-only from retained files.

The `metrics` target is therefore a deliberate target mode. At Snakefile parse time it
requires an existing, ready response inventory, verifies that all native
artifacts and required variables are present, and builds a DAG containing the
metric rules but **omitting the Wflow preparation and execution producers**.
This conditional DAG is acceptable because the target expresses a different
operation, not a hidden fallback. A missing response inventory or required
variable raises before DAG construction with `MissingResponseRequirement`; it
does not become a producer edge. [proposed, untested]

The default `all` target retains normal producer edges: stage 2 creates the
response inventory and stage 3 consumes it. Both paths call the same metric
implementation and validate the same response-series protocol; the only
difference is whether stage 2 producers are admitted to the DAG.

How requested targets are inspected before rule definition is an unproven
Snakemake integration premise, not an assumed API. The feasibility gate in
§6.8 must establish the supported public mechanism, including direct filenames
and dry-runs, before extraction. If it cannot, the specified shipped-runner
fallback selects explicit rule modules and enforces the same pair matrix.

### 4.2 Logical adapters first, entry points second

Implementation is sequenced in three landings:

1. **Contract extraction in current WF3.** Introduce generator, simulator, native
   response reader, and metric declarations behind the current rule graph. Use
   production `weathergenr` and Wflow bindings plus fixture-only synthetic and
   dummy bindings. No entry point or config name changes yet.
2. **Durable handoff in current WF3.** Materialize and validate the scenario
   collection, response inventory, fingerprints, readiness, and metrics-only
   path while the old entry point still supplies one end-to-end comparison.
3. **Entry-point extraction.** Create the two selected Snakefiles, split config
   ownership, migrate the runner and live references, and retire
   `run_stress_test.smk` and `workflows.run_stress_test` in the same
   reference-atomic landing.

This ordering isolates contract defects from file-split defects. It does not
authorize a compatibility layer indefinitely; the old entry point is an
intermediate comparison harness and is retired in landing 3.

### 4.3 Production and fixture bindings

The architecture uses explicit constructors selected in repository code, not
runtime discovery:

| seam | production binding | fixture binding |
|---|---|---|
| scenario generation | stochastic provider wrapping current `weathergenr` generation and perturbation | synthetic provider that writes a structurally valid tiny collection with no `rlz` or `st_id` |
| simulation | Wflow adapter wrapping preparation, batch execution, and native-result reading | dummy simulator emitting non-Wflow data through the same response protocol |

Fixture bindings are importable only from tests. A production config cannot name
them. Adding a production binding requires a new design decision; the synthetic
route demonstrates boundary neutrality, not a supported backend.

### 4.4 Architectural invariants

1. One scenario-table row is one potential simulation run.
2. `run_id` has no embedded feature and is meaningful only inside its collection.
3. Simulation rules address scenarios only by `run_id`; no simulator rule reads the
   scenario type block or `derived_from`.
4. The scenario collection is immutable after its ready manifest is published.
5. A consumer records both `collection_id` and `collection_revision` and verifies
   both before using a byte.
6. Native Wflow paths and headers terminate at the Wflow response reader.
7. Metrics consume `ResponseSeries`, never Wflow CSV names or TOML paths.
8. A response need not be duplicated: a lazy view over retained native output is
   conforming if the response inventory is sufficient to reopen and validate it.
9. Metrics-only execution never schedules scenario generation or simulation.
10. `unit_id` kind and membership are resolved by `unit_index.csv`, never parsed
    from the id.
11. Every ordering used to mint an id, serialize an inventory, or reduce a bundle
    is explicitly deterministic.
12. Every bounded coverage loss, unsupported variable, incompatible forcing, or
    uncheckable completeness condition is reported; no cap or omission is silent.

## 5. Stage 1 contract: a durable scenario collection

### 5.1 Scenario table

**Artifact:** `<collection>/scenario_table.csv`. UTF-8, LF, comma-separated,
header present, no index column. Id columns are read as text in every language.
One table carries exactly one scenario type.

**Universal core, exactly and in order:**

| column | type | nullable | meaning |
|---|---|---|---|
| `run_id` | zero-padded decimal text at width `W` | no | collection-scoped case handle, assigned before execution; the only scenario-derived value admitted to simulator paths |
| `derived_from` | `run_id` text | yes | generation dependency: this forcing transforms the named forcing; empty means generated without another collection row |
| `evaluated` | lowercase `true`/`false` | no | whether a simulation response is required; false is reserved for a forcing-only ancestor |

`derived_from` edges must form a forest. Every non-empty value resolves in the
same table; self-reference, cycles, and missing ancestors are refused before the
generation DAG is built. Empty does not mean unperturbed. It means only that this
row has no in-collection forcing ancestor.

After the core comes the labelled scenario type block. The first column is
`scenario_type`, and the remaining names are registered by the provider. The
current production block is:

| column | type | meaning |
|---|---|---|
| `scenario_type` | text | literal `stochastic` |
| `rlz` | zero-padded decimal text | stochastic realization draw |
| `st_id` | zero-padded decimal text or empty | foreign key to `stress_test_lookup.csv`; empty for the unperturbed row |

The scenario type registry also declares:

```text
scenario_type             stochastic
pairing                   paired_across_design_points
completeness              configured_cross_product
surface_axes              stress_test_lookup
reference_grouping        unperturbed_by_realization
```

`paired_across_design_points` is accepted only when non-empty `derived_from`
edges support the claim. A paired declaration with all edges empty is refused
(`domain-2`, GF-18). A scenario type may instead declare `independent` or `none`.

The universal interface retains the forest rule. The production stochastic
provider adds a stronger same-realization ancestry invariant: every row with a
non-empty `st_id` derives **directly** from the unique empty-`st_id` root whose
`rlz` is identical; every such root has empty `derived_from`; and roots for
distinct `rlz` values have distinct `run_id` values. A perturbed-parent chain,
a missing edge, or an edge to another realization is refused before generation.
This structural rule establishes common-random-number ancestry; distinct root
ids alone do not empirically establish independent stochastic draws. Provider
validation must also show that `transform` opens and consumes the exact ancestor
artifact named by `derived_from` (`domain-v3-1`, GF-18).

For the stochastic scenario type, table order is normative and deterministic:

1. increasing `rlz`;
2. within each realization, the unperturbed row first;
3. then increasing `st_id` from the configured perturbation lookup.

The perturbed rows must equal the configured cross-product of
`1..n_realizations × 1..ST_NUM`, and exactly one unperturbed row exists per
realization. Completeness is checked against configured axes, not observed axes,
so uniformly missing rows cannot redefine the expected set. A scenario type without a
declared expected cardinality is reported `UNCHECKABLE` by name rather than
passed (`domain-9`).

R14 fixes the current stochastic evaluation set: every row, including every
unperturbed `st_0` row, has `evaluated: true`. The retired `run_historical` key
must not be read, accepted, translated into `evaluated`, or mentioned as a
remedy. A fixture-only scenario type may include an unevaluated forcing ancestor to
exercise the general invariant that a metric reference must resolve to an
evaluated run.

`forcing_uri` is absent. Stage 1 owns the forcing location through the collection
inventory after generation; a source URI is not part of the simulator seam and
no ingest path for supplied scenarios is being built.

### 5.2 Parse-time enumeration

The stochastic scenario rows are returned by a pure function of the composed
generation config. It reads `n_realizations`, `simulation_window`,
`climate_perturbations`, the resolved seed, and the registered scenario type rules; it
does no I/O. The generation Snakefile uses that in-memory object to expand the
DAG and a rule writes the identical object to `scenario_table.csv`.

This preserves P1's measured feasible case. A file written by a rule and then
read at module scope in the same invocation would require a checkpoint or a
second invocation; it is forbidden. A guarded parse-time read returning `[]` is
also forbidden because P1 measured exit 0 with zero scenario jobs. The minter
raises `EmptyScenarioSetError` on a zero-row table.

The `derived_from` mechanism must pass the still-unexecuted P2b composition gate
before implementation landing 1: a standalone Snakefile combines the
data-derived wildcard alternation with the ancestor input function in three
states—producer subtree resolvable, subtree missing, and no derived rows. P2
measured the two ingredients separately and measured `ruleorder` to fail; it did
**not** measure their composition. A fresh-project in-workflow gate follows P2b.

### 5.3 Generator adapter

The logical provider interface is:

```text
enumerate(generation_spec) -> ordered ScenarioRows
generate_roots(root_rows, source_inputs) -> ClimateArtifacts
transform(derived_row, ancestor_artifact, scenario_type_payload) -> ClimateArtifact
describe(artifact) -> ForcingDescriptor
```

Only the provider may interpret `rlz`, `st_id`, the perturbation lookup, or any
other scenario type field. Rule addressing is by `run_id`; the scenario type payload is selected
by `run_id` and handed opaquely to the provider. The collection publisher and
simulation consumer do not interpret it.

The production provider wraps current `weathergenr` generation and perturbation.
It must preserve the current stochastic seed, spell-factor, simulation-window,
right-labelled daily-time, and variable semantics. These scientific properties
are handed to `model-validator`; adapter tests alone cannot accept them.

Temporal provenance distinguishes three axes rather than treating `calendar` as
one inherited label: (a) the source generated-forcing calendar, currently
`noleap`; (b) the prepared Wflow-forcing calendar and actual first/last
timestamps, currently produced by the existing CFTime-to-`datetime64`
conversion, configured-window clip, and TOML endpoint refresh; and (c) the
response calendar and actual first/last timestamps exposed by the Wflow reader.
The adapter records each conversion, clip, endpoint, timestep, and interval
label. These existing operations are part of numerical preservation, not new
calendar repair. Any mismatch exposed by the bounded preservation gate is
reported for a separate method decision; this migration must not silently alter
calendar conversion, leap-day handling, annual-block anchoring, partial-year
retention, or endpoint semantics (`domain-v3-6`).

### 5.4 Collection location and files

`<project_dir>/scenario_collections/<collection_id>/` is the collection root.
`collection_id` is the 64-character lowercase SHA-256 defined in §8.1, so two
different generation intents cannot share a directory. The root contains:

```text
collection_intent.json
generation_config.json
source_inventory.json
provider_code_inventory.json
generation_environment.json
scenario_table.csv
stress_test_lookup.csv
forcing/run_<run_id>.nc
collection.json
```

`stress_test_lookup.csv` is present for the stochastic scenario type and retains WG-2's
existing monthly perturbation schema. It has no `st_0` row. A scenario type that does
not use that lookup omits the file and says so in `collection_intent.json`.

All paths stored in either manifest are POSIX-style paths relative to the
collection root. Empty segments, absolute paths, drive letters, `..`, and a
resolved target outside the collection root are refused. Consumers resolve from
the manifest's directory, not their working directory. The config path used to
select a collection follows the repository's existing rule for ordinary paths
(resolved from the run directory); its normalized resolved path and digests are
recorded in the simulation manifest.

### 5.5 `collection_intent.json`

This record is immutable and written before generation. Its required shape is:

```json
{
  "schema_version": "scenario-collection/1",
  "canonicalization_id": "collection-canon/1",
  "collection_id": "<sha256>",
  "scenario_type": "stochastic",
  "provider": {"name": "weathergenr", "revision": "<immutable digest>"},
  "generation_config": {"path": "generation_config.json", "sha256": "<sha256>"},
  "scenario_spec": {
    "scenario_type": "stochastic",
    "n_realizations": 0,
    "n_design_points": 0,
    "unperturbed_per_realization": 1,
    "expected_run_count": 0,
    "simulation_window": {"start": 0, "end": 0},
    "pairing": "paired_across_design_points",
    "row_order": "rlz-major/unperturbed-first/st-id-ascending"
  },
  "source_inventory": {"path": "source_inventory.json", "sha256": "<sha256>"},
  "provider_code": {"path": "provider_code_inventory.json", "sha256": "<sha256>"},
  "environment": {"path": "generation_environment.json", "sha256": "<sha256>"},
  "scenario_semantics_sha256": "<sha256>",
  "unit_id_capacity": 0,
  "unit_id_width": 0,
  "run_count": 0
}
```

The zeroes illustrate integer fields; actual counts and years satisfy the
configured-domain constraints and §8. `expected_run_count`, the design-axis
counts, unperturbed count, pairing claim, simulation window, and normative row
order are persisted values rather than facts a consumer must reconstruct from
the original config. The collection validator checks the scenario table against
this payload, including the configured-axis cross product and expected count.

`generation_config.json` is the canonical result-affecting generation projection,
including seed request/resolution and capacity, with project paths normalized;
it excludes `compute` and console settings. `source_inventory.json` is canonical
JSON containing an ordered entry for every
external provider input: source role, normalized path or provider locator, byte
size, SHA-256, and the metadata needed to interpret the generated artifact.
Consumption verifies this stored document, its digest, and generated artifacts;
it does not require the original source paths to remain available. A producer
reusing or reproducing the collection additionally verifies live inputs against
the stored inventory.

`provider_code_inventory.json` lists every invoked script and imported
repository module with normalized repository path and byte digest.
`generation_environment.json` stores the immutable environment descriptor and
package/lock revisions used in identity, rather than only an otherwise
unrecoverable hash. Their canonical document digests are the values in the
intent. A consumer can therefore recompute identity from persisted descriptors;
live-code or live-environment comparison is a producer/reproduction check.

The integer fields outside `scenario_spec` must be positive and satisfy
§8. The record contains no timestamp in the hashed body. An optional
`created_at_utc` may be stored outside `intent` for audit display and is excluded
from every identity.

The generation-config digest covers the generation workflow's result-affecting
projection only. `compute` and console options are excluded. The source inventory
covers the historical climate store and every other external input the provider
reads, by normalized relative path, size, and SHA-256. The provider code digest
covers the invoked script and imported repository modules that affect enumeration,
generation, or perturbation; byte-level hashing deliberately over-fires on
comments because P4 measured that this closes the imported-module blind spot.

### 5.6 `collection.json`: inventory and ready marker

`collection.json` is written **last** by same-directory temporary-file creation,
flush, and atomic replacement. Its presence with `status: ready` is the only
readiness marker. A scenario table produced at DAG construction, a directory,
or some `.nc` files do not establish readiness.

Required shape:

```json
{
  "schema_version": "scenario-collection/1",
  "status": "ready",
  "collection_id": "<sha256>",
  "collection_revision": "<sha256>",
  "intent_path": "collection_intent.json",
  "intent_sha256": "<sha256>",
  "scenario_table": {"path": "scenario_table.csv", "sha256": "<sha256>"},
  "scenario_type_artifacts": [
    {"role": "perturbation_lookup", "path": "stress_test_lookup.csv", "sha256": "<sha256>"}
  ],
  "forcing": [
    {
      "run_id": "001",
      "path": "forcing/run_001.nc",
      "sha256": "<sha256>",
      "size_bytes": 0,
      "descriptor": {
        "source_calendar": "<declared source calendar>",
        "timestep": "<ISO-8601 duration>",
        "time_label": "interval_end",
        "start": "<timestamp>",
        "end": "<timestamp>",
        "spatial_representation_sha256": "<sha256>",
        "variables": [
          {"name": "<canonical name>", "units": "<units>", "missing_value": "<encoding>"}
        ]
      }
    }
  ]
}
```

The forcing array is sorted by numeric `run_id`; variables are sorted by
canonical name; scenario type artifacts are sorted by role then path. Every table row
has exactly one forcing entry, including an unevaluated ancestor. No extra forcing
entry is permitted. `size_bytes` is informative but checked; SHA-256 is
authoritative. `collection_revision` is the §8.2 digest and excludes itself.

Readiness validation performs, in order:

1. schema and canonicalization version support;
2. `collection_id` recomputation from the intent;
3. path confinement for intent, scenario table, scenario type artifacts, and forcing;
4. exact file existence, size, and SHA-256 comparison;
5. scenario-table schema, ordering, forest, completeness, pairing, and id-width
   checks;
6. one-to-one run-to-forcing inventory coverage;
7. descriptor extraction from each file and exact comparison with the recorded
   source-forcing descriptor, including calendar and actual endpoints; and
8. `collection_revision` recomputation.

Any failure raises `ScenarioCollectionNotReady` naming the collection, failed
field or artifact, expected value, and observed value. System simulation stops
before preparing Wflow input.

### 5.7 Immutability, ownership, and retention

Scenario generation is the sole writer; simulation runs are read-only consumers.
The generator atomically creates the exact `<collection_id>` directory before
writing and refuses if a partial directory already exists. This is a bounded
single-collection ownership claim, not the broader ancestor/descendant namespace,
fencing, attempt, or resume protocol. A crash leaves an incomplete collection
that no consumer can use and that the owner must explicitly remove before retry.

If a ready collection already exists, generation verifies the complete manifest.
An exact match is reused and reported; any mismatch is `ImmutableCollectionError`.
No file is overwritten in place, and a recomputation that produces different
bytes for the same intent is a reproducibility failure rather than a new revision
silently replacing the old one.

Collection forcing files are durable outputs and must not be wrapped in
Snakemake `temp()`. Provider work files that are neither inventoried nor needed
for reproduction remain temporary. No consumer cleanup rule may delete or mutate
the collection.

Retention is `durable_until_explicit_delete`. The generation summary reports the
collection root, file count, total retained bytes, `collection_id`, and
`collection_revision`; there is no silent size cap. An explicit project
maintenance command may list collection sizes and the simulation manifests that
reference each collection. Deletion requires an explicit `--delete` target and
refuses while a retained simulation manifest references the collection unless the
owner also supplies an explicit force option. No automatic age-based deletion is
part of this design.

## 6. Stage 2 contract: simulation and simulator adapter

### 6.1 Simulation identity and namespace

The human namespace remains `<project_dir>/experiments/<experiment_name>/`.
`experiment_name` chooses where one simulation assessment is written; it is not its
freshness identity. The immutable machine identity is `simulation_id`, defined in
§8.3.

Two experiment names may consume the same collection without copying or changing
it. One experiment name may not change collection revision, model digest,
simulator binding, settings, or requested response set after successful
simulation. A mismatch with retained outputs raises `SimulationFrozenError` and
names the changed digest. The remedy is a new experiment name or explicit removal
of that experiment's simulation outputs; the collection remains untouched.

The simulation root contains:

```text
config/simulation.json
config/response_request.json
config/simulator_settings.json
config/simulator_adapter_code_inventory.json
config/simulation_environment.json
config/model_reference.yml
hydrology/wflow/forcing/inmaps_run_<run_id>.nc
hydrology/wflow/config/run_<run_id>.toml
hydrology/wflow/config/run_<run_id>.yml
hydrology/wflow/output/run_<run_id>.csv
hydrology/wflow/output/outstates_run_<run_id>.nc
responses/response_inventory.json
results/metric_sets/<metric_set_id>/metrics.json
results/metric_sets/<metric_set_id>/unit_index.csv
results/metric_sets/<metric_set_id>/<token>_indicators.csv
```

Wflow forcing, config, catalogs, and native outputs are implementation artifacts
of the Wflow adapter. `run_` is a fixed token carrying no scenario feature.
Nothing parses it. Warm-state lifecycle remains governed by the Wflow contract;
it is not required for metrics-only recomputation unless a declared response
reader actually needs it.

### 6.2 `simulation.json`

Required fields:

```json
{
  "schema_version": "simulation/1",
  "simulation_id": "<sha256>",
  "experiment_name": "<name>",
  "collection": {
    "manifest_path": "<normalized path>",
    "collection_id": "<sha256>",
    "collection_revision": "<sha256>"
  },
  "model": {"model_digest": "<existing model_digest>", "reference_path": "config/model_reference.yml"},
  "simulator": {"name": "wflow", "revision": "<immutable digest>"},
  "settings": {"path": "simulator_settings.json", "sha256": "<sha256>"},
  "simulator_adapter_code": {"path": "simulator_adapter_code_inventory.json", "sha256": "<sha256>"},
  "environment": {"path": "simulation_environment.json", "sha256": "<sha256>"},
  "response_request": {"path": "response_request.json", "sha256": "<sha256>"},
  "response_inventory_sha256": "<sha256 or null>"
}
```

`response_request.json` is immutable simulation input. It persists the ordered
variable/location/time/units/missingness request and the complete
`expected_series` key set derived from evaluated runs and requested locations.
Its digest enters `simulation_id`; a consumer validates coverage from the
persisted payload without a live model. Selected metric declarations keep their
own requirements in `metrics.json` and do not rewrite this simulation request.

`simulator_settings.json` persists the canonical result-affecting Wflow/adapter
settings projection. `simulator_adapter_code_inventory.json` lists invoked and
imported repository code with byte digests. `simulation_environment.json` persists
the immutable environment descriptor and dependency/lock revisions. Their
digests are identity inputs; live comparison is required only to execute or
claim reproduction. `simulation_id` is recomputed from these documents, the
recorded collection identity, and `model_digest`. Its calculation excludes
`simulation_id`, `experiment_name`, and the mutable completion fields.

The existing pointer-derived `model_digest` and `model_reference.yml` remain the
model fingerprint; this design does not replace them with a shorter file list.
The three leaves in `shared/cross_workflow_leaves.py` remain the runner's
existence preflight for system simulation, while `model_digest` supplies the
freshness check. [cited]

The initial record is written before simulation with
`response_inventory_sha256` null. Completing stage 2 fills it by atomic
replacement. Metric-set completions live only in their immutable `metrics.json`
manifests, so multiple metric sets do not mutate the simulation record. The response
completion fact does not enter `simulation_id`. Immutable inputs may never be
edited after a successful response inventory exists.

### 6.3 Simulator adapter boundary

The logical interface is:

```text
requirements(model_reference, response_request) -> ForcingRequirement
validate_forcing(run_forcing, requirement) -> ValidatedForcing
prepare(run_id, validated_forcing, model_reference, settings) -> PreparedRun
execute(prepared_run) -> NativeRunArtifacts
open_responses(run_id, native_artifacts, response_request) -> ResponseSeriesSet
```

The Wflow adapter owns every HydroMT/Wflow-specific operation: validating the
forcing against the current model, preparing the model-grid forcing and per-run
catalog/TOML, invoking Wflow, and mapping native columns into response series.
Snakemake may retain separate rules for those operations so resource requests,
logs, retry boundaries, and per-run visibility remain observable. The adapter
boundary is responsibility and interface, not a requirement to collapse jobs.

The adapter receives one `RunForcing` record independent of scenario type:

```text
run_id
forcing_path
forcing_sha256
ForcingDescriptor
collection_id
collection_revision
```

It does not receive `scenario_type`, `rlz`, `st_id`, `derived_from`, pairing,
the perturbation lookup, or a provider payload. A synthetic collection with no
`rlz`/`st_id` must reach the dummy simulator through this same record.

### 6.4 Forcing compatibility and refusal

`ForcingRequirement` declares, from the built model and Wflow binding:

- required canonical variables and exact accepted units;
- accepted spatial representation, CRS/grid relation, and dimension names;
- accepted calendar(s), timestep, interval labelling, and simulation coverage;
- missing-value policy; and
- any Wflow-specific conversion that the existing HydroMT preparation surface
  performs.

The adapter compares every `ForcingDescriptor` before any preparation or Wflow
process starts. Variable absence, unit mismatch, incompatible space, unsupported
calendar, wrong timestep/label, insufficient coverage, or forbidden missingness
raises `IncompatibleForcingError` naming `run_id`, field, required value, observed
value, and source artifact. A conversion is allowed only when it is an existing
HydroMT/hydromt_wflow/Wflow convention and is recorded in the prepared-run
metadata. This design adds no private unit, calendar, or regridding algorithm.

Compatibility and freshness are independent. A compatible file whose digest no
longer matches the collection inventory is stale and refused by collection
validation. An unchanged forcing with a changed model or setting has a different
`simulation_id` and cannot reuse the old response.

### 6.5 Batch execution and failure visibility

The current flat batch shape is retained: deterministic increasing numeric
`run_id`, sliced by the configured execution-only batch size. Batch membership,
logs, benchmarks, and per-run native outputs remain visible. A batch failure
reports the batch id plus every contained `run_id`; partial native files do not
enter a ready response inventory.

The batch driver receives an explicit ordered list of `(run_id, toml_path,
native_output_path)` records. It must not derive `run_id` from a TOML stem or
assume parallel arrays have the same order. Wflow's own files and log messages
remain native; only their association with a run is explicit.

### 6.6 Response-series protocol

`ResponseSeries` is the only value interface exposed to metrics:

```text
ResponseSeries:
  run_id: text
  variable: canonical metric token
  location_id: text
  location_ordinal: non-negative integer in the persisted native response order
  time: ordered typed coordinate
  calendar: text
  timestep: duration
  time_label: interval_end | instant
  units: text
  values: one-dimensional numeric array
  missing: boolean mask or declared native missing representation
```

Cardinality and validity rules:

1. `(run_id, variable, location_id)` is unique, and each variable/run location
   order has unique contiguous `location_ordinal` values.
2. `run_id` resolves to an evaluated scenario row.
3. Time is strictly increasing and unique; values and missingness have the same
   length.
4. Calendar, timestep, label, units, and missingness are explicit; no metric
   infers one from a filename or defaults one silently.
5. Every response required by the request has exactly one series. Extras are
   allowed only when inventoried and are never treated as requested implicitly.
6. Bundle members used by a metric have compatible calendars, time coverage,
   timestep, units, and location sets, or the metric refuses before reduction.
7. Metrics never infer a scientific reference from iterator or sorted order;
   any order-sensitive legacy reference is resolved to an explicit
   `reference_location_id` and persisted before reduction.

The protocol may be an in-memory iterator or lazy view. Production is not
required to persist a normalized duplicate of Wflow's CSV. The Wflow reader may
open retained native CSVs lazily and yield conforming `ResponseSeries` objects.
The dummy simulator may persist a minimal neutral fixture. Both routes enter the
same validator and metric function.

### 6.7 `response_inventory.json`

Metrics-only execution needs enough information to reopen the neutral view
without rerunning Wflow. The inventory is written last after every evaluated
run succeeds:

```json
{
  "schema_version": "response-inventory/1",
  "simulation_id": "<sha256>",
  "collection_id": "<sha256>",
  "collection_revision": "<sha256>",
  "model_digest": "<sha256>",
  "simulator": {"name": "wflow", "revision": "<immutable digest>"},
  "settings_sha256": "<sha256>",
  "response_request": {"path": "../config/response_request.json", "sha256": "<sha256>"},
  "temporal_preparation": {
    "source_calendar": "noleap",
    "prepared_forcing_calendar": "standard",
    "response_calendar": "<recorded response calendar>",
    "operations": ["cftime_to_datetime64", "clip_to_configured_window", "refresh_toml_endpoints"],
    "prepared_start": "<timestamp>",
    "prepared_end": "<timestamp>",
    "response_start": "<timestamp>",
    "response_end": "<timestamp>",
    "time_label": "interval_end"
  },
  "artifacts": [
    {"run_id": "001", "path": "../hydrology/wflow/output/run_001.csv", "sha256": "<sha256>", "size_bytes": 0}
  ],
  "series": [
    {"run_id": "001", "variable": "q", "location_id": "130000086", "location_ordinal": 0, "artifact": 0, "native_selector": "<adapter-private selector>", "units": "<units>", "calendar": "<calendar>", "timestep": "P1D", "time_label": "interval_end", "start": "<timestamp>", "end": "<timestamp>", "missing_value": "<encoding>"}
  ],
  "response_inventory_sha256": "<sha256>"
}
```

Artifacts are sorted by numeric `run_id` then path; series by numeric `run_id`,
variable, and persisted `location_ordinal` (with `location_id` as the final
tie-breaker). `artifact` is a zero-based array index, avoiding repeated
paths without creating a string-parsing contract. `native_selector` is opaque to
metrics and interpreted only by the named simulator reader. All paths resolve
from the inventory directory and must remain inside the simulation experiment.

`response_inventory_sha256` is SHA-256 over canonical JSON with only that field
omitted. No timestamp or filesystem mtime enters it. The stored value must equal
that recomputation before any series is opened.

The inventory validator resolves and digests the persisted response request,
recomputes every artifact digest and the inventory digest, verifies that the
inventory's series keys equal `expected_series`, opens every selector through
the recorded adapter revision, checks declared series metadata, verifies that
location ordinals reproduce the native response column order for every run, and
checks the source/prepared/response calendar and endpoint chain. A missing or
changed native file makes the inventory unready. An adapter revision unavailable
in the current environment is an explicit `UnavailableResponseReader`, not a
request to simulate again.

### 6.8 Metrics-only operation

`simulate_system` gains a required result-neutral enum in its workflow file:

```yaml
operation: simulate-and-metrics  # or: metrics-only
```

It is recorded in the invocation record and excluded from scientific identity.
`simulate-and-metrics` is the default scaffold value. In `metrics-only` mode the
Snakefile validates `response_inventory.json` at parse time and does not define
the Wflow preparation or execution producers. It defines only stage-3 rules and
their supporting validation. Direct requests for Wflow output paths therefore
fail with no producer rather than escaping the mode.

This mechanism is **[proposed, untested]**. Before entry-point extraction a
standalone feasibility probe must show:

1. the default invocation defines and orders stage 2 before stage 3;
2. metrics-only defines no Wflow producer and recomputes metrics from retained
   native responses;
3. missing inventory, missing required variable, and missing native artifact
   fail before any simulation command;
4. requesting `all`, `metrics`, a metric filename, or a Wflow filename cannot
   bypass the configured operation; and
5. a dry-run and a real fixture invocation agree on which rules are present.

If conditional rule definition cannot satisfy those five without private
Snakemake APIs, entry-point extraction pauses. The fallback is a thin shipped
runner selecting one of two explicit rule modules inside the same
`simulate_system.smk`; creating a third workflow is not an allowed fallback.

## 7. Stage 3 contract: metric declarations, units, and results

### 7.1 Metric declaration

The existing class letters become structured declarations in the shared metric
registry. Every metric declares:

| field | required content |
|---|---|
| `grain` | `run` or `bundle` |
| `required_responses` | canonical variables, temporal resolution/coverage, location grain, units, and missingness tolerance |
| `bundle_by` | registered grouping function name, required only for bundle grain |
| `reference` | registered reference grouping or `None`; required for Class C |
| `reference_location` | registered location-selection rule or `None`; required for Class C and resolved to an explicit id before reduction |
| `return_period` | years or `None` |
| `blocks_per_return_period` | positive ratio or `None` |
| `implementation_revision` | immutable digest of the metric and imported reducer code |

The registry keeps current internal statistic keys separate from emitted output
names. `Q_METRIC_SUFFIXES` remains the authoritative mapping from an internal
key to the suffix appended to `q_`; `BASIN_METRIC_SUFFIXES` remains the mapping
from a basin-variable token to its suffix. The current emitted vocabulary is:

| class | metrics | grain | bundle | reference | block ratio |
|---|---|---|---|---|---|
| A | `q_annual_mean`, `q_mean_annual_max`, `q_mean_annual_min`, `q_mean_annual_p95`, `q_mean_annual_7day_max`, `q_mean_annual_7day_min`, `q_baseflow_index`; plus `<token>_annual_total` for `aet`, `gwr`, `precip`, `snow_annual_max`, and `overland_flow_annual_mean` | `run` | — | none | none |
| B | `q_return_level_10yr_max`, `q_return_level_2yr_7day_min` | `bundle` | `same_design_point` | none | proposed `1.0` |
| C | `q_wettest_month_mean`, `q_driest_month_mean` | `run` | — | required | none |

`required_responses` belongs to the metric declaration persisted in
`metrics.json`; it is not the simulation's `response_request.json`. The latter
is fixed when a simulation run is created and may retain a superset of responses.
Stage 3 unions the selected metrics' requirements and proves that the retained
inventory satisfies them. Adding a metric that reads only already-retained
series changes the metric-set identity alone. A missing requirement is refused
by name; satisfying it requires a deliberately new simulation run with an enlarged
simulation request, never mutation of the completed request.

### 7.2 R-1 and R-2: Class C

The wet or dry month is resolved **once per metric set**, from the registered
reference grouping, before per-run values are computed. For the stochastic
scenario type that grouping selects every unperturbed run and pools their response
years. The current Q5 behavior remains, but its hidden native-order dependency
becomes data: the metric planner resolves `class_c_first_gauge` from the
persisted response `location_ordinal` values, requires the same first q-gauge
location for every contributing reference member, and writes that explicit
`reference_location_id` into `metrics.json` before reduction. `_category_month`
reads only that named series; reversing native-file discovery,
neutral-series iteration, or sorted location order cannot change the reference.
The chosen month is shared by every location and realization. It is not
recomputed per location or per run.

`metrics.json` persists, for each Class-C metric, the reference member run ids,
resolved `reference_location_id`, selection statistic (`monthly sum` followed
by wet `argmax` or dry `argmin`), month tie rule (the current pandas first-label
result in ascending calendar-month order), exact analysis coverage and effective
year/month counts, and the resolved wet and dry month numbers. The complete
reference rule and resolved values enter metric identity. A change to reference
location, statistic, tie handling, coverage, or resolved month therefore creates
a new metric set (`domain-v3-2`).

Each Class-C value is then computed separately for each run at that fixed month.
For equal-length realizations on one calendar,

```text
old pooled Class-C value
    = mean over realizations(new per-run Class-C value).
```

That equality is the premise of R-2 and is tested by the migration comparator;
it is not presumed from a zero perturbation. A reference group with no evaluated
run, an incompatible response, or more than one selected month refuses before
any results table is written. The message names metric, scenario type, grouping,
expected reference, and observed members. The retired `run_historical` key is
never suggested as a remedy.

### 7.3 Metric bundles

`bundle_by` names a function registered for the scenario type. For stochastic
scenarios, `same_design_point` groups equal `st_id` across realizations. Empty
`st_id` is a real grouping key; implementations must retain it (`dropna=False`
where pandas is used). The unperturbed Class-B bundle therefore always exists in
the current scenario type.

A valid metric bundle:

1. contains only unique evaluated runs from one collection;
2. equals exactly the membership returned by its declared grouping;
3. does not silently drop an empty/null grouping key;
4. satisfies the metric's response compatibility and estimator preconditions;
5. agrees with the scenario type's pairing declaration and `derived_from` evidence;
6. is ordered by numeric `run_id` for every non-commutative operation; and
7. is recorded once in `unit_index.csv` for that metric set.

A run may belong to different bundles for different declared groupings. Bundle
membership is never added to the scenario table, collection inventory, simulator
adapter, or response inventory.

### 7.4 Metric-unit index and result tables

Each immutable metric-set directory contains:

```text
<exp>/results/metric_sets/<metric_set_id>/
    metrics.json
    metric_environment.json
    unit_index.csv
    <token>_indicators.csv
```

`metric_set_id` is defined in §8.4. A new metric definition produces a new
directory and never overwrites a prior accepted result set. `metrics.json` is
written last as its ready marker. Its required content is `schema_version`,
`status: ready`, `metric_set_id`, `simulation_id`, collection id/revision,
response-inventory path/digest, the complete selected metric declarations,
metric-definition digest, metric-execution environment path/digest,
grouping/reference semantics and resolved Class-C reference provenance,
unit-index path/digest,
an ordered indicator-table inventory of token/path/digest/row count, and
`metrics_manifest_sha256`. The manifest digest is canonical SHA-256 with only
`metrics_manifest_sha256` omitted; no timestamp or mtime enters it. Thus every
ready marker and identity input can be checked without a live registry.

`metric_environment.json` is a canonical immutable descriptor of the actual
stage-3 execution environment. It records the lock/environment revision and the
resolved numerical dependency versions used by the response reader and reducer,
including xclim, SciPy, pandas, NumPy, xarray, and their load-bearing transitive
numerical libraries. Its SHA-256 is computed before reduction, enters
`metric_set_id`, and is persisted by path and digest in `metrics.json`. The past
stage-2 environment remains simulation provenance; it cannot stand in for the
environment of a later metrics-only recomputation (`domain-v3-4`).

`unit_index.csv` has exactly three columns:

```text
unit_id,grain,member_run_id
```

A run unit has one row, `grain=run`, and `member_run_id=unit_id`. A bundle unit
has one row per member, `grain=bundle`. The table is long so membership is joined,
not parsed. It carries no bundle label or scenario type column; meaning comes from
joining member runs to `scenario_table.csv` and the registered grouping.

Each indicator table has exactly four columns:

```text
metric,location,unit_id,value
```

`metric` remains the current composite token; `location` remains the bare id;
`unit_id` is zero-padded text at collection width `W`; and `value` retains the
current significant-digit and `float32` output contract. `st_id`, `rlz_id`, and
`POOLED_REALIZATION` are removed. Consumers resolve `unit_id` in the index before
grouping. An unresolved unit is a mismatched artifact set and stops consumption.

The validator asserts:

1. every result `unit_id` resolves in the index;
2. every `member_run_id` resolves in the consumed collection's scenario table;
3. no `unit_id` has two grains;
4. a run unit has one self-membership row;
5. every metric's declared grain matches its unit grain;
6. the index unit set is exactly every evaluated run plus every bundle required
   by the selected declarations;
7. the empty-`st_id` bundle exists for stochastic Class-B metrics;
8. every unit id shares the collection's width and is at or below its capacity;
9. the stochastic join
   `unit_id → member_run_id → scenario_table.st_id → stress_test_lookup.st_id`
   is complete in both required directions, with the unperturbed empty key
   outside the lookup by construction; and
10. each emitted variable, location, and time basis satisfies the persisted
    response request.

Invariant 6 is evaluated from declarations and scenario rows, not from emitted
tables, so a minter and writer cannot agree on the same omission. A forcing-only
unevaluated row has a climate file and no run unit, response, or metric row.

### 7.5 Return-level estimator precondition

Return-level acceptance has three separate gates: minimum-sample screening,
fit validity, and bounded methodological adequacy. Passing one never certifies
the next (`domain-v3-3`).

For each Class-B bundle, metric, and response location, count finite usable
blocks after applying the declared temporal and missingness rules. Persist the
count by member run and in total, member count, actual temporal coverage, and
the preserved partial-block and missingness rule. The provisional screening
minimum is:

```text
required = max(
    ceil(blocks_per_return_period × T),
    GEV_SCREENING_BLOCK_FLOOR,
)
```

Block extraction preserves E10 and the current reducer's numerical order. It
never concatenates daily trajectories across realization boundaries. For each
member run independently, the reducer first selects the recorded analysis
coverage after the existing Wflow warm-up/spin-up handling, applies the current
`water_year_start` end-anchor, and then extracts blocks: annual maxima directly;
for low flow, the current seven-observation rolling mean first and annual minima
second. Only these per-run scalar block series are concatenated, in increasing
numeric `run_id`, for the bundle fit. A rolling window may not cross from one
run into the next.

The migration preserves the current anchor, analysis start/end, rolling-window
alignment and completeness behavior, and missing-value treatment. Those facts
are persisted in the response request or metric declaration. Compatibility
checks refuse mismatched calendars, coverage, or missingness before reduction;
they do not coerce, resample, trim a new spin-up interval, or otherwise change a
valid current numerical path. After block extraction, the fit discards only the
same non-finite block values the current `_return_level_from_blocks` path
discards.

Here `T` is the declared return period. R-4 fixes this ratio-based **shape**;
it does not scientifically ratify a number. This design carries v2's proposed,
untested `blocks_per_return_period = 1.0` and
`GEV_SCREENING_BLOCK_FLOOR = 10`. The renamed constant makes the bounded claim:
it is a screening floor, not an identifiability or precision threshold. If the
location-specific `actual < required`, reduction raises
`InsufficientReturnLevelBlocks` and names metric, unit, location, return period,
required blocks, total usable blocks, per-member usable counts, and coverage.
It does not fit, omit, pool locations, or emit a caveated row.

Samples that pass the count gate then face fit-validity checks using only the
current xclim/SciPy GEV estimator and its supported returned parameters. A
constant sample, an estimator exception, an exposed unsuccessful-convergence
flag, non-finite fitted shape or
location, non-finite or non-positive fitted scale, or a non-finite requested
quantile raises `InvalidReturnLevelFit`. The refusal records metric, unit,
location, sample count/range, estimator and environment revisions, failed check,
and available fit parameters. It writes no metric row. This adds no estimator
fallback and no interval.

At the current periods (`T=10` peak, `T=2` low flow), the floor binds for both.
The ratio becomes discriminating for `T>10`. The rapid fixture's current 18
pooled years and regression-baseline fixture's current 18 pooled years pass; a one-
realization nine-year bundle refuses. The old v2 text naming 32 regression-baseline blocks
described the pre-R14 regression-baseline window and is not a current-tree fact.

The stricter `2.0` ratio remains an alternative methodological tightening. It is
not silently introduced by this architecture migration.

The values `1.0` and `10` remain **provisional screening heuristics**. The
following grid and tolerances are **author-proposed scientific acceptance
criteria awaiting Astra model-validator review**; G1 approved the obligation to
add explicit bounded criteria, not these numerical choices. Using the
unchanged estimator, draw 1,000 deterministically seeded samples for each cell
of GEV shape `{-0.2, 0.0, 0.2}` × usable-block count `{10, 18, 30, 60}` at unit
location and scale; evaluate the 10-year upper and 2-year lower quantiles against
their analytic GEV values. Report fit-refusal rate, median signed relative error,
median absolute relative error, and 90th-percentile absolute relative error for
every cell. The provisional policy may be described as scientifically validated
only for cells where at least 95% of samples yield valid fits, absolute median
bias is at most 10%, and 90th-percentile absolute relative error is at most 50%
for the 10-year level and 25% for the 2-year level. Every boundary cell at
`n=10` and the current-config cell at `n=18` must pass for the corresponding
shipped metric before the screening values receive that description. Failure
leaves the count policy usable only as an explicitly limited operational
screen; it triggers a separate owner method ruling and does not automatically
select ratio `2.0`, change the estimator, remove partial years, or add intervals.
The validation record pins RNG seed, xclim/SciPy environment, analytic
parameterization, cell counts, and complete results. It does not claim
stationarity, independent annual extrema, fit precision outside the tested
matrix, or basin-model adequacy.

### 7.6 Fit uncertainty and surface metadata

The retained position from `domain-7` remains explicit: the toolbox emits
point estimates that pass the operational sample and fit-validity checks, and
carries no Class-B fit interval across this seam. Until §7.5's author-proposed
criteria pass scientific review and execution, these estimates are not described
as scientifically adequate merely because the count and fit gates pass.
Class A and C preserve per-run spread; Class B does not. A companion metric name
can add intervals later without changing the four-column schema. The trigger is
a requirement to interpret threshold crossings with estimator uncertainty.

Each ready metric set records the scenario type's pairing value and surface-axis
declaration. Stage 3 reads stochastic axes through `stress_test_lookup.csv`.
A scenario type without declared axes is reported as not surface-plottable. No stage
derives a CMIP change factor. Projection products, if overlaid later, remain
terminal plausibility evidence and never select scenarios.

## 8. Identity, fingerprints, and invalidation

### 8.1 One mixed sequence without metric-to-generation coupling

`run_id` and `unit_id` retain one decimal sequence and one width under R-5/W4,
but v2's minting mechanism is superseded. V2 used
`W=index_width(len(runs)+len(bundles))`; therefore generation evaluated stage-3
groupings and changing metrics could rename climate files. That cannot support a
durable collection consumed before the metric set is known.

This revision introduces a required generation setting:

```yaml
unit_id_capacity: <positive integer>
```

The collection sets `W = index_width(unit_id_capacity)`. Stage 1 mints run ids
`1..n_runs` in normative scenario order. Stage 3 reuses those exact strings for
run units and mints bundle units from `n_runs+1` upward, sorted by
`(bundle_by name, canonical grouping key)`. No prefix, feature, or reserved type
range is embedded.

Generation refuses only when `n_runs > unit_id_capacity`; it is metric-blind and
does not know `n_bundles`. The metric planner later refuses unless
`n_runs + n_bundles <= unit_id_capacity`. In either context
`UnitNamespaceCapacityError` reports capacity, known runs, known bundles (or
`not-evaluated` during generation), required total where known, and the minimum
replacement value. Generation summaries always report capacity and remaining
post-run slots, so the bound is not silent. Increasing capacity creates a new
collection id and may widen every id; it never mutates a ready collection.

This is an explicit cost: an undersized collection cannot admit a later grouping
without regeneration. It buys independent generation, one spelling per run, and
the single mixed sequence already accepted. The migration helper proposes the
minimum capacity needed by the current run-and-bundle set but requires the value
to be visible in the generated config; it may not hide headroom.

### 8.2 Collection identities

`collection-canon/1` is canonical JSON: UTF-8, object keys sorted by Unicode code
point, arrays kept in declared order, no insignificant whitespace, final LF,
integers in decimal, finite JSON numbers only, and no NaN/Infinity. Paths are
normalized relative POSIX text before encoding.

The persisted `scenario_spec` contains the facts needed to validate the table
without the original project config:

```json
{
  "scenario_type": "stochastic",
  "n_realizations": 2,
  "n_design_points": 4,
  "unperturbed_per_realization": 1,
  "expected_run_count": 10,
  "simulation_window": {"start": 2046, "end": 2054},
  "pairing": "paired_across_design_points",
  "row_order": "rlz-major/unperturbed-first/st-id-ascending"
}
```

Numbers above illustrate the schema, not a new shipped config. The intent also
references `source_inventory.json`, a canonical list of source role, normalized
path or provider locator, size, digest, and relevant metadata. The collection
stores this inventory and its digest. Consumption verifies the stored inventory
document and generated artifacts; it does **not** require the original historical
source files to remain mounted. Reproduction or producer-side reuse additionally
verifies the live sources against the inventory.

The identities are:

```text
collection_id = SHA256(canon({
    schema_version,
    scenario_spec,
    scenario_semantics_sha256,
    generation_config_sha256,
    source_inventory_sha256,
    provider_name_and_revision,
    provider_code_sha256,
    environment_sha256,
    unit_id_capacity,
}))

collection_revision = SHA256(canon({
    collection_id,
    intent_sha256,
    scenario_table_sha256,
    scenario_type_artifact_inventory,
    ordered_forcing_inventory_with_descriptors,
}))
```

`collection_id` is known before generation and names the directory.
`collection_revision` proves the produced bytes and metadata. Sequential ids are
handles; neither digest replaces them.

Every item in the first equation is stored in `collection_intent.json` or in a
referenced canonical document. The `collection_id` calculation omits the
`collection_id` field itself. `scenario_semantics_sha256` is computed from the
parse-time semantic rows without `run_id` and later checked by stripping
`run_id` from the persisted table. `collection_revision` excludes its own field;
the recorded `intent_sha256` covers the complete immutable intent.

### 8.3 Simulation identity

```text
settings_sha256 = SHA256(canon(simulator_settings.json))
simulation_response_request_sha256 = SHA256(canon(response_request.json))

simulation_id = SHA256(canon({
    collection_id,
    collection_revision,
    model_digest,
    simulator_name_and_revision,
    simulator_adapter_code_sha256,
    settings_sha256,
    simulation_response_request_sha256,
    environment_sha256,
}))
```

Batch size, cores, console verbosity, and `operation` are recorded execution
facts and excluded. A changed forcing byte moves `collection_revision`; a changed
model moves `model_digest`; changed physics or output selection moves settings or
response request; changed adapter logic moves the code digest. Equal sequential
ids never authorize reuse.

Every equation input is stored in `simulation.json` or one of its referenced
documents; no original workflow config or live environment is needed to
recompute it. `simulation_id` omits itself, `experiment_name`, execution facts,
and completion fields. The recorded `model_digest` is sufficient for identity
recomputation; simulation still requires the referenced model to verify and use
that digest.

`response_request.json` is persisted beside `simulation.json`. It is the
immutable **simulation response request**, not the union of currently selected
metric requirements. It contains the
ordered required variable/location/time/units/missingness declarations plus an
`expected_series` set derived from evaluated scenario rows and requested output
locations. The response inventory is complete only if its series keys equal that
set. Metrics-only validation reads this payload and its digest; it does not need
the live model to rediscover what was requested.

### 8.4 Metric-set identity and provenance

```text
metric_definition_sha256 = SHA256(canon({
    selected_metric_declarations,
    grouping_registry_semantics,
    reference_registry_semantics,
    resolved_reference_provenance,
    metric_and_imported_reducer_code_sha256,
}))

metric_environment_sha256 = SHA256(canon(metric_environment.json))

metric_set_id = SHA256(canon({
    simulation_id,
    response_inventory_sha256,
    metric_definition_sha256,
    metric_environment_sha256,
}))
```

`metrics.json` persists the complete selected declarations, response-request
path and digest, grouping/reference names, bundle membership digest, unit-index
digest, metric-environment path and digest, indicator file digests, and evidence
labels for validation performed.
This is sufficient to explain a metric result without the live registry.

Changing only a formula, grouping body, reference rule, or grain changes
`metric_definition_sha256` and schedules only stage 3. The collection and response
inventory remain reusable. Changing metric selection in a way that needs a
response already retained also schedules only stage 3. A required response absent
from the retained set causes `MissingResponseRequirement`; it does not silently
change `simulation_id` or run Wflow in metrics-only mode.

### 8.5 Invalidation matrix

| changed fact | collection | stage-2 responses | metric set |
|---|---|---|---|
| generation config, seed, source inventory, provider code/environment | new `collection_id`; regenerate | new simulation identity | new metric set |
| generated forcing byte or descriptor | collection revision mismatch; refuse mutation | stale/refuse | stale/refuse |
| model digest, simulator setting, adapter code/environment | reusable | new simulation identity; simulate | new metric set |
| immutable simulation response request | reusable | new simulation identity; simulate the enlarged request | new metric set |
| selected metric set whose requirements are already retained | reusable | reusable and **must not rerun** | new metric set only |
| selected metric requires an unretained series | reusable | metrics-only refuses; a separately requested simulation with an enlarged response request is required | no result until satisfied |
| metric formula, grain, grouping/reference body | reusable and **must not rerun** | reusable and **must not rerun** | new metric set only |
| metric execution environment or numerical dependency resolution | reusable | reusable and **must not rerun** | new metric set only |
| batch size, cores, operation | reusable | same scientific identity | unchanged results identity |

This re-expresses v2 GF-16/GF-17 rather than carrying their stale mechanism:

- Current rule 3.09 already re-fires when its resolved config mapping changes;
  this design inherits that behavior and does not claim to add it. [measured P4]
- A stage-1 imported-module change is caught by `provider_code_sha256`, changes
  `collection_id`, and schedules a new collection. The byte digest may over-fire
  on comments; that measured cost is accepted. [measured P4]
- A stage-3 grouping/declaration change moves only
  `metric_definition_sha256`. It must **not** change `scenario_table.csv`, width,
  collection id/revision, or response inventory. That separation is now the
  falsifier, replacing v2's requirement that grain changes re-fire 3.09.
- Width changes only when the explicit capacity changes and therefore create a
  new collection id. A rename of a scenario type column requires a schema-version or
  semantic-registry change; it cannot masquerade as unchanged intent.

### 8.6 Interrupted generation tradeoff

V2 preserved the existing legal behavior in which a failed run could change
config before the success marker and retry. Content-addressed collection intent
preserves that case differently: changing config produces a new `collection_id`
and leaves the failed directory isolated. It does not preserve in-place repair of
a **same-intent partial collection**. The bounded claim in §5.7 refuses that
directory until explicit cleanup, and no checkpoint is reused.

This is deliberate scope restraint, not a claim of equivalent resumability. It
may waste completed forcing files after an interruption, but cannot treat partial
or unvalidated files as ready. A bounded safe-resume protocol would need
per-artifact checkpoints, writer fencing, and transition state—explicitly the
broader run-control system excluded here. The validation plan measures the
current choice: same intent + partial directory refuses with the cleanup path;
changed intent proceeds in a different directory; a ready collection remains
immutable.

## 9. DAG, configuration, and runner migration

### 9.1 Workflow identities and rule ownership

The selected workflow identifiers are `wf3` for `generate_scenarios.smk` and
`wf4` for `simulate_system.smk`. Existing `wf0`, `wf1`, and `wf2` retain their
identities. Rule-number prefixes follow the owning workflow: generation rules
use `3.xx`; simulation and metric rules use `4.xx`. The exact suffix is assigned in
the rule index during implementation so references, logs, and contract rows land
atomically.

Current WF3 responsibilities move as follows; names identify current functions,
not promises that a proposed rule name already exists:

| current responsibility | destination | boundary change |
|---|---|---|
| resolve stochastic rows and write perturbation lookup | generation | writes `scenario_table.csv` and collection intent from the same parse-time object |
| configure and execute `weathergenr` | generation | uses the provider interface and independent seed resolution |
| create unperturbed and perturbed climate netCDFs | generation | publishes `forcing/run_<run_id>.nc` under one immutable collection |
| verify weather-generator catalog/grid | generation | validates collection cardinality, descriptors, and inventory; per-run intermediates remain `temp(...)` where they are not collection artifacts |
| validate model reference and prepare Wflow forcing/catalog/TOML | simulation | consumes only the collection's run-forcing view, independent of scenario type |
| execute flat Wflow batches | simulation | keeps resource and log visibility; associates records explicitly by `run_id` |
| export Wflow responses | simulation | writes native artifacts plus the neutral response inventory |
| reduce indicators | metric stage inside simulation | reads `ResponseSeries`, metric declarations, and the unit namespace |

Generation's historical climate input and basin/region facts become explicit
source leaves or generation-owned preparation rules. They may be shared climate
artifacts, but no dependency reaches the built-model snapshot, Wflow TOML,
`.outputs_configured`, model digest, or model run. If a current producer mixes a
climate-source artifact with model construction, the climate-source portion is
first moved behind a shared data-preparation rule; generation must not call WF1
to obtain it. This is a stage-boundary extraction, not a new data method.

The extraction updates `shared/cross_workflow_leaves.py`. Its current fixed
`LEAVES` tuple and `LEAF_PRODUCER = build_model` cannot describe the split.
The replacement declares leaves by consumer and operation:

| consumer/operation | required external leaves | accepted producer |
|---|---|---|
| scenario generation | declared historical climate source and required basin/region artifacts | their existing climate/data preparation owner; never `build_model` merely to obtain Wflow state |
| simulation `simulate-and-metrics` | ready collection manifest; WF1 config snapshot, Wflow TOML, `.outputs_configured` | external collection or `generate_scenarios`; `build_model` for the three model leaves |
| simulation `metrics-only` | ready collection manifest; simulation record; response request and ready response inventory/native artifacts | a prior completed system simulation |

The helper validates leaves. It does not add producer edges across entry points.
The runner may tell a user which disabled workflow normally produces a missing
leaf, but each Snakefile treats it as external and refuses independently.

### 9.2 Normative seam-contract replacements

The accepted design updates all nine live WG/HM clauses identified in v2. The
replacement text is complete enough to implement; unchanged means the existing
contract clause remains verbatim.

| clause | successor normative clause |
|---|---|
| WG-2 perturbation lookup | `<collection>/stress_test_lookup.csv`; schema, multiplier semantics, precision, and domain remain unchanged. `st_id` is same-width text within the lookup and joins the stochastic scenario type block. Every non-empty scenario `st_id` resolves; the unperturbed empty key has no lookup row. The provider receives the id from the table, never a filename. |
| WG-4 weather forcing | `<collection>/forcing/run_<run_id>.nc`, exactly one per scenario row. The existing raster shape, `{precip,temp}` minimum, CRS, and asserted-if-present metadata rules remain. **Its old `temp()` lifecycle is superseded:** these are durable inventoried collection artifacts, including unperturbed files, and no consumer may delete them. |
| WG-5 per-run HydroMT catalog | `<exp>/hydrology/wflow/config/run_<run_id>.yml`, `temp()`, one per evaluated run, with one `run_<run_id>` entry. The existing emitted HydroMT data-catalog field subset remains unchanged. Entry keys equal the evaluated run set across the catalog set. |
| WG-6 prepared forcing | `<exp>/hydrology/wflow/forcing/inmaps_run_<run_id>.nc`, one per evaluated run. Existing raster/content rules and temporary adapter lifecycle remain. |
| HM-2 WF3 forcing twin | Same prepared-forcing path as WG-6, zero-padded `run_id`, no parsing; existing variables, raster, CRS, and lifecycle stand. |
| HM-4 Wflow config | `<exp>/hydrology/wflow/config/run_<run_id>.toml`, one per evaluated run; existing TOML content, pinned key subset, and HydroMT/Wflow conventions stand. |
| HM-5 native response | `<exp>/hydrology/wflow/output/run_<run_id>.csv`, one per evaluated run; existing columns, units, time axis, and numerical output semantics stand. Stage 3 reaches it only through `response_inventory.json`. |
| HM-6b warm state | `<exp>/hydrology/wflow/output/outstates_run_<run_id>.nc`, one per evaluated run, `temp()`; existing content and lifecycle stand. |
| HM-7 result interchange | `<exp>/results/metric_sets/<metric_set_id>/<token>_indicators.csv`, exactly `metric,location,unit_id,value`, with `unit_index.csv` and `metrics.json` in the same ready metric set. Existing variable tokens, location spelling, value precision, and metric vocabulary stand subject to R-2. |

For WG-5, `validate_wg5` changes its selector from `rlz_` to `run_`, changes its
docstring pattern, and changes the empty-selection diagnostic to
`no 'run_<run_id>' entries in catalog`; per-entry field validation is unchanged.
The relational validator is renamed `validate_wg5_catalog_runs` and verifies
that each catalog has its intended `run_<run_id>` key and that the aggregate key
set equals evaluated scenario rows. It derives no `0..ST_NUM` grid and contains
no special `st_0` clause.

For HM-7, `unit_id` is text. Every id in one metric set has one width, and a
standalone consumer **discovers that width from `unit_index.csv`**; it never
computes it from run counts, bundles, metric declarations, or repository code.
A mixed-width set is malformed. Consumers join before grouping and refuse every
unresolved unit. `validate_hm7` checks the exact header and vocabulary; each
result id and member id domain; declared metric grain; all §7.4 unit invariants;
and stochastic design coverage through
`unit_id → member_run_id → scenario_table.st_id → stress_test_lookup.st_id`,
including at least one unit resolving to the empty unperturbed key. The latter
checks configured design coverage rather than treating an omitted row as a
smaller surface.

The successor ADR also carries the neighbouring sealed-ruling dispositions:

- **C24 is superseded in full.** Pooling is declared by metric and membership,
  not encoded in an id; the surviving design-point identity is `st_id`; current
  batch rules are flat rather than realization-wildcard groups; and a failed
  batch names `run_id`, which resolves to fuller context in the table.
- **C28 is superseded.** Its denormalized axis columns already disappeared, and
  `st_id` is specific to the scenario type. Results carry only `unit_id`; axes are reached by
  joins. The existing hard stop on an unknown stochastic axis survives and cites
  the successor ADR.
- **C25's ordered, scoped-run-id principle stands, while its physical experiment
  container is refined by the approved split.** A `run_id` is still a sortable
  zero-padded sequence and never a global content hash. Its namespace is now the
  immutable collection rather than an experiment directory; `unit_id` is scoped
  to that collection and metric set. The content hash names the collection, not
  an individual run. This preserves C25's collision and opacity concerns while
  allowing two simulation experiments to reuse one run namespace.

Validator-index rows, seam documents, naming records, and the successor ADR are
updated in the same reference-atomic landing. Historical C24/C25/C28 records are
sealed and remain unchanged.

### 9.3 Configuration split

The closed project-workflow stanza set changes from four names to five:
`analyze_climate`, `build_model`, `analyze_projections`,
`generate_scenarios`, and `simulate_system`. Every project file keeps all five
closed `{enabled, config_path}` stanzas, matching the existing composition
contract. Workflow files remain beside the project file; `config_path` remains
relative to that project file, while ordinary paths keep their current
run-directory basis.

The old `run_stress_test` workflow file is split by ownership:

| generation workflow | simulation workflow |
|---|---|
| `n_realizations` | `experiment_name` |
| `simulation_window` | `scenario_collection` selector (§9.5), resolving to one exact `collection.json` |
| `climate_perturbations` | `operation` |
| `weathergen_config` and generator result-affecting options | immutable simulation response request or its config projection |
| `seed` | Wflow result-affecting settings |
| `unit_id_capacity` | `compute` and execution-only batch settings |

Shared basin, climate, and model keys stay in the project file under their
current owning sections. A key read by both workflows is promoted there only if
it describes the shared project rather than the handoff. The collection manifest
path is a simulation input, not duplicated generation config. Metric selection and
declarations belong to the simulation workflow but remain outside the immutable
simulation response request as specified in §7.1.

Current retirement behavior is preserved. `run_historical`, `stress_test`,
`realizations_num`, `horizontime_climate`, `run_length`, and `batch_size` remain
rejected old keys; they are not accepted as aliases in either new workflow.
Current keys such as `n_realizations`, `climate_perturbations`,
`simulation_window`, and `compute` are the migration inputs. Seed configs retain
the `project_config_` prefix: for example the current
`test_case/project_config_rapid_run_stress_test.yml` is replaced by distinct
`project_config_rapid_generate_scenarios.yml` and
`project_config_rapid_simulate_system.yml` files, referenced by the project
file. No `snake_config_*` name is introduced.

`config_composition.WORKFLOW_NAMES`, its closed-stanza validator, config-path
composition, ownership checks, and retirement map move together. A project with
`workflows.run_stress_test` fails with a migration message identifying both new
stanzas; it is never interpreted as enabling both implicitly. This breaking
config change is justified by the new ability to generate, reuse, simulate, and
recompute independently. A hidden compatibility translation would erase the
choice of durable collection and operation.

### 9.4 Acyclic seed resolution

The current `seed: auto` is resolved from `experiment_name`; carrying that rule
would make generation depend on a simulation namespace. Deriving the seed from
`collection_id` would be circular because the collection identity includes the
resolved seed. Both are forbidden.

The new generation resolver accepts an explicit integer or `auto`. An explicit
integer is used unchanged. `auto` applies a versioned domain-separated mapping
to an explicit canonical `generation-seed-material/1` projection containing only
the scenario type, stochastic draw/perturbation settings that select climate
values, simulation window, provider revision, and source-inventory digest. The
projection excludes `seed` itself; `unit_id_capacity`; `unit_id_width`; run-id
spelling/order; collection/storage paths; retention/readiness choices; compute,
batch, and console settings; `experiment_name`; simulation settings; timestamps;
and `collection_id`. Adding another generation-config field requires declaring
it included as climate-draw-affecting or excluded with a reason; it is never
included merely because it lives in the generation stanza. The intent persists
the complete projected object and its digest beside `seed_request`,
`resolved_seed`, and `seed_resolution_id`; the collection identity hashes the
resolved integer and resolution id. This order is acyclic:

```text
source inventory + explicit climate-draw seed projection
    -> resolved seed
    -> scenario rows and complete generation intent
    -> collection_id
```

Migration preserves numerical intent instead of applying the new `auto` rule
retrospectively. For every old config, composition first resolves the old seed
with the old experiment name and writes that integer into the new generation
workflow file. Thus the current advanced default remains `123`, and an old
`auto` project retains its previously resolved integer even if the simulation
experiment is renamed. Only newly authored `auto` configurations use the new
resolver. GF-27 falsifies dependency or migration drift.

### 9.5 Runner ordering and modes

`scripts/run_workflows.py` expands its fixed module contract to five entries.
For an all-enabled invocation its operational order is:

```text
analyze_climate -> generate_scenarios -> build_model
                -> simulate_system -> analyze_projections
```

This order is a convenience sequence, not a dependency chain. `analyze_climate`
remains optional and should still run alone when forcing selection is the
question. Generation can run before, after, or without a model build. Simulation
needs both a ready collection and, in simulation mode, a ready model. WF2 stays
last because projections are a terminal plausibility overlay; it has no edge
back to either successor workflow.

Preflights are workflow-local and run immediately before each enabled workflow,
after every earlier enabled producer in the fixed sequence has completed. Thus a
fresh all-enabled invocation checks WF1 leaves after `build_model`, not before
the build that creates them. The runner applies these preflights:

1. if generation is enabled, compute the intended content-addressed path and
   invoke the generator; the generator alone atomically claims the directory and
   applies §5.7's reuse/partial-state rules—the runner makes no second claim;
2. if system simulation is enabled while generation is disabled, validate the
   configured ready collection as an external leaf;
3. for `simulate-and-metrics`, require the WF1 leaves and model digest whether
   WF1 is enabled in this invocation or was completed earlier;
4. for `metrics-only`, require no WF1 leaf, Wflow executable, or producer rule;
   validate the retained request, response inventory, and native artifacts; and
5. reject an operation/target mismatch before launching Snakemake.

A direct Snakefile invocation enforces the same conditions. The runner is never
the only safety boundary.

`scenario_collection` is a closed discriminated selector:

```yaml
scenario_collection:
  selection: generated
```

`generated` means exactly the collection intent produced by the composed
`generate_scenarios` workflow in this same project config. Before invoking the
generator, the runner calls the shared pure intent resolver, including the
prepared source inventory, and holds the resulting expected
`<project_dir>/scenario_collections/<collection_id>/collection.json` path in
memory. After generation exits, it validates that exact ready manifest and
passes that path as the resolved simulation input. It never scans the collection
directory, follows a `latest` pointer, or selects an older ready collection. A
mismatch between the precomputed id and produced manifest is a hard failure.

`selection: manifest` requires an explicit normalized `manifest_path` and is the
portable independent-consumer form; it does not require original generator
sources. `selection: generated` is allowed for a direct simulation invocation only
when the generation config and source inputs needed to recompute intent are
available; it performs the same read-only resolution and requires the ready
manifest without invoking its producer. `manifest_path` is forbidden with
`generated` and mandatory with `manifest`, so selection cannot fall back. The
resolved path, selector, collection id, and revision are recorded in
`simulation.json`.

### 9.6 Reference-atomic landing and output migration

Landing 3 retires `run_stress_test.smk`, its stanza, and its workflow file after
logical adapter and comparison gates pass. It updates all live references in one
reference-atomic branch landing: README and AGENTS workflow tables/commands,
workflow-name and config-shape migration docs, rule index, naming and seam
contracts, DAG renderer examples, test fixtures, `scripts/run_workflows.py`,
`config_composition.py`, `cross_workflow_leaves.py`, indicator glossary,
surface readers, regression-baseline tooling, the tracked indicator reference, and the
in-repository Climate Stress Test notebook. Historical milestone and probe files
remain sealed with their then-valid names.

Old experiment output is not renamed in place. A migrated generation produces a
new content-addressed collection; a simulation writes a new experiment namespace.
The migration note carries the deterministic old `(rlz, st_id)` to new `run_id`
crosswalk and the old pooled-sentinel to bundle-unit mapping. Half-renamed trees
are unsupported and refused.

The numerical comparison cannot use the currently retained regression-baseline manifest as
its pre-change side. The repository documents that manifest and fixture tree as
pre-R14 while the current regression-baseline config uses the nine-year window; the next run
will move values for that reason alone. The identity migration therefore records
a fresh **pre-change** run and a post-change run from the same current composed
config in separate output roots, then applies §12.3's crosswalk. It does not
overwrite the standing regression baseline until the identity comparison is accepted. WF1
uses `--notemp` when its discharge output is part of that recording.

## 10. Alternatives and decision reversals

| alternative | advantage | cost and decision | what would change the decision |
|---|---|---|---|
| keep one `run_stress_test.smk` and expose intermediate targets | smallest file/config change | rejected: generation remains coupled to model readiness, experiment namespace, and metric-aware minting | evidence that independent collection ownership/reuse has no user or orchestration value |
| create three entry points, including `compute_metrics.smk` | strongest process isolation | rejected by approved scope: metric recomputation is independently targetable inside simulation, and a third workflow adds config/runner surface | a future need to schedule metrics under a separate deployment, security, or retention owner |
| runtime provider/simulator plugins | extensibility | rejected: no second production binding and discovery/version negotiation exceed R12 | an accepted production backend with an incompatible construction lifecycle |
| retain `W=index_width(n_runs+n_bundles)` | automatic minimum width | rejected: a future metric renames immutable forcing and makes generation evaluate metric groupings | abandoning independent durable generation |
| two sequences or visible `r_`/`b_` prefixes | removes capacity planning and makes kind visible | rejected on R-5 merits: kind parsing would become an alternate contract and weaken mandatory index joins; reserved ranges add policy | measured recurrent capacity regeneration, plus a consumer contract that can prohibit kind parsing |
| fixed repository-wide id width | no regeneration on ordinary growth | rejected: it hides an arbitrary global cap and changes W4's minimum-width direction | a platform-wide namespace convention ratified beyond this milestone |
| explicit `unit_id_capacity` | metric-blind generation with one mixed sequence | selected; costs visible headroom choice and possible regeneration | replaced if recurrent grouping growth proves this cost operationally dominant |
| persist normalized response netCDF beside Wflow CSV | simplest simulator-neutral reopen | not mandatory: duplicates large retained data; allowed only when measured read cost or native stability warrants it | response-reader performance, native-format instability, or cross-language access failure |
| lazy native response view | avoids mandatory duplicate persistence | selected, conditional on GF-21/GF-24 and adapter-revision availability | failure to reopen deterministically or unacceptable repeated-read cost |
| resume same-intent partial collection | saves completed generation work | deferred: safe reuse needs checkpoints and writer fencing | generation cost measurements justify a bounded resume protocol design |
| mutable human-named collection | approachable paths | rejected: reuse and stale-consumption decisions become ambiguous | none within the approved split; aliases may point to immutable ids later |
| keep an indefinite old compatibility wrapper | easier transition | rejected: it cannot express independent producer/consumer ownership without guessing | a time-bounded external-client obligation with an explicit sunset and unambiguous mapping |
| tighten `blocks_per_return_period` to `2.0` | more conservative extrapolation | deferred methodological choice; would reject current short bundles | owner validation of the threshold and acceptance of the affected run cost |

## 11. Consequences, roadmap, and remaining risks

### 11.1 Improvement roadmap

| problem | selected change | expected effect | affected stages |
|---|---|---|---|
| filenames encode scenario meaning | scenario table plus opaque sequential `run_id` | explicit joins and simulation independent of scenario type | all three |
| generator requires a built Wflow context | durable collection and climate-only leaves | independent generation and reuse | generation, runner |
| metrics influence forcing ids | explicit capacity and metric-set identity | metric edits no longer invalidate collection or simulation | generation, metrics |
| native Wflow CSV is a hidden metric interface | response inventory plus `ResponseSeries` reader | simulator-specific parsing ends at adapter | simulation, metrics |
| pooled sentinel hides grain | declaration plus long unit index | each result unit has checked kind and membership | metrics |
| one command conflates production and reduction | operation/target matrix | metrics-only cannot invoke Wflow accidentally | simulation, metrics, runner |
| stale artifacts judged by paths | layered collection, simulation, response, and metric digests | reuse follows result-affecting identity | all three |
| split creates shared-artifact lifetime questions | immutable ready marker and explicit reference-aware retention | consumers can safely reuse or clearly refuse | collection, simulation |

### 11.2 Material consequences and risks

- Existing WF3 configs, commands, output paths, table headers, workflow count,
  and runner order change. The reference-atomic landing is large even though
  the scientific method is deliberately stable.
- `unit_id_capacity` is a real advance choice. A later grouping can exhaust it;
  the error is explicit, but regeneration may be expensive.
- Same-intent partial generation is not resumable. The cleanup refusal is safer
  than accidental reuse and less capable than v2's legal interrupted-run retry.
- Retaining reusable collections and native responses consumes disk. Listing
  exact bytes and references prevents silent retention but does not choose an
  owner-specific quota.
- Byte digests of imported provider, adapter, grouping, and reducer code can
  over-fire on comments. This is the accepted price of closing P4's imported-code
  blind spot until a semantic build artifact exists.
- The lazy response view may be slower than a normalized store and depends on
  the recorded reader revision remaining available. Both premises are untested.
- Wflow forcing compatibility and numerical equivalence after path/config
  extraction require real validation. Structural fixture success cannot accept
  scientific equivalence.
- The target/operation parse-time mechanism and direct-filename behavior are
  unprobed. Entry-point extraction waits on the §6.8 feasibility gate.
- Class-B `1.0` and screening floor `10` are provisional operational values.
  They may be called scientifically validated only after §7.5's bounded matrix
  passes; even then the claim is limited to that matrix and is not an uncertainty
  interval, stationarity result, or basin-skill result. Historical `domain-7`
  remains deferred: no fit interval crosses the seam.
- The response request must be chosen with likely metric needs in mind. A later
  metric needing an unretained variable requires a new simulation run; metrics-only
  correctly refuses rather than expanding scope silently.

### 11.3 Empirical premises still open

1. P2b has not run. Its three-state composition result is a pre-implementation
   gate, despite v2 having accidentally described it as measured in one place.
2. Conditional target selection must be proven through supported Snakemake
   surfaces for default, mixed, direct-filename, and dry-run invocations.
3. The current stochastic provider must reproduce old climate bytes or explain
   every intended metadata-only difference after collection extraction.
4. Wflow must accept the neutral run-forcing adapter with identical result-
   affecting configuration and numerically equivalent responses.
5. The native response reader must expose all current q, basin-scalar, and
   subcatchment requirements with unambiguous units/time semantics.
6. The seed migration must preserve the resolved old integer, particularly for
   every `auto` fixture, while new `auto` remains experiment-independent.
7. Collection and response inventory hashing cost, lazy reader cost, and retained
   disk volume are unmeasured. No cap is inferred from their absence.
8. The R-2 Class-C averaging premise must pass on equal-calendar old/new outputs;
   it is not accepted merely because the formula is linear.
9. Return-level thresholds need §7.5's bounded methodological validation;
   passing the count and fit-validity gates establishes only operational
   admissibility under this design.
10. E19 remains outside current production scope: no operational example yet
    establishes that a future provider's reference period, temporal aggregation,
    units, and surface coordinates are scientifically comparable.

## 12. Validation plan: claim to falsifier

### 12.1 Structural and orchestration gates

All statuses below describe this design stage. `[proposed, untested]` means no
implementation result may be reported as measured until the named gate runs.

| ID | preserved or revised claim | falsifier / required observation |
|---|---|---|
| GF-1 | `derived_from` alternation and ancestor input compose on a fresh project | P2b first; then a fresh generation DAG has no ambiguity/cycle and a missing ancestor fails cleanly |
| GF-2 | empty `derived_from` matches no transform rule | synthetic no-edge fixture schedules root generation only |
| GF-3 | scenario enumeration is parse-time derivable without checkpoint | one fresh invocation builds the complete expected DAG; no checkpoint/two-pass behavior |
| GF-4 | current unperturbed cases are always evaluated under R14 | every stochastic unperturbed row is `evaluated:true`, scheduled, and inventoried; old `run_historical` is refused, not revived |
| GF-5 | empty scenario set refuses | `EmptyScenarioSetError`; no successful zero-job generation |
| GF-6 | grouping/declaration body or metric execution environment changes rerun only stage 3 | each change independently creates a new metric-set id while collection and response digests remain byte-identical; the environment case changes a recorded numerical dependency descriptor with repository source unchanged |
| GF-7 | HydroMT resolves every `run_` catalog entry | one real rapid preparation reads the intended source for each run |
| GF-8 | inventory recognizes the successor trees | `tree-check` reports no undeclared new leaves after a complete rapid run; renamed prefixes already classify as P5 measured |
| GF-10 | every result unit resolves with one grain | synthetic pass/fail contract pairs plus all completed result tables |
| GF-11 | simulator never receives scenario type concepts | AST/signature test plus synthetic scenario type lacking `rlz`/`st_id` reaches dummy simulator |
| GF-12 | stale collection/simulation reuse refuses | changed ready byte, collection revision, model digest, setting, or response request names the mismatched digest before execution |
| GF-13 | empty `st_id` remains a Class-B grouping key | unperturbed metric bundle exists in index and carries both return-level rows |
| GF-14 | unevaluated metric reference refuses generally | fixture-only unevaluated reference raises a named parse-time error; no retired toggle is accepted |
| GF-15 | return-level sample screening, fit validity, and methodological adequacy are separate | `required-1` refuses with metric/unit/location/count/coverage; constant blocks, location-specific missingness, injected fit failure, invalid parameters, and non-finite quantile each refuse by the named contract; the bounded seeded matrix in §7.5 reports every cell and alone decides whether `1.0`/`10` may be called scientifically validated |
| GF-16 | stage-1 freshness is independent of metric/grouping code | imported provider-body change moves collection id; metric/grouping change cannot move any collection artifact |
| GF-17 | interrupted/config/width behavior matches §8.6 | same-intent partial refuses cleanup; changed intent uses new directory; metric growth within capacity leaves collection unchanged; overflow refuses explicitly |
| GF-18 | pairing claims require exact same-realization ancestry | paired fixture with all-empty edges, one missing perturbed edge, cross-realization ancestry, and a perturbed-parent chain each refuse before generation; roots have no parents; distinct realizations have distinct roots; an instrumented transform proves it consumes the declared direct ancestor; an independent fixture may pass, without treating distinct ids as proof of independent draws |

GF-4 and GF-14 deliberately re-express the older tests. Current config has no
supported `run_historical:false` state; keeping that stale premise would test a
retired interface instead of the underlying invariants. GF-16/GF-17 likewise
replace v2's metric-coupled width and success-marker guard rather than claiming
those mechanisms survive the durable split.

### 12.2 New split and persistence gates

| ID | claim | falsifier / required observation |
|---|---|---|
| GF-19 | generation runs without built Wflow | fresh generation succeeds with WF1 model leaves absent; DAG contains no Wflow/model rule |
| GF-20 | simulation consumes but cannot produce a collection | missing/not-ready collection refuses; simulation DAG contains no generation provider rule |
| GF-21 | response protocol is simulator-independent | the same metric function passes on dummy neutral series and Wflow reader series; no Wflow name reaches it |
| GF-22 | metrics-only never schedules simulation | supported target/operation matrix passes; missing inventory/variable/artifact fails before any Wflow command; mixed/default/direct targets are covered |
| GF-23 | ready collections are immutable, reusable, and reference-protected | two experiments consume one revision; attempted mutation refuses; deletion lists exact referencing simulations and requires explicit force |
| GF-24 | persisted payloads make coverage self-contained | unmounted original sources and absent live model still allow collection/response completeness validation; missing expected row/series refuses |
| GF-25 | config/runner migration is closed and complete | five stanzas compose; old stanza/keys/current old command refuse with migration text; runner and direct invocation agree |
| GF-26 | projections remain terminal | generated DAGs have no WF2 input; full runner schedules WF2 last; no projection digest enters any collection/simulation identity |
| GF-27 | seed resolution is acyclic, migration-preserving, and independent of namespace headroom | renaming simulation experiment cannot change new collection; old explicit/default/auto each resolve to their pre-split integer; capacity-only and id-width-only variants preserve `resolved_seed` and forcing values under a run crosswalk while creating the required distinct collection namespace; collection-id construction has no seed cycle |
| GF-28 | calendar and endpoint migration preserves the current adapter path | bounded fixtures cover a leap year, right-labelled terminal timestamp, and non-January water year; source/prepared/response calendars, conversion/clip operations, actual endpoints, partial blocks, and annual reductions match the pre-change comparator or fail with a reported mismatch and no silent repair |

### 12.3 Numerical migration gate (GF-9)

GF-9 remains a one-off crosswalk comparison because `check_baseline.py` keys on
the old table shape and cannot compare a column and row-count migration. On two
fresh runs made from the same current config and code except for the identity
landing, the comparator:

1. joins old `(rlz_id, st_id)` to the new scenario type block in the scenario table and
   `run_id`, then through `unit_index.csv` to `unit_id`;
2. compares every Class-A per-run row one-to-one within `INDICATOR_RTOL` and the
   existing group-relative absolute tolerance;
3. compares every Class-B pooled row to the corresponding bundle unit, including
   the empty-`st_id` unperturbed bundle;
4. compares each old Class-C pooled value to the mean of new per-run values at
   the same design point and location; uses two gauges with opposite seasonal
   peaks; records the current first-native-gauge `reference_location_id`; and
   repeats with reversed native-artifact enumeration and neutral-series
   iteration while retaining persisted ordinals, requiring
   the reference id and resolved wet/dry months to remain unchanged; and
5. proves coverage both ways: every old row is accounted for and every new row
   is its counterpart or an expected Class-C sibling.

Any unexplained Class-A/B numeric change, Class-C mean mismatch, changed
reference under iteration-order reversal, duplicate join, or lost row fails the
landing. The comparator records config digests, source
digests, model digest, environment, code revisions, row counts, unmatched keys,
and maximum differences. It does not compare the stale standing fixture to a
current-config run.

### 12.4 Validation ladder and acceptance handoffs

Implementation starts with contract/unit fixtures, then `pytest tests/test_cli.py`
after every Snakefile or config-shape edit. Because the landing changes
`shared/`, rule signatures, runner/config composition, and numerical outputs,
the pre-merge gate is `pixi run test-full`, with output redirected to a file.
Before the milestone seals: run P2b, fresh dry-runs for both entry points and
both simulation modes, one rapid generation/simulation execution, `tree-check`, GF-9,
GF-15's bounded methodological matrix, GF-28's temporal preservation fixtures,
and the standing regression-baseline/tree comparison under its documented current-config
limitations. No such command has run for this design draft.

Model-validator acceptance is required separately for:

- generation: forcing completeness, time/calendar/units, pairing evidence, and
  perturbation plausibility, including direct same-realization ancestry and
  declared-ancestor consumption;
- simulation: forcing compatibility, model/settings identity, Wflow completion, and
  hydrological plausibility/equivalence, including the recorded
  source/prepared/response calendar and endpoint chain; and
- metrics: response coverage, estimator preconditions, metric vocabulary,
  explicit Class-C reference-location migration, stage-3 environment identity,
  per-location fit validity, the bounded GEV screening validation, and
  result/index integrity. The model-validator record states whether `1.0`/`10`
  passed §7.5's bounded criteria; absence or failure leaves them provisional.

## 13. Implementation ownership briefs

These are bounded handoffs after design acceptance, not work authorized by this
draft.

| owner | implementation scope | deliverable | acceptance gates |
|---|---|---|---|
| Python engineer | logical adapters, manifests/digests, validators, Snakefiles, config composition, runner, tests, reference migration | reference-atomic implementation in the files inventoried by §9.6 | GF-1..GF-28 structural gates, CLI/full suite, tree check |
| model builder | bind current weathergenr and Wflow operations to the specified provider/simulator interfaces; retain execution resources/logs | production bindings and rapid fixture outputs | generator and simulation model-validator handoffs |
| geospatial data analyst | verify source inventory and forcing descriptors for climate/grid metadata | descriptor and compatibility assessment | path/CRS/grid/time/unit acceptance |
| model validator | judge generated forcing and Wflow response equivalence/plausibility | signed stage-1 and stage-2 acceptance records | §12.4 criteria; no stage integrates before return |
| stress-test analyst | implement/verify declarations, grouping/reference rules, response needs, and migration comparator | accepted metric registry and comparison record | GF-6, GF-9, GF-13..GF-15, GF-21/GF-24 |
| CST architect | integrate handoffs, verify slot bindings and DAG boundaries, maintain decision record | accepted successor design and integration gate | all required handoffs returned; no projection forcing edge |

## 14. Traceability and revision history

### 14.1 Decision-to-section map

| retained decision | disposition in v3 |
|---|---|
| S1–S8 | §§2.2, 3, 4, 5–7, 9.1 |
| R-1, R-2 | §§2.2, 7.2, 12.3 |
| R-3 | §§2.2, 5.1, 12.1 GF-18 |
| R-4 | §§2.2, 7.5, 10, 12.1 GF-15 |
| R-5 / W4 | §§2.2, 8.1, 10, 12.1 GF-16/GF-17 |
| R-6 / E18 | §§1, 2.2, 5.1 |
| W1, W2 | §§7.4, 8.1 |
| W3 | §§5.1–5.3, 7.2; scenario type reference stays registered rather than embedded |
| D1, D2 | §§4.3–4.4, 5.3, 6.3, 12.1 GF-11 |
| D3 | §§5.5–5.7, 8.2, 8.5 |
| D4, D5 | §§7.1–7.5 |
| D6 | §§5.2, 12.1 GF-1..GF-3 |
| D7 | §§4.2, 9.5 |
| D8 | §12 |

V4 preserves all earlier gate identifiers GF-1 through GF-27 and records their
changed premises in §12.1. The temporal-preservation falsifier is GF-28.
Earlier evidence E1–E17 remains the basis for eliminating parsed ids, sentinels,
and hidden bundling; E18 is confirmed by the candidate scenario-type schema; E19's
overlay-coordinate concern remains outside the execution seam; E20's member
hash role is subsumed by collection and response artifact digests (§§8.2–8.4).

#### 14.1a Qualified evidence closure from the v3 domain review

The frozen intake remains unchanged. V4 carries the authoritative review's
qualified dispositions rather than converting historical premises into blanket
endorsement (`domain-v3-7`):

| premise | qualification retained in v4 | settling observation / scope limit |
|---|---|---|
| E6 | Realization-wildcard batching has expired, but failure-identification needs have not: batch filenames are batch keyed while the Julia driver still associates success/failure messages with each TOML-derived run tag. | Stage 2 preserves explicit per-`run_id` failure association (§6.5); no further production change is required. |
| E13 | The current member naming pattern and pinned-surface wording are in WG-4, not WG-2. | Reading the live seam headings settles attribution; §9.2 already replaces WG-4 correctly. |
| E17 | Renumbering is conditional. Increasing only realization count appends rows under the approved ordering, while changing the design-point count shifts later realizations; capacity can change width. | The algebra settles the overbroad claim without a run. Immutable collection scoping remains required even when some positions survive. |
| E19 | A paper schema proves representability, not scientific comparability of future projection-derived coordinates. | Outside current production scope. A future provider must supply an example with explicit reference period, aggregation, units, and comparable surface coordinates before this premise can be supported; it remains terminal and cannot select a run. |

### 14.2 Finding-to-section map

Every cumulative-ledger id remains accepted except the explicitly deferred
`domain-7`; v3 changes mechanisms where the approved split supersedes v2.

| finding IDs | v3 resolution |
|---|---|
| `domain-1`, `domain-8` | per-run Class C with one shared reference month; §§7.2, 12.3 |
| `domain-2`, `domain-10` | pairing evidence and confirmed neutral-scenario-type need; §§1, 5.1 |
| `domain-3`, `domain-4` | ratio-shaped return-level precondition and reachable falsifier; §§7.5, 12.1 |
| `domain-5` | executable Class A/B/C crosswalk and coverage comparator; §12.3 |
| `domain-6` | general unevaluated-reference fixture without retired config; §§5.1, 7.2, GF-14 |
| `domain-7` | **deferred** fit-uncertainty transport; §7.6 and §11.2 |
| `domain-9` | configured-axis payload and completeness; §§5.1, 5.5, GF-24 |
| `arch-1`, `arch-2` | simulator independent of scenario type and no unsupported forcing URI; §§5.3, 6.3 |
| `arch-3`, `risk-4` | `run_` inventory keys and evaluated-set equality; §§5.6, 6.7, 9.1 |
| `arch-4`, `arch-10` | complete standalone unit/index invariants and discovered width; §§7.4, 8.1 |
| `arch-5` | current always-evaluated unperturbed cases and explicit requested run set; §§5.1, 6.7 |
| `arch-6`, `risk-11` | complete reference-atomic live inventory; §9.6 |
| `arch-7`, `risk-8` | separated provider/metric code digests and invalidation; §§8.2–8.5 |
| `arch-8`, `risk-1` | content-addressed immutable readiness and honest interrupted-run limitation; §§5.6–5.7, 8.6 |
| `arch-9` | collection climate files deliberately become durable; simulation adapter intermediates retain temporary lifecycle; §§5.7, 9.2 |
| `risk-2` | cheap forest validation retained while unsupported ingest path remains absent; §§5.1, 10 |
| `risk-3` | unexecuted P2b is a pre-implementation gate; §§5.2, 11.3, 12.1 |
| `risk-5` | empty design key retained in bundle/index/results; §§7.3–7.5 |
| `risk-6` | mixed sequence retained on merits with explicit capacity; §§8.1, 10 |
| `risk-7` | normative stochastic row order; §§5.1, 8.1 |
| `risk-9` | honest evidence taxonomy; front matter and §12 |
| `risk-10` | concrete schema/path/validator replacements throughout §§5–9 |
| `domain-v3-1` | direct same-realization stochastic ancestry and declared-ancestor consumption; §§5.1, 12.1 GF-18 |
| `domain-v3-2` | persisted Class-C reference location, statistic, tie rule, coverage, and resolved months; §§6.6–6.7, 7.1–7.2, 8.4, 12.3 |
| `domain-v3-3` | separate per-location sample screening, fit validity, and bounded scientific adequacy; §§7.5–7.6, 11.2–11.3, 12.1 GF-15 |
| `domain-v3-4` | stage-3 environment descriptor enters metric-set identity; §§7.4, 8.4–8.5, 12.1 GF-6 |
| `domain-v3-5` | explicit seed-material projection excludes capacity and identity/storage choices; §§9.4, 12.2 GF-27 |
| `domain-v3-6` | source/prepared/response calendars and current conversion/clip/endpoint behavior are explicit preservation cases; §§5.3, 6.4, 6.6–6.7, 7.5, 12.2 GF-28 |
| `domain-v3-7` | E6/E13/E17/E19 retain qualified dispositions and settling observations; §14.1a |

This table covers all ten original `domain-*`, ten `arch-*`, eleven `risk-*`,
and seven `domain-v3-*` ids in the cumulative ledger. It does not change the
original reviews or their dispositions.

### 14.3 Revision history

| version | date | state | change |
|---|---|---|---|
| v1 | 2026-09-07 | historical | initial design from frozen intake and P1/P2 evidence |
| v2 | 2026-09-07 | historical reviewed revision | incorporated 31 internal findings and R-1..R-6; selected one-workflow logical three-stage design |
| v3 | 2026-09-09 | proposed, unreviewed successor | incorporates approved two-workflow scope expansions; durable scenario collection; simulator-neutral response view; independent metrics mode; revised fingerprints, readiness, retention, config/runner migration; current R14 config facts; and corrected P3/P4/P5 premises |
| v3 naming revision | 2026-09-09 | owner-approved naming; design still unreviewed | selects “Simulate system behavior” and `simulate_system.smk`; aligns workflow/config/runner names and proposed simulation-run identifiers to describe long-term behavior under scenarios |
| v3 terminology revision | 2026-09-09 | owner-approved terminology; design still unreviewed | defines scenario, design point, realization, metric bundle/unit, response series, and metric/indicator value; separates unperturbed, historical, reference, and regression baseline; renames collection-wide `simulation_run_id` / `simulation_run.json` to `simulation_id` / `simulation.json`, with `simulation/1` and `SimulationFrozenError`, preserving `run_id` and `unit_id` semantics |
| v3 scenario-type revision | 2026-09-09 | owner-approved terminology; design still unreviewed | replaces family with scenario type (`stochastic`) throughout the proposed contract, including `scenario_type`, payload/artifact identifiers, registry declarations, and simulator independence; preserves historical source filenames and classification semantics |
| v4 | 2026-09-09 | proposed revision; not reviewer-approved | incorporates the G1-v3 correction package: exact stochastic ancestry, explicit Class-C reference provenance, separate GEV screening/fit-validity/bounded-validation contracts, metric-execution environment identity, capacity-free automatic seed material, temporal preservation gates, and qualified E6/E13/E17/E19 closure |

V4 retains v3's intentional supersession of v2's one-entry-point non-goal, metric-coupled width,
in-place success-marker guard, live `run_historical` premise, and experiment-name
seed dependency. It preserves v2's run/unit identities, settled method rulings,
seam independent of scenario type, explicit grain, formulas, comparator obligations, and finding
traceability. V4 does not claim that the provisional GEV thresholds or any
unrun numerical result pass. Proposed choices remain proposals until the named
empirical gates and reviews accept them.
