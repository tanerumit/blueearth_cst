# Named indicator sets and WF4 operation selection

Status: Proposed candidate v1 for G1 review; not implementation authorization.
Date: 2026-10-16. Owner: CST architect. Source checkout: main, `791fd1f9162d675eabc63de48825a6e4b4e74265`.
The seed remains a discussion record. This candidate is a frozen review snapshot; revise in a new version.

## Decision and boundary

Expose `operations: [simulations, indicators]` and `indicator_sets: [default, low_flows]`.
Either operation can run alone. Named YAML sets select shared registered Python calculations and publish
separate readable tables over shared retained responses. Indicator-only execution cannot start Wflow.
These interfaces, user YAML, reusable methods, named exports and machine data under `_engine/` are agreed.
Every detailed choice marked P below is a recommendation for G1, not approved policy.

The reusable gap is WF4's single metric request/export selection, not a geographic assessment gap.
Serve existing WF4 default users and projects needing multiple analyses of the same response inventory.
Minimum delivery: named selection, default preservation, independent reuse and recoverable publication.
No new formulas, scenario generation, model physics, expression language, dynamic plugins, cross-set
calculation cache, robustness scoring, or new orchestration engine are commissioned.
The second scientific set remains unspecified; `low_flows` is only an example name.

## Current behavior and evidence

All source paths here are repository-root paths; line numbers refer to the source commit above.
These are inspection observations, not execution evidence.

- **E1: operation and targets constrain each other:** Supported: `experiment/simulation_runner.py:45-91` under
  `blueearth_cst/`; two scalar operations, one checked target.
- **E2: one flat export and pointer:** Supported: `blueearth_cst/experiment/metric_export.py:43`;
  `results/metric_sets/*.csv`, `_engine/metric_sets/current.json`.
- **E3: run/bundle and group policies:** Supported:
  `blueearth_cst/experiment/metric_registry.py:128,298,342,522`.
- **E4: response, code and environment identity:** Supported:
  `blueearth_cst/experiment/metric_plan.py:242,350`; definition, response and environment digests, groups and
  references.
- **E5: frozen simulation inputs for indicator-only:** Supported with qualification: `metric_plan.py:84` still
  reads live metrics, model.outvars and water-year settings; it does not open generation/model workflow files.
- **E6: default adapter can preserve numbers:** Testable hypothesis; policy map and C4 below define the
  falsifier. No parity evidence yet.

Current `metric-set/3` writes paired token/run and token/group tables. Their four columns are
`metric,location,run_id,value` and `metric,location,group_id,value`, respectively; lookup is
`group_id,run_id`, metadata is `group_id,st_id,is_reference`.
Authority: `metric_plan.py:822` and `shared/interchange_contracts.py:849` under `blueearth_cst/`.
Some shared indicator-table prose still describes retired five-column/grain behavior; do not copy it.
Wet/dry reference-month indicators now have run values and equal-weight group summaries.

## User configuration and execution (P1)

Keep the project's closed `workflows.simulate_system: {enabled, config_path}` descriptor.
The WF4 YAML contains the following new fields alongside its existing simulation settings:

```yaml
experiment_name: experiment_rapid
operations: [indicators]
indicator_sets: [default, low_flows]
indicator_set_definitions:
  low_flows:
    config_path: indicator_sets/low_flows.yml
```

- **operations:** Nonempty list of unique strings from simulations, indicators; omitted means both. Order does
  not control dependency order.
- **indicator_sets:** Nonempty list of unique set IDs when indicators selected; omitted means [default].
- **indicator_set_definitions:** Optional mapping from set ID to exactly {config_path: nonempty string};
  default {}.
- **ID:** `[a-z][a-z0-9_]*`, at most 64 characters; reject Windows reserved basenames, path components,
  separators and aliases.

Reject nulls, scalar/list type substitutions, unknown fields in these structures, duplicate YAML mapping
keys, duplicate selections, unknown names, and bundled/custom name collisions. Require definition ID to
match its mapping/selected name. No environment interpolation or arbitrary YAML object construction.
With simulations alone, validate selection structure but do not open/resolve set files or require
nonempty indicator_sets; an explicit empty list is allowed only on this inactive branch.

