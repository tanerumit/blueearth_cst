# Named indicator sets and WF4 operation selection

Status: Final design v3; sealing record in status.md; implementation not started.
Date: 2026-10-16. Owner: CST architect. Source checkout: main, `791fd1f9162d675eabc63de48825a6e4b4e74265`.
The owner requested application of the final reviewer points and sealing on 2026-10-16.
This specification is immutable once sealed; status.md records its exact acceptance identity.

## Decision and boundary

Expose `operations: [simulations, indicators]` and `indicator_sets: [default, example_subset]`.
Either operation can run alone. Named YAML sets select shared registered Python calculations and publish
separate readable tables over shared retained responses. Indicator-only execution cannot start Wflow.
These interfaces, user YAML, reusable methods, named exports and machine data under `_engine/` are agreed.
G1 framing and the final revision/seal request authorize the decisions below. P1-P6 identify contract
sections, not pending choices. Design approval does not establish numerical parity or applicability.

The reusable gap is WF4's single metric request/export selection, not a geographic assessment gap.
Serve existing WF4 default users and projects needing multiple analyses of the same response inventory.
Minimum delivery: named selection, default preservation, independent reuse and recoverable publication.
No new formulas, scenario generation, model physics, expression language, dynamic plugins, cross-set
calculation cache, robustness scoring, or new orchestration engine are commissioned.
The second scientific set remains unspecified; `example_subset` illustrates reuse only. Any low-flow set,
including conventional low-flow exceedance percentiles, requires a separate scientific commission.

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
Shared indicator-table prose and METRIC_CLASSES/metric_grain still describe retired grain behavior;
they are not grain authority. Wet/dry reference-month indicators now have run values and equal-weight
group summaries. Legacy /3 immutable data may also occupy results/metric_sets/<short-digest>/;
new names must not adopt those directories.

## User configuration and execution (P1)

Keep the project's closed `workflows.simulate_system: {enabled, config_path}` descriptor.
The WF4 YAML contains the following new fields alongside its existing simulation settings:

