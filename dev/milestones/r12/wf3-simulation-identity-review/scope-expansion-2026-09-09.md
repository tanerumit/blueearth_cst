# Scope expansion — explicit WF3 simulator boundary

**Status:** approved scope expansion; temporary addendum awaiting successor design revision and review

**Date:** 2026-09-09

**Lifecycle:** temporary; transfer its obligations into the next `design-vN.md`, then retain this as historical run evidence

**Parent design:** `design-v2.md` (2026-09-07)

**Code reference:** repository commit `e3b77760757efa4f33fdd9d39b5133fde1ecfc66`

**Review state:** external r1 paused, zero external rounds complete; no prior review covers this expansion

**Revision:** addendum v2

**Authority:** owner approval on 2026-09-09: “yes, lets broaden to cover as you describe”

**Additional authority:** owner approval on 2026-09-09: “yes, lets expand it in this direction”, following the proposal for two independently runnable workflows with three logical stages and contract extraction before workflow extraction.

## 1. Authority

This widens the open R12 `wf3-simulation-identity` design boundary. It is scope authority and a revision handoff, not an accepted revised design, implementation plan, or review verdict.

The frozen intake and ledger dispositions remain scope inputs, except that this revision explicitly supersedes the intake's deferred WF3 file split and v2 §2.2's one-entry-point constraint. Owner rulings remain binding:

- **R-1:** Class C uses one month selected in advance and shared by all realizations.
- **R-2:** Class C is stored at `grain: run` with a required `reference`.
- **R-3:** the family registry declares `paired_across_design_points`, `independent`, or `none`; a paired claim requires supporting `derived_from` edges.
- **R-4:** the precondition is expressed per return period. V2 selects `blocks_per_return_period = 1.0` plus a separately argued ten-block identifiability floor; this expansion neither changes nor validates that proposed design text.
- **R-5:** W4 is direction, not a ruling; the single mixed sequence stands on the merits argued in v2.
- **R-6:** E18 is confirmed and remains a milestone precondition.

V2’s `run_id` for simulation runs and `unit_id` for run-or-bundle results already provide the neutral identity vocabulary. `result_id` is only a considered name; it does not override that later ruling or authorize another rename. [cited: v2 §5.5.1]

## 2. Request and affected capabilities

**Request type:** improve the in-progress WF3 architecture by widening its simulation seam and targeting two independently runnable workflows while retaining the current assessment method.

Affected slots are `decision_framing` (frozen intake and R-1..R-6), `data_adapter` (HydroMT/`hydromt_wflow`), `ensemble_generator` (`weathergenr`), `simulation_engine` (Wflow), `system_model_validation`, `performance_analysis` (current metrics), and `orchestrator` (Snakemake). Bindings are the code reference above; weathergenr and Wflow remain the only production implementations. `impact_model` and `robustness_evaluation` are not applicable because no impact output or option×scenario matrix is added. `projection_overlay` is not part of execution; WF2 remains a terminal plausibility overlay.

The broader execution-control system (run manifests, namespace claims, fencing, resume ledgers, and atomic publication machinery) remains outside this design. The split does require a bounded handoff contract for collection readiness, identity, retention, and invalidation; deferring the execution-control system must not defer those obligations.

## 3. Expanded boundary

The selected destination is **two independently runnable workflows with three logical stages**. Establish and verify the adapter contracts within existing WF3 first, then extract the workflow entry points. The adapters make stage contracts testable; they do not create a general plugin system.

| workflow | stages and responsibility | durable handoff/output |
|---|---|---|
| Scenario generation | Stage 1: define the experiment, generate climate realizations, apply perturbations | Scenario collection: inventory and referenced climate series |
| Impact simulation | Stage 2: prepare model-specific forcing, execute, expose responses; stage 3: derive metrics as an independently targetable operation | Simulation inventory and retained response artifacts sufficient to recompute supported metrics |

These are responsibility labels, not approved filenames or config keys. The successor design must settle those names and the fate of `run_stress_test.smk` explicitly. A third metrics workflow is not required: independent targeting inside the impact workflow is the initial destination.

Stage 1 produces identified climate scenarios. Scenario-family metadata stays outside simulator execution. A generator adapter may interpret its family payload; the simulator receives universal run identity, compatible forcing, and the built model/settings required for that run.

