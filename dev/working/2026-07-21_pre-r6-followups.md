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

## Wave D — big / scientific (PENDING, final)

- **t260719a** — restore the 14 dropped Wflow constant parameters via CSDMS
  Standard Names. Scientific decision + parameter-reconciliation table +
  direct staticmaps.nc/TOML assertions + data-level wf1 discharge comparison +
  a clean re-record that also ADDS staticmaps/TOML fingerprints to the manifest.
  Warrants its own design doc.
- **Baseline manifest rebuild** — entangled with t260719a (both touch the
  manifest). The M2b manifest is still the contract of record (invariance-by-
  construction). A clean tracked-seed re-record is a natural companion to t260719a.

## Board reconciliation (verified 2026-07-21)

- t260716a `test_cli` xfails — DONE (MissingInput in R3, CyclicGraph in R5).
- t260716b historical wiring — DONE in R5 (`shared.historical_window`).
- t260716c outlet naming — DONE in R3 (`outlet_index.csv`).
- t260716c "CMIP6 attr loss on merge" — duplicate of **t260720e** (D-ATTRS); merge.
