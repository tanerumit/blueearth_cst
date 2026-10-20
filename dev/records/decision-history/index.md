# Decision history

These records answer why a significant choice was made at the time. Use
[dev/reference/README.md](../../reference/README.md) for current decisions and compliance.
An old acceptance label, imperative statement or implementation plan is historical evidence,
not an instruction to implement or enforce it today.

Retained records preserve alternatives and qualified measurements. Condensed ADRs 0001, 0003 and 0022
include original-section recovery maps and full-source pins at `e9bbd72d`; historical section citations
resolve against those originals rather than a newly numbered summary.
Their original dates and status fields are not maintained as a second current account.
The [lifecycle](../../reference/dev-record-lifecycle.md) governs admission and retention;
ordinary reference updates do not require a new history record.

## History and current topic owners

- [0001-restore-wflow-constant-parameters.md](0001-restore-wflow-constant-parameters.md)
  — [wf1-model-construction.md](../../reference/wf1-model-construction.md).
  Numerical evidence and historical configs moved to `../validation/wflow-constant-restoration/`.
- [0002-revive-subcatchment-climate-plots.md](0002-revive-subcatchment-climate-plots.md)
  — superseded plotting lineage; current ownership is in
  [wf1-model-construction.md](../../reference/wf1-model-construction.md).
- [0003-one-shared-region-artifact.md](0003-one-shared-region-artifact.md)
  — [toolbox-spatial-foundation.md](../../reference/toolbox-spatial-foundation.md).
- [0004-order-model-readers-on-a-terminal-sentinel.md](0004-order-model-readers-on-a-terminal-sentinel.md)
  — [wf1-model-construction.md](../../reference/wf1-model-construction.md#mutable-model-root-ordering).
- [0005-adopt-ruff-format-in-two-stages.md](0005-adopt-ruff-format-in-two-stages.md)
  — [dev-validation.md](../../reference/dev-validation.md); `pyproject.toml` owns formatter scope.
- [0006-retire-subcatchment-climate-plots.md](0006-retire-subcatchment-climate-plots.md)
  — [wf1-model-construction.md](../../reference/wf1-model-construction.md#outputs-and-consumers).
- [0007-draw-basin-area-from-the-spatial-foundation.md](0007-draw-basin-area-from-the-spatial-foundation.md)
  — [toolbox-spatial-foundation.md](../../reference/toolbox-spatial-foundation.md#basin-maps).
- [0008-ship-blueearth-cst-unpackaged.md](0008-ship-blueearth-cst-unpackaged.md)
  — [toolbox-architecture.md](../../reference/toolbox-architecture.md#implementation-ownership).
- [0009-split-scenario-generation-and-system-simulation.md](0009-split-scenario-generation-and-system-simulation.md)
  — [toolbox-architecture.md](../../reference/toolbox-architecture.md#workflow-boundaries).
- [0010-check-the-reviewed-variables-not-the-catalog-shape.md](0010-check-the-reviewed-variables-not-the-catalog-shape.md)
  — [toolbox-forcing-units.md](../../reference/toolbox-forcing-units.md).
- [0011-preserve-config-sources-with-run-records.md](0011-preserve-config-sources-with-run-records.md)
  — [toolbox-architecture.md](../../reference/toolbox-architecture.md#configuration-and-execution-records).
  The old pending status and proposed paths are not a current implementation assessment.
- [0022-cst-capability-slots-and-run-contract.md](0022-cst-capability-slots-and-run-contract.md)
  — [toolbox-architecture.md](../../reference/toolbox-architecture.md#configuration-and-execution-records).
  Historical accepted design with conditional applicability, not universal launcher adoption.
  The `cst-run-control` skill owns the shared operational specification.
- [task-lanes.md](task-lanes.md)
  — [dev-task-and-session-workflow.md](../../reference/dev-task-and-session-workflow.md).
  Retained rationale and measurements; obsolete operational instructions were retired.

## Evidence and recovery

Experiment-numbering evidence moved to
[implementation-evidence.md](../validation/experiment-numbering-2026-10-10/implementation-evidence.md).
It is a record of verification, not a decision-policy source.

[decision-history-transition-2026-10-20.md](../migrations/decision-history-transition-2026-10-20.md)
maps all former paths and retired sidecars to their retained homes or pinned Git originals.
Use that map for historical citations rather than recreating the former `decisions/` folder.
