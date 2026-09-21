# Master Brief — Complete-run output schema migration

### Goal

Implement the proposed output tree and record schemas in [complete-run-output-schema.md](../complete-run-output-schema.md), §§2–8, without changing scientific computations. This is a handoff, not approval of every working recommendation in that document.

### Subsystem map

| Phase | Owner | Input | Expected output |
|---|---|---|---|
| P0 | Design owner and reviewer | Schema §§2–10; ADR 0011; WF3 intake | Accepted contracts, clean output boundary, seed policy and comparison reference |
| P1 | Next-session executor | P0; schema §§4–5 | Exact source archive and common record/reference writer |
| P2 | Next-session executor | P1 | WF0–WF2 and artifact-local archives |
| P3 | Next-session executor | P1 | Unified parent/child invocation history |
| P4 | Next-session executor | P1; schema §§3, 7–8 | Versioned collection contract and shared elevation ownership |
| P5 | Next-session executor | P3–P4 | Static WF3 plan and provider output paths |
| P6 | Next-session executor | P4–P5 | WF4 simulation and metric-set records/results |
| P7 | Next-session executor | P1–P6 | Isolated complete-run evidence |

### Sequencing

P0 settles the contract decisions listed below and obtains a review of the selected design before runtime implementation. P1 establishes archive/reference interfaces before P2–P4 adopt them. P2 and P3 may proceed independently after P1 if they do not edit the same entry points; otherwise sequence their shared files. P4 is an additive contract and reader foundation: it must not switch the default WF3 producer while its Snakefile and WF4 consumers still require the old layout. P5 makes the coordinated WF3 producer/consumer switch, including the paths and archive adoption; WF4 must explicitly refuse the new collection until P6 adopts it, rather than misread it. P6 then adopts the new collection in WF4 and its own archive and metric contracts. Each phase exit must state which schema versions it emits and reads and pass focused checks before its commit. P7 runs only after P1–P6 pass their focused checks. Some modules are deliberately touched in successive phases; ownership is time-sliced, never concurrent. Re-measure file ownership and consumer paths before scheduling work; the 2026-09-21 candidate map in schema §11 is not a verified exhaustive inventory.

### Shared constraints

- Read `AGENTS.md`, the proposed schema and ADR 0011 first. Treat the schema's working recommendations as proposed contracts, not implemented facts; resolve genuine open decisions before changing identity-bearing code.
- Preserve Wflow-owned setting YAML/TOML names and upstream HydroMT/Wflow behavior. Keep WF3 model-independent and WF2 a plausibility overlay.
- Do not add resume semantics or regenerate the baseline as incidental cleanup. Use fresh project outputs for the new schema. Treat baseline regeneration as an explicit planned task if existing baseline readers cannot consume the new schema.
- Maintain scientific ordering and numerical behavior under a matched explicit seed. Preserve the current `seed: auto` calculation, as the owner selected; identical seed material must yield the same value. Test it with a separate automatic-seed fixture because the rapid fixture uses an explicit seed. P0 must resolve whether numeric parity is required across P5's inventoried provider-code edits and whether the seed's indirect elevation contribution is acceptable before claiming strict WF3 model independence. Distinguish intentional identity/path differences from scientific changes. Update live references and documentation with each contract change.
- Work in the allocated session branch. Commit each verified phase or smaller coherent contract change separately; do not land or push without the repository's approval gate.

### Human gates

1. Before runtime implementation, finish P0 and ask the owner to accept the selected contracts in schema §§2–8, including the clean break from pre-migration output schemas and the reconciled seed/collection-identity boundary. Agreement with the current working tree alone authorizes design finalization, not runtime implementation.
2. Pause only if remeasurement reveals a further material contract choice or required verification cannot be run. Do not turn routine complexity into an approval gate.

### P0 contract-finalization deliverable

Revise the existing schema in place, with a reviewable decision table and versioned interface sketches, before P1. Preserve the selected `generation-seed-material/1` calculation and resolve its indirect elevation contribution to collection identity; then settle exact schema versions and canonical digest projections; one coherent archive generation and crash recovery; source-path/absolute-reference rerun policy; launcher versus raw-Snakemake coverage and parent launch failures; immutable plan pinning, receipt, pointer and shared-workspace policy; WF3/WF4 elevation reference resolution; and the clean-break policy for pre-migration outputs. Re-measure baseline/test dependencies and specify an explicit regeneration or replacement gate rather than preserving old readers. Record which P1–P6 phase implements each decision and the first phase that emits each new version.

Capture a clean pre-change scientific reference and comparison method before any provider-code or seed-projection edit. Include an automatic-seed case and a matched explicit-seed case; record tolerances and the reference owner. The accumulated `test_local` and `test_rapid` trees do not establish this reference. Review the revised contract before the owner acceptance gate.

### Cross-cutting validation

Use the repository validation ladder in `AGENTS.md` and schema §11. Run focused tests per phase; run `tests/test_cli.py` when rule signatures or declared inputs change, and `pixi run lint` plus `pixi run format-check` for Python edits. At approved batch landing, run `pixi run test-fast` once; run `pixi run test-full` before merging a batch that touched `shared/` or a `script:` signature. Run baseline checks only when numeric outputs or a milestone seal warrant them, after the planned baseline schema transition, with the baseline config and WF1 `--notemp`. P7 must compare a fresh isolated rapid tree with the accepted tree and test the falsifiers in schema §11, plus both P0 seed cases. Record both passes and failures fixed; do not claim an end-to-end run from accumulated local outputs.

### Phase brief index

- P0 — Contract finalization (this master brief; design only) — in progress
- [P1 — Archive foundation](p1-archive-foundation.md) — not started
- [P2 — Workflow archives](p2-workflow-archives.md) — not started
- [P3 — Invocation history](p3-invocation-history.md) — not started
- [P4 — Collection contract](p4-collection-contract.md) — not started
- [P5 — WF3 static generation](p5-wf3-static-generation.md) — not started
- [P6 — Simulation and metrics](p6-simulation-metrics.md) — not started
- [P7 — Complete-run evidence](p7-complete-run-evidence.md) — not started