Bundled names resolve against toolbox `config/indicator_sets/<id>.yml`, anchored to the installed
repository/package resource root, never current directory. Custom `config_path` accepts absolute paths;
relative paths resolve against the WF4 YAML containing the mapping. Other existing project path rules
remain as implemented. This new local path rule must be documented beside that field.
Resolve and read selected YAML once before execution; capture bytes and use that resolved snapshot
throughout the invocation. A concurrent source edit must not change an admitted plan.

Both public runners infer targets; the ordinary command needs no target:
`pixi run python scripts/simulate_system.py --config path/to/project_config.yml`.
The all-workflow runner retains its own workflow-enable contract. Selecting indicators in WF4 never
implicitly enables WF1/WF3. Independently enabled upstream workflows remain explicit user requests.

- **both, in either order:** Validate selected definitions/requirements; run or reuse simulations once;
  plan/reduce selected sets over completed responses.
- **simulations only:** Existing simulation path and identity; no indicator planning or publication.
- **indicators only:** Read completed retained simulation/response inventory and applicable live analysis
  settings; no generation, forcing preparation, model build, Julia probing or Wflow producers.

Neither operation means force. Missing/incompatible responses fail with set, method, variable and reason;
suggest a separate simulation request when necessary, never schedule one as repair.
Check the union of required variables against configured response_request before costly simulation
work and against actual retained inventories before reduction. Do not silently add model outputs.
Water-year start remains project `climate.water_year_start`; indicator-only uses its current value,
as today, and records it in analysis identity. Users need not reopen simulation/model configuration.

## Closed set schema and ownership (P2)

A set file has exactly required `schema_version: 1`, `id`, nonempty `title`, `description` (string),
and `selection`. Selection is exactly one of `{preset: current_default}` or
`{indicators: [<entry>, ...]}`; explicit lists are nonempty and cannot repeat resolved metric IDs.
Only bundled `default` may use the preset. No YAML include/inheritance machinery is introduced.

```yaml
schema_version: 1
id: default
title: Default indicators
description: Existing WF4 indicator suite for the selected response variables.
selection:
  preset: current_default
```

A custom set selecting existing definitions uses the same file schema:
```yaml
schema_version: 1
id: example_subset
title: Example discharge subset
description: Illustrative reuse, not an approved second scientific set.
selection:
  indicators:
    - definition: q_annual_mean
    - definition: q_mean_annual_7day_min
```

An entry is exactly `{definition: <registered definition ID>}` OR exactly
`{id, title, description, references, calculation}`. Authored IDs use the safe ID rule above;
titles/descriptions are strings, references is a list of nonempty citation strings, and calculation
is exactly `{method: <registered method ID>, parameters: <method-validated mapping>}`.
Authored IDs cannot shadow a registered definition; no metadata/parameter overrides on references.
No user units, calendar, grain, missingness, aggregation or reference-policy fields are accepted.
Those are method contracts; unsupported declarations fail instead of being silently ignored.

Extend `blueearth_cst/experiment/metric_registry.py` as the single registry owner, keeping pure
calculations in `shared/metrics_definition.py` and existing estimator adapters. Add a small
`experiment/indicator_sets.py` resolver; avoid a parallel `indicators/` framework or wholesale move.
Existing definition IDs, suffixes and variable vocabulary remain owned by `shared/indicator_tables.py`;
the registry derives definition records from them. Set YAML references those records, not copies.
The default preset delegates to existing token/declaration selection rather than duplicating a list.

Initial registered method contracts wrap existing reductions only:
| Proposed method ID | Exact parameters; existing calculation |
|---|---|
| annual_summary/1 | {variable, statistic}; q allows mean/max/min/p95; aet/gwr/precip only sum; snow only max; overland_flow only mean. |
| annual_rolling7_extreme/1 | {extreme: min or max}; q only; existing Q7d_min/Q7d_maxyear. |
| annual_min7_mean_ratio/1 | {}; q only; existing BFI. |
| reference_month_mean/1 | {which: wet or dry}; existing fixed Class-C reference resolver/reduction. |
| pooled_return_level/1 | {kind: annual_max or rolling7_annual_min}; fixed current periods 10/2 years respectively. |

All parameter maps reject extras and omitted required keys; no implicit numerical defaults.
These method IDs are proposed toolbox vocabulary, not claims that functions already expose it.
A registered definition resolves to method, validated parameters, authoritative metadata and policies.
The adapter must preserve existing reducers; it must not reimplement their arithmetic.
Method registration declares response variable/units/timestep/time-label/calendars, output units,
run or bundle grain, group policy, references, temporal/missingness/validity policies and implementation
revision, plus closed parameter validation. Do not infer output units from input units: BFI is
dimensionless; annual totals integrate mm dt-1 to mm over an annual block.
Registry metadata describes the method truthfully; scientific changes require separate qualification.

