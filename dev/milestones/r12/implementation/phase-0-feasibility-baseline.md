# Task Brief — P0 feasibility and pre-change baseline preparation

### Context

- Follow repository `AGENTS.md`, the [accepted design](../wf3-simulation-identity-design.md) §§5.2, 6.8, 8.4a, 9.6, 12, and [readiness](readiness.md).
- Environment readiness and synthetic P2b passed. The operation/target probe
  reached Master Gate 3; the owner approved the mandatory simulation runner.
- P2b must pass before landing 1. Operation/target and checkpoint feasibility must pass before landing 3.
- The standing baseline predates the current nine-year config and cannot be GF-9's reference.

### Goal

Prove the accepted Snakemake mechanisms with synthetic fixtures, then have the model builder capture the fresh pre-change numerical snapshot in isolated evidence roots before P1 changes numerical call sites.

### Non-goals

No production adapter, successor manifest, entry-point/config migration, estimator benchmark, GF-9 post-change comparison, or standing-baseline record. The authorized pre-change capture is the sole production numerical execution in this phase.

### Allowed scope

**Permitted:** [proposed paths] `dev/milestones/r12/implementation/feasibility/` and `tests/test_r12_wf3_feasibility.py`; this phase brief's progress section; read-only inspection of current `run_stress_test.smk`, `scripts/run_workflows.py`, `test_case/project_config_baseline*.yml`, and baseline tooling.

**Approval-gated:** P0 execution, including the fresh pre-change capture, is released once by Master Gate 1. Master Gate 2 does not apply unless this phase proposes a new tolerance.

**Forbidden/generated:** production runtime edits; `dev/baseline/manifest.json`; `test_case/test_local`; review archives; lockfiles; generated catalogs.

### Required changes (checklist)

- [x] Re-run the readiness source/environment checks against the execution checkout and record any changed premise.
- [x] Implement P2b as a standalone synthetic Snakefile: producer subtree resolvable, subtree missing, and no derived rows. Exercise row-derived wildcard alternation plus ancestor input together; do not use `ruleorder` or private APIs.
- [x] Probe the §6.8 operation/target matrix for `all`, `metrics`, exact metric filename, and Wflow filename in both modes. Show defined producer classes in dry-run and real fixture execution.
- [x] Probe source-planning and metric-planning checkpoint/input-function composition in one invocation, including honest unresolved fresh dry-runs. These are feasibility results, not GF-29/GF-30 end-to-end passes.
- [x] Choose explicit `<PRECHANGE_CONFIG>`, `<PRECHANGE_ROOT>`, `<POSTCHANGE_CONFIG>`, `<POSTCHANGE_ROOT>`, and sidecar manifest paths. Both configs must compose to identical scientific settings and keep the `project_config_` prefix; output roots must be separate from the standing baseline and from each other.
- [x] Define the pre-change provenance record: config/source/model/code/environment digests, resolved seed, command, expected targets, and `--notemp` WF1 requirement. Do not execute until released.
- [x] After Master Gate 1, the model builder runs the current WF1 and WF3 pre-change workflows into `<PRECHANGE_ROOT>` (`--notemp` on WF1), retains the raw outputs and every scope-dependent model check, records separate manifest/reference sidecars and complete command logs in the isolated run home, linked from `dev/milestones/r12/implementation/evidence/p0/`, and hands outputs to model validation for completeness/provenance review. Preserve the root read-only for the later GF-9 crosswalk. WF2 is intentionally excluded because projections are a terminal overlay and do not drive this migration comparison.
- [ ] Mark the snapshot accepted as comparison evidence before any P1 edit changes provider/simulator/reducer call sites or numerical outputs. Missing, stale, partially written, or scientifically non-current evidence blocks those edits.

### Commit plan

| Subject | Paths | Invariant preserved |
|---|---|---|
| `test: prove R12 Snakemake feasibility` | proposed feasibility fixture/test paths | P2b and supported-API conclusions are independently reviewable before production edits |
| `evidence: freeze R12 pre-change comparison` | proposed P0 runbook plus `dev/milestones/r12/implementation/evidence/p0/`; generated run root stays untracked | old-side numerics and provenance exist before numerical rewiring and cannot overwrite the standing baseline |

