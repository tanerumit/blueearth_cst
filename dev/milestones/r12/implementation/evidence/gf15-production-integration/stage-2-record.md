# GF15 production Stage 2 — adapter and report implementation record

Date: 2026-09-14. Session `session-3`, branch `feat/wp3-improvements`, worktree
`C:/Users/taner/workspace/.worktrees/blueearth_cst/session-3`. Authority: the
accepted [adapter design](../../../gf15-production-adapter-design.md) D1–D7, the
[Stage 2 brief](../../gf15-production-stage-2.md) and the owner's 2026-09-14
Windows-only sequencing override.

Implementation is complete and gated. **E7 parity was subsequently ACCEPTED for
Windows** by the independent model-validator at `5cd2d8ce`, after a first-round
REJECTION at `ebd85b88` that found a real warnings-retention defect; the verdict
and both rounds are recorded in [e7-parity-verdict.md](e7-parity-verdict.md).
Linux is deferred and unexecuted, so cross-platform acceptance under D8 handoff
2/4 remains open. The body below was written before that review and is left as
it stood, with the two findings corrected in place where they touched it.

## What landed

Six commits, in the runnable groupings the master brief requires: no consumer
precedes its dependency, and no candidate writer precedes its report.

| Commit | Grouping |
|---|---|
| `ce4d3bfa` | dependency support: `lmoments3==1.0.8` in `[pypi-dependencies]`, solver-regenerated lock |
| `99efe9e4` | shipped report asset, its generator, and the package-resource loader |
| `9fa0eece` | typed adapter `gev_lmoments.fit_case` → `FitResult` |
| `eaedeaea` | reducer integration — **this is the commit that changes fitted values** |
| `3cb71076` | identity binding, live-environment freshness, reader dispatch |
| `eba69df2` | user documentation and the detached-CSV disclosure |

## Identities

| Item | Value |
|---|---|
| Estimator | `gf15-lmoments-c/1` |
| Dependency | `lmoments3` 1.0.8, wheel `984d1f1b0c3feefd57afc7a270931c1d28e4face2df1c2293559faf47681ef5e` |
| Installed `__init__.py` | `1d2c066a2ec4925bb838b7680d63ae8ae87c5234aa3c986d6ebe81500d75d6e2` |
| Installed `distr.py` | `f8859d11f10c3206e3e5009c1b238a328c6c9215b1cc7436800160fa929bb2ee` |
| Shipped report | `blueearth_cst/experiment/data/gf15-accuracy-8x-v1.json`, 787,487 bytes, `89905f1889a08177ff9225535a7a590b0081c76b2e6765e31e83390bee412b2c` |
| Policy | `gf15-accuracy-8x-v1`, declaration schema `return-level-validation/1` |
| Repository lock | `43d11fc5297160152d0c728f9c9e4d4816c816b2876fc75cb3c3d210f437ffc6` (byte-identical to the Stage 1 qualified lock) |
| Qualified interpreter | `.../windows-environment-pypi/.pixi/envs/default/python.exe` |

## Commands

Every gate ran on the **isolated** interpreter, never through `pixi run`: once
`lmoments3` is in the repository manifest, a bare `pixi run` would repair the
shared environment, which the brief forbids.

```powershell
$Iso = "C:/Users/taner/workspace/blueearth_cst-artifacts/r12/gf15-production-integration/windows-environment-pypi/.pixi/envs/default/python.exe"
& $Iso -B -m pytest tests/test_gev_lmoments.py tests/test_return_level_validation.py -q
& $Iso -B -m pytest tests/test_metric_registry.py tests/test_metric_plan.py `
    tests/test_content_identity.py tests/test_export_wflow_results.py -q
