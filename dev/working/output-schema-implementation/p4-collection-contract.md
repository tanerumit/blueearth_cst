# Task Brief — P4 Collection contract

### Context

Read `AGENTS.md`, [master brief](master-brief.md), [schema](../complete-run-output-schema.md) §§2–3, 7–8. P1 supplies archives; P4 establishes the new WF3 collection identity consumed by P5/P6.

### Goal

Establish the versioned, model-independent collection contract and readers as an additive foundation. P5 makes the coordinated default WF3 producer switch after its Snakefile and provider paths are ready; P6 completes WF4 adoption. Do not claim P4 has published a new default-layout collection.

### Non-goals

No change to stochastic science, upstream HydroMT/Wflow internals, or sealed collection bytes.

### Allowed scope

Permitted: `blueearth_cst/experiment/scenario_collection.py`, `collection_resolution.py`, `scenario_provider.py`, `generation_plan.py`, `content_identity.py`, directly affected readers/tests/docs, and the WF4 elevation-binding code identified by remeasurement. Approval-gated: unresolved identity semantics beyond the schema. Forbidden: hand-edited `project_dir` output and Wflow-owned setting filenames.

### Required changes (checklist)

- [ ] Implement and test readers and validators for the accepted new scenario root/engine split, embedded four WF3 sidecars, full-ID/short-path binding, lookup headers and stochastic lineage. No pre-migration reader is required.
- [ ] Specify and test the new collection identity projection without WF4 elevation/preparation; implement the P0 automatic-seed policy independently of incidental provider-code/path edits.
- [ ] Implement shared orography storage/reference validation and prepare the WF4 elevation handoff specified in P0, without switching the default WF3 producer or requiring unfinished P6 experiment records.
- [ ] Inventory current producer and consumer paths before the P5 switch; hand P5 a concrete WF3 change list and P6 the WF4 collection-consumption change list.

### Commit plan

| Subject | Paths | Invariant |
|---|---|---|
| Establish the new collection reader and identity | Readers, validators, identity projections, tests/docs | Current producer remains runnable during P4; new fixtures validate the accepted contract. |

### Validation

Per edit: matching focused tests. Falsifiers: an orphan marker reads ready, changed WF4 orography changes a new collection ID, or reconstructed lineage differs from the current stochastic rows. Exercise reuse/refusal with before/after checksums on new-schema fixtures. Run the master brief's broader gates at its named boundary.

### Acceptance criteria

The accepted new schema is readable and validated from fixtures while the current production workflow remains runnable during P4. P5 owns first production emission and its end-to-end collection publication check.

### Output requirements

Report new-reader evidence, identity deltas, lineage comparison and unresolved cross-workflow risks.

### Task constraints

Honor the master brief's human gate and shared constraints. Do not silently treat a scenario series as Wflow-ready forcing.
