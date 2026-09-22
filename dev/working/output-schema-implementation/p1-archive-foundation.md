# Task Brief — P1 Archive foundation

### Context

Read `AGENTS.md`, [master brief](master-brief.md), [accepted schema](../complete-run-output-schema.md) §§4–5 and 10.2–10.4, and ADR 0011. P0 settled the archive transaction, rerun-path and version contracts. Pin the predecessor WF4 environment and inputs before runtime edits as §10.9 requires. This phase establishes the archive/reference implementation consumed by later phases.

### Goal

Capture exact user-provided configuration bytes and publish a verifiable run record with resolvable source references.

### Non-goals

No workflow-wide path switch or scientific computation change.

### Allowed scope

Permitted: `blueearth_cst/shared/workflow_config_snapshot.py`, `blueearth_cst/shared/provenance.py`, `blueearth_cst/shared/config_composition.py`, the actual config-copy writer located by remeasurement, and directly matching tests/docs. Approval-gated: identity semantics beyond schema §§4–5. Forbidden: generated `project_dir` trees and upstream packages.

### Required changes (checklist)

- [ ] Define one mapping from loaded configuration and custom dependencies to preserved original bytes/names.
- [ ] Publish `run_record.yml` and `sources/` as a matching archive; do not expose a mixed record/source state on interruption.
- [ ] Implement P0's source-path and recovery policy for sibling/nested YAMLs, absolute references and colliding names; capture the exact pre-parse bytes that are loaded, not a later reread of mutable paths. Preserve the accepted A→B rerun→relocated C mapping and retained predecessor evidence.
- [ ] Implement `run-record/2` and the versioned source/reference projections in §10.2; update current consumers. No pre-migration archive reader is required. Keep terminal rollback/unpublished states and next-writer admission explicit.

### Validation

Per edit: run matching focused tests. New behavior: test comment/CRLF and basename preservation, missing originals during reuse, pre-parse mutation, duplicate basenames, A→B→C relocation, and interrupted publication at every named boundary with second-reader/recovery/next-writer admission. A byte mismatch or mixed archive falsifies the claim. Before commit: applicable Python lint/format checks. Run broader gates only at the master brief's named boundary.

### Acceptance criteria

Every source named in a new record resolves to its exact archived bytes; a failed publication does not look complete.

### Output requirements

Report changed files, schema/version effects, focused commands/results and remaining archive risks.

### Task constraints

Honor the master brief's human gate and shared constraints. Do not invent a fallback source when exact bytes are unavailable.