& $Iso -B -m ruff check .
& $Iso -B -m ruff format --check .
& $Iso -B -m pytest tests/            # redirected to stage-2-test-full.txt
& $Iso -B dev/scripts/build_gf15_report.py --check
```

## Results

| Gate | Result |
|---|---|
| Adapter tests | 53 passed |
| Loader / declaration tests | 29 passed |
| Registry, plan, identity, export owning set | 93 passed |
| Repository lint | `ruff check .` clean; `ruff format --check .` 367 files already formatted |
| Independent E7 parity verdict | **ACCEPTED (Windows)** at `5cd2d8ce` after a first-round rejection; see [e7-parity-verdict.md](e7-parity-verdict.md) |
| Full non-integration suite | **3808 passed, 15 skipped, 1 xfailed** in 1744.67 s at the accepted HEAD `5cd2d8ce`; log retained as `stage-2-test-full.txt` |
| Asset reproducibility | `--check` confirms the committed asset rebuilds byte for byte |

The 15 skips and the single xfail are pre-existing and self-describing: eleven
`test_interchange_contracts` skips state "standing fixture predates R12; GF9
successor run has not replaced it", three need `--run-integration`, one predates
R14, and the xfail is the known hydromt 1.3 `to_yml` upstream defect.

Intermediate full runs reported 3794 passed at `eaedeaea` and 3804 at `ebd85b88`;
each difference is exactly the tests added between them — ten freshness and
reader tests in `3cb71076`, four warning-retention tests in `5cd2d8ce`.

**One run stalled and was discarded, not counted.** A full-suite attempt froze at
`tests/test_climate_store_freshness.py` — 0.09 CPU-seconds across 45 wall-seconds,
log byte-frozen, ~60 minutes against a 17-minute norm. Killing it exposed a
four-deep nested python chain and a `.snakemake/` workdir whose `locks/`,
`incomplete/` and `metadata/` were stamped at the stall; the lock cleared with the
tree. The file then passed in isolation (2 passed, 157 s) and the full suite passed
on a verified-lock-free workdir, so this was contention from concurrent test runs
in one worktree — that test shells out to Snakemake, which locks its workdir — and
not a defect. **Carried to Stage 3:** its metrics run takes a Snakemake workdir
lock of its own and must not overlap with a suite in the same worktree.

## Design rows discharged, and by what

| Row | Discriminator used |
|---|---|
| C mapping | Bit-for-bit parity against the **frozen candidate** over seven sample shapes (ties, negatives, translation, scaling, minimal n, dense); all 19 retained branch references and all 44 retained quantile bit patterns; four mutant families that must and do change outputs |
| Extraction | Block extraction, member locality, finite filtering, screening and member ordering asserted unchanged; the constant sample now produces a structured `invalid_range` refusal and the predecessor's unstructured guard is asserted absent |
| Probability coverage | An off-domain return period (T=4 → p=0.75) raises `ReturnLevelProbabilityNotCovered` with **zero** recorded library invocations |
| Fault boundary | The real line-1307 raising statement is exercised; line 1342 is classified from a real frame; subclasses, identical messages from foreign frames, wrong line numbers and arbitrary errors are all faults; one inversion call, no retry |
| Diagnostics | Support and density counts recorded, never vetoing; a warning alone never refuses; faults keep their traceback with warnings as notes |
| Identity / report | Tampered asset, tampered embedded text, altered criteria, altered declaration and mismatched digests each fail; unknown schemas refused, never defaulted |
| Live environment | Stale descriptor aborts reduction with zero fit calls; no marker on a stale publish; late drift leaves an unready partial destination |
| Resource portability | Loader works from a relocated copy with the checkout, `dev/` and scratch unreachable; absent or corrupt asset fails rather than degrading |
| Compatibility | Legacy record reads without a report and must not carry one; the loader imports with `lmoments3` made unimportable |

## Deliberate divergence, recorded

`export_wflow_results._return_level_from_blocks` **still uses the predecessor
xclim/SciPy fit.** D2 scopes the estimator change to `reduce_bundle` and D8 names
the export module a preservation surface, so it was left alone. The repository
therefore now carries two GEV estimators.
`test_legacy_export_helper_keeps_the_predecessor_estimator` asserts they
disagree, so the divergence is a pinned fact rather than a later surprise.
Whether the legacy helper should follow is a Stage 4 question, not a Stage 2 one.

> **Corrected 2026-09-14 after independent review (finding F2).** A first draft
> of this paragraph justified the decision by saying the helper "sits on the
> legacy `analyze_wflow_results` path" while "the production rule is
> `analyze_response_runs`". That named a live path that does not exist in this
> tree, and the reviewer was right to reject the reasoning. Verified: **no
> Snakefile references `export_wflow_results`**, `metric_plan.py` imports only
> `_format_value` from it, and `_return_level_from_blocks` is reachable solely
> from line 443 inside its own module and from `tests/test_metric_registry.py`.
> The correction cuts in the change's favour — the mixed-vintage risk is *lower*
> than the original wording implied, because the predecessor helper is not
> reachable from any current run — but an acceptance record must not rest on a
> rule that has been removed. The scoping decision itself stands on D2 and D8.

## What this record does not establish

- **E7 parity.** No independent model-validator verdict exists yet. Fixed
  tolerances, exact acceptance and refusal codes, and a wrong-result mutant that
  demonstrably fails must be judged by the reviewer, not the executor.
- **Linux.** Nothing was installed or executed on linux-64. Windows parity
  cannot release cross-platform acceptance.
- **Numerical adequacy on real data.** No fit has run against retained
  production responses. That is Stage 3's comparison.
- **The standing baseline.** Nothing here re-records it, and it is not the check
  for this change; Stage 3's metrics comparison is.
- **Actual-bundle applicability.** The 8x evidence remains a development
  rescore under a relaxed retained-data policy.

## Handoff

Stage 3 may proceed on Windows once the model-validator returns parity. Before
launching it, resolve the collection-anchor exposure tracked as `t2609140745`
and set the ambient environment deliberately — the old run captured none, so its
variables are unknown rather than matched.
