# Task Brief — P4 Collection contract

### Context

Read `AGENTS.md`, [master brief](master-brief.md), [schema](../complete-run-output-schema.md) §§2–3, 7–8. P1 supplies archives; P4 establishes the new WF3 collection identity consumed by P5/P6.

### Goal

Publish model-independent `scenarios/<collection-id>/` products with one scenario `_engine/`, two collection scientific JSON records, and versioned discovery.

### Non-goals

No change to stochastic science, upstream HydroMT/Wflow internals, or sealed collection bytes.

### Allowed scope

Permitted: `blueearth_cst/experiment/scenario_collection.py`, `collection_resolution.py`, `scenario_provider.py`, `generation_plan.py`, `content_identity.py`, directly affected readers/tests/docs, and the WF4 elevation-binding code identified by remeasurement. Approval-gated: unresolved identity semantics beyond the schema. Forbidden: hand-edited `project_dir` output and Wflow-owned setting filenames.

### Required changes (checklist)

- [ ] Move new collection records to `scenarios/_engine/collections/<id>/`; preserve request/collection distinction and full-ID/short-path binding.
- [ ] Embed the four WF3 sidecars in `collection_intent.json`, publish `collection.json` only after product verification, and keep legacy readers for old collections.
- [ ] Move WF4-only elevation/preparation binding out of new collection identity; keep shared orography under project climate data and bind it in experiment intent.
- [ ] Publish `series/run_<id>.nc`, `scenario_run_lookup.csv` (`run_id,evaluate,type,rlz,st_id`) and `perturbation_lookup.csv`; validate the unique empty-`st_id` root per realization and full cross-product.

### Commit plan

| Subject | Paths | Invariant |
|---|---|---|
| Version the collection contract | Producers, identity digests, readers, tests/docs | New schema and all consumers switch together; old sealed outputs remain unchanged. |

### Validation

Per edit: matching focused tests. Falsifiers: an orphan marker reads ready, changed WF4 orography changes a new collection ID, reconstructed lineage differs from old rows, or legacy collections stop reading. Exercise reuse/refusal with before/after checksums. Run the master brief's broader gates at its named boundary.

### Acceptance criteria

New collections have the proposed paths and two machine JSONs, bind checked products, and remain model-independent; sealed collections still read without byte changes.

### Output requirements

Report old/new reader evidence, identity deltas, lineage comparison and unresolved cross-workflow risks.

### Task constraints

Honor the master brief's human gate and shared constraints. Do not silently treat a scenario series as Wflow-ready forcing.
