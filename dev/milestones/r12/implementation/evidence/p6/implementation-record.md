# P6 simulation and metric-set/2 implementation record

P6 adopts the versioned WF3 collection in WF4 and completes the successor
simulation, response, and metric-set storage contracts. This is implementation
evidence, not the fresh numerical acceptance record; P7 owns that comparison.

## Artifact contract

| Record or artifact | Schema/path |
|---|---|
| Simulation intent | `experiments/<name>/_engine/simulation_intent.json` (`simulation-intent/2`) |
| Ready simulation | `experiments/<name>/_engine/simulation.json` (`simulation/2`) |
| Response inventory | `experiments/<name>/_engine/response_inventory.json` (`response-inventory/2`) |
| Metric-set marker | `experiments/<name>/_engine/metric_sets/<short-id>/metrics.json` (`metric-set/2`) |
| Metric membership | `experiments/<name>/results/metric_sets/<short-id>/metric_run_lookup.csv` |
| Metric indicators | `experiments/<name>/results/metric_sets/<short-id>/<token>_indicators.csv` |

The paired `_engine` and `results` directories derive their shared short ID
from one full metric-set ID. The membership header is
`run_group_id,grain,run_id`; every indicator table uses
`metric,location,run_group_id,value`. No successor user-facing metric table
uses `unit_id`.

## Behavior retained and added

- WF4 freezes the selected collection, source/config archive, simulator,
  preparation, response request, and environment before native responses run.
- Readiness is published only after native response verification and its
  complete response inventory have been published.
- Metrics-only resolves an existing ready v2 simulation and exact planned
  metric output. It does not schedule WF1, WF3, forcing preparation, or Wflow
  execution.
- The established metric declarations, allocation order, and reduction
  calculations remain shared with the predecessor implementation. Versioned
  dispatch changes storage identity, record layout, and join-key spelling only.

## Focused validation

| Check | Result |
|---|---|
| `pixi run pytest tests/test_response_inventory_v2.py tests/test_simulation_record_v2.py tests/test_simulation_runner_v2.py tests/test_wf4_preparation_v2.py tests/test_metric_plan.py tests/test_p2_current_carrier.py tests/test_cli.py -q` | 71 passed |
| `pixi run lint` | passed |
| `pixi run format-check` | passed |
| `git diff --check` | passed |

The tests exercise path-neutral simulation/response identities, source capture,
local temporal references, retained collection-source binding, exact
operation/target validation, v2 metric publication/read-back, paired directory
identity, and the two successor CSV headers.

## Numerical boundary

No metric definition, aggregation, or numerical tolerance was changed. The
synthetic metric-set/2 test proves storage translation and retained read-back,
but it is not a scientific equivalence result. P7 must run an isolated rapid
successor tree and compare its native responses and requested metrics against
the pinned predecessor comparator under the required seed controls.
