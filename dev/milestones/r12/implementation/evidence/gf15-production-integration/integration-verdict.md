# GF15 production integration — Stage 4/4 verdict

Date: 2026-09-15. Session `session-3`, branch `feat/wp3-improvements`, worktree
`C:/Users/taner/workspace/.worktrees/blueearth_cst/session-3`. Authority: the
[Stage 4 brief](../../gf15-production-stage-4.md), the accepted
[design](../../../gf15-production-adapter-design.md) D1–D8, and the owner's
2026-09-14 Windows-only sequencing override.

## Verdict

**BOUNDED WINDOWS ACCEPTANCE IS NOT YET ISSUED.** One prerequisite is
outstanding and it is procedural, not scientific: Stage 3's artifact changed
after its independent review, so the reviewer has not seen the tree this verdict
would cover.

| Component | Status |
|---|---|
| Stage 1 — isolated Windows setup and qualification | **accepted**, independently reviewed |
| Stage 2 — adapter, report, identity binding | **accepted** (E7 parity, Windows) at `5cd2d8ce` |
| Stage 3 — metrics comparison | **executed and complete**; **REJECTED** twice, against the record rather than the run both times; round-2 findings now discharged; **second re-review pending** |
| Stage 4 — reconciliation and software gates | **complete** (this document) |
| Linux parity — D8 handoff 2/4 | **outstanding**, owner-deferred 2026-09-14 |
| §7.5 owner method ruling | **outstanding** |

This is the honest position rather than a formality. The Stage 3 reviewer
verified a metric set (`7a0c4052…`) that no longer exists: acting on its own
finding 3 changed the reducer, which moved the identity to `7572a9a1…`. The
comparison was re-executed and is unchanged in substance — both published tables
are byte-identical to the reviewed run — but "unchanged in substance, verified by
the executor" is precisely the claim an independent reviewer exists to test.

## Implementation

| Item | Value |
|---|---|
| Estimator | `gf15-lmoments-c/1` |
| Dependency | `lmoments3` 1.0.8, wheel `984d1f1b0c3feefd57afc7a270931c1d28e4face2df1c2293559faf47681ef5e` |
| Installed `__init__.py` / `distr.py` | `1d2c066a…` / `f8859d11…` |
| Shipped report | `gf15-accuracy-8x-v1.json`, 787,487 bytes, `89905f1889a08177ff9225535a7a590b0081c76b2e6765e31e83390bee412b2c` |
| Repository lock | `43d11fc5297160152d0c728f9c9e4d4816c816b2876fc75cb3c3d210f437ffc6` |
| Qualified interpreter | `…/windows-environment-pypi/.pixi/envs/default/python.exe` |
| Stage 2 commits | `ce4d3bfa` → `eba69df2`, accepted at `5cd2d8ce` |
| Stage 3 / 4 commits | `4745a8b3`, `782941c1`, `5f0412ed`, `12c3948f`, and this one |
| Current metric set | `7572a9a10825fee5d4b4cbcd4e8a322000d266144bb223f493c52d9ec03dc274` |

## Design falsifiers, against executed evidence

The brief requires each to be checked rather than asserted.

| Falsifier | Outcome |
|---|---|
| Missing per-platform parity | **Windows present** (E7, two rounds). **Linux absent** — outstanding, not failed |
| Surviving mutant | None. Six mutant families fail; M6 — the one that changes a published value while still returning `accepted` — is caught only by bit-parity against the frozen candidate, and that boundary is recorded |
| Stale environment publication | `check_live_metric_environment` refuses at three points; a stale descriptor aborts reduction with zero fit calls and leaves no ready marker |
| Broken old reader | D6 dispatch accepts the legacy MLE set, the new set and the gwr-only set, with `lmoments3` unimportable |
| Incomplete comparison | 756 of 756 keys, zero unevaluated, zero surplus rows either direction |
| Model invocation during the comparison | None. Three rules in the DAG, no toolchain path in any config, native responses byte- and mtime-unchanged |
| Upstream hash drift | None across collection, responses, inventory and config |
| Changed non-return-level row | None |

**SHA bindings reconcile to the actual implementation.** The reviewer rebuilt
every member sample from the snapshot and reproduced all 70 published values at
`atol=0, rtol=0`, plus each `fit.input.sample_sha256`. Stage 2's `test-full` log
is **not** offered as this stage's gate — the brief is explicit that passing
tests from another source version do not satisfy it, and the source has changed
since. Fresh gates are below.

## Software gates, at this tree

Run on the qualified isolated interpreter. `pixi run` is unusable here: with
`lmoments3` in the repository manifest it would repair the shared environment,
which every stage brief forbids. The `pixi.toml` task bodies were therefore
translated verbatim onto that interpreter.

| Gate | Command | Result |
|---|---|---|
| `test-fast` (`pixi.toml:161`) | `-m "not workflow_contract and not process_isolation" -n auto --dist loadfile` | **3713 passed, 15 skipped, 1 xfailed**, 184.81 s — `stage-4-test-fast.txt`, re-run at the corrected tree |
| `test-contract` (`pixi.toml:162`) | `-m "workflow_contract or process_isolation"` | **101 passed**, 335.56 s — `stage-4-test-contract.txt` |
| Owning set + entry points | `pytest tests/test_metric_registry.py tests/test_metric_plan.py tests/test_config_composition.py tests/test_cli.py` | 186 passed |
| Lint / format | `ruff check` / `ruff format --check` | clean |