```yaml
experiment_name: experiment_rapid
operations: [indicators]
indicator_sets: [default, example_subset]
indicator_set_definitions:
  example_subset:
    config_path: indicator_sets/example_subset.yml
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
Authored IDs cannot equal any registered definition ID. The authored ID is the result-row metric key
and belongs to numerical identity; changing it creates a new numerical result. Titles, descriptions
and authored citations are publication-only. No overrides are allowed on definition selectors.
For authored entries, YAML references become dictionary authored_references; dictionary references
contains registry citations only. Registry quantity, units, method, parameters, grain and scientific
policies cannot be overwritten by authored presentation. Validators do not interpret titles as
scientific definitions; a title cannot establish that a high-flow p95 is conventional low-flow Q95.

Retain authored entries under external review resolution 2B. The initial parameter whitelists span
the same 16 calculations as the registry (11 q and five other-variable definitions), so authored
entries initially provide naming/presentation flexibility, not additional numerical capability.
Compare the resolved calculation contract (method, normalized parameters, resolved reducer statistic,
implementation revision and registry scientific policies) with registered definitions, excluding ID
and presentation. Expose the matching ID in equivalent_definition; otherwise leave it empty.
For registered definition selectors, equivalent_definition and authored_references are empty: their
metric key already names the registered definition. Authored equivalents carry the matching ID;
their authored_references retain the author's citation strings separately from registry references.
Within one set, reject two entries with the same calculation contract, including a selector and an
authored equivalent or two differently named authored equivalents. Across sets they remain allowed.
No user units, calendar, grain, missingness, aggregation or reference-policy fields are accepted.
Those are method contracts; unsupported declarations fail instead of being silently ignored.

Extend `blueearth_cst/experiment/metric_registry.py` as the single registry owner, keeping pure
calculations in `shared/metrics_definition.py` and existing estimator adapters. Add a small
`experiment/indicator_sets.py` resolver; avoid a parallel `indicators/` framework or wholesale move.
Existing definition IDs, suffixes and variable vocabulary remain owned by `shared/indicator_tables.py`;
the registry derives IDs/suffixes/variables from them, but grain and group-policy authority is
metric_registry.declarations alone. Correct or retire stale METRIC_CLASSES, metric_grain and
POOLED_REALIZATION prose in the same implementation; verify wet/dry run and group key coverage.
Set YAML references registered definitions, not copies. The default preset delegates to token/declaration
selection rather than duplicating a list.

Initial method contracts wrap existing reductions only:

- **annual_summary/1:** {variable, statistic}; q allows mean/max/min/p95; aet/gwr/precip only sum;
  snow only max; overland_flow only mean. p95 means quantile(0.95), NON-exceedance HIGH flow.
- **annual_rolling7_extreme/1:** {extreme: min or max}; q only; existing Q7d_min/Q7d_maxyear.
- **annual_min7_mean_ratio/1:** {}; q only; existing BFI.
- **reference_month_mean/1:** {which: wet or dry}; existing fixed Class-C reference resolver/reduction.
- **pooled_return_level/1:** {kind: annual_max or rolling7_annual_min}; fixed periods 10/2 years.

All parameter maps reject extras and omitted required keys; no implicit numerical defaults.
These method IDs are the designed toolbox vocabulary; the functions do not yet expose this interface.
A registered definition resolves to method, validated parameters, authoritative metadata and policies.
The adapter must preserve existing reducers; it must not reimplement their arithmetic.
Method registration declares response variable/units/timestep/time-label/calendars, output units,
run or bundle grain, group policy, references, temporal/missingness/validity policies and implementation
revision, plus closed parameter validation. BFI is dimensionless; do not infer output units from inputs.

For aet/gwr/precip annual_summary(sum), output_units=mm. Quantity: mean water-year block depth:
daily mm dt-1 values (dt=86400 s) summed within each block of the resolved anchor and averaged with
equal block weight. Partial first/last blocks remain without duration normalization; missing values
contribute zero to sums, and an all-missing block enters as 0 mm.
With no missing values this equals D/B, retained accumulated depth divided by block count. This is
mean annual accumulated depth only when every block is complete and values are nonmissing. It is
not D/L, a duration-normalized annual rate under an explicitly chosen year-duration convention.
L/B is conditional estimand algebra, not measured bias; no N-year member-window assumption is made.

This explicitly affirms the 2026-08-08 owner ruling in shared/indicator_tables.py: sum reductions,
annual_total names and refusal to rescale to mm/day remain. Its mm/yr interpretation is limited to
complete water-year blocks with no missing values; arbitrary partial-block results are labelled mm.
Update that ruling's maintained explanation and affected documentation during implementation. No
arithmetic or existing metric ID changes; the owner has adopted this reporting decision by directing
the final revision and sealing. Runtime verification remains a future acceptance requirement.

No empirical bias magnitude or unconditional direction of extreme-value effects is claimed.

All initial methods must declare the following existing semantics, and positive behavior fixtures must
confirm them: bins use interval_end timestamp labels directly, without shifting to interval starts;
the reader's first label is starttime+step. Values at a year/month boundary therefore follow the end
label, not an inferred interval overlap. Annual and reference-month reductions retain partial edge
blocks and weight each finite block equally, without duration normalization. GEV extraction also
retains partial member-local blocks; pooling weights each usable block equally.

Annual sums skip NaNs with pandas default min_count=0, including zero for all-NaN blocks; mean/max/min
and quantile skip NaNs, retaining NaN for all-missing blocks. Rolling(7).mean requires seven nonmissing
values. The final pandas mean skips NaN block values; group means instead propagate NaN run results.

BFI preserves its annual ratio arithmetic: 0/0 may be NaN and an infinite final value is refused.
A zero denominator does not always cause an infinite final value; capture both cases.

GEV discards nonfinite extracted blocks and applies existing block-count/fit/probability refusals.
Wet/dry month selection uses pooled calendar-month sums, not mean flow rate; the selected month depends
on month length, member coverage and missingness. With fixed daily timestep these sums are proportional
to accumulated volume, without claiming numerical volumes in m3. Do not label the selection as the
month with the highest/lowest daily mean rate, or assert a universal percentage effect.
Record these policies in declarations and the readable dictionary; no new exclusion or imputation rule.

### Immutable coverage evidence

Each result records coverage per ResponseSeries.key=(run_id, variable, location_id), preserving that
series' missingness association. Never summarize missingness solely by run/variable.
The evidence records calendar, timestep, time_label, resolved anchor, first/last labels and for every
block: end label, observed label count, expected daily count, missing count and all-missing flag.
Also record B, complete-label-block count, total missing values and all-missing-block count.
A complete label block has the full expected contiguous daily coordinate; it can still contain NaNs.
Expected days follow the actual Gregorian anchor interval, including leap days. Derive these fields
from retained indices/masks at reduction, not from requested config dates or regenerated source data.
They are immutable diagnostic evidence bound by the existing response digest, not a new identity input.
Their serialized evidence file/fields remain beneath the result's _engine root and its manifest inventory.

For each dictionary row, block_coverage reports all distinct evidence patterns for its variable and
consumed members/locations, including baseline-reference members when applicable. A pattern includes
the full per-block coverage-count vector, not just totals that hide block differences. Associate each
pattern with its exact run/location pairs and any differing evaluation/reference role; include run
counts without replacing the associations. Sort patterns by (calendar, timestep, time_label, anchor,
first_label, last_label, ordered per-block evidence vector), then sort member pairs by
(run_id, location_id, role). This total key uses every pattern field; no arbitrary tie order or
truncation/sampling is allowed. Match pairs to group_members when interpreting bundle results.
Render readable quoted identifiers and deterministic counts, for example:
"run_01 at location 9: anchor YE-SEP; 4 blocks (2 complete label blocks; first 273/366 d;
last 92/365 d); labels 2000-01-02..2002-12-31; missing 0; all-missing blocks 0",
with full labelled per-block counts appended. Equal coverage-count patterns may list multiple explicit
run/location pairs; this does not claim their missing-value positions match. Exact missing masks remain
in retained responses and are not duplicated in the dictionary or coverage evidence.
The cell discloses contributing run/location coverage for individual and pooled/group views, not a
per-output effective sample size or bias estimate. It does not establish within-month, rolling-window
or GEV sample adequacy; retained method-specific evidence governs those questions.

Package-level example planned; independent calendar counts checked: precip=1 mm per daily step, labels
2000-01-02 through 2002-12-31, 1095 labels. October-start YE-SEP block depths are
273,365,365,92, giving 273.75 mm, with two complete label blocks; first 273/366 and last 92/365 days.
January-start YE-DEC depths are 365,365,365, giving 365 mm; first block has 365/366 labels.
For illustration only, L=1095/365.25 years gives D/L=365.25 mm yr-1; that is a different estimand,
not the reported value. With January-start 2001 values all NaN, depths are 365,0,365 and the result
is 730/3 mm; missing evidence identifies the zero's origin. The coordinator checked the calendar counts
with standard-library date arithmetic. Package reducers, actual member windows and NaN behavior were
not executed for this example.

Applicability: existing bindings require contiguous daily standard/Gregorian/proleptic Gregorian
datetime labels and refuse inconsistent coordinates. Behaviour under noleap-generated forcing,
actual member windows and pandas-version semantics must be exercised, not inferred from a WF3 window.
Do not certify unsupported calendars or coordinate gaps as complete. D/B concerns sum reductions;
coverage is disclosure for other methods and does not establish their adequacy.

### Anchor binding and preservation

At the inspected source, WF4 metric_plan.py:136 and rules/simulate_and_metrics.smk:64 under
blueearth_cst/experiment/ construct YS-* directly. The existing shared.snake_utils.water_year_end_anchor
helper returns YE-DEC for January and YE-SEP for October. The reviewer called this current production
helper usage; inspection establishes the helper, not that current WF4 already invokes it.
The final implementation must bind through that helper only after O2 verifies unchanged numerical rows
and result-key coverage for supported midnight daily labels. Record actual resolved anchor, right-closed/
right-labelled bin semantics and any bin-label metadata change explicitly in /4 evidence.
Retain the exact current YS-* path in the pre-change oracle. A failed parity check blocks helper
adoption and delivery; do not silently alter arithmetic to satisfy this design. This is an anchor
consistency requirement with a concrete parity condition, not permission to redefine periods.

## Default preservation map (P3)

New-mode default selection uses model.outvars when it is a nonempty list; if absent, use
DEFAULT_WFLOW_OUTVARS on simulation paths or retained response_request variables on indicator-only.
Reject explicit null outvars when consulted by this preset and reject an empty expansion, including [].
Null operations/indicator selections are already invalid under P1; metrics is legacy-only.
Explicit definition lists are independent of this preset and still require compatible response outputs.

Legacy mode preserves captured prior resolution/refusal behavior, including its branch differences:

- metrics list selects those tokens (an empty list produces an empty selection); metrics absent falls
  through; metrics null currently fails at list(None) on the simulation rule path, but falls through
  in metrics_only_configuration and export_selected_metrics.
- With that fallback, absent outvars uses toolbox defaults on simulation, retained variables on
  indicator-only; null outvars gives no tokens on the simulation rule path but retained variables on
  indicator-only. Empty outvars gives no tokens on both paths.
- The legacy simulation exporter differs again: absent/null outvars uses toolbox defaults. Capture
  whether the entire invocation later refuses; do not present a resolver result as successful execution.

P6's compatibility promise covers these observed branches, not silent null normalization.
Expand selected tokens with existing declarations, including all 11 q definitions; the default is
configuration-dependent, not every physically available variable. E6 parity is asserted for supported
nonambiguous selections; legacy edge behavior is captured separately as compatibility evidence.

- **q mean/max/min/p95:** Annual statistic then mean over years; p95 is 95th NON-exceedance percentile, a high
  flow. `metric_registry.reduce_run`.
- **q 7-day extrema:** Rolling(7).mean over each complete member first, then annual min/max then mean; windows
  can cross water-year boundaries, never member boundaries. `metrics_definition.Q7d_*`.
- **q BFI:** Mean over years of annual minimum rolling-7 mean divided by annual mean; existing NaN/infinity
  handling. `metrics_definition.BFI`.
- **aet/gwr/precip, snow, overland_flow:** Mean of annual sum, max, mean respectively; retain arithmetic/names
  and per-location treatment; accumulated-depth reporting convention is defined in P2.
  `BASIN_METRIC_SUFFIXES`, `reduce_run`.
- **wet/dry q month:** Pooled unperturbed evaluated members, same first native q gauge, calendar-month sums;
  first month on ties; apply that one resolved month to every run/location. `resolve_month_reference`.
- **Non-return-level groups:** Equal-weight mean of run reductions, explicit NaN propagation, not length
  weights or a pooled daily series. `reduce_group_mean`.
- **Return levels:** Member-local annual maxima / rolling-7 annual minima, then pool blocks by design group;
  L-moment GEV adapter, fixed 10/2-year quantiles. `reduce_bundle`, `gev_lmoments`.
- **Return-level screening:** Retain partial periods; drop nonfinite annual blocks; minimum max(ceil(T),10);
  finite values, no clipping; tested probability guard and retained shape-coverage reporting. Existing
  screening is provisional operational policy, not scientific adequacy proof.
- **All families:** Daily interval-end labels binned without shifting; current Gregorian calendar
  declarations, project water-year anchor and partial-block/pandas policies explicitly stated in P2.
  No new exclusion policy.

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
Numerical identity retains actual responses, normalized metric definitions (including each result-row
metric ID), parameters, resolved reducer statistic, scientific policies, baseline-reference policy/
resolved baseline members and months, groups, anchor, code inventory, environment and estimator evidence.
Registry definition selectors resolve before hashing; bibliographic citations never mean baseline inputs.
Exclude set ID and set/metric titles, descriptions, citations, source path and selection order.
Identical normalized metric definitions, including metric IDs, may reuse an immutable result across sets.
An authored equivalent with a different metric ID has a distinct numerical result; only its numeric
values must match the registered definition. Sort definitions canonically; parameter, metric-ID or
numerical implementation changes alter identity. No cross-set intermediate computation cache is required.

Retain repository_code_inventory's transitive static import closure rooted at metric_plan.py.
Any parameter-to-reducer mapping or validation affecting numbers must be in that closure or declared
as an explicit inventory entry; persist the resolved statistic by value as well. A resolver imported
by metric_plan or metric_registry is already covered; do not create a second hashing framework.
A runner-only un-inventoried mapping cannot govern numerical resolution. C3 must verify a mapping
change changes identity. Use distinct terms: definition selector, baseline-reference dependency,
and bibliographic citations (registry references / authored_references).
Presentation-only metadata edits create a new publication identity and refresh the dictionary while reusing
numerical results; this includes authored citations. Registry units/policies cannot change through YAML
metadata.
Never mutate old records or promise reuse across changed implementation inventories.

New records use `metric-request/4`, `metric-set-identity/4`, `metric-set/4`.
Their delta is explicit resolved method/parameter/output-unit/policy records in declarations and
named-set-independent definition identity; current response/membership/environment integrity remains.
Keep read-only /3 support with its original projection validator. New writes use /4, with new IDs;
no rewriting old manifests or speculative aliasing of old numerical identities.
Reuse `collection-canon/1` content hashing and collision checks already owned by content_identity;
this change does not migrate to the separate cst-canon run-manifest protocol.

Generated layout; immutable objects are authoritative, readable exports are derived:

```text
experiments/<experiment>/
  results/metric_sets/<set-id>/          # scoped CSVs, group tables, readable indicators.csv
  _engine/metric_requests/<request>.json
  _engine/metric_sets/<result>/          # immutable metrics.json, environment/evidence and data/*.csv
  _engine/metric_sets/names/<set-id>/
    definitions/<source-sha>.yml        # captured authored YAML bytes
    publications/<publication-id>.json  # immutable selection, metadata and file inventory
    current.json                       # replaceable pointer to committed publication
