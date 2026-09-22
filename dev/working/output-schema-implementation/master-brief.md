# Master Brief — Complete-run output schema migration

### Goal

Implement the owner-accepted P0 contract in [complete-run-output-schema.md](../complete-run-output-schema.md), especially normative §10, without changing scientific computations. The reviewed contract was accepted on 2026-09-21; implementation and scientific comparison remain to be completed.

### Subsystem map

| Phase | Owner | Input | Expected output |
|---|---|---|---|
| P0 | Design owner and reviewer | Schema §§2–10; ADR 0011; WF3 intake | Accepted contracts and clean WF3 reference; predecessor WF4 comparator still required before P4 |
| P1 | Phase executor | P0; schema §§4–5, 10.2–10.4 | Exact source archive and common record/reference writer |
| P2 | Phase executor | P1 | WF0–WF2 and artifact-local archives |
| P3 | Phase executor | P1 | Unified parent/child invocation history |
| P4 | Phase executor | P1; predecessor WF4 comparator; schema §§3, 7–8, 10.6–10.8 | Additive versioned collection contract and shared elevation ownership |
| P5 | Phase executor | P3–P4 | First new WF3 collection emission, static plan and provider output paths |
| P6 | Phase executor | P4–P5 | WF4 adoption, simulation and metric-set records/results |
| P7 | Phase executor | P1–P6 | Isolated complete-run evidence |

### Sequencing

P0 settles the contract decisions listed below and obtains a review of the selected design before runtime implementation. P1 establishes archive/reference interfaces before P2–P4 adopt them. P2 and P3 may proceed independently after P1 if they do not edit the same entry points; otherwise sequence their shared files. P4 is an additive contract and reader foundation: it must not switch the default WF3 producer while its Snakefile and WF4 consumers still require the old layout. P5 makes the coordinated WF3 producer/consumer switch, including the paths and archive adoption; WF4 must explicitly refuse the new collection until P6 adopts it, rather than misread it. P6 then adopts the new collection in WF4 and its own archive and metric contracts. Each phase exit must state which schema versions it emits and reads and pass focused checks before its commit. P7 runs only after P1–P6 pass their focused checks. Some modules are deliberately touched in successive phases; ownership is time-sliced, never concurrent. Re-measure file ownership and consumer paths before scheduling work; the 2026-09-21 candidate map in schema §11 is not a verified exhaustive inventory.

### Shared constraints

- Read `AGENTS.md`, the accepted schema and ADR 0011 first. Treat the schema as accepted design, not implemented fact; resolve any genuinely new material decision before changing identity-bearing code.
- Preserve Wflow-owned setting YAML/TOML names and upstream HydroMT/Wflow behavior. Keep WF3 model-independent and WF2 a plausibility overlay.
- Do not add resume semantics or regenerate the baseline as incidental cleanup. Use fresh project outputs for the new schema. Treat baseline regeneration as an explicit planned task if existing baseline readers cannot consume the new schema.
- Maintain scientific ordering and numerical behavior under a matched explicit seed. The owner requires strict WF3 independence, which supersedes the v1 automatic-seed input projection: remove WF4 elevation and preparation code from a new versioned seed material while retaining the canonical digest-to-integer method. The owner accepts numeric `seed: auto` changes when material or inventoried generator code changes; test them with a separate fixture because the rapid fixture uses an explicit seed. Distinguish intentional seed/identity changes from algorithmic scientific changes. Update live references and documentation with each contract change.
- Work in the allocated session branch. Commit each verified phase or smaller coherent contract change separately; do not land or push without the repository's approval gate.

### Human gates

1. **Satisfied 2026-09-21:** The owner accepted the reviewed P0 contract after the clean WF3 automatic and explicit-123 references completed. Runtime implementation may proceed under the remaining phase gates.
2. Pause only if remeasurement reveals a further material contract choice or required verification cannot be run. Do not turn routine complexity into an approval gate.

### P0 contract-finalization deliverable

Revise the existing schema in place, with a reviewable decision table and versioned interface sketches, before P1. Define the WF3-only `generation-seed-material/2` inputs and code inventory, preserving the digest-to-integer method and proving that WF4-only changes affect neither seed nor collection ID. The current `generation_plan.py` contains WF4 preparation logic; specify the module-boundary change needed to keep WF4 code out of generator identity. Then settle exact schema versions and canonical digest projections; one coherent archive generation and crash recovery; source-path/absolute-reference rerun policy; launcher versus raw-Snakemake coverage and parent launch failures; immutable plan pinning, receipt, pointer and shared-workspace policy; WF3/WF4 elevation reference resolution; and the clean-break policy for pre-migration outputs. Re-measure baseline/test dependencies and specify an explicit regeneration or replacement gate rather than preserving old readers. Record which P1–P6 phase implements each decision and the first phase that emits each new version.

The clean pre-change WF3 reference and comparison method were captured before any provider-code or seed-projection edit: [reference report](../design-runs/output-schema-contract/prechange-reference-retry.md). It includes automatic seed and explicit seed 123, source/record/series hashes and comparison scope. The accumulated `test_local` and `test_rapid` trees do not establish this reference. Before P1 runtime edits, pin the executable predecessor WF4 environment and inputs; before P4, complete the independent predecessor WF1/WF4/metrics comparator required by schema §10.9. Review and owner acceptance of P0 are recorded; neither substitutes for those later numerical gates.

### Cross-cutting validation

Use the repository validation ladder in `AGENTS.md` and schema §11. Run focused tests per phase; run `tests/test_cli.py` when rule signatures or declared inputs change, and `pixi run lint` plus `pixi run format-check` for Python edits. At approved batch landing, run `pixi run test-fast` once; run `pixi run test-full` before merging a batch that touched `shared/` or a `script:` signature. Run baseline checks only when numeric outputs or a milestone seal warrant them, after the planned baseline schema transition, with the baseline config and WF1 `--notemp`. P7 must compare a fresh isolated rapid tree with the accepted tree and test the falsifiers in schema §11, plus both P0 seed cases. Record both passes and failures fixed; do not claim an end-to-end run from accumulated local outputs.

### Phase brief index

- P0 — Contract finalization (this master brief; design only) — accepted 2026-09-21
- [P1 — Archive foundation](p1-archive-foundation.md) — complete (`31d7aa15`)
- [P2 — Workflow archives](p2-workflow-archives.md) — complete (`3eae8654`)
- [P3 — Invocation history](p3-invocation-history.md) — complete (`02e568e2`)
- [P4 — Collection contract](p4-collection-contract.md) — complete (`ceeb9835`)
- [P5 — WF3 static generation](p5-wf3-static-generation.md) — complete (`c83ead70`)
- [P6 — Simulation and metrics](p6-simulation-metrics.md) — complete
- [P7 — Complete-run evidence](p7-complete-run-evidence.md) — complete; [acceptance record](../../milestones/r12/implementation/evidence/p7/complete-run-record.md)
