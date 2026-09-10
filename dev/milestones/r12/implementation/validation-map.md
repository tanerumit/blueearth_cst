# R12 GF-1..GF-32 validation map

Status at preparation baseline `dffa4625…`: every successor-specific GF is **NOT IMPLEMENTED**. Existing commands below protect predecessor behavior but do not count as a GF pass. Proposed test paths are labels for implementation ownership, not current files.

Execution update, 2026-09-10: the GF-1 P0 prerequisite (synthetic P2b) passes;
its production and final-entry-point checks remain outstanding. The operation/
target precursor to GF-22 reached [Master Gate 3](evidence/p0/operation-target-feasibility.md);
conditional rules fail target exclusivity, although metrics-only producer omission
works. The owner approved the mandatory runner; its synthetic matrix and both
checkpoint lifecycles now pass. Production GF-22/GF-29/GF-30 remain unimplemented.
Fresh WF1/WF3 reference capture and its isolated manifest check passed; named
model-validator accepted the snapshot. Pure P1 rows now have 13 passing tests;
production binding awaits the separate unit-provenance gate. Other GF statuses
remain at the preparation state. See [P2b evidence](evidence/p0/p2b-feasibility.md).

Existing reusable checks:

- Current seams/metrics: `pixi run pytest tests/test_indicator_tables.py tests/test_interchange_contracts.py tests/test_export_wflow_results.py`
- Current config/runner: `pixi run pytest tests/test_config_composition.py tests/test_run_workflows.py tests/test_cross_workflow_inputs.py`
- Current entry points: `pixi run pytest tests/test_cli.py`
- Baseline tooling: `pixi run pytest tests/test_check_baseline_scope.py tests/test_check_baseline_provenance.py tests/test_check_baseline_discharge.py tests/test_check_baseline_indicator.py`
- Full non-integration gate: `pixi run test-full`; actual workflow/model acceptance remains separate.