```

No hashes, machine JSON, plans or nested engine roots are exposed under named result folders.
Each named folder contains existing scoped CSVs, group_members/group_metadata and derived indicators.csv.

The dictionary is UTF-8 CSV with one row per metric and this ordered header:
metric,set_id,set_title,set_description,title,description,variable,input_units,output_units,quantity,
method,parameters,equivalent_definition,grain,group_policy,water_year_start,calendar,time_label,
block_assignment,partial_blocks,block_coverage,missingness,validity,references,authored_references.

The wrapped header above denotes one physical CSV header, not three lines. Parameter and reference cells
use deterministic human text (sorted key=value pairs / citation strings separated by "; "); ordinary CSV
quoting handles punctuation. No JSON, hashes or internal result/publication identities appear in this
dictionary; run/location labels remain visible for coverage association.
Calendar/anchor fields describe actual responses/analysis; block_assignment names the resolved helper
anchor and its closure/label semantics. Grain/group_policy distinguish run summaries from pooled fits.
Temporal/missingness cells carry P2's semantics, including month selection by pooled sums with month-length/
coverage dependence. Registry references and authored_references remain separate; equivalent_definition
exposes an authored calculation's registered counterpart. YAML owns authored selections/presentation;
registry owns calculation semantics, and immutable result evidence owns block_coverage.
The dictionary is a generated read-only view, never an editable second authority.

The publication record is a closed `named-metric-export/1` object with schema_version, set_id,
metric_set_id, metric_manifest (experiment-relative path + sha256), definition_source (path + sha256),
resolved_metadata (every dictionary field resolved from captured YAML, registry, plan and immutable evidence),
files (basename -> sha256), publication_id and created_at. Compute publication_id from all semantic
fields except created_at/publication_id. current.json is exactly {schema_version: named-metric-current/1,
publication_id, publication: {path, sha256}}; all paths are confined experiment-relative paths.
Unknown schema/fields or digest mismatch fail; resolved metadata is immutable per publication.

Include indicators.csv in the publication's file inventory and stage/rollback/recover it with the tables.
Coverage stays in this dictionary and internal evidence; no additional public coverage CSV is introduced.
Recover numerical CSVs from immutable results and regenerate the dictionary from its committed publication;
verify every expected digest. A presentation-only edit must visibly refresh indicators.csv.

Hold existing project execution ownership through read/plan/publication. Validate complete immutable
results, stage all files and rollback copies under _engine, then replace owned exports and commit
the per-name pointer last. Reject symlinks/aliases and unknown files being overwritten.

Before creating/replacing results/metric_sets/<set-id>, check legacy /3 manifest result_root claims and
named ownership. Refuse an occupied legacy result root (including a matching hex-prefix set ID), an
unowned existing directory or a different set's claim; preserve contents and report the exact collision.

An existing directory is refreshable only when the verified current publication proves same-set ownership
and its inventory matches, or explicit recovery restores that committed inventory. An empty unowned
directory is still unowned. Do not blanket-refuse legitimate same-set refresh or reserve all hex-like names.

Ordinary I/O failure rolls back; preserve backups and diagnose if rollback fails.
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

Retain compatibility through one subsequent feature release; removal requires an explicit
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
(0) capture pre-change oracle below BEFORE implementation edits; (1) resolver/registry and schemas;
(2) runner/planner/DAG integration; (3) named export/readers; (4) docs/migration and acceptance evidence.
No independent new calculation is needed.
Future managed case bindings record revisions and authorities. A new scientific selection needs new
intent/analysis lineage; post-hoc exploration cannot mutate frozen framing or imply predeclared evidence.
Scientific stage order and projection independence remain governed by the CST contracts.

### Pre-change oracle and C4 coverage

Before the first implementation edit, the Python engineer captures a task-owned evidence set named
indicator-default-parity-prechange, produced with 791fd1f or an explicitly identified clean successor
that precedes implementation. Record source SHA, environment, input/settings digests, exact commands
and sha256 of retained reference bytes. Model-validator reviews coverage and acts as acceptance authority.
Keep the evidence index/logs in the task's permitted .tmp/ evidence area; retain bulk responses/outputs
in their configured external output root. They must not be overwritten by candidate execution.
If implementation starts before capture, recover the unchanged source/environment and independent
inputs in a separate location before any parity claim; candidate code cannot generate its own oracle.

This is bounded change evidence, not a new maintained baseline suite.

Reuse existing fixtures/assertions and retained rapid /3 outputs first; add only the smallest missing
cases. No new simulation is needed for retained-response reductions. Coverage IDs below name sources
to be inspected/captured; none is represented as already run:

- **O1 variables and real integration:** Retained rapid q/aet/gwr run+group tables, membership and metadata;
  existing registry/reader fixture coverage plus minimal producer-schema CSV/TOML cases for
  precip/snow/overland_flow. Assert actual headers/units from the response reader's format contract.
- **O2 groups, grain and anchors:** Existing test_metric_registry group/reference/bundle cases cover
  unequal member lengths, NaN propagation, native gauge selection and singleton policies. Re-reduce
  rapid retained responses by setting climate.water_year_start to January/October. Capture current
  YS-* oracle results exactly, then require value/key parity before adopting the existing helper's
  YE-DEC/YE-SEP anchors. Include the constant-depth example, a singleton and boundary-labelled series;
  expose partial blocks, interval_end bin assignment and rolling across year/member boundaries.
  Require wet/dry run+group keys and bundle-only header-only run tables. Verify value*B equals
  retained summed depth before float32 conversion for each nonmissing rapid annual-sum series.
- **O3 missingness, ties and BFI zero:** Reuse test_metrics_definition/test_metric_registry known answers;
  fill gaps with NaN days, all-NaN blocks, seven-day completeness, a monthly-sum tie, 0/0 and a zero
  annual mean producing infinity. Verify block evidence and dictionary patterns for two runs with
  different windows and two locations with different missing masks; key association and ordering must
  expose both differences. Check pooled-month sums against a daily-mean counterexample and the tie
  rule. Capture final NaN/refusal behavior and P2 policies, including the all-missing example.
- **O4 GEV:** Reuse test_metric_registry cases for pooled member-local blocks, fewer than ten usable
  blocks and constant-sample InvalidReturnLevelFit, plus existing tested-probability refusal cases.
  Retain the frozen GF15 oracle and qualification evidence; no new GEV benchmark is required.
- **O5 token precedence:** Cross metrics absent/null/list (include [] and a nonempty list) with
  outvars absent/null/[]/nonempty list for simulation-rule, indicator-only and export resolution.
  Record tokens or exception class/message and any later invocation refusal; test new-mode null/empty
  rejection separately. Do not assume the three legacy branches agree.
- **O6 independent meanings:** For each of the five method IDs, retain at least one small
  hand-solvable calculation outside package calls: annual summary, rolling extrema, BFI ratio and
  fixed-month selection; for pooled_return_level use hand-listed extracted blocks/probabilities/counts
  plus the existing independently frozen estimator oracle for fitted values, not a bespoke hand GEV fit.

Capture run/group CSV bytes, group_members/group_metadata, expected_result_keys, resolved reference
months/counts and return_level_evidence (member/block counts, parameters, fit and shape coverage).
For refusals retain exception class, structured reasons and message; normalize only relocated paths or
implementation digests with documented reasons. Post-change IDs/manifests are expected to differ.
Compare old numerical bytes and scientific evidence against /4, allowing only explicitly specified
schema/path/identity changes and the adopted unit-description clarification; unexplained numeric/key/
reference/refusal differences block E6. Positive metadata checks bind every P2 policy to O2/O3/O4.
Existing assertions count only where their inputs and expected behavior actually cover the claim.

Acceptance below is planned, not executed. Select concrete commands from the live validation ladder
at implementation time; reuse this evidence and outputs rather than create duplicate checks.

- **C1 operation contract:** Either runner schedules wrong activities, reversed order changes behavior,
  invalid config passes; exercise three selections, defaults and invalid structures.; Existing runner tests /
  architect.
- **C2 indicator-only boundary:** Fail if model/generation files, Julia probing or simulation launch are
  touched; fixture uses completed responses and missing live files.; Model-builder integration exercise /
  architect.
- **C3 named independence:** Inspect plans/IDs and two export inventories. Shared registered definitions
  must produce byte-identical rows across sets on the same responses. An authored equivalent must match
  all values/keys after replacing only its metric key with equivalent_definition. Metric-ID changes
  change numerical identity; title/description/authored-citation changes refresh only publication.
  Identical normalized metric definitions may reuse; set ID changes cannot change numerical identity.
  Changing the parameter-to-reducer mapping must change identity through existing inventory/value
  contracts. Conflict, divergence, unrelated invalidation or changed simulation identity fails.
  Stress-test analyst exercises results; architect accepts the interface evidence.
- **C4 default preservation:** O1-O6 must be captured before edits; compare exact numerical keys/values,
  membership, references, policies and refusals as specified above. Missing coverage or an unexplained
  difference falsifies E6. Confirm the D/B example and actual retained coverage; package-level checks
  verify the adopted descriptive unit contract without claiming model adequacy. Model-validator.
- **C5 reliable publication:** Inject calculation/write/pointer and rollback failures, forced reuse/refusal;
  old committed result bytes lost, incomplete current set accepted, or retry changes identity falsifies
  claim.; Existing integration validators / architect.
- **C6 migration/metadata:** Fail if legacy matrix changes, /3 reads change, unknown YAML passes, a P2
  policy lacks positive fixture evidence, dictionary metadata/units/grain disagree with the resolved method,
  or a metadata-only refresh is invisible. Exercise legacy-immutable/unowned folder collision refusal with
  byte preservation and verified same-set refresh; fail stale flat-reader adoption or machine JSON/hash
  leakage into results. Also refuse within-set duplicate calculation contracts; verify authored ID
  noncollision, equivalent_definition, separate registry/authored citations and truthful units/policies.
  Check block_coverage comes from committed per-series evidence, preserves run/location associations
  and uses total deterministic ordering. Alias titles cannot override method meaning.
  Contract/affected-reader checks under architect; numerical/coverage checks under model-validator.

Proportionate delivery gates: affected tests and CLI/DAG dry-runs, retained-response WF4 execution,
independent numerical parity evidence for C4, scoped Ruff and final lint/format once. No all-five
execution or new baseline is prescribed unless actual shared impact requires it under the ladder.
No scientific acceptance exists for an unspecified second set. A second subset exercises mechanics;
a genuinely new method later needs its own definition, independently checkable example and authority.

## Decisions, review provenance and limits

The owner directed final revision and sealing after the full external review and its focused follow-up.
This adopts mm block-depth reporting with immutable coverage disclosure, authored-entry resolution 2B,
and the six finding resolutions below. No design choice remains pending in this specification;
implementation parity, applicability and failure-recovery evidence remain delivery obligations.

- **ext1-1:** P2 defines D/B, limits the prior mm/yr interpretation, retains arithmetic, specifies immutable
  per-series coverage and the hand-solvable example; P4 publishes coverage in the existing dictionary;
  O2/O3 and C4/C6 test the description. No public coverage CSV or measured-bias claim is introduced.
- **ext1-2:** P2 retains authored definitions with metric-ID identity, equivalent_definition, duplicate
  calculation refusal and separated citations; P4 and C3/C6 make numerical/publication identity explicit.
- **ext1-3:** C3 directly compares shared rows and authored-equivalent values across named sets.
- **ext1-4:** P2's anchor section and O2 require the existing YE helper, conditional on value/key parity;
  current YS construction is retained as oracle evidence and metadata differences are declared.
- **ext1-5:** P2/P4 disclose pooled-month sums and duration/coverage dependence; O3 exercises their meaning.
- **ext1-6:** P4 uses the existing static import closure and resolved statistic by value; C3 tests numeric
  mapping changes. Definition selectors, baseline-reference dependencies and citations are distinguished.

The original domain-1 through domain-6 dispositions remain: bounded pre-change evidence O1-O6;
truthful policy/unit metadata; readable dictionary; registry grain authority and stale-helper correction;
neutral example_subset; and ownership-aware legacy collision refusal with verified same-set refresh.
The earlier unit interpretation issue is resolved as a design decision here; empirical acceptance remains.

Alternatives retained: scalar operations would be simpler but the agreed interface is a list.
Reference-only entries would defer authored naming, contrary to the capability retained by the owner.
A separate coverage CSV would add another public contract; the dictionary and internal evidence suffice.
Versioned public folders could support uninterrupted concurrent reads; current named views require
completion/inventory checks. Revisit only if actual consumers need that stronger read isolation.

Evidence provenance: internal-review-domain.md assessed v1; external-review-r1.md assessed v2;
external-review-r2.md examined unchanged v2's coverage/authored-ID decisions and qualified minor findings.
The owner selected the final applications; internal-review-index.md retains coordinator qualifications.
Those reviews did not inspect this v3. No claim of independent v3 approval, general risk-stage completion,
runtime parity, actual member-window coverage or publication recovery is made. status.md records the
sealing decision, exact document identity and process limitations outside this immutable specification.
Previous snapshots and raw reports remain unchanged.

Inspected relevant registry/reducers, response key/mask contract, current anchor construction and helper,
code-inventory closure, exporter/planner, rule branches, tests and review records. No implementation,
package execution, simulation, numerical parity or filesystem-fault experiment was performed by the
author. The coordinator's date-arithmetic check supports only the illustrative label counts.
Preserving current indicators does not scientifically qualify them for a case; case selection and
acceptance thresholds remain with the case manager.

Revision history: 2026-10-16 v1 established the contract; v2 applied the six domain findings; v3 applies
the six external findings and the owner's final decisions. The sealing record remains in status.md.
