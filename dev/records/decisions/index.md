# Historical decisions and current references

These records preserve rationale, evidence and former designs. Their status fields describe the time
recorded; they are not a second source of current requirements. Update the owning current reference
when policy or implementation changes. New work does not require another numbered ADR.

| Retained record | Current owner / interpretation |
|---|---|
| [0001 — Wflow constants](0001-restore-wflow-constant-parameters.md) | [Model construction](../../reference/workflows/model_creation.md); exact values remain in the build template |
| [0002 — Subcatchment climate plots](0002-revive-subcatchment-climate-plots.md) | Superseded historical proposal; use the model construction contract |
| [0003 — Shared region](0003-one-shared-region-artifact.md) | [Spatial foundation](../../reference/spatial-foundation.md) and current spatial code |
| [0004 — Model-root sentinel](0004-order-model-readers-on-a-terminal-sentinel.md) | [Model construction](../../reference/workflows/model_creation.md#mutable-model-root-ordering) |
| [0005 — Formatter adoption](0005-adopt-ruff-format-in-two-stages.md) | [Validation ladder](../../reference/validation-ladder.md); tool configuration owns scope |
| [0006 — Retire duplicate climate plots](0006-retire-subcatchment-climate-plots.md) | [Model construction](../../reference/workflows/model_creation.md#outputs-and-consumers) |
| [0007 — Basin-area maps](0007-draw-basin-area-from-the-spatial-foundation.md) | [Spatial foundation](../../reference/spatial-foundation.md#basin-maps) |
| [0008 — Repository-based distribution](0008-ship-blueearth-cst-unpackaged.md) | [Toolbox architecture](../../reference/toolbox-architecture.md#implementation-ownership) |
| [0009 — Generation/simulation split](0009-split-scenario-generation-and-system-simulation.md) | [Toolbox architecture](../../reference/toolbox-architecture.md#workflow-boundaries) |
| [0010 — Forcing admission](0010-check-the-reviewed-variables-not-the-catalog-shape.md) | [Forcing units](../../reference/contracts/forcing-units.md) |
| [0011 — Configuration archives](0011-preserve-config-sources-with-run-records.md) | [Configuration and records](../../reference/toolbox-architecture.md#configuration-and-execution-records); original pending label is historical, not a current implementation assessment |
| [0022 — Scheduler-neutral run contract](0022-cst-capability-slots-and-run-contract.md) | Retained accepted design; no blanket runtime-adoption claim. Consult the current launcher boundaries in toolbox architecture |
| [Experiment numbering evidence](experiment-numbering-2026-10-10/implementation-evidence.md) | [Repository layout](../../reference/repo-layout.md#scripts) |
| [Former atomic task-lane policy](task-lanes.md) | [Development workflow](../../reference/development-workflow.md); atomic-lane prose is historical |

The sidecar folders retain evidence cited by these records. Preserve original IDs and cited details;
follow [record lifecycle](../../reference/record-lifecycle.md) before shortening or deleting them.
Pending future changes belong on the canonical board. Do not implement a retained proposal merely
because its historical status says accepted.
