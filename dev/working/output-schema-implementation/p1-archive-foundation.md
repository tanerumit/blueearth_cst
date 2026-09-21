# Task Brief — P1 Archive foundation

### Context

Read `AGENTS.md`, [master brief](master-brief.md), [schema](../complete-run-output-schema.md) §§4–5 and ADR 0011. This phase establishes the archive/reference contract consumed by later phases.

### Goal

Capture exact user-provided configuration bytes and publish a verifiable run record with resolvable source references.

### Non-goals

No workflow-wide path switch, scientific computation change or old-output rewrite.

### Allowed scope

Permitted: `blueearth_cst/shared/workflow_config_snapshot.py`, `blueearth_cst/shared/provenance.py`, `blueearth_cst/shared/config_composition.py`, the actual config-copy writer located by remeasurement, and directly matching tests/docs. Approval-gated: identity semantics beyond schema §§4–5. Forbidden: generated `project_dir` trees and upstream packages.

### Required changes (checklist)

- [ ] Define one mapping from loaded configuration and custom dependencies to preserved original bytes/names.
- [ ] Publish `run_record.yml` and `sources/` as a matching archive; do not expose a mixed record/source state on interruption.
- [ ] Keep provenance/reference semantics versioned and readable for old archives.

### Validation

Per edit: run matching focused tests. New behavior: test comment/CRLF and basename preservation, missing originals during reuse, and interrupted publication; a byte mismatch or mixed archive falsifies the claim. Before commit: applicable Python lint/format checks. Run broader gates only at the master brief's named boundary.

### Acceptance criteria

Every source named in a new record resolves to its exact archived bytes; a failed publication does not look complete. Old records still read unchanged.

### Output requirements

Report changed files, schema/version effects, focused commands/results and remaining archive risks.

### Task constraints

Honor the master brief's human gate and shared constraints. Do not invent a fallback source when exact bytes are unavailable.