Stage 2’s simulator adapter owns the full engine boundary:

1. validate forcing compatibility;
2. prepare engine-native forcing and run configuration;
3. execute the simulator; and
4. read native results into the response-series interface used by stage 3.

Stage 3 declares each metric’s input requirements and grain. It must not parse Wflow filenames, TOML names, or `rlz`/`st` tokens to recover identity.

The impact workflow must consume a completed scenario collection without executing its producer. Scenario generation must not require a built Wflow model or execute the simulator; shared spatial/climate prerequisites may still be required. Metrics must be recomputable from retained simulation outputs without regenerating scenarios or rerunning Wflow. If a newly requested metric requires a response variable that was not retained, refuse with an explicit requirement rather than silently starting simulations. [proposed, untested]

This scope adds no production second backend, discovery system, CMIP-driven run, baseline-method revision, or local calibration. The two-workflow split is now in scope; the previous no-extra-workflow clause is superseded.

## 4. Interface obligations

### 4.1 Generator output

Each climate scenario has the existing sequential `run_id` and a forcing reference. Family metadata stays in the scenario table/family block, including pairing and derivation edges where applicable. The simulator adapter may not branch on those fields. [proposed extension of v2 §§5.1–5.2]

### 4.2 Forcing compatibility

Before preparation, the adapter validates and records forcing variables, units, spatial representation, calendar, timestep, and temporal coverage. The successor must state where each fact originates, which are required, and the refusal for mismatch; it must reuse HydroMT semantics rather than duplicate them. [proposed]

Compatibility and freshness are distinct. Passing compatibility does not prove forcing is current, and equal `run_id` values never authorize reuse after a result-affecting forcing change.

### 4.3 Simulator adapter

The adapter is addressed by `run_id` and returns it unchanged. Wflow paths and formats stay private to its implementation. Preparation, execution, and native-result reading are one adapter responsibility even if Snakemake retains separate scheduling and persistence rules. [proposed]

Existing per-run visibility and batch failure semantics remain unless the successor argues and reviews a change.

### 4.4 Response series

For each series, metrics receive run identity, response variable, location, time coordinate, units, values, and missingness representation. The successor must define cardinality and refusals without prescribing a Wflow filename or CSV header. [proposed]

This is an interface or view, not a required persisted normalized copy. Fixtures may materialize it; production persistence needs separate justification. [proposed, untested]

### 4.5 Metric grain and bundles

Each metric declares required response variables, temporal coverage/granularity, location grain, missingness tolerance, output grain, and any reference or bundle requirement. R-1 through R-4 remain the initial metric decisions. [proposed extension of v2 §5.4]

A valid bundle contains unique evaluated runs, equals the membership produced by its declared grouping, and passes the metric’s record/precondition checks. Pairing claims must agree with the family registry and `derived_from` evidence. A run may enter different metric-specific bundles; membership is never a simulator property. [proposed]

### 4.6 Identity and freshness

Sequential `run_id`/`unit_id` values remain human-and-join handles. Stale reuse must instead depend on separate fingerprints for scenario inventory, forcing content/metadata, built model, and result-affecting settings. The successor defines composition and ownership; this addendum does not invent an API or storage schema. [proposed]

The scenario-table digest remains an inventory identity, not a forcing/model/settings fingerprint. None of these fingerprints replaces the sequential id. [cited: v2 §§5.5.3–5.5.4]

### 4.7 Durable scenario handoff and independent consumption

The successor must specify a scenario collection that survives the producer process and can be consumed by separate impact runs. Resolve the following before extracting entry points. These are design obligations, not a selected storage or publication mechanism. [proposed, untested]

