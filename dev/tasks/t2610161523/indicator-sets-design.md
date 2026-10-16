# Named indicator sets and WF4 operation selection

Status: Draft design; core interface agreed, implementation details proposed.
Date: 2026-10-16.
Owner: BlueEarth CST, WF4 simulation and indicator processing.
Implementation status: Not implemented. This document does not authorize implementation or landing.

## Decision and purpose

WF4 will expose one list of operations and one list of named indicator sets. Users can run simulations,
calculate indicators from retained responses, or do both. Multiple indicator sets share the same
simulation responses and publish results in separate named folders.

```yaml
operations: [simulations, indicators]
indicator_sets: [default, low_flows]
```

Each set has a user-facing YAML definition. It references reusable, registered Python calculations
by stable method names. Users do not configure hashes, internal JSON records, or execution plans.
Generated machine-oriented artifacts remain under the existing experiment `_engine/` structure.

This design serves workflow users selecting analyses and developers adding new indicators. It does
not change scenario generation, model physics, simulation selection, or scientific definitions in
the existing default indicator suite.

## Decision state

The following choices were agreed in the design discussion:

- Replace the user-facing operation/target split with `operations: [simulations, indicators]`.
- Support either operation alone; indicator-only execution must never run Wflow.
- Select one or more named sets with `indicator_sets: [default, low_flows]`.
- Give each set a YAML definition containing user-facing metadata and calculation configuration.
- Share registered Python calculations across sets, rather than require one script per set.
- Publish readable tables separately for each set; preserve immutable internal result identities.
- Keep hashes, generated JSON, resolved machine definitions, and plans under `_engine/`.

Exact field schemas, compatibility duration, custom-path syntax, and omitted-setting defaults below
are proposals, not separately approved contracts. No independent review or runtime validation has
been performed for this design.

## Current behavior and limitation

`simulation_runner.py` accepts `operation: simulate-and-metrics` with `all` or `simulations_only`.
It accepts `operation: metrics-only` with `simulations_and_indicators` or a selected output path.
The standalone runner defaults its target to `all`, so indicator-only execution currently requires
an additional target argument. Both public runners enforce this operation/target contract.

The current metric registry declares response requirements, statistics, reference dependencies,
run or bundle grain, validity rules, and group reduction. The metric planner creates immutable,
response-dependent result identities. Multiple historical results can exist, but the current export
mechanism publishes one selected set into flat `results/metric_sets/` and tracks it with one
`_engine/metric_sets/current.json` record. Merely looping over that exporter would overwrite the
previous selection; multiple named exports need their own publication bookkeeping.

Current metric selection also depends on workflow `metrics`, project `model.outvars`, or retained
response declarations. The default-set adapter must preserve these existing selection semantics
until an explicit migration replaces them.

## Operation contract

| Selection | Requested behavior |
|---|---|
| `[simulations, indicators]` | Run or reuse simulations, then derive all selected sets. |
| `[simulations]` | Run or reuse simulations without calculating indicators. |
| `[indicators]` | Calculate selected sets from completed retained responses only. |

The list represents selected work, not ordering. Dependencies determine execution order, including
when the list is reversed. Empty lists, duplicates, and unknown operation names are errors.
Neither operation means force execution: existing valid products remain reusable.

Both public runners resolve internal Snakemake targets automatically. Routine commands therefore
need no target argument:

```powershell
pixi run python scripts/simulate_system.py --config path/to/project_config.yml
```

The main project configuration continues to reference the WF4 configuration through its existing
`workflows.simulate_system.config_path` stanza. Indicator-only execution must retain its current
ability to use frozen simulation inputs without opening live generation or model workflow files.
Missing or incompatible retained responses produce a clear failure, never an implicit simulation.

Proposed defaults are both operations and `[default]` when their respective keys are omitted.
An explicit empty indicator selection is invalid when indicators are requested. Under simulation-only
execution, set definitions need not be loaded; configured selections can remain for a later run.
These defaults and inactive-selection behavior require confirmation before implementation.

## Set definitions and discovery

Bundled sets resolve by name from the proposed `config/indicator_sets/<name>.yml` directory.
This is a new runtime configuration family, distinct from scaffolds under `config/templates/`.
Its introduction requires updating the repository layout reference.

Proposed repository layout:

```text
config/
  indicator_sets/
    default.yml                     # Shipped definition preserving existing calculations
  templates/
    indicator-set.template.yml      # Authoring scaffold; never loaded as a runtime default
blueearth_cst/
  indicators/
    registry.py                     # Stable method identifiers and calculation contracts
    flow_statistics.py              # Reusable implementations grouped by scientific purpose
    low_flows.py                    # Added only when actual methods justify this module
```

