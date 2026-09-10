# Master Brief — Implement the accepted R12 WF3 successor

### Goal

Implement the accepted [R12 v6 design](../wf3-simulation-identity-design.md) without changing its method, interfaces, or three-landings sequence. This program starts only after execution scope is released; this preparation creates no production implementation or scientific result.

### Subsystem map

| Phase | Primary owner | Input | Expected output |
|---|---|---|---|
| P0 | Python engineer; CST architect integrates | [readiness](readiness.md), accepted §§5.2, 6.8, 8.4a, 9.6, 12 | Synthetic feasibility evidence plus a concrete, isolated pre-change snapshot runbook |
| P1 | Python engineer; R developer and model builder own production bindings | P0 P2b pass | Landing 1: logical provider, simulator, response, and metric contracts behind current `run_stress_test.smk` |
| P2 | Python engineer; model builder/R developer bind; geospatial analyst and model validator validate | P1 | Landing 2: durable collection, simulation/response, metric-set handoffs and metrics-only operation behind current WF3 |
| P3 | Python engineer; CST architect integrates; model validator accepts scientific comparisons | P2 feasibility and handoff gates | Landing 3: two entry points, five-stanza config, runner/reference migration, and old WF3 retirement atomically |

**Capability-slot contract.** Repository bindings are pinned to implementation baseline `dffa4625c9c1f01bd8a77e0d91ae1a0a8f3538e8`; [readiness](readiness.md) records that its runtime/config/test surfaces match design baseline `4e26c239…`. Re-measure before dispatch.

| Slot | Binding and immutable revision | Delegated owner | Validation authority |
|---|---|---|---|
| `decision_framing` | accepted v6 design at `dffa4625…`, including owner rulings R-1..R-6 | CST architect | owner for framing; model validator for consequences |
| `data_adapter` | HydroMT/hydromt_wflow surfaces at `dffa4625…` | model builder; geospatial analyst for metadata | model validator plus interchange validators |
| `ensemble_generator` | weathergenr 2.0.0 binding and current WF3 at `dffa4625…` | R developer and model builder | model validator |
| `simulation_engine` | Wflow binding/current Julia batch driver at `dffa4625…` | model builder | model validator |
| `system_model_validation` | model-reference/model-digest contract at `dffa4625…` | model validator | model validator |
| `impact_model` | `not_applicable`: outputs stop at hydrological responses and metrics | — | — |
| `performance_analysis` | current metric vocabulary at `dffa4625…` plus accepted R-1..R-4 | Python engineer | model validator; GF-9 crosswalk evidence |
| `robustness_evaluation` | `not_applicable`: no option×scenario robustness matrix is declared | — | — |
| `projection_overlay` | `not_applicable` to these execution DAGs: WF2 remains a terminal plausibility overlay at `dffa4625…` | — | model validator if separately interpreted; never run selection |
| `orchestrator` | Snakemake 9.6.2 and runner at `dffa4625…` | CST architect; Python engineer implements | CLI/DAG/fresh-project gates |

### Sequencing

`P0 P2b pass + fresh pre-change snapshot → P1 → P2 → P3`. P2b blocks P1 because §5.2 requires the wildcard/ancestor composition to work before adapter extraction. The model-builder snapshot blocks P1's first numerical call-site edit so the old side cannot be reconstructed after behavior has moved. P2 blocks P3 until the operation/target matrix, current-carrier equivalents of both one-invocation checkpoints (GF-29/GF-30), default/advanced resolution (GF-32), and portable preparation closure (GF-31) have executable evidence. P3 reruns GF-29/GF-30 through the final entry points and runner. P3 alone changes entry-point/config names and retires the old contract.

The accepted migration deliberately uses `run_stress_test.smk` as a serial carrier: P1 changes logical call sites, P2 adds durable handoffs, and P3 deletes it. One Python engineer has custody across all three; the phases never run concurrently. Every other proposed path has one phase owner.

### Shared constraints

- Treat proposed paths as proposed until the executor confirms repository naming rules; preserve every exact existing path listed in the phase scopes.
- Production remains weathergenr/Wflow; synthetic and dummy bindings are test-only. CMIP remains terminal and cannot select or drive a run.
- Preserve seed, calendars/endpoints, spell factors, perturbation semantics, HydroMT/Wflow conventions, and current output vocabulary except the accepted R-2/Class-C and identity migrations.
- Internal digests are mandatory; routine users provide scientific settings and `experiment_name`, not fingerprints or selectors.
- No ready artifact is integrated before its named model-validator handoff returns. Future scientific or methodological evaluation uses Astra.
- Section 13's unavailable stress-test-analyst handoff is split explicitly: Python engineering owns metric declarations, grouping/reference code, and the GF-9 comparator; model validation owns scientific acceptance.
- Do not edit review archives, sealed records, generated catalogs, lockfiles, upstream packages, or the standing baseline as a shortcut.

### Human gates

1. **Execution release:** if P0 execution is not yet authorized, pause once for its scope. After authorization, select and document safe isolated roots within that scope without asking again; ask only when a root needs an authority exception. Accepted design approval is already settled.
2. **New criteria only:** before GF-15's proposed benchmark or any proposed change to an accepted tolerance, obtain Astra model-validator review and owner acceptance. GF-9, GF-28, and GF-31 already carry accepted criteria; execute them without another criteria-approval pause, with Astra model validation judging the results.
3. **Material deviation only:** pause if supported Snakemake APIs cannot satisfy the accepted one-invocation contract, a scientific value changes outside accepted tolerances, or implementation would alter a selected interface/method. Ordinary implementation choices do not reopen design approval.

### Cross-cutting validation

- Per edit: owning narrow tests; per Python change: `pixi run lint` and `pixi run format-check`; after every Snakefile/config-shape edit: `pixi run pytest tests/test_cli.py`.
- Once per landing: all phase-specific behavioral gates in [validation-map](validation-map.md). Capture durable evidence under `dev/milestones/r12/implementation/evidence/<phase>/`.
- Once before merge because `shared/`, rule signatures, runner/config, and numeric outputs change: `pixi run test-full *> dev/milestones/r12/implementation/evidence/final/test-full.log`. This non-integration suite does not replace model acceptance.
- Before milestone seal: GF-9/GF-27/GF-28/GF-29/GF-30/GF-31/GF-32 executions plus GF-15 after its criteria gate; `pixi run python dev/scripts/snapshot_project_tree.py --config <POSTCHANGE_CONFIG> --project-dir <POSTCHANGE_ROOT>` after the tool migration; and the documented standing baseline/tree comparison after identity acceptance.
- Preserve a fresh pre-change and post-change run under the same current composed config in separate roots. Never overwrite `dev/baseline/manifest.json` before GF-9 acceptance.

### Phase brief index

- [P0 — feasibility and baseline preparation](phase-0-feasibility-baseline.md) — not started
- [P1 — logical contract extraction](phase-1-contract-extraction.md) — not started
- [P2 — durable handoffs](phase-2-durable-handoffs.md) — not started
- [P3 — workflow extraction and migration](phase-3-workflow-extraction.md) — not started
- [GF-1..GF-32 validation map](validation-map.md)
