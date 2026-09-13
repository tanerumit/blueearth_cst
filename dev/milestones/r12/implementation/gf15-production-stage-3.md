# Task Brief — GF15 metrics comparison, Stage 3/4

### Context
Follow AGENTS.md, the [master brief](gf15-production-integration-brief.md), accepted D8 and passed Stage1/2 evidence.

### Goal
Demonstrate complete, explainable predecessor-to-C differences using retained native responses and unchanged upstream identities.

### Non-goals
No Wflow/generation run, snapshot write, old-set relabeling, arbitrary old/new equality tolerance or baseline refresh.

### Allowed scope
Permitted: separate new metric namespace and `evidence/gf15-production-integration/` comparison record; required existing invocation/attempt logs identified in Stage1. Approval-gated: incomplete comparison or scientific mismatch requires disposition. Forbidden: collection/simulation/response mutation and snapshot changes.

### Required changes (checklist)
- Run the Stage1 materialized metrics command with Wflow/Julia/generation access disabled.
- Compare every metric/location/unit key, non-return-level rows exactly and return levels with float64 evidence and preserved member extraction/coverage.
- Verify upstream bytes/requests/inventories fixed; new identity/report correct. Record allowed operational logs separately from experiment results.
- On any abort, record first failure and every remaining unevaluated key; no ready marker or migration pass. Separate diagnostics cannot convert failure to acceptance.

### Validation
Accepted design Metrics-only row: exact Stage1 argv plus before/after inventories. Model invocation, upstream hash drift, changed non-return-level row, missing comparison key or ready marker after refusal falsifies the claim. Verify four-column formatting and documentation/migration disclosure of detached CSV vintage ambiguity.

### Acceptance criteria
Model-validator accepts complete comparison, preserved extraction and documented estimator differences. Aborted or partial comparison cannot pass.

### Output requirements
Comparison table, coverage/failure inventory, original/new provenance and independent verdict; outputs remain outside Git.

### Task constraints
Keep snapshot immutable until independent acceptance. No retry that changes estimator policy or evidence identity to hide a failure.