## Default preservation map (P3)

Default token precedence must match today:
legacy metrics override when admitted by P6; otherwise project model.outvars if present;
otherwise DEFAULT_WFLOW_OUTVARS on simulation paths, retained response_request variables on
indicator-only paths. Expand each token with the existing declarations, including all 11 q definitions.
The preset is configuration-dependent; it does not silently mean all physically available variables.

- **q mean/max/min/p95:** Annual statistic then mean over years; p95 is 95th NON-exceedance percentile, a high
  flow. `metric_registry.reduce_run`.
- **q 7-day extrema:** Rolling(7).mean over each complete member first, then annual min/max then mean; windows
  can cross water-year boundaries, never member boundaries. `metrics_definition.Q7d_*`.
- **q BFI:** Mean over years of annual minimum rolling-7 mean divided by annual mean; existing NaN/infinity
  handling. `metrics_definition.BFI`.
- **aet/gwr/precip, snow, overland_flow:** Mean of annual sum, max, mean respectively; retain names/units and
  per-location treatment. `BASIN_METRIC_SUFFIXES`, `reduce_run`.
- **wet/dry q month:** Pooled unperturbed evaluated members, same first native q gauge, calendar-month sums;
  first month on ties; apply that one resolved month to every run/location. `resolve_month_reference`.
- **Non-return-level groups:** Equal-weight mean of run reductions, explicit NaN propagation, not length
  weights or a pooled daily series. `reduce_group_mean`.
- **Return levels:** Member-local annual maxima / rolling-7 annual minima, then pool blocks by design group;
  L-moment GEV adapter, fixed 10/2-year quantiles. `reduce_bundle`, `gev_lmoments`.
- **Return-level screening:** Retain partial periods; drop nonfinite annual blocks; minimum max(ceil(T),10);
  finite values, no clipping; tested probability guard and retained shape-coverage reporting. Existing
  screening is provisional operational policy, not scientific adequacy proof.
- **All families:** Daily interval-end responses; current standard/Gregorian/proleptic Gregorian declarations;
  current project water-year anchor, partial years retained and native pandas skipna/rolling completeness. No
  new incomplete-year exclusion policy.

Reference-free subsets must not acquire wet/dry reference requirements. Bundle-only subsets retain
header-only run tables; all declared groups, including singleton groups, keep explicit membership.
Keep current numerical serialization (including float32 conversion and value formatting) and exact
result-key coverage. New metadata may clarify units/limitations without redefining old metric IDs.

## Planning, identity and publication (P4)

Resolve selected sets once, deduplicate only identical numerical requests, then create one existing
metric plan per distinct resolved set contract over the shared response inventory.
Extend the current checkpoint/rule interface to carry that mapping; never obtain set IDs by parsing
an escaped wildcard. No run per set and no projection-derived dependency is introduced.

Keep simulation identity independent of operations, set IDs, files and metadata. Set selection is
analysis intent, not frozen simulation intent. Update admission/reservation/snapshot projections
accordingly; raw source snapshots may record it without making it simulation identity.
Numerical identity retains current response, normalized declarations/parameters/policies, references,
groups, water-year anchor, code inventory, environment and estimator validation evidence.
Exclude set display name/title/description/citations/source path and selection order. Sort resolved
definitions canonically; changing a numerical parameter or implementation changes numerical identity.
Metadata edits create a new publication identity, reuse numerical results and never mutate old records.
Do not promise reuse across changed implementation inventories.

Proposed new records use `metric-request/4`, `metric-set-identity/4`, `metric-set/4`.
Their delta is explicit resolved method/parameter/output-unit/policy records in declarations and
named-set-independent definition identity; current response/membership/environment integrity remains.
Keep read-only /3 support with its original projection validator. New writes use /4, with new IDs;
no rewriting old manifests or speculative aliasing of old numerical identities.
Reuse `collection-canon/1` content hashing and collision checks already owned by content_identity;
this proposal is not a migration to the separate cst-canon run-manifest protocol.