### Validation

- Per fixture edit: `pixi run pytest tests/test_r12_wf3_feasibility.py` (29 cases cover P2b, the counterexample, mandatory runner and checkpoint lifecycles).
- Once after fixture completion: direct Snakemake dry-run and real synthetic invocation commands recorded by the fixture; require the same allowed producer classes.
- Once before P1: P2b three-state evidence must pass. Any ambiguity, zero-job success, missing clean refusal, private API need, or second required invocation blocks P1.
- Once before P3: operation/target and both checkpoint feasibility cases pass. The owner discharged Master Gate 3 by selecting the mandatory runner and two explicit rule modules inside `simulate_system.smk`; prove that replacement. A further material one-invocation failure returns to the gate.
- After execution release, the model builder records the pre-change side with `pixi run python dev/scripts/check_baseline.py record --project-dir <PRECHANGE_ROOT> --manifest <PRECHANGE_MANIFEST> --workflow build_model --workflow run_stress_test`; capture the command output in the P0 evidence directory. The explicit scope covers the model and stress-test outputs needed by the migration and excludes WF2's terminal overlay. This recorder supplements the preserved raw outputs and all scope-dependent model checks; it does not implement GF-9.

### Acceptance criteria

P2b passes before P1; supported public Snakemake surfaces can enforce operation/target and both checkpoint contracts; the model builder has captured and model validation has accepted the isolated current-config pre-change evidence before numerical rewiring; failures name the blocking observation rather than weakening the accepted design.

### Output requirements

Return committed feasibility fixtures/evidence, exact commands and versions, the selected pre/post paths, and a pass/fail decision for each accepted mechanism. Record red-then-fixed behavior, not only terminal passes.

### Execution progress — 2026-09-10

Master Gate 1 is released by the owner's instruction to continue with the next
logical step. P2b is the first bounded implementation increment. At source
`123e91b1`, the runtime/config/test comparison against the accepted design
baseline is empty and `main` is already ancestral. The environment check passed
again; installed Python, Snakemake, pytest, HydroMT, hydromt-wflow and weathergenr
versions match the readiness inventory. No production numerical run has started.

P2b passes in all three states, in dry-run and real execution. The
[evidence record](evidence/p0/p2b-feasibility.md) documents exact producer counts,
ancestor-content checks and the missing-subtree refusal. Remaining P0 work is
the operation/target matrix, checkpoint composition and isolated pre-change
snapshot; P2b alone does not complete GF-1 or release numerical rewiring.

The operation/target probe reached **Master Gate 3**. Simulation-mode direct
Wflow targets succeed without metrics (including zero-job success for a retained
output); conditional producer definitions cannot provide the accepted target
exclusivity. Metrics-only producer omission correctly refuses a Wflow target.
See the [gate evidence and fallback proposal](evidence/p0/operation-target-feasibility.md).
Those diagnostic cases rejected the conditional-rule candidate. The owner then approved the mandatory
simulation runner, discharging this gate. Replacement runner/checkpoint probes
and fresh numerical capture resumed under the existing P0 execution release.

Replacement feasibility passed: 29 cases, followed by the two affected lifecycle
cases after the final missing-plan correction; CLI 20 passed, lint and formatting
passed. See [runner/checkpoint evidence](evidence/p0/runner-checkpoint-feasibility.md).
Fresh WF1 (20 jobs) and WF3 (41 jobs) completed; the isolated four-target manifest
record/check passed. [Snapshot evidence and handoff](evidence/p0/prechange-snapshot.md)
records 242 artifact hashes and coverage. **Stopped at P0 comparison-evidence
acceptance: named model-validator review remains required before P1.**

### Task constraints

No scientific claims. Use Astra for any later methodological/tolerance judgment. Do not infer current-tree freshness from retained `test_case/test_local` artifacts.