| GF | Owner / phase | Claim falsifier | Command status / proposed test |
|---|---|---|---|
| 1 | Python engineer / P0 composition; P1 integrated DAG; P3 final generation | P2b or fresh generation DAG has ambiguity/cycle, or missing ancestor does not refuse | **P0 P2b PASSED; production checks NOT IMPLEMENTED** — `pixi run pytest tests/test_r12_wf3_feasibility.py -k p2b`; follow with fresh-project current-carrier and final generation DAG checks in `tests/test_cli.py` |
| 2 | Python engineer / P1 | Empty edge schedules a transform | **NOT IMPLEMENTED** — `pixi run pytest tests/test_scenario_rows.py -k empty_edge_schedules_roots_only` |
| 3 | Python engineer / P1 | Rows require generated-table read, row checkpoint, or second invocation | **PURE FUNCTION PASSED; DAG integration pending** — `pixi run pytest tests/test_scenario_rows.py -k rows_are_parse_time_pure` |
| 4 | Python engineer / P1 | Any stochastic unperturbed row is unevaluated/uninventoried or retired toggle is accepted | **NOT IMPLEMENTED** — `pixi run pytest tests/test_scenario_rows.py -k unperturbed_is_evaluated` |
| 5 | Python engineer / P1 | Empty set exits successfully or schedules zero jobs | **NOT IMPLEMENTED** — `pixi run pytest tests/test_scenario_rows.py -k empty_set_refuses` |
| 6 | Python engineer / P2 | Metric/grouping/environment change moves collection/response digests or fails to move metric id | **NOT IMPLEMENTED** — `pixi run pytest tests/test_metric_plan.py -k metric_only_invalidation` |
| 7 | Model builder + model validator / P2 | Any real rapid `run_` catalog resolves the wrong source | **NOT IMPLEMENTED** — proposed `tests/test_run_catalogs.py` plus one rapid preparation |
| 8 | Python engineer / P3 | Complete rapid tree has undeclared successor leaves | **NOT IMPLEMENTED** — extend `tests/test_project_tree_inventory.py`; run `pixi run python dev/scripts/snapshot_project_tree.py --config <POSTCHANGE_CONFIG> --project-dir <POSTCHANGE_ROOT>` |
| 9 | Python engineer + Astra model validator / P3 | Any unexplained A/B delta, C mean mismatch, order-sensitive reference, duplicate, or lost row | **NOT IMPLEMENTED** — proposed GF-9 crosswalk tool/test and two fresh same-config runs |
| 10 | Python engineer + model validator / P2 | Missing/duplicate/extra/invalid expected key publishes ready | **NOT IMPLEMENTED** — `pixi run pytest tests/test_metric_plan.py -k exact_result_keys` |
| 11 | Python engineer / P1 | Simulator signature/AST contains scenario fields or neutral fixture cannot reach dummy | **NOT IMPLEMENTED** — `pixi run pytest tests/test_simulator_adapter.py -k scenario_neutral_boundary` |
| 12 | Python engineer / P2 | Changed byte/revision/model/settings/request reaches execution before named refusal | **NOT IMPLEMENTED** — `pixi run pytest tests/test_simulation_record.py -k stale_reuse_refuses` |
| 13 | Python engineer + model validator / P1 | Empty `st_id` bundle or either return-level row is absent | **NOT IMPLEMENTED** — `pixi run pytest tests/test_metric_registry.py -k unperturbed_bundle` |
| 14 | Python engineer / P1 | Unevaluated reference is accepted or old toggle returns | **NOT IMPLEMENTED** — `pixi run pytest tests/test_metric_registry.py -k unevaluated_reference_refuses` |
| 15 | Python engineer + Astra model validator / P1 + seal gate | Screening/fit/benchmark/policy collapse, refusals fail, or benchmark hides cells/limitations | **NOT IMPLEMENTED** — proposed operational tests in `tests/test_metric_registry.py`; benchmark command awaits reviewed record |
| 16 | Python engineer / P2 | Provider-body change does not move collection id or metric code moves it | **NOT IMPLEMENTED** — `pixi run pytest tests/test_scenario_collection.py -k stage_identity_separation` |
| 17 | Python engineer / P2 | Partial same-intent mutates/reuses, changed intent shares dir, metric growth within fixed capacity changes the collection, or overflow is silent | **NOT IMPLEMENTED** — `pixi run pytest tests/test_scenario_collection.py -k 'partial or capacity'` |
| 18 | Python engineer + model validator / P1 | Invalid ancestry passes or transform consumes a different ancestor | **NOT IMPLEMENTED** — `pixi run pytest tests/test_scenario_rows.py -k pairing_ancestry` |
| 19 | Python engineer + model validator / P3 | Generation needs/model rule appears in fresh DAG | **NOT IMPLEMENTED** — successor CLI test plus real rapid generation without WF1 leaves |
| 20 | Python engineer / P3 | Simulation DAG can produce collection or missing/not-ready collection proceeds | **NOT IMPLEMENTED** — successor CLI test in `tests/test_cli.py` |
| 21 | Python engineer + model validator / P1 | Dummy/Wflow readers need different metric code or Wflow name reaches metric | **NOT IMPLEMENTED** — `pixi run pytest tests/test_response_series.py -k reader_neutral_metrics` |
| 22 | Python engineer / P2 | Metrics-only schedules Wflow, switches identity, or incomplete state reaches execution | **P0 mandatory-runner precursor PASSED; production NOT IMPLEMENTED** — `tests/test_r12_wf3_feasibility.py`; owner-approved runner enforces the synthetic matrix |
| 23 | Python engineer / P2 | Mutation succeeds, shared reuse fails, or referenced delete lacks force | **NOT IMPLEMENTED** — `pixi run pytest tests/test_scenario_collection.py -k immutability_reuse_delete` |
| 24 | Python engineer + model validator / P2 | Unmounted sources/absent model prevent persisted coverage validation or missing row/series passes | **NOT IMPLEMENTED** — `pixi run pytest tests/test_response_inventory.py -k self_contained_coverage` |
| 25 | Python engineer / P3 | Five stanzas/direct/runner disagree or old surfaces do not refuse with migration text | **NOT IMPLEMENTED** — extend `tests/test_config_composition.py`, `test_run_workflows.py`, `test_cli.py` |
| 26 | Python engineer + CST architect / P3 | WF2 edge/digest enters successor identities or runner does not place WF2 last | **NOT IMPLEMENTED** — successor DAG/runner tests |
| 27 | Python engineer + Astra model validator / P3 | Experiment rename/capacity changes seed/forcing or old default/explicit/auto integers drift | **NOT IMPLEMENTED** — proposed `tests/test_generation_seed.py` plus crosswalk execution |
| 28 | Python engineer + Astra model validator / P3 | Leap/right-label/water-year calendar, endpoints, partial blocks, or reductions drift silently | **NOT IMPLEMENTED** — proposed temporal migration fixtures and old/new comparator |
| 29 | Python engineer / P2 mechanism; P3 final entry points/runner | Fresh generation needs a second invocation, stale plan passes, or dry-run invents resolved targets | **NOT IMPLEMENTED** — `pixi run pytest tests/test_source_checkpoint.py`; P2 proves current-carrier equivalent, P3 reruns final direct/runner |
| 30 | Python engineer / P2 mechanism; P3 final entry points/runner | Fresh responses cannot publish matching metric set in one call, or stale/forced/direct target behavior violates §8.4a | **NOT IMPLEMENTED** — `pixi run pytest tests/test_metric_checkpoint.py`; P2 proves current-carrier equivalent, P3 reruns final direct/runner |
| 31 | Python engineer + geospatial analyst + Astra model validator / P2 | Any supported source branch needs live catalog or changes forcing/TOML values; ancillary mismatch passes | **NOT IMPLEMENTED** — proposed portable preparation fixture/comparison covering CHIRPS, CHIRPS-global, non-CHIRPS, E-OBS |
| 32 | Python engineer / P2 | Default scans/falls back, advanced needs sources, or metrics-only accepts a different collection | **NOT IMPLEMENTED** — `pixi run pytest tests/test_collection_resolution.py -k resolution_modes` |

Gate frequency: narrow proposed tests per edit; relevant GF cluster once per commit; P2 current-carrier GF-29/GF-30 plus GF-31/GF-32 once before P3; final-entry-point/runner GF-29/GF-30 again in P3; GF-9/GF-27/GF-28 once at the accepted scientific migration boundary and GF-15 only after its criteria gate; `test-full` once before merge and again only after a new failure or materially changed surface. Store durable logs under `dev/milestones/r12/implementation/evidence/<phase>/`.
