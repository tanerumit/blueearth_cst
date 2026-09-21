# Task Brief — P4 Collection contract

### Context

Read `AGENTS.md`, [master brief](master-brief.md), [accepted schema](../complete-run-output-schema.md) §§2–3, 7–8 and 10.2, 10.6–10.9. P1 supplies archives; P4 establishes the new WF3 collection identity consumed by P5/P6. The independent predecessor WF1/WF4/metrics comparator in §10.9 must be captured before P4 changes the collection/module boundary.

### Goal

Establish the versioned, model-independent collection contract and readers as an additive foundation. P5 makes the coordinated default WF3 producer switch after its Snakefile and provider paths are ready; P6 completes WF4 adoption. Do not claim P4 has published a new default-layout collection.

### Non-goals

No change to stochastic science, upstream HydroMT/Wflow internals, or sealed collection bytes.

### Allowed scope

Permitted: `blueearth_cst/experiment/scenario_collection.py`, `collection_resolution.py`, `scenario_provider.py`, `generation_plan.py`, `content_identity.py`, directly affected readers/tests/docs, and the WF4 elevation-binding code identified by remeasurement. Approval-gated: unresolved identity semantics beyond the schema. Forbidden: hand-edited `project_dir` output and Wflow-owned setting filenames.

### Required changes (checklist)

- [ ] Implement and test `scenario-collection/2` readers and validators for the accepted new scenario root/engine split, embedded four WF3 sidecars, full-ID/short-path binding, lookup headers and stochastic lineage. Apply the closed nested profiles and digest operations in §10.2.1. No pre-migration reader is required.
- [ ] Implement and test `generation-seed-material/2` and collection identity without WF4 elevation/preparation. Retain the canonical digest-to-integer method; accept numeric seed changes caused by new material or generator-code inventory. Move WF4 preparation logic out of inventoried WF3 code. Test that changing WF4 elevation, settings or WF4-only code leaves the new seed and collection ID unchanged while consumed WF3 changes remain sensitive or refuse. Hand the §10.6 excluded-field acceptance matrix to P5 for empirical execution.
- [ ] Implement shared orography storage/reference validation and prepare the WF4 elevation handoff specified in P0, without switching the default WF3 producer or requiring unfinished P6 experiment records.
- [ ] Inventory current producer and consumer paths before the P5 switch; hand P5 a concrete WF3 change list and P6 the WF4 collection-consumption change list.

### Commit plan

| Subject | Paths | Invariant |
|---|---|---|
| Establish the new collection reader and identity | Readers, validators, identity projections, tests/docs | Current producer remains runnable during P4; new fixtures validate the accepted contract. |

### Validation

Per edit: matching focused tests. Falsifiers: an orphan marker reads ready, changed WF4 orography or WF4-only code changes a new collection ID or automatic seed, or reconstructed lineage differs from the clean predecessor stochastic rows. Exercise complete canonical vectors, reuse/refusal with before/after checksums, and fixed verified WF3 source bytes on new-schema fixtures. Run the master brief's broader gates at its named boundary.

### Acceptance criteria

The accepted new schema is readable and validated from fixtures while the current production workflow remains runnable during P4. P5 owns first production emission and its end-to-end collection publication check.

### Output requirements

Report new-reader evidence, identity deltas, lineage comparison and unresolved cross-workflow risks.

### Task constraints

Honor the master brief's human gate and shared constraints. Do not silently treat a scenario series as Wflow-ready forcing.