These module paths describe a proposed ownership boundary, not a mandate to relocate every existing
function. Existing `experiment/metric_registry.py`, `shared/metrics_definition.py`, and
`shared/indicator_tables.py` remain authoritative until a deliberate migration moves their contracts.
Do not introduce a second competing registry during that transition.

Project-specific sets must also be supported without editing the toolbox installation. A proposed
explicit mapping in the WF4 file is:

```yaml
operations: [indicators]
indicator_sets: [default, low_flows]
indicator_set_definitions:
  low_flows:
    config_path: indicator_sets/low_flows.yml
```

The proposed `config_path` resolves relative to the WF4 YAML containing it. This is a new path rule
that must be documented explicitly; it is not implied by the current project-file path contract.
Require the selected name to match the definition's `id`. Reject ambiguous bundled/custom collisions
rather than silently shadow a bundled set. Reject unknown and duplicate selected names.
Use lowercase snake_case identifiers that are safe as a single folder component.

## Authoring template and calculation interface

The YAML owns human-authored meaning and configuration. The following is illustrative schema,
not a supported configuration or a change to the existing low-flow calculation:

```yaml
schema_version: 1
id: low_flows
title: Low-flow indicators
description: Indicators of sustained low-flow conditions.

indicators:
  - id: annual_min_7day_flow
    title: Annual minimum 7-day flow
    description: Minimum 7-day mean discharge within each water year.
    units: m3 s-1
    references: []
    calculation:
      method: annual_rolling_minimum
      parameters:
        window_days: 7
    inputs:
      discharge:
        variable: q
        units: m3 s-1
        timestep: daily
    temporal:
      year_basis: water_year
      incomplete_years: exclude
      missing_values: require_complete_window
    aggregation:
      run: mean_of_annual_values
      group: equal_weight_mean_of_runs
```

Method identifiers resolve through a registry, not arbitrary script paths, imports, or executable
YAML expressions. A new set using existing methods needs only YAML. A new scientific calculation
needs a registered implementation and verification against an independently checkable example.
Modules group related methods; sets may share those methods with different validated parameters.

The method contract must define accepted inputs and units, parameters, temporal semantics, output
grain and keys, validity behavior, and supported aggregation. YAML settings must be checked against
that contract: declarations cannot claim units or policies the implementation does not support.

The final schema must express the existing registry's distinctions:

- Per-run reduction versus calculations over pooled groups of realizations.
- Equal-weight aggregation of run results versus fitting to pooled member-local annual blocks.
- Reference/unperturbed-run dependencies and their location selection.
- Time labels, calendars, water-year anchor, incomplete years, missingness, and finite-value rules.
- Return-period units, sample adequacy, estimator settings, and method limitations where relevant.

The illustrative seven-day indicator leaves rolling-window boundary semantics unspecified; its
method must settle whether windows may cross water-year boundaries before that method is shipped.
No illustrative missingness or incomplete-year choice overrides the current default suite.

Reuse registered indicator definitions where possible rather than copy their metadata into every
set. The exact shorthand for selecting an existing definition remains open. Permit only declared
parameter overrides; never allow metadata to contradict the selected calculation silently.

## Execution, identity, and output ownership

Resolve selected sets and validate their definitions before expensive calculations. For a full run,
check the union of required response variables against configured model outputs early. For an
indicator-only run, check against retained response inventories. Neither path silently changes
the model's requested outputs to satisfy a set.

Simulations execute once for their selected inputs. Each requested set then has an independent
plan and completion state over those shared responses. Set changes must not alter simulation or
scenario identities. Unchanged valid sets are reused; changed calculations create new immutable
results. Removing a name from selection does not delete its previous results.

Readable names identify selections and export folders; they are not substitutes for result identity.
Resolved calculation parameters, actual response identity, implementation identity, and relevant
environment information remain part of reproducibility. Reuse the existing identity machinery.
Whether purely descriptive metadata changes re-key numerical results remains an explicit open choice.

Proposed generated layout, retaining the existing experiment engine root:

```text
experiments/<experiment>/
  results/metric_sets/
    default/                        # Current successfully published default-set tables
    low_flows/                      # Current successfully published low-flow tables
  _engine/
    metric_sets/
      <immutable-result-id>/        # Immutable results and generated machine records
      ...                           # Internal plans and per-name publication tracking
```

Exact internal filenames are implementation details to settle against existing reader contracts.
All generated hashes, JSON manifests, resolved definition snapshots, identity records, and internal
tracking remain beneath `_engine/`. Do not create nested engine roots for each readable set folder.
User-authored YAML stays in its source configuration location; internal captured copies are generated
evidence and belong under `_engine/`.

Publication must validate a complete set before replacing its readable export. Preserve existing
ownership protections and recoverability on ordinary write failures. A failed set must not be
reported as current or replace a previous valid export. Successful independent results can be
retained for retry; the invocation succeeds only when every requested set is complete. Mixed-age
exports after a partial failure must be identified in internal tracking and the console summary.