- **Readiness:** define when inventory and referenced climate artifacts form a complete, compatible collection. An inventory written at DAG construction is not evidence that its climate files exist or are complete. State how missing, partial, or changed artifacts are refused before simulation.
- **Resolution and identity:** define collection identity/version, how paths resolve from the collection, and how an impact run records exactly which collection it consumed. Run ids are scoped to their collection; consuming one collection in multiple impact runs must not overwrite or relabel it.
- **Retention and ownership:** identify durable producer outputs versus disposable internals. Consumer completion must not delete shared climate inputs. Preserve sufficient native response artifacts for metrics-only execution; no normalized duplicate is required. State who may remove either collection and how disk cost is exposed to the user.
- **Invalidation:** distinguish changes to scenarios, model/settings, and metric definitions. Specify which downstream artifacts become stale, and how a consumer detects collection changes after its inventory was recorded. A metric-only change with available inputs must not invalidate scenario generation or simulation.
- **Prerequisites:** map shared spatial/climate preparation separately from Wflow model preparation. Name what each workflow actually requires; removing an entry-point dependency must not hide an artifact dependency.

## 5. Alternatives

**A — identity only.** Keep v2 and leave Wflow preparation, execution, and reading implicit. Smaller, but unable to prove simulator substitution without leaking `rlz`, `st`, TOML, or native-output knowledge. Rejected for the successor because it misses the approved expansion.

**B — adapters inside one workflow (intermediate step).** Define and test the contracts within current WF3. This minimizes simultaneous changes and remains preferable as the first implementation step, but stops short of the approved independent-execution destination.

**C — plugin framework.** Add discovery, third-party loading, version negotiation, and another production implementation. Deferred until a real external implementation supplies requirements; preferable only when independent deployments must extend WF3 without repository edits.

**D — two workflows, three stages (selected destination).** Extract scenario generation and impact simulation after their durable handoff works; make metrics independently targetable within impact simulation. Independent reuse justifies the additional configuration, retention, and migration contracts. A separate third metrics entry point is deferred until independent targeting proves insufficient.

## 6. Current-code grounding

- Rule 3.14 and `downscale_climate_forcing.py` prepare Wflow forcing and write the per-run catalog and TOML: the current forcing-preparation boundary. [cited]
- Rule 3.15 builds static forcing/TOML batches and CSV outputs; `run_wflow_batch.jl` derives its visible member tag from the TOML stem and calls Wflow: the execution boundary. [cited]
- Rule 3.16 and `export_wflow_results.py` read Wflow CSVs, recover `(rlz, st)` from stems, discover variable/location columns, and compute metrics: the native-reader/metric seam to split. [cited]
- P3 measured that `run_<id>` works as the HydroMT catalog key, subject to its recorded filename limits. [measured]
- P4 measured rerun triggers and corrected GF-16: config changes already re-fire 3.09; imported-module body changes remain invisible without a digest. [measured]
- P5 measured that run-path renames classify under directory prefixes; v2’s two new config leaves need explicit inventory rows. [measured]
- No synthetic-provider/dummy-simulator architecture check has run. Every new adapter, compatibility, response, bundle, and multi-fingerprint clause remains proposed. [untested]
- Current `generate_weather_realizations` and `perturb_climate_realization` outputs are declared `temp()` in `run_stress_test.smk`; a durable collection cannot inherit that lifecycle unchanged. `scripts/run_workflows.py` declares a closed four-workflow contract. Both are migration surfaces for the split, not conventions the new design can assume already support it. [cited: named rules and runner module docstring, 2026-09-09]

## 7. Acceptance criteria and falsifiers

