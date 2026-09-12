# Master Brief — Implement the accepted R12 WF3 successor

### Goal

Implement the accepted [R12 v6 design](../wf3-simulation-identity-design.md) without changing its method, interfaces, or three-landings sequence. P0 execution was released on 2026-09-10 by the owner's instruction to continue with the next logical step; P2b is the first bounded increment. Preparation itself created no production implementation or scientific result.

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

**Gate 3 ruling — 2026-09-10:** owner approved the mandatory simulation runner
after the measured target bypass. It validates targets before one Snakemake
invocation and selects two fixed rule modules; bare simulation Snakefile commands
are no longer the supported target-contract interface. Direct generation remains
supported. This gate is discharged; prove the replacement and continue P0.

### Cross-cutting validation

**Gate 2 ruling — 2026-09-12:** owner approved execution of the exact
[reviewed GF15 criteria](evidence/p3/scientific-review-preparation.md#gf15-recommendation-for-the-owner-gate)
after the P3 completion handoff. The benchmark proceeds with the unchanged
estimator and criteria. A failed criterion returns to the owner for a method
ruling; the approval does not validate the screening policy or real-bundle
applicability.

**GF15 result — 2026-09-12:** all approved cells completed; the retained-draw
audit passed, but accuracy and translation criteria failed. The
[scientific handoff](evidence/gf15/scientific-handoff.md) records the bounded
failure and unchanged policy/estimator. Section 7.5 now requires the owner method
ruling; R12 remains unsealed. [Standing baseline/tree status](evidence/standing-seal-status.md)
records the separate successor-fixture prerequisite.

**Investigation ruling — 2026-09-12:** owner approved the recommended bounded
investigation of fitting stability and sample-size accuracy, keeping production
behavior unchanged. The original GF15 failure record remains immutable. This
authorizes diagnostic tracing and analysis of retained witnesses; replacement
estimator execution, changed criteria and adequacy/seal acceptance remain
separate method decisions after the investigation.

**Investigation result — 2026-09-12:** the
[bounded diagnosis](evidence/gf15-investigation/scientific-handoff.md) inspected
all 132,000 retained fits and reproduced 186 optimizer traces exactly. The six
extreme witness fits exhausted their evaluation budget; the fixed-grid 180
reported convergence. Accuracy failures persist after descriptive outlier
exclusion. Original evidence and production behavior remain unchanged. A
reviewed candidate-method decision is now needed; no new qualification or
milestone-seal claim follows from diagnostic completion.

**Candidate-study ruling — 2026-09-12:** owner approved the status-only wrapper
and mean/population-standard-deviation normalized candidate on the same 186
diagnostic cases. Existing GEV likelihood, optimizer defaults and GF15 criteria
remain fixed. New evidence belongs under `evidence/gf15-candidates/`; original
records remain immutable. This is not approval for a full qualification matrix,
production integration, fallback estimator, or changed screening policy.

**Candidate-study result — 2026-09-12:** the
[bounded comparison](evidence/gf15-candidates/scientific-handoff.md) completed
372 fits and 450 quantiles. The status-only candidate preserved original raw
results; the normalized candidate passed all 144 both-accepted translation pairs.
Both refused the six extreme fits. The three both-refused pairs per candidate
are not numerical proof. B merits a full qualification attempt under unchanged
criteria, subject to a separate owner execution-scope decision. No
accuracy-adequacy, production-integration or seal approval follows from this subset.
The subsequent authorization and full-study outcome are recorded below.

**Full normalized-qualification ruling — 2026-09-12:** owner approved B-only
execution of the original 132,000-fit, 144,000-quantile matrix using retained
samples and unchanged criteria. Normalization and explicit optimizer-status
refusal are fixed to the candidate study committed as `743a4d24`. New evidence
belongs under `evidence/gf15-normalized-qualification/`. Refusals retain full
draw denominators; both-refused pairs are not numerical-equivalence successes.
This authorizes execution and assessment, not production integration, retuning,
fallback, changed screening policy, or milestone sealing.

**Full normalized-qualification result — 2026-09-12:** all 132,000 fits and
144,000 quantiles completed; the independent audit passed. Scientific
qualification failed: 3/24 baseline accuracy cells and 6/72 eligible relative
cells pass; all six current `n=18` baseline cells fail. All cells meet the 95%
valid-fit threshold, with 78 refused fits in total. Of 120,000 translation pairs,
119,899 pass numerically, 30 fail, 70 are both refused without numerical proof,
and one changes validity; 106/120 translation cells pass. The maximum accepted
paired difference is `4.5263e-6` against the unchanged `1e-6` limit. All 186
embedded candidate cases replay exactly. See the
[signed handoff](evidence/gf15-normalized-qualification/scientific-handoff.md).
Section 7.5 still requires an owner method ruling; neither normalization nor
successful evidence verification establishes GF15 adequacy or permits sealing.

**Alternative-estimator design accepted — 2026-09-12:** owner approved the
[range-normalized L-moment/PWM GEV design](../gf15-alternative-estimator-design.md)
and all recorded resolutions after two external rounds, owner arbitration and an
approved scoped v4 review. The [complete review archive](../gf15-alternative-estimator-review/status.md)
preserves prior versions and verdicts. The next bounded assignment is
[Stage 1 implementation readiness](gf15-lmoments-readiness-brief.md); its execution
is not released by design acceptance. Original GF15 criteria and both failed
qualification records remain authoritative. A readiness pass would not establish
GF15 adequacy, production applicability or milestone-seal acceptance.

- Per edit: owning narrow tests; per Python change: `pixi run lint` and `pixi run format-check`; after every Snakefile/config-shape edit: `pixi run pytest tests/test_cli.py`.
- Once per landing: all phase-specific behavioral gates in [validation-map](validation-map.md). Capture durable evidence under `dev/milestones/r12/implementation/evidence/<phase>/`.
- Once before merge because `shared/`, rule signatures, runner/config, and numeric outputs change: `pixi run test-full *> dev/milestones/r12/implementation/evidence/final/test-full.log`. This non-integration suite does not replace model acceptance.
- Before milestone seal: GF-9/GF-27/GF-28/GF-29/GF-30/GF-31/GF-32 executions plus GF-15 after its criteria gate; `pixi run python dev/scripts/snapshot_project_tree.py --config <POSTCHANGE_CONFIG> --project-dir <POSTCHANGE_ROOT>` after the tool migration; and the documented standing baseline/tree comparison after identity acceptance.
- Preserve a fresh pre-change and post-change run under the same current composed config in separate roots. Never overwrite `dev/baseline/manifest.json` before GF-9 acceptance.

### Phase brief index

- [P0 — feasibility and baseline preparation](phase-0-feasibility-baseline.md) — complete; named model-validator accepted comparison evidence
- [P1 — logical contract extraction](phase-1-contract-extraction.md) — acceptance gate passed: adapters integrated, three bounded scientific handoffs accepted, combined software gate passed
- [P2 — durable handoffs](phase-2-durable-handoffs.md) — complete: current-carrier checkpoint/resolution/metrics-only gates, bounded scientific handoffs and final software checks accepted; see [acceptance](evidence/p2/acceptance.md)
- [P3 — workflow extraction and migration](phase-3-workflow-extraction.md) — accepted: successor interfaces, scientific/orchestration handoffs and final full software gate pass; GF15 adequacy and milestone seal remain separately owner-gated
- [GF-1..GF-32 validation map](validation-map.md)