The contract tier was run because this stage changed a **rule's declared
outputs**, which `test-fast` excludes by construction. Together the two tiers
cover the suite's **3,829** collected tests — the contract log reports 101
selected against 3,728 deselected. (An earlier draft said 3,813, which added
`test-fast`'s *passes* to the contract tier's selections and so conflated tests
passed with tests covered.) The 15 skips and the xfail are the known
pre-existing set.

**Translation caveat, recorded rather than omitted.** Invoking the interpreter
directly drops pixi's `[activation.env]` — `HDF5_USE_FILE_LOCKING=FALSE` and
`GCSFS_EXPERIMENTAL_ZB_HNS_SUPPORT`. Neither is load-bearing for these tiers on a
local filesystem, established by two clean full runs, but that is an observation
on one platform and not a guarantee.

## What Stage 4 changed

**A latent defect in the pre-push gate itself.** The first `test-fast` attempt
aborted with nine collection errors: "Different tests were collected between gw7
and gw8". `test_config_composition.py` parametrized from `cc.GENERATION_KEYS` and
`cc.SIMULATION_KEYS`, both **frozensets**, whose iteration order depends on
`PYTHONHASHSEED` and so differs between xdist worker processes. It predates the
GF15 work but is **not** pre-existing relative to `main`: `868c4b7c` is
branch-local, 31 commits back, so **this branch introduced it** and the accurate
statement is that the documented pre-push rung went unexercised here for 31
commits. It is invisible to CI, which runs `pixi run pytest tests/ -q -rs` in a
single process. `test-fast` with `-n auto`
is the only invocation that exposes it, and `test-fast` is exactly what the
validation ladder names as the gate before pushing. Fixed by sorting both
parametrizations, with the reason in a comment so it is not "tidied" back.

**The undeclared rule output** (Stage 3 reviewer, finding 5).
`publish_metric_set` now declares `return_level_benchmark.json`. Previously
Snakemake neither tracked nor cleaned it, so a `--forcerun` or partial clean
could leave a manifest whose `return_level_benchmark.sha256` bound a missing
file. Identity-free: `repository_code_inventory` walks Python imports from
`metric_plan.py` and never reaches a `.smk`.

**Validation-map reconciliation.** Row 1 claimed "P3 pending … final entry points
do not yet exist" — falsified by the map's own P3 boundary section and by Stage 3
running through `scripts/simulate_system.py`. Rows 17 and 23 were half stale: P3
discharged production source-plan resolution and production reuse/force through
both interfaces, so those clauses were cleared, while **metric growth within
fixed capacity** and **reference-aware deletion** remain unexecuted and are now
stated as such. A stale "pending" and a premature "passed" are both defects; each
row was narrowed to what the evidence supports.

**Board.** `t2609140745` (collection anchor) closed on its own trigger, with the
durable finding — the anchor is byte-identical to the snapshot's copy and so
restorable — recorded in the ledger row. `t2609151037` opened for the second,
unreachable return-level estimator in `export_wflow_results`, carrying the
reviewer's measurement that the two paths can differ by 3x.

**Documentation.** The SciPy sign convention (ξ = −c) and the shape-domain
boundary now appear where a reader of the published parameters will meet them.

## Owner rulings recorded

- **2026-09-14** — Linux deferred; Windows-only setup and verification
  authorized. Linux parity remains an explicit R12 item and Windows evidence
  cannot satisfy it.
- **2026-09-15** — **B + A** on
  [shape-coverage-options.md](shape-coverage-options.md): record shape-domain
  coverage per fit, non-gating, plus user documentation. A hard guard (D) was
  recommended against and not taken: `InvalidReturnLevelFit` is caught nowhere in
  the package, so one refused fit would abort the entire metric set including
  statistics fully inside the assessed domain.

## Outstanding — nothing below is discharged by this verdict

1. **Stage 3 re-review** at this tree. The blocking item. Round 2 rejected
   again — narrowly, and again against the evidence bundle rather than the run,
   which it re-derived bit-for-bit through two separately executed package
   revisions. Its findings are discharged in
   [stage-3-rereview-verdict.md](stage-3-rereview-verdict.md); a third pass has
   not yet seen the result.
2. **Linux setup and parity** — D8 handoff 2/4.
3. **§7.5 owner method ruling** on the estimator.
4. **Actual-bundle applicability** — still `unestablished`; the 8x evidence
   remains a post-results development rescore under a relaxed retained-data
   policy, and is not independent validation.
5. **Low-flow return-level accuracy**, in both the near-zero and the
   outside-shape regimes. 21 of 70 production fits fall outside the assessed
   shapes, all on `q_return_level_2yr_7day_min`.
6. **Metric growth within fixed capacity** and **reference-aware deletion** —
   GF-17 and GF-23, unexecuted in production.
7. **The second estimator** in `export_wflow_results` — `t2609151037`.
8. **Milestone seal**, successor baseline, standing tree — all separate, and no
   part of this verdict infers any of them.

## Constraint compliance

No milestone seal, successor baseline, new adequacy claim, merge or push. No
prior verdict, source evidence or test was edited to manufacture acceptance: the
Stage 3 rejection stands recorded in full, its findings are discharged by
correction rather than by removal, and the one falsified claim in this record's
own predecessor is marked and dated in place. Nothing has been pushed.
