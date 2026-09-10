# Scoped verification of design v6

Review the v5-to-v6 delta under the design-review-loop process. This is a scoped
verification of an owner-requested interface simplification, not external round 2.
Act as an independent architectural and scientific/methodological verifier using
Astra. The author is the registered CST architect (Sol); the review has a fresh
context. No nested delegation.

## Inputs and settled authority

Start with `v5-v6.diff`, then read the affected sections and necessary interactions
in `design-v5.md` and `design-v6.md`; a full reread of the unchanged baseline is
unnecessary. Read the
owner simplification ruling dated 2026-09-10 in `status.md` and only the associated
v6 owner-change entry in `ledger.md`. Inspect directly relevant repository sources
when needed to test a factual premise. Do not re-review unchanged decisions or
seed findings from unrelated historical reports.

The owner approved hiding computed collection and simulation identities from
ordinary use while retaining their internal provenance and correctness functions.
Ordinary use should expose experiment_name, scientific/model settings, run_id and
unit_id. The routine config should not require hashes, manifest paths, or a
collection selector. Explicit external manifest reuse remains an advanced option.
No rename to seed_id, simulation_set_id, model_config, or model_setup was approved.
Independent generation, direct simulation, and metrics-only execution must remain.
This approval establishes the desired behavior, not proof that the design meets it.

Production remains stochastic/Wflow, with CMIP as a terminal plausibility overlay.
Scientific treatments, capacity safeguards, exact identities, source and response
checkpoints, immutable artifact validation and stale-result refusal remain intact.
The historical Class-B fit-interval deferral still needs a separate G2 owner ruling.
Scientific benchmarks and runtime gates remain unexecuted; approval of this delta
does not validate those empirical claims or authorize implementation.

## Review questions

1. Does the routine scaffold and documented flow actually remove the need to
   choose/copy collection or simulation identifiers, while keeping advanced reuse?
2. Is omitted-selector resolution deterministic and fail-closed for missing,
   changed, stale, ambiguous or incompatible inputs? Check runner and direct entry
   points, generation disabled, moved/portable inputs, and metrics-only semantics.
3. Are hashes still computed/validated at the correct boundaries? Could a friendly
   name, inferred default or retained simulation accidentally select stale data?
4. Are config tables, examples, summaries, migration, alternatives and acceptance
   gates internally consistent? Are user-facing errors actionable without requiring
   knowledge of internal identity machinery?
5. Did this delta alter any scientific assumption, seed behavior, coverage
   obligation, portability contract or prior correctness safeguard inadvertently?

Review changed mechanisms and their interactions; do not copyedit. Distinguish
unexecuted acceptance gates from a false claim that they already passed.

## Authority and report

Read-only; no file writes, commits, simulations, implementation or delegation.
The driver captures the final response as an immutable report. Return Markdown:

```yaml
verdict: approve | revise | reject
doc_version: design-v6.md
scope: v5-to-v6 owner-approved interface simplification
```

Include a verification table for the five questions, with section evidence.
New findings use `delta-v6-1`, etc., severity `blocking | major | minor`, affected
section, observable consequence and concrete suggested fix. Blocking means fails,
produces wrong results or cannot be implemented; major means meaningful observable
degradation/risk with a clear fix; minor is discretionary. No approve verdict with
blocking or major findings. An empty finding list is valid. Conclude with remaining
empirical gates and owner decisions, separate from new design defects.
