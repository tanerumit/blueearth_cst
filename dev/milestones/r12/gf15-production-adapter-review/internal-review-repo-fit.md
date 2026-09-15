---
verdict: revise
doc_version: design-v2.md
findings:
  - id: repo-1
    severity: major
    section: D5-D7; validation plan, Identity/report
    finding: The design does not close the existing gap between the retained metric environment and the environment actually executing a retained plan.
    rationale: build_metric_plan passes request.metric_environment back into metric_request unchanged. Both reduce_metric_plan and publish_metric_set use that rebuild as their freshness check. D7 adds lmoments3 roots and its source guard, while D5 explicitly rechecks the packaged report and source bindings; neither specifies recomputing the live numerical environment at execution. Consequently a plan created with NumPy/SciPy environment A can execute under environment B and publish estimates bearing A's metric_environment and metric_set_id, even when the lmoments3 files remain correctly pinned. Existing identity tests change the supplied environment or create a fresh request, so they do not detect this retained-plan case. This is a pre-existing mechanism that the new reproducible-mapping claim relies on without closing, not a newly introduced implementation regression.
    suggested_fix: Require a single bounded metric-environment projection, including D7 source identity, shared by current_metric_request and the new-set execution freshness check. Recompute it before reduction/publication and refuse a retained-plan mismatch with MetricPlanStale before fitting or payload publication. Keep historical read_metric_set validation independent of the live environment. Add a discriminating retained-plan test that changes the observed numerical environment after planning, without changing the retained request or lmoments3 source hashes, and expects refusal and no ready marker.
  - id: repo-2
    severity: minor
    section: D5; D8 affected files
    finding: The proposed distributable/package-asset verification does not specify the repository's actual source-tree distribution model.
    rationale: pyproject.toml explicitly declares that blueearth_cst is a plain importable directory, with no project or build-system table, and that real packaging needs a superseding decision. Package resources can work in that existing model, but an instruction to test without the source checkout can also be interpreted as introducing a wheel/build backend, which would expand this adapter task beyond the listed files and accepted packaging boundary.
    suggested_fix: State that this task adds a tracked resource to the existing importable source tree and tests a relocated copy containing the required package source and asset, with dev/scratch and the original checkout unavailable. Do not introduce an installable distribution or packaging manifest in this task; handle that separately if it becomes necessary.
  - id: repo-3
    severity: minor
    section: D8; validation plan, Metrics-only
    finding: The literal artifact allowlist excludes an invocation record that the required existing entry point always writes.
    rationale: scripts/simulate_system.py creates and updates project_dir/config/runs/invocations/simulation-<id>.json before and after its Snakemake invocation. Therefore the proposed command can satisfy retained-response-only computation while failing the stated condition that only new metric-plan/set/report artifacts appear. The invocation record is existing operational behavior, not a new adapter output or upstream scientific mutation.
    suggested_fix: Limit the strict metric-artifact allowlist to the selected experiment's results namespace, and separately allow the existing invocation record and declared attempt logs outside retained scientific inputs. Continue requiring exact collection, simulation, response request/inventory and native response bytes.
---

Repository-fit review of design-v2.md under the settled G1 Option A scope. Verdict: **REVISE** — 0 blocking, 1 major, 2 minor. The major concerns provenance correctness when executing an existing plan; it does not reopen C, the approved 8x policy, screening, or actual-bundle adequacy.

The proposed implementation otherwise extends actual repository patterns. `metric_registry.reduce_bundle` already extracts member-local annual blocks, orders members numerically, filters finite blocks, screens before fitting, and returns float64 values with per-location evidence. D1 preserves those boundaries. Replacing the predecessor fitting section and its broad exception conversion is a contained change. Existing estimator-equality and broad-exception tests in `tests/test_metric_registry.py:136` and `:196` must be updated to the explicitly changed C/fault contract while keeping their extraction assertions; they are not valid unchanged acceptance tests for a different estimator.

`metric_plan.publish_metric_set` already completes all reduction before writing payloads and publishes `metrics.json` last. Adding the checked report to its payload dictionary fits that sequence. `_read_metric_set` validates retained definitions rather than calling the current registry, so the proposed legacy/new inner-validation dispatch can preserve historical reads without loading lmoments3 or the current report. `content_identity.repository_code_inventory` follows static imports, including imports inside functions; the proposed adapter and loader can therefore be included while numerical imports stay lazy. Explicit report binding through the declaration is necessary because JSON assets are not discovered as Python imports.

Evidence for repo-1: `blueearth_cst/experiment/metric_plan.py:139`, `:229`, `:239`, `:403`, `:529`; `blueearth_cst/experiment/content_identity.py:140`; `tests/test_metric_plan.py:132` and `:303`. The existing stage_environment projection tracks numerical package versions, Python distribution metadata and native Conda closure, but it is only freshly obtained by current_metric_request. D7 can extend that returned dictionary locally with verified estimator source hashes; a shared-helper rewrite is not intrinsically required.

Evidence for repo-2: `pyproject.toml:4` and its opening packaging decision comments. The design's package-resource approach is feasible without changing that decision. Evidence for repo-3: `scripts/simulate_system.py:46`, `:59` and `:77`.

The D7 file hashes match the directly cited readiness environment record. Isolated Pixi solving, platform parity, a suitable pre-change snapshot, relocated resource inclusion and scientific comparison remain unexecuted prerequisites, as the design states. They are not treated as completed merely because their contracts are reviewable.

Validation was source inspection only. No tests, collection, numerical fits, installs, network operations, Git operations or implementation changes were performed, per the review boundary. Only this review artifact was written. Other review artifacts, the ledger and the review index were not consulted.