## Affected interfaces and migration

| Owner or consumer | Required change |
|---|---|
| Public runners and `simulation_runner.py` | Resolve operations and remove routine target coupling. |
| `simulate_system.smk` and its indicator branch | Schedule all selected sets over one response inventory. |
| Metric registry, planner, and declarations | Resolve named definitions without changing default science. |
| `metric_export.py` and readers of `current.json` | Track and publish each selected name independently. |
| Config composition, snapshots, reservation context | Keep indicator changes independent of simulations. |
| Templates, seeds, CLI help, and published WF4 guides | Explain the new interface and paths. |
| Interchange checks, inventories, baseline tools, tests | Handle named folders and set-specific tables. |

Migration must map existing requests explicitly:

| Existing request | Replacement |
|---|---|
| `simulate-and-metrics` + `all` | `[simulations, indicators]` |
| `simulate-and-metrics` + `simulations_only` | `[simulations]` |
| `metrics-only` + `simulations_and_indicators` | `[indicators]` |

The `default` adapter must preserve current output-variable selection, indicator labels, units,
reference handling, and numerical policies. Existing immutable results and simulation records must
remain readable. Define a migration for flat exports and downstream path readers; do not duplicate
or delete them silently. Existing explicit metric-output targets and legacy `metrics` selections
need a deliberate compatibility policy. Reject conflicting old and new settings.

Implementation must include the repository-required rename/migration record and update live old
key, command, and path references. This draft records the intended change, not completed migration.

## Alternatives and tradeoffs

A single scalar operation with three values also covers the current execution combinations. The
agreed list keeps the two selectable activities explicit, at the cost of validation for duplicates
and order independence. Keeping separate operation and target controls preserves the current CLI
but retains invalid combinations and exposes internal workflow targets.

One script per set is easy to start but duplicates shared calculations and mixes selection with
implementation. Registered methods require a small explicit interface but support reuse, validation,
and auditable calculation identity. Arbitrary executable YAML is unnecessary for this scope.

Named exports improve discoverability but change existing consumer paths. Preserve immutable internal
storage and implement the path migration rather than weakening identity to use names alone.
This design does not require cross-set computation caching, dynamic third-party plugin loading,
new numerical methods, or a general expression language.

## Acceptance and verification plan

These are implementation acceptance claims, not checks executed for this document. Select actual
commands and execution gates from the live [validation ladder](../../reference/validation-ladder.md).

| Claim | Check and input case |
|---|---|
| One operation interface works in both runners | Exercise all three selections and reversed list order. |
| Indicator-only cannot simulate | Retained-response fixture; forbid simulation launch and live-model reads. |
| Two sets coexist | Same rapid responses, two definitions, two complete named export inventories. |
| Default science is unchanged | Matched responses and settings; compare existing/default-adapter results. |
| Calculations mean what metadata claims | Small independently calculated series for each new method. |
| Parameter changes do not rerun simulations | Change one set; inspect identities and scheduled producers. |
| Invalid requirements fail clearly | Unknown method, wrong units, absent response, and duplicate names. |
| Failure remains recoverable | Fail one set/publication; preserve valid exports and retry incomplete work. |
| Legacy readers are handled | Old records, flat export fixture, and affected downstream readers. |
| Machine artifacts stay internal | Inspect generated tree from the same affected integration execution. |

Reuse affected execution outputs across checks. A second scientific set must be specified before
its numerical acceptance can be defined. A successful workflow run alone does not validate a new
indicator formula. No baseline regeneration is required merely to write this document.

## Remaining decisions

1. Confirm omitted-key defaults and the exact custom-definition mapping syntax.
2. Finalize the closed YAML schema and reuse shorthand for registered indicator definitions.
3. Specify the second set's indicators, calculation policies, and independent numerical examples.
4. Choose compatibility duration for old operations, targets, `metrics`, and flat export paths.
5. Decide metadata-only identity behavior and per-name publication tracking details.

## Source anchors

Current implementation inspected while drafting:

- [Operation and target validation](../../../blueearth_cst/experiment/simulation_runner.py)
- [Standalone runner](../../../scripts/simulate_system.py)
- [All-workflow runner](../../../scripts/run_workflows.py)
- [Metric declarations](../../../blueearth_cst/experiment/metric_registry.py)
- [Metric plans and immutable results](../../../blueearth_cst/experiment/metric_plan.py)
- [Current export behavior](../../../blueearth_cst/experiment/metric_export.py)
- [Indicator names and table contract](../../../blueearth_cst/shared/indicator_tables.py)
- [Repository layout](../../reference/repo-layout.md)
- [Naming and migration conventions](../../reference/naming.md)

## Revision history

- 2026-10-16: Initial draft capturing the agreed interface and ownership boundaries; proposed detailed
  schema, migration, failure behavior, and acceptance work remain subject to refinement.
