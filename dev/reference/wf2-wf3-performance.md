# WF2 and WF3 performance changes

Implemented in session-4, September 2026. Scientific calculations and persisted indicator/change-factor formats are preserved.

## Removed work

- WF2 Stage B combines annual and monthly datasets in memory. It removes `2 * points * horizons + 1` temporary compressed NetCDF writes and their subsequent reads. Legacy file-writing helper calls remain supported.
- Each distinct scalar series is opened, identity-validated, loaded and closed once per Stage B job. Historical aggregates/statistics are reused across horizons and scenarios with keys covering the historical identity, analysis windows, calendar, water year, statistics, variable specification and reference thresholds. Only basin scalar series are retained, not gridded CMIP data.
- WF3 disables weather-generator PET by default; HydroMT remains responsible for the PET used by Wflow.
- WF3 omits the unconsumed final-state NetCDF. Input-state pointers and variable mappings remain intact; WF1 still writes its state artifact.
- Indicator export reads each simulation CSV once for all requested variables, retaining discharge columns for only one perturbation at a time. Seasonal pooling keeps only the two selected months.
- WF2/WF3 heavy rules declare memory reservations. Julia batches reserve their actual Snakemake thread allocation; automatic disk batching accounts for the resulting process concurrency and omits final-state size.

The memory reservations are initial scheduling estimates, not measured peak-RSS limits. A total `--resources mem_mb=...` budget is needed to constrain concurrency. See `docs/guide/running.qmd` for overrides. Correct CPU accounting can reduce simultaneous Julia processes for the same `-c` setting; no universal end-to-end speedup is claimed.

## Numerical evidence

- Synthetic before/after WF2 annual/monthly outputs: exact xarray equality for standard, noleap and 360-day calendar settings, January/October water years, and mean/median/std/q90 statistics.
- Cache regression: one open per scalar input, stale identity rejected, historical cache reused across horizons and scenarios, annual/monthly disk-roundtrip merge equivalence including monthly dataframe order.
- Weather-generator PET on/off: exact equality of every non-PET column, using 20 cells and 6,205 days, seed 123, temperature +2 and precipitation x1.2, for both transient and constant changes. Single-run elapsed times were 1.91 vs 1.37 seconds (constant), 1.24 vs 1.11 seconds (transient); these are indicative probes, not replicated benchmarks.
- Actual two-year HydroMT before/after forcing: identical datasets. Wflow configurations under Julia 1.11.7 preserve input state and mappings; both runs produce byte-identical CSVs. Only the original run emits a final-state NetCDF.
- PET NetCDF seam: PET-on/off weather-generator output retains pressure and radiation; both pass HydroMT downscaling and produce exactly identical final forcing, including recomputed PET.
- Actual baseline WF3 reduction: all 14 simulation CSVs regenerated both q and gwr indicator tables byte-identically. Synthetic three-variable exports also match byte-for-byte for December and September year anchors.
- Numerical comparison discrimination: an intentional temperature perturbation was detected by the reference comparisons.

Probes and command logs are retained locally under `.tmp/scratchpad/2026-09-06_2310/`; they are not shipped artifacts. GPT-5.6 Python-engineer review covered both workflow diffs. Full workflow timing and peak-RSS benchmarking are outside these equivalence probes.

## Validation commands

- `pixi run pytest tests/test_workflow_performance.py tests/test_series_identity.py -q`: 74 passed before the review extension; the four performance cases passed again after adding monthly and second-scenario coverage.
- Focused WF2/WF3 regression modules: 125 passed.
- `pixi run pytest tests/test_cli.py -q`: all 19 dry-run contracts passed as part of the broader test commands.
- `pixi run lint` and `pixi run format-check`: passed.
- Baseline regeneration: WF2 `reduce_gcm_series` and `derive_change_factors` ran from local raw data; WF3 indicators were re-reduced from the existing 14 baseline simulations. Missing copied-fixture config snapshots were generated through `snapshot_config`.
- `pixi run python dev/scripts/check_baseline.py check`: all seven targets match. This covers the regenerated reductions; it does not claim a fresh full 14-member stochastic simulation run.
- Regenerated WF2 change-factor cloud rendered and visually inspected.

- `pixi run test-full`: 3,276 passed, 9 skipped, 1 expected failure (875.93 seconds). Opt-in full-workflow integration tests were skipped; the targeted real-run probes above cover the changed numerical paths.

The baseline equivalence runs used the pre-rebase baseline configuration at `26c81500` (17-year WF3 window and `far` WF2 horizon). Concurrent main changes later shortened that configuration; the baseline manifest has intentionally not yet been updated (see `AGENTS.md`). This performance validation establishes equivalence for the recorded configuration, not numerical equivalence between those different windows.

- Post-rebase `pixi run test-fast`: 3,303 passed, 8 skipped, 1 expected failure (381.18 seconds), including the additional checks landed concurrently on main.

- Post-rebase CLI dry-runs: 20 passed; lint and formatting passed.

## Review decisions

GPT-5.6 review prompted restoration of the explicit file-wrapper signature, broader monthly/cross-scenario coverage, the PET NetCDF seam probe, and refreshed state-file documentation. Configurable memory estimates and honest Julia accounting remain with their limitations stated above. One header-only CSV read is retained to resolve columns cheaply; each simulation's full data is parsed once. The HM-4 validator's optional output-state mode remains backward-compatible with historical captures; the real generated TOML and Wflow probe establish that new runs omit the pointer. Additional schema validation for inconsistent later CSV headers is pre-existing behavior outside this refactor.