1. **Same route:** a fixture-only synthetic provider and dummy simulator traverse the same stage-2 orchestration and stage-3 metric entry points as production. Falsifier: a test-only bypass or alternate workflow.
2. **No family leakage:** the synthetic scenario has neither `rlz` nor `st` and still runs. Falsifier: stage 2 requires either field or parses it from identity/path.
3. **No Wflow leakage:** dummy output has no TOML or Wflow filename/header. Falsifier: stage 3 needs one to identify or reduce the response.
4. **Compatibility refusal:** fixtures vary every required forcing fact. Falsifier: incompatible variables, units, space, calendar, timestep, or coverage reach execution without a named refusal.
5. **Response completeness:** metrics receive identity, variable, location, time, units, and missingness. Falsifier: a required fact is inferred from a native path or silently defaulted.
6. **Metric declaration:** a response or bundle violating declared inputs/membership is refused. Falsifier: reduction relies on loop placement, a sentinel, or undeclared pooling.
7. **Freshness separation:** equal sequential ids with changed forcing/model/settings do not qualify for reuse. Falsifier: id equality or the inventory digest alone authorizes reuse.
8. **Numeric migration:** the one-off crosswalk comparator required by v2 GF-9 preserves Class-A/Class-B values, verifies old Class-C pooled values against the mean of new per-run values under R-2, and accounts for every row. Falsifier: unexplained numeric movement or missing coverage; a structural `check_baseline.py` failure is not this comparison.
9. **Production restraint:** only weathergenr and Wflow are production bindings. Falsifier: another backend, discovery, a third metrics workflow, CMIP forcing selection, baseline-method change, or calibration path lands here without a new scope decision.
10. **Rulings preserved:** R-1..R-6 and `run_id`/`unit_id` remain consistent. Falsifier: the successor silently changes one.
11. **Independent execution:** finish generation, end that invocation, then consume its collection in a separate impact invocation. Falsifier: generation requires the built Wflow model, or impact invokes the generator to consume a valid completed collection.
12. **Durable reuse:** two separate impact outputs consume the same collection without changing it. Falsifier: consumer completion deletes climate inputs or one consumer overwrites the other's results. A dummy adapter may demonstrate this; no second production backend is required.
13. **Incomplete/stale collection:** remove or alter a declared climate artifact after inventory creation. Falsifier: execution silently treats the collection as ready and unchanged.
14. **Metrics-only execution:** change a metric definition with required responses retained. Falsifier: generation or simulation executes, or required response data is silently fabricated when absent.

## 8. Successor revision and review handoff

The next `cst-architect` author must write a self-contained successor to v2, replacing superseded normative text rather than appending this addendum wholesale. Update at least §§2.1–2.2, 5.1–5.2, 5.3, 5.4, 5.5.4, 5.6, 6, 7, 8, 9, 10, and 11.

The implementation sequence to design is: **(1)** specify collection handoff and independent execution; **(2)** extract and verify contracts within existing WF3; **(3)** extract the two workflow entry points and expose metrics-only targeting. Preserve the existing atomic identity/schema migration obligation within that sequence; it does not require collapsing every architectural step into one change.

The successor's derived-artifact register must cover new entry-point names, project/workflow config composition and templates, `scripts/run_workflows.py` and its contract tests, DAG checks, prerequisite ordering, storage inventories and cleanup policies, and live user references (`README.md`, `AGENTS.md`, workflow/config migration docs). Decide compatibility or retirement of the old WF3 command and update every live reference in the implementation migration. These runtime and user-facing artifacts remain unchanged during this scope amendment.

Refresh evidence for rule 3.14, batch construction/driver behavior, and native-result reading; incorporate P3/P4/P5 corrections; mark claims cited, measured, argued, proposed, or untested. Every modeling boundary hands its forcing and response acceptance criteria to `model-validator` before integration.

Then repeat domain review over the changed forcing, response, and metric contracts, present the revised framing at the gate, and resume clean-room external review only against that successor. Prior reviews and `ledger.md` remain historical evidence for v1/v2, not verdicts on this expansion.

## 9. Remaining risks

- The smallest response view preserving calendars, units, and missingness without an expensive copy is untested.
- Fingerprint composition and persistence ownership remain undecided; omissions could permit stale reuse.
- Existing batches couple scheduling and paths to Wflow artifacts; preserving visibility and failure behavior needs proof.
- Metric bundle validity may expose assumptions beyond R-1..R-4 and needs domain review.
- The architecture check proves contract substitution, not scientific equivalence; production Wflow outputs still require `model-validator` acceptance.
- Durable climate collections may increase retained disk use relative to today's temporary files. Collection completion, reuse, and cleanup semantics remain untested; their cost and ownership must be resolved before workflow extraction.

## 10. Revision log

| revision | date | change |
|---|---|---|
| addendum v1 | 2026-09-09 | Records the approved adapter scope, preserves R-1..R-6 and v2 identity rulings, defines bounded interfaces and falsifiers, and hands the change to a successor revision and fresh review |
| addendum v2 | 2026-09-09 | Owner expands the destination to two independently runnable workflows and three logical stages; supersedes the deferred split, adds durable collection and metrics-only obligations, and sequences contract extraction before entry-point extraction |
