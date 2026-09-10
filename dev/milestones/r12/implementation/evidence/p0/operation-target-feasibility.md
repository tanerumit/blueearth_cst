# P0 operation/target feasibility — Master Gate 3

Lifecycle: maintained-current until the owner ruling and P0 handoff.
Execution date: 2026-09-10. Starting checkout: `38db2f51`.
Scope: accepted design §§4.1 and 6.8, with the direct-invocation promise in §9.5.
Production code, scientific settings and the standing baseline are unchanged.

## Gate finding

Conditional producer definitions do not enforce the accepted top-level target
contract. In `simulate-and-metrics`, an explicit Wflow output target succeeds
and executes only the simulation rule, omitting metrics. The design permits
only `all` in that mode and requires other target choices to refuse before DAG
execution. This is a concrete counterexample, not a speculative API concern.

Metrics-only producer isolation works: the fixture does not define a simulation
producer, and a Wflow output request raises `MissingRuleException`, even when
that file exists. The initial hypothesis that this metrics-only request could
succeed with zero jobs was disproved by the first test run. The evidence does
not claim a metrics-only simulation bypass.

The retained candidate is [operation-target.smk](../../feasibility/operation-target.smk).
Its successful bypass is deliberately asserted by the regression test to retain
the reason this candidate was rejected. A passing counterexample test means
the contract defect was reproduced; it does not mean the design gate passed.

| Operation / explicit target | Dry-run and real result |
|---|---|
| `simulate-and-metrics` / `all` | 3 jobs: aggregate target, simulation, metric reduction |
| `metrics-only` / `metrics` | 2 jobs: aggregate target and reduction; no simulation |
| `simulate-and-metrics` / fresh Wflow filename | **Forbidden success:** 1 simulation job, no metrics |
| `simulate-and-metrics` / existing Wflow filename | **Forbidden success:** exit 0, nothing to do, no metrics |
| `metrics-only` / existing Wflow filename | Refuses with `MissingRuleException` after parsing |

[Complete command/output transcript](operation-target-transcript.txt): ten
invocations across five cases. Machine identifiers are replaced with
`<WORKTREE>`, `<HOST>` and `<HOST_TEMP>`; trailing whitespace is stripped.
Raw logs remain in session scratch under `operation-target-fixed/`.

## Public interface evidence

The [documented target directive](https://snakemake.readthedocs.io/en/v9.6.2/snakefiles/rules.html#target-rules)
chooses the default target, not an exclusive list of permitted targets. The
[external public API](https://snakemake-api.readthedocs.io/en/stable/api_reference/snakemake_api.html)
supplies target-bearing DAG settings outside the Snakefile. That API site's
version is 8.30.0; the version-specific timing evidence below is from the
installed Snakemake 9.6.2 source, inspected read-only.

In `snakemake/api.py`, `WorkflowApi.dag` constructs `DAGApi` at lines 328–345.
The `_workflow` property includes and checks the Snakefile at lines 389–397;
`DAGApi.__post_init__` accesses that property before assigning `dag_settings` at
lines 445–446. File SHA-256:
`AAA8CBAA099B68A8D965FDF84EEF73E46C5406FAEC6D3EF6F581A0C83D9C22C0`.
The fixture does not call these internals. Inference: no supported parse-time
requested-target inspection mechanism was established, and the conditional DSL
counterexample fails the accepted exclusivity guarantee. This is not a claim
that every possible upstream extension has been ruled out.

## Decision required

The design already names the fallback: a thin shipped runner selecting one of
two explicit rule modules within the same simulation workflow. Adopting it
requires reconciling §9.5, which currently promises a bare Snakemake simulation
command and says that the runner is never the only safety boundary.

Recommended ruling: make the shipped simulation runner the supported invocation
boundary for operation/target validation. It validates the actual target list
before invoking Snakemake, selects the simulation-plus-metrics or metrics-only
rule module, and preserves one-command execution. Generation retains its direct
Snakemake entry point. This keeps two workflow entry points and introduces no
third workflow. Bare direct simulation Snakefile invocation would no longer
carry the operation/target guarantee.

Concrete proposed command surface (not implemented):

```text
pixi run python scripts/simulate_system.py --config <project> --target all
pixi run python scripts/simulate_system.py --config <project> --target metrics --dry-run
```

The runner would parse its own arguments, read the composed operation, normalize
targets, validate the exact allowed pair, then invoke Snakemake once with one
of two fixed rule-module selections. For metrics-only, it would resolve and
validate the selected retained metric-set filename before accepting a direct
file target. Snakefile preflight would still check retained inventory, required
variables and artifacts and omit simulation producers. The all-workflow runner
would use the same validation path. No arbitrary unchecked Snakemake arguments
would be forwarded as an escape from target validation. This is a reviewable
fallback proposal, not a tested replacement.

The alternative is to retain bare simulation Snakefile commands while relaxing
the target-pair exclusivity: directly requesting internal outputs would be
supported, while metrics-only producer omission would still prevent a model
run. That changes an accepted interface guarantee and also requires an owner
ruling. Private Snakemake state or reparsing its process arguments is not an
adopted workaround.

## Verification scope

The five new diagnostic cases passed in 27.41 seconds; three existing P2b cases
were deselected in that targeted iteration. Initial wrong metrics-only
expectation was corrected from observed behavior, not made into a design change.
The final combined fixture-file check and repository gates are recorded below.

Verification: rapid / numerical unaffected. All commands ran in the existing
Pixi environment with `--as-is`; complete gate logs are in
`.tmp/scratchpad/2026-09-10_2046/`.

| Command | Result |
|---|---|
| `pixi run --as-is python -m pytest tests/test_r12_wf3_feasibility.py -q --basetemp .tmp/scratchpad/2026-09-10_2046/r12-feasibility-final` | 8 passed, 59.91 s; includes diagnostic counterexamples |
| `pixi run --as-is pytest tests/test_cli.py --basetemp .tmp/scratchpad/2026-09-10_2046/cli-operation-gate` | 20 passed, 63.11 s |
| `pixi run --as-is lint` | Passed |
| `pixi run --as-is format-check` | Passed after one line-wrap correction; 292 files already formatted |

This deliberately stops after the decisive contract failure. Exact metric-file
targets, mixed/unknown/default selections and missing-inventory/variable/artifact
cases remain to be tested against the owner-selected replacement. Checkpoint
composition was not started. No full suite, model run or numerical baseline
comparison was performed; no production behavior changed.

## Work held at the gate

Checkpoint composition, the isolated fresh pre-change run, and production
extraction remain unexecuted. Snapshot preparation confirmed the unchanged
baseline settings: ERA5 for 2000–2016, two realizations, a 2 × 3 perturbation
grid, simulation years 2046–2054, experiment name `experiment`, and default
seed 123. No new snapshot config or output root was created. The owner must
rule on Master Gate 3 before the selected invocation contract is implemented.
