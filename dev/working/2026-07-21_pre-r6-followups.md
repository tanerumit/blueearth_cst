# Pre-R6 followups campaign

Clearing the deferred backlog before the R6 structural refactor, so R6 does not
carry latent defects. Branch `fix/pre-r6-followups` off `main`.

**Scope decisions (2026-07-21):**
- t260719a (CSDMS constant-params restoration) — **included** as the final wave
  (settle the baseline before R6 freezes structure).
- Upstream weathergenr fixes (spatial_ref, wavelet message) — **out**, tracked as
  separate `tanerumit/weathergenr` issues; in-repo workarounds stay.
- wf1 `| tee` exit-masking — resolve with a **portable Python tee wrapper**
  (keeps live console output + fixes exit-safety).

Cut by cost: does the item need a workflow run + baseline re-record, or just
`pytest` + an xfail flip?

## Wave A — no-run batch (DONE 2026-07-21)

All tripwire-wired, latent on the current seed, verified by `pytest` alone.
Suite before: 119 passed / 3 skipped / 7 xfailed. After: **123 / 3 / 1**
(the lone remaining xfail is the upstream hydromt `to_yml` workaround, M2b).

| Task | Fix | Commit |
|---|---|---|
| t260720a | `prepare_cst_parameters` read `variance["min"]` into the max endpoint → `["max"]` | `d2de843` |
| t260720c | D-CAL: cftime-safe slicing in `get_change_annual_clim_proj` (convert object-dtype index up front) | `c57eda0` |
| t260720d | D-VAR/D-MEM: fail loud (ValueError) on asymmetric hist/clim vars & members; corrected stale split-IDs in tests | `735cc20` |
| t260716a (part) | `extract_climate_grid` truncation warning in `prep_historical_climate` | `ce56bc3` |

## Wave B — run + re-record (PENDING)

- **t260720e (D-ATTRS)** — CF-metadata loss on `annual_change_scalar_stats_summary.nc`.
  Localized (R4 probe) to the hydromt catalog read, a dependency op. Needs a real
  CMIP6 catalog read to confirm the source, then a workflow-2 attrs re-attach (or
  upstream hydromt). Moves the summary `.nc` fingerprint → a `baseline_diffs.md`
  entry + re-record of the wf2 slice.

## Wave C — decision-gated code / sweeps

- **wf1 `| tee` exit-masking (t260721a) — DONE 2026-07-21, commit `d13ba37`.**
  `Snakefile_model_creation`'s 3 shell rules route through `src/run_logged.py`
  (a CLI over `snake_utils.run_and_tee`): live console output + log + child exit
  code. Verified end-to-end (failing child propagates its code; old `| tee`
  masked to 0). Tests in `tests/test_run_logged.py`; DAG dry-runs green.
- **M1 warnings triage sweep** (t260716a remnant, PENDING) — now that all three Snakefiles
  write per-rule `log:` files, re-run the workflows, sweep captured logs, fix
  bucket-2/3 warnings. Needs runs.
- **`extract_climate_grid` config-staleness** (t260716a remnant) — a config edit
  to `historical:` does not invalidate the existing output (Snakemake freshness is
  file-existence based). Declare the config (or a hash of the relevant keys) as a
  rule input. DAG change → dry-run.

## Wave D — big / scientific (design ACCEPTED, implementation PENDING)

- **t260719a — design ACCEPTED 2026-07-21 (G2) as
  [ADR 0001](../decisions/0001-restore-wflow-constant-parameters.md)** via a full
  `design-review-loop` (internal risk/architecture/repo-fit panel + 2 external
  GPT rounds via codex + user arbitration at the cap; 26 findings all resolved;
  consolidated record `dev/reviews/2026-07-21_adr-0001-constant-pars.md`). The
  review caught two class-of-error bugs before any build compute: the protocol
  targeted `staticmaps.nc` but constants land as TOML scalars, and a
  build-sequence identity-comparison trap. **Implementation is the remaining,
  build-heavy work** (route to `model-builder`). All 15
  CSDMS mappings resolved from `hydromt_wflow/naming.py` (the M2b "5 unresolved"
  all map to real names; none is `wflow_v1: None`): 1 retained (`KsatHorFrac`),
  1 forced-drop (`InfiltCapSoil`, deprecated), 13 mappable → RESTORE. Decision:
  evidence-gated restoration (adopt-default is the null; restore posture
  justified by cross-basin correctness; the discharge diff blesses the move,
  it does not decide per-param drop). Implementation protocol (restored-vs-clean
  builds, staticmaps/TOML landing asserts, discharge materiality, manifest
  extension + re-record) is §"Validation protocol" of the ADR.
  - **Implementation — build-independent slice DONE 2026-07-21.** Artifacts under
    `dev/working/const-pars/` + `dev/scripts/`:
    - **Equivalence gate (step 3c) — all 13 PASS, restored count = 13** (gate log
      `dev/working/const-pars/equivalence-gate-log.md`). Two-sided authoritative
      evidence (Wflow.jl v0.8 params + glacier melt eqn / stable 1.x param ref /
      `naming.py`). `g_ttm`/`g_tt` collapse sound (`g_tt` is the melt threshold);
      `MaxLeakage` 1.x default = 0 → 9th default-equal pin. Nothing fails closed.
    - `config_baseline.yml` (pinned M2b snapshot) + `config_restored.yml` (13 CSDMS
      entries + KsatHorFrac; drop-comment rewritten to point at ADR 0001).
    - `check_baseline.py`: step-6 time-index-aligned discharge comparator (`compare`
      subcommand + `discharge` target, v2 manifest, sidecar ref series) and step-7
      `record --workflow` merge semantics. Tests: `tests/test_check_baseline_scope.py`
      (rewritten, 15 targets) + new `tests/test_check_baseline_discharge.py`; 19 pass.
    - `dev/scripts/verify_constant_pars.py` (step 3a/3b landing/precedence);
      smoke-tested against the baseline model (KsatHorFrac OK, other 13 ABSENT).
  - **Remaining (build-heavy, steps 2/4/4b/5/7):** build wf1 from `config_restored`
    and `config_baseline` into clean dirs; reproducibility (4b) + materiality (5) via
    `check_baseline.py compare`; run `verify_constant_pars.py` on the restored build;
    if material, re-run wf3 + coherence review; `record --workflow` the wf1 (and
    affected wf3) slice(s). Route to model-builder / a real build environment.
- **Baseline manifest rebuild** — entangled with t260719a (both touch the
  manifest). The M2b manifest is still the contract of record (invariance-by-
  construction). ADR 0001 step 7 folds the clean re-record + fingerprint
  extension into t260719a.

## Board reconciliation (verified 2026-07-21)

- t260716a `test_cli` xfails — DONE (MissingInput in R3, CyclicGraph in R5).
- t260716b historical wiring — DONE in R5 (`shared.historical_window`).
- t260716c outlet naming — DONE in R3 (`outlet_index.csv`).
- t260716c "CMIP6 attr loss on merge" — duplicate of **t260720e** (D-ATTRS); merge.