Proposed generated layout; immutable objects are authoritative, readable exports are derived:
```text
experiments/<experiment>/
  results/metric_sets/<set-id>/          # CSVs for latest successfully published named selection
  _engine/metric_requests/<request>.json
  _engine/metric_sets/<result>/          # immutable metrics.json, environment/evidence and data/*.csv
  _engine/metric_sets/names/<set-id>/
    definitions/<source-sha>.yml        # captured authored YAML bytes
    publications/<publication-id>.json  # immutable selection, metadata and file inventory
    current.json                       # replaceable pointer to committed publication
```

No hashes, machine JSON, plans or nested engine roots are exposed under named result folders.
Each named folder contains existing scoped CSVs and group_members/group_metadata only.
The publication record is a closed `named-metric-export/1` object with schema_version, set_id,
metric_set_id, metric_manifest (experiment-relative path + sha256), definition_source (path + sha256),
resolved_metadata (set and per-indicator ID/title/description/references/output_units),
files (basename -> sha256), publication_id and created_at. Compute publication_id from all semantic
fields except created_at/publication_id. current.json is exactly {schema_version: named-metric-current/1,
publication_id, publication: {path, sha256}}; all paths are confined experiment-relative paths.
Unknown schema/fields or digest mismatch fail. Metadata resolves once and is immutable per publication.

Hold existing project execution ownership through read/plan/publication. Validate complete immutable
results, stage all files and rollback copies under _engine, then replace owned exports and commit
the per-name pointer last. Reject symlinks/aliases, unknown files being overwritten, and ID/path
collisions. Ordinary I/O failure rolls back; preserve backups and diagnose if rollback fails.
CSV replacement is not an atomic multi-file read: consumers wait for completion and verify the pointer
inventory before use. After a crash, mismatched exports are not current; restore last committed
owned bytes from immutable results or refuse with retained recovery evidence. Never adopt user edits.
Validate existing results before scheduling forced producers: Snakemake update() alone does not
protect retained files during failed-job cleanup. Immutable data must survive forced reuse/refusal.

Preflight all requested sets before any calculation. Thereafter successful sets may commit
independently; a failed set keeps its prior publication. Return nonzero unless every requested set
completes, summarize current/failed names and identities, and identify mixed-age exports.
Retries reuse verified immutable results and retry failed publication; unselected names are untouched.
This is per-set completion, not an all-set transaction or a claim of managed run conformance.

## Compatibility and migration (P5/P6)

Recommend a deprecation window through one subsequent feature release; removal requires an explicit
follow-up decision and migration note. Do not invent a calendar date or silently remove aliases.
No automatic config rewrite occurs during execution.

- **operation: simulate-and-metrics + all:** operations [simulations, indicators], sets [default].
- **Same + simulations_only (alias responses):** operations [simulations].
- **operation: metrics-only + simulations_and_indicators (alias metrics):** operations [indicators], sets
  [default].
- **metrics-only + exact selected immutable output path:** Validate it belongs to the resolved default
  request; preserve this narrow legacy target path.
- **metrics token list:** Legacy-only default-preset filter; preserve precedence. New mode uses explicit
  definition references instead.

Legacy mode is selected by scalar operation; it retains its old explicit-target/default validation.
New operations/indicator keys cannot mix with operation/metrics/legacy target flags; reject with
replacement guidance. New mode uses inferred targets. Both runners share this normalization.
Legacy mode still publishes the named default export; it does not silently maintain two active views.

Old flat CSVs/current.json and old immutable /3 results remain readable evidence. Before first named
default publication, detect legacy flat export and report its migration; preserve its bytes and pointer.
New consumers explicitly select default or another name and never treat flat files as current /4 output.
Do not copy/delete/rewrite old files automatically. A separately requested cleanup can remove them later.
Readers supporting historical /3 use its manifest; current named readers use the new pointer.

Update public CLI/help, config templates and seeds, WF4 guides, layout/naming references, HM-7 validators,
inventory/baseline/tree-diff readers and all flat-path consumers in the same implementation.
Add the required migration note; register retired user keys when removal actually happens.
Do not regenerate the known-stale baseline to disguise a contract migration.

## Capability map, handoffs and acceptance

The ten run-control slots are the interface map, not a claim the current runner implements its manifests.
Only affected slots below change; the other six retain bindings: data_adapter (HydroMT),
ensemble_generator (weathergenr), system_model_validation, impact_model (not applicable here),
robustness_evaluation, projection_overlay. No slot or scientific-stage-graph version changes.

