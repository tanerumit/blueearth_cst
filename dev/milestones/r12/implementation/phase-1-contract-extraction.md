# Task Brief — P1 logical contract extraction in current WF3

### Context

- Follow repository `AGENTS.md`, [master brief](master-brief.md), and accepted §§4.2 landing 1, 4.3–4.4, 5.1–5.3, 6.3–6.6, 7.1–7.5, and 8.1.
- P0 P2b and the accepted model-builder pre-change snapshot are blocking inputs. Current `run_stress_test.smk` remains the sole entry point and comparison harness.
- Production bindings stay weathergenr and Wflow; fixtures alone use synthetic provider/dummy simulator.

### Goal

Introduce scenario-provider, simulator, neutral-response, and metric-declaration interfaces behind the current WF3 graph while preserving current execution and output behavior.

### Non-goals

No durable collection/simulation/metric manifests, metrics-only path, planning checkpoints, entry-point/config names, output-tree migration, numerical baseline update, or new production backend.

### Allowed scope

**Exact existing targets:** `run_stress_test.smk`; `blueearth_cst/experiment/prepare_cst_parameters.py`, `prepare_weathergen_config.py`, `downscale_climate_forcing.py`, `run_wflow_batch.jl`, `export_wflow_results.py`; `blueearth_cst/weathergen/generate_weather.R`, `impose_climate_change.R`, `read_member_grid.R`; `blueearth_cst/shared/indicator_tables.py`, `metrics_definition.py`, `interchange_contracts.py`; their narrow tests.

**Proposed paths:** `blueearth_cst/experiment/scenario_rows.py`, `scenario_provider.py`, `simulator_adapter.py`, `response_series.py`, `metric_registry.py`; `tests/_wf3_successor_fixtures.py`, `tests/test_scenario_rows.py`, `test_simulator_adapter.py`, `test_response_series.py`, `test_metric_registry.py`.

**Forbidden:** P2/P3 artifacts and names; config stanza changes; docs/reference retirement; model physics, HydroMT internals, estimator choice, standing baseline.

### Required changes (checklist)

- [ ] Implement pure deterministic stochastic row enumeration, forest/completeness/pairing validation, explicit `unit_id_capacity`, and `EmptyScenarioSetError`; persist the same rows later without rereading a generated table.
- [ ] Wrap current R generation/transform operations in the accepted provider interface. R developer owns R changes; model builder confirms operation parity. Provider alone interprets `rlz`, `st_id`, `derived_from`, and pairing.
- [ ] Wrap preparation/execution/native reading in the simulator interface. Its `RunForcing` input exposes only `run_id`, forcing/descriptor/preparation context, and collection ids; no scenario-type concepts cross the seam.
- [ ] Introduce validated `ResponseSeries`/set and make metric functions consume it. Native Wflow filenames, headers, and selectors terminate at the reader.
- [ ] Encode current metric declarations, run/bundle grain, response needs, Class-C reference rules, unit-index semantics, and operational count/fit refusals exactly as §§7.1–7.5 specify. Python engineering implements; Astra model validation judges scientific consequences.
- [ ] Add test-only synthetic provider and dummy simulator that cannot be selected by production config.
- [ ] Route current WF3 through the adapters with no entry-point/config rename and no unintended numerical change.

### Commit plan

| Subject | Paths | Invariant preserved |
|---|---|---|
| `refactor: extract scenario provider contract` | scenario rows/provider, R seam, current WF3, tests | same stochastic inputs/ordering and current entry point |
| `refactor: extract simulator response contract` | simulator/response modules, preparation/batch/export call sites, tests | same Wflow resources/logs/native outputs; no scenario payload reaches simulator |
| `refactor: declare metric grains and references` | registry/reducer/index code and tests | current vocabulary/numerics remain attributable; accepted R-2 difference is deferred to GF-9 |

### Validation

- Per edit: proposed narrow test files plus existing `pixi run pytest tests/test_stress_test_grid.py tests/test_prepare_weathergen_config.py tests/test_export_wflow_results.py tests/test_indicator_tables.py tests/test_interchange_contracts.py`.
- Per Python commit: `pixi run lint` and `pixi run format-check`.
- After each current-WF3 rule/signature edit: `pixi run pytest tests/test_cli.py`.
- Once for landing 1: GF-1 fresh-project current-carrier DAG after P2b, plus validation-map GF-2..GF-5, GF-11, GF-13..GF-14, GF-18, and GF-21 structural fixtures. GF-15 implementation tests only; its proposed benchmark requires Master Gate 2.
- Model-validator handoffs: stage 1 pairing/forcing descriptors; stage 2 response metadata/compatibility; stage 3 declaration/reference/count/fit semantics. No scientific acceptance is inferred from unit tests.

### Acceptance criteria

Current WF3 remains runnable; fixture-only neutral types traverse both seams; no simulator or metric parses scenario meaning from paths; every metric declares grain/requirements/reference/value validity; P1 tests pass; no P2/P3 surface lands early.

### Output requirements

Return the landing diff, changed call graph, narrow/CLI/lint results, GF evidence, and three model-validator handoff packages. Report any value delta as a blocker for the later controlled comparison.

### Task constraints

No hidden cap, fallback, defaulted response metadata, or private upstream patch. Preserve projection terminality and the accepted Class-B uncertainty limitation.

### Execution progress — 2026-09-10

The named Astra model-validator accepted the P0 snapshot as comparison evidence;
the owner then released P1 by asking to continue. Pure row contracts are now in
`blueearth_cst/experiment/scenario_rows.py`: capacity-padded ids, immutable
ordered rows, textual record serialization, forest validation, configured
stochastic cross-product and same-realization direct-root ancestry. Every
stochastic row is evaluated; empty sets, the retired toggle and insufficient
capacity refuse. Capacity is an explicit function argument; this increment adds
no config setting or durable identity. No production rule calls this module yet.

`pixi run --as-is python -m pytest tests/test_scenario_rows.py -q` passed
**13 tests in 0.11 s**. Repository lint and format-check passed (296 files).
The existing workflow was not edited, so no CLI or numerical rerun was needed
for this standalone increment. These checks do not establish GF-1's integrated
DAG, GF-18's consumption of the ancestor bytes, or complete P1 acceptance.

**Binding gate:** the validator found native forcing unit labels inconsistent
with apparent effective units, including generated `temp: units=K` and prepared
`temp: units=m, unit=degree C.`. Pressure and radiation labels are also implicated.
See the [separate P1 disposition](evidence/p0/prechange-snapshot.md#separate-p1-forcing-metadata-disposition).
Production descriptor/compatibility binding is held until an explicit trace
through current generation/catalog transformations establishes effective units.
Preserve native bytes and retain raw attributes separately; do not infer physical
units from ranges or add conversions. A verified interpretation can be documented
as an implementation binding; an unresolved interpretation or numerical repair
returns to the accepted scientific/method decision gate.
