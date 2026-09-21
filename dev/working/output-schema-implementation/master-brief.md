# Master Brief — Complete-run output schema migration

### Goal

Implement the proposed output tree and record schemas in [complete-run-output-schema.md](../complete-run-output-schema.md), §§2–8, without changing scientific computations. This is a handoff, not approval of every working recommendation in that document.

### Subsystem map

| Phase | Owner | Input | Expected output |
|---|---|---|---|
| P1 | Next-session executor | Schema §§4–5 | Exact source archive and common record/reference writer |
| P2 | Next-session executor | P1 | WF0–WF2 and artifact-local archives |
| P3 | Next-session executor | P1 | Unified parent/child invocation history |
| P4 | Next-session executor | P1; schema §§3, 7–8 | Versioned collection contract and shared elevation ownership |
| P5 | Next-session executor | P3–P4 | Static WF3 plan and provider output paths |
| P6 | Next-session executor | P4–P5 | WF4 simulation and metric-set records/results |
| P7 | Next-session executor | P1–P6 | Isolated complete-run evidence |

### Sequencing

P1 establishes archive/reference interfaces before P2–P4 adopt them. P2 and P3 may proceed independently after P1 if they do not edit the same entry points; otherwise sequence their shared files. P4 must settle collection identity and elevation ownership before P5 freezes generation plans or P6 binds simulations. P5 precedes P6 because WF4 consumes the published collection schema. P7 runs only after the selected implementation phases pass their focused checks. Some modules are deliberately touched in successive phases (for example collection contract in P4, then its WF3 scheduling in P5); ownership is time-sliced, never concurrent. Re-measure file ownership and consumer paths before scheduling work; the 2026-09-21 candidate map in schema §11 is not a verified exhaustive inventory.

### Shared constraints

- Read `AGENTS.md`, the proposed schema and ADR 0011 first. Treat the schema's working recommendations as proposed contracts, not implemented facts; resolve genuine open decisions before changing identity-bearing code.
- Preserve Wflow-owned setting YAML/TOML names and upstream HydroMT/Wflow behavior. Keep WF3 model-independent and WF2 a plausibility overlay.
- Do not rewrite sealed output bytes, prune existing output trees, add resume semantics, regenerate the baseline as incidental cleanup, or introduce old metric-CSV compatibility under D21. Other legacy readers remain required as specified in schema §11.
- Maintain scientific ordering, seeds and numerical behavior; distinguish intentional path/schema differences from numerical changes. Update live references and documentation with each contract change.
- Work in the allocated session branch. Commit each verified phase or smaller coherent contract change separately; do not land or push without the repository's approval gate.

### Human gates

1. Before runtime implementation, ask the owner to confirm that the working recommendations in schema §§2–8 are accepted as the migration target, including the D21 metric-CSV compatibility exception. The request to prepare this brief does not itself approve implementation.
2. Pause only if remeasurement reveals a material contract choice not settled in the schema, or if required verification cannot be run. Do not turn routine complexity into an approval gate.

### Cross-cutting validation

Use the repository validation ladder in `AGENTS.md` and schema §11. Run focused tests per phase; run `tests/test_cli.py` when rule signatures or declared inputs change, and `pixi run lint` plus `pixi run format-check` for Python edits. At approved batch landing, run `pixi run test-fast` once; run `pixi run test-full` before merging a batch that touched `shared/` or a `script:` signature. Run baseline checks only when numeric outputs or a milestone seal warrant them, with the baseline config and WF1 `--notemp`. P7 must compare a fresh isolated rapid tree with the proposed tree and test the falsifiers in schema §11. Record both passes and failures fixed; do not claim an end-to-end run from accumulated local outputs.

### Phase brief index

- [P1 — Archive foundation](p1-archive-foundation.md) — not started
- [P2 — Workflow archives](p2-workflow-archives.md) — not started
- [P3 — Invocation history](p3-invocation-history.md) — not started
- [P4 — Collection contract](p4-collection-contract.md) — not started
- [P5 — WF3 static generation](p5-wf3-static-generation.md) — not started
- [P6 — Simulation and metrics](p6-simulation-metrics.md) — not started
- [P7 — Complete-run evidence](p7-complete-run-evidence.md) — not started