- **decision_framing:** Case manager's chosen indicators -> named definitions as recorded selections; case
  criteria unchanged.; Python engineer for serialization; case manager for selection/threshold authority.
- **performance_analysis:** Existing registry/planner/reducers -> YAML resolver + method adapters + /4
  records; retain /3 reads.; Python engineer; stress-test analyst for contract exercise, model-validator for
  policy/parity claim evaluation.
- **simulation_engine:** Wflow unchanged; response requirement preflight and simulation identity insulation
  exercised.; Python engineer adapter; model-builder exercises boundary, model-validator retains behavior
  authority.
- **orchestrator:** Two runners + Snakemake single-set path -> operation normalization and multiple
  plans/publications.; Python engineer; existing contract/integration validators under CST architect review.

These are scoped handoff requirements, not commissioned implementation briefs. Implement in order:
(1) resolver/registry and closed schemas; (2) runner/planner/DAG integration; (3) named export and
legacy readers; (4) docs/migration and acceptance evidence. No independent new calculation is needed.
Record immutable implementation revisions and actual validation authorities in any future managed
case binding. For such cases, a new scientific selection needs a new intent/analysis lineage;
post-hoc exploration must not mutate frozen decision framing or imply predeclared decision evidence.
Stage order and projection independence remain governed by climate-stress-testing/cst-run-control.

Acceptance below is planned, not executed. Use existing test fixtures derived from producer schemas;
select concrete commands from dev/reference/validation-ladder.md at implementation time.
Reuse the same affected rapid responses/outputs; no new simulation is required merely for this design.

- **C1 operation contract:** Either runner schedules wrong activities, reversed order changes behavior,
  invalid config passes; exercise three selections, defaults and invalid structures.; Existing runner tests /
  architect.
- **C2 indicator-only boundary:** Fail if model/generation files, Julia probing or simulation launch are
  touched; fixture uses completed responses and missing live files.; Model-builder integration exercise /
  architect.
- **C3 named independence:** Two subset sets conflict, metadata edit recomputes numbers, one changed set
  invalidates unrelated result, or set selection alters simulation identity; inspect plans/IDs and two export
  inventories.; Stress-test analyst / architect.
- **C4 default preservation:** Capture current default outputs/settings on matched retained responses before
  change; exact keys, units, membership, serialized values and refusals must match /4 adapter, excluding
  planned path/manifest changes. Cover all tokens, references/ties, missing/partial years, rolling boundaries,
  singleton and pooled GEV policies. Any unexplained difference blocks parity claim.; Model-validator;
  independent check of hand-solvable reductions, retain existing estimator evidence.
- **C5 reliable publication:** Inject calculation/write/pointer and rollback failures, forced reuse/refusal;
  old committed result bytes lost, incomplete current set accepted, or retry changes identity falsifies
  claim.; Existing integration validators / architect.
- **C6 migration/metadata:** Legacy matrix fails, /3 reads change, unknown YAML passes, output metadata
  contradicts method, flat consumer silently reads stale data, machine files leak into results.; Contract
  tests and affected-reader checks / architect.

Proportionate delivery gates: affected tests and CLI/DAG dry-runs, retained-response WF4 execution,
independent numerical parity evidence for C4, scoped Ruff and final lint/format once. No all-five
execution or new baseline is prescribed unless actual shared impact requires it under the ladder.
No scientific acceptance exists for an unspecified second set. A second subset exercises mechanics;
a genuinely new method later needs its own definition, independently checkable example and authority.

## Review decisions and limits

G1 must resolve P1 defaults/inactive settings and path rule; P2 schema/method vocabulary;
P3 preservation contract; P4 metadata identity/schema/publication; P5/P6 compatibility/readers.
Alternatives: scalar operation is simpler but superseded by agreed list; separate scripts duplicate
methods; immutable versioned public folders improve concurrent reading but add user navigation.
Choose current named folders with explicit completion/inventory rules for this minimum delivery;
revisit if readers need uninterrupted concurrent access.

Inspected runner, registry, reductions, planner/writer, exporter, reservation projections, rule branches,
HM-7 schema and repository/skill references. No code changed, runtime simulations, numerical parity,
DAG execution, independent review, full consumer sweep or filesystem-fault experiment was performed.
This candidate is architectural evidence only; later checks can reject its preservation/recovery claims.

Revision: 2026-10-16 v1 completes the seed with proposed contracts, current policy map and falsifiers.

