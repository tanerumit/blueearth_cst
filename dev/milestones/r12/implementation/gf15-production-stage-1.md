# Task Brief — GF15 snapshot and setup, Stage 1/4

### Context
Follow AGENTS.md, the [master brief](gf15-production-integration-brief.md) and accepted design D7-D8. Current source is still the predecessor estimator. Scratch is disposable; durable manifests and commands belong with new execution evidence.

### Goal
Secure an immutable, complete pre-change comparison and qualify isolated dependency setup before numerical implementation.

Owner sequencing override, 2026-09-14: qualify Windows now; Linux provisioning
and execution are deferred to the R12 TODO checklist. A Windows-only handoff
may release Windows implementation, with Linux explicitly outstanding.

### Non-goals
No adapter edits, fits, model/generation reruns, standing baseline repair or scientific requalification.

### Allowed scope
Permitted: read retained P3 projects and recorded commands; create fresh snapshot/setup evidence under `evidence/gf15-production-integration/` and isolated session scratch. Inspect executable availability and solve/install only in a separate environment. Approval-gated: unavailable exact platform targets or a missing complete comparison require owner direction. Forbidden: mutating shared Pixi, existing evidence, retained source projects or hand-editing locks.

### Required changes (checklist)
- Locate a complete retained experiment from P3 evidence; prove its retained ready set and all reader dependencies are present. Do not substitute the stale standing fixture.
- Freeze a separate read-only snapshot; record every D8 identity, source/config/environment field and exact old command. Hash original and copy; document scientific and operational namespaces.
- Resolve Pixi executable and isolated win/linux setup with lmoments3==1.0.8 and D7 source/wheel checks. Record actual numerical/native closure; exact parity targets are prerequisites, not installed-version assumptions.
- Materialize the new metrics operation/config and exact documented CLI from source without executing it. Independent integrity review must accept snapshot/setup before Stage2.

### Commit plan
Snapshot inventory precedes the first implementation commit. Preserve snapshot and predecessor sources through independent comparison acceptance.

### Validation
Use retained P3 execution records to locate projects; verify with current `read_metric_set` and byte inventories in read-only mode. Record the exact invocation in evidence. Missing reader dependency or differing copy hash falsifies completeness/integrity. D7 hashes and installed metadata falsify source/environment qualification. Unavailable supported-platform execution stays outstanding. Re-measure availability and paths on execution; none is guaranteed by this brief.

### Acceptance criteria
Independent reviewer accepts complete immutable snapshot, reproducible old/new commands and isolated qualified setup. If any prerequisite fails, retain diagnostic evidence and stop before implementation.

### Output requirements
Retained inventory, setup/command record and explicit pass/fail/outstanding handoff; no raw production outputs committed.

### Task constraints
No nested delegation by the executor. Request the independent reviewer through the driver. Keep source and data copies outside output write targets; do not silently relax platform pins or replace the comparison.
