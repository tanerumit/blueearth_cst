# Followups

Issues surfaced during pre-M1 cleanup that belong to later milestones.
Per the roadmap's "no milestone touches the next milestone's territory" rule,
captured here and resolved in passing when the relevant milestone starts.

Convention: one bullet per item. Keep the diagnosis date and reproducible
context so future-you can confirm the issue still applies before fixing.

---

## R3 — Workflow 1: model builder

- **Resolve test_cli xfails.** Two of the three parametrizations in
  `tests/test_cli.py` are marked `xfail` since M2:
  - `Snakefile_climate_projections`: dry-run trips
    `MissingInputException` because the workflow expects
    `staticgeoms/region.geojson` (produced by Snakefile_model_creation)
    even when only dry-running. Either change the test fixture to
    pre-stage that file, or refactor `Snakefile_climate_projections` so
    `--dry-run` doesn't require it.
  - `Snakefile_climate_experiment`: dry-run trips
    `CyclicGraphException` at `rule generate_climate_stress_test`. The
    rule's wildcard pattern `rlz_{rlz_num}_cst_{st_num}.nc` overlaps
    with `generate_weather_realization`'s output `rlz_{rlz_num}_cst_0.nc`.
    Production configs (`config/snake_config_model_test_local.yml`) work
    fine because Snakemake disambiguates from concrete paths in
    `expand(...)`, but the `--dry-run` resolver flags the cycle on the
    test config. Add a wildcard constraint (`{st_num,[1-9][0-9]*}` or
    similar) or a `ruleorder:` directive.

  These are pre-M2 failures masked by the fact that M1 closure didn't
  actually run pytest. Both belong to R3's "tighten ruleorder + Snakefile
  hygiene" deliverables.

- **`Path(fn, resolve_path=True)` is a non-existent kwarg in
  `src/prepare_climate_data_catalog.py:76,85`.** Surfaced 2026-05-08 by
  M02c tests via pytest deprecation warnings:
  *"support for supplying keyword arguments to pathlib.PurePath is
  deprecated and scheduled for removal in Python 3.14"*. `Path()` does
  not accept `resolve_path`; it is silently swallowed today, which means
  the orography-path resolution the author intended **is not happening**.
  The two lines:
  ```python
  fn_oro = Path(fns[0], resolve_path=True)
  ...
  fn_oro = Path(fn_oro, resolve_path=True)
  ```
  *Fix:* replace with `Path(fns[0]).resolve()` and `Path(fn_oro).resolve()`.
  Hard deadline: Python 3.14 (currently capped at 3.12 in `pixi.toml`,
  but the cap will lift eventually). Existing M02c tests
  (`test_chirps_source_adds_orography_entry`,
  `test_processing_metadata_mentions_chirps_and_era5_for_chirps_source`)
  exercise the affected path and will catch behavior changes.

- **Redo M1 warnings triage exhaustively.** M1 closed with an incomplete
  triage (`dev/phase-1/m01/warnings.md`) because most rules don't write stderr
  to disk. Once R3's cross-cutting deliverable adds `log:` directives
  to every non-trivial rule across all three Snakefiles, re-run all
  three workflows, sweep the captured logs, and fix any bucket-2
  (config/data-catalog) or bucket-3 (our-code) warnings that surface.
  Update `dev/phase-1/m01/warnings.md` (or supersede it with an `m03_*` doc).

- **`extract_climate_grid` silently truncates the historical range.**
  When the snake config's `historical:` window asks for years that the
  staged source doesn't cover, the rule produces a shorter `extract_historical.nc`
  without any warning. Downstream rules then fail in cryptic ways far from
  the actual cause.

  *Observed 2026-05-07:* config asked `historical: 1980, 2010` (31 years),
  the staged era5 only had data from 2000-01-01 onward, so the extracted
  netCDF held 2000–2010 = **11 years**. That fell below weathergenr's
  16-year wavelet minimum and crashed `generate_weather_realization`
  with `'series' must have at least 16 observations`.

  *Fix:* in `extract_climate_grid` (or its underlying script), log a warning
  when the extracted time span is shorter than the requested span. Optionally,
  fail the rule if the shortfall is large enough to break a downstream step
  (e.g. < 16 historical years when weathergenr is in the pipeline).

  *Related Snakemake-staleness issue:* a snake-config edit that changes what
  the rule *should* produce does not invalidate the existing output, because
  Snakemake's freshness check is file-existence-based, not config-content-aware.
  Reproduced 2026-05-07: changing `historical:` in the config didn't trigger
  re-extraction; the user had to `--forcerun extract_climate_grid` to pick up
  the change. Worth fixing alongside the truncation warning — declare the
  snake config (or a hash of the relevant keys) as an input of
  `extract_climate_grid` so config edits propagate automatically.

  *Workaround applied 2026-05-07:* `historical: 2000, 2020` in the local test
  config + `--forcerun extract_climate_grid` for the immediate run. Treats
  the symptom; doesn't fix either of the two underlying issues.

---

## R5 — Workflow 3: climate experiment

- **`extract_climate_grid` ignores the `historical:` config and hardcodes
  the date range.** Pre-R5 unblocking edit on 2026-05-07 changed the
  hardcoded `starttime="2000-01-01"` / `endtime="2020-12-31"` in
  `src/extract_historical_climate.py`. The snake config's `historical:`
  key is read by `Snakefile_climate_projections` (workflow 2) but never
  by `Snakefile_climate_experiment` (workflow 3) — the rule
  `extract_climate_grid` only receives `data_sources` and `clim_source`
  as params; `historical:` is silently ignored.

  *Proper fix:* in `Snakefile_climate_experiment`, parse `historical:`
  from the config and pass `starttime` / `endtime` as rule params; in
  `src/extract_historical_climate.py`, replace the hardcoded date
  strings with `sm.params.starttime` / `sm.params.endtime`. While at it,
  drop the misleading function defaults at lines 20–21 (currently still
  say `1980` / `2010`).

  *Also touches the R3 followup:* this is the same shape as the
  config-key-not-wired pattern — fixing it should be paired with a
  general audit of every rule whose behavior depends on a config key
  that isn't actually read.

- **`weathergenr::write_netcdf` does not propagate `spatial_ref` attributes
  from `template_path` to the output.** Confirmed 2026-05-07: the historical
  template (`extract_historical.nc`) has `x_dim='longitude'` and
  `y_dim='latitude'` on its `spatial_ref` variable, but the realization
  files written by `write_netcdf` (`rlz_*_cst_0.nc`) have an *empty*
  attribute list on their `spatial_ref` variable. Downstream
  (`impose_climate_change.R`) then crashes when it uses the realization
  as its own template, because `write_netcdf`'s `x_dim` lookup returns
  `0` (numeric, from `ncatt_get` on a missing attr) — which slips past
  the existence check and causes
  `Error in nc_in$dim[[x_dim_name]] : attempt to select less than one element`.

  *Workaround applied 2026-05-07:* in `src/weathergen/generate_weather.R`,
  after each `write_netcdf` call, manually copy `spatial_ref` attributes
  from the historical input file to the just-written realization file
  via `ncdf4::ncatt_get` / `ncatt_put`. Marked clearly so it can be
  removed when weathergenr is fixed.

  *Proper fix:* in `tanerumit/weathergenr` `R/io_netcdf.R`, the
  attribute-copy loop in `write_netcdf` looks correct on the surface
  (`ncatt_get(nc_in, spatial_ref)` → `ncatt_put`) but evidently isn't
  executing or isn't writing through. Investigate why the loop produces
  zero attributes on the output. Separately, the missing-attribute check
  should also assert `hasatt = TRUE` on the `ncatt_get` result, not just
  test the value for NA / NULL — the current check accepts the numeric
  `0` returned for a missing attribute and crashes one line later.

- **weathergenr's wavelet minimum surfaces as a cryptic error.**
  `wavelet_cwt.R` enforces `length(series) >= 16` on the *annual* aggregate
  (i.e. ≥ 16 historical years), but the user-facing error is just
  `'series' must have at least 16 observations` — no mention of years,
  wavelet, or how to remedy.

  *Fix:* improve the error in `tanerumit/weathergenr` (upstream of this repo).
  Suggested message: *"historical period (N years) is below weathergenr's
  wavelet minimum of 16 years; extend the historical range or reduce the
  wavelet decomposition depth."*

  *Note:* this fix lives in the weathergenr package, not this repo. Mention
  in R5 deliverables if R5 is also touching the R layer; otherwise track as
  a separate weathergenr issue.

---

## R3+ — Surfaced during M02c (test coverage)

Lessons learned writing the M02c unit tests. Not bugs — testing-discipline
notes for R3-R5 to inherit when they add their own test files.

- **Test pollution between `sys.modules.setdefault` files.** pytest collects
  test files in alphabetical order. The first file to call
  `sys.modules.setdefault("hydromt", <stub>)` (or any heavy dep) wins, and
  later files using `setdefault` for the same key get a silent no-op —
  their import of the source module then binds to the *previous* test
  file's stub. Symptom: tests pass when run in isolation, fail in the full
  suite with `KeyError` on fixture-set catalog data.

  *Pattern:* don't rely on `setdefault` alone for shared keys. Use
  `monkeypatch.setattr(<source_module>.<dep>, "<attr>", <fake>)` inside
  fixtures so each test gets a clean override regardless of collection
  order. See `tests/test_prepare_climate_data_catalog.py` for the
  reference implementation; commit `f65244e` for the diagnosis.

- **dask cannot be stubbed at module level.** pandas does a lazy
  `import dask` and accesses `dask.__spec__` during type compatibility
  checks. A `types.SimpleNamespace` stub for dask there raises
  `ValueError: dask.__spec__ is not set` during collection of *any* test
  file that imports pandas. dask is in the env via pixi; let it import
  normally. If the cost matters, mock the specific dask object at call
  time within the test, not at module level.

---

## R3+ — Surfaced during M2b (library upgrades)

Items surfaced during the hydromt 0.x → 1.x / hydromt_wflow 0.x → 1.x /
Wflow.jl 0.7 → 1.0.2 / pandas 3.x / Python 3.12 jump. See `dev/phase-1/m02b/`
for the full M2b record.

- **`hydromt 1.x` `to_dict` / `to_yml` silently strips `driver.options.preprocess`.**
  Round-tripping a catalog dict through `DataCatalog().from_dict(...).to_yml(path)`
  loses the preprocess hook even though `from_dict` preserves it on read.
  *Workaround applied:* `src/prepare_climate_data_catalog.py` bypasses
  `to_yml` and uses `yaml.safe_dump` directly.
  *Proper fix:* file upstream against `hydromt`. Reproducer is the
  three-line snippet in `dev/phase-1/m02b/handoff.md` decision section.

- **conda-forge does not ship `julia` for win-64 at all.** linux-64 / osx-64
  have 1.10.x and 1.12.x but skip 1.11.x; win-64 has nothing. This blocks the
  "single env via pixi" goal on Windows for the Julia layer. Today juliaup
  manages Julia 1.11.7 outside pixi.
  *Possible fixes:* (a) wait for conda-forge to ship win-64 Julia; (b) wrap
  juliaup in a pixi `[tasks]` step that calls `juliaup install 1.11.7` at
  env-setup time; (c) move to a different distribution channel.

- **weathergenr cannot be installed into the conda r-base site-lib on
  Windows.** `pak::pkg_install(..., lib=R_HOME/library)` and
  `install.packages(..., lib=R_HOME/library)` both fail at the byte-compile /
  lazy-load step with `Mingw-w64 runtime failure: 32 bit pseudo relocation
  ... out of range`. The conda r-base toolchain's mingw runtime is
  ABI-incompatible with one or more of weathergenr's Imports (likely
  `ncdf4`) when loaded inside the install transaction. The package itself
  is pure R; the failure is in the deps it loads at install-time lazy
  binding.
  *Workaround applied:* `dev/scripts/install_weathergenr.R` installs without
  `lib=` so the package lands in `.libPaths()[1]` (user lib on Windows,
  conda site-lib on Linux). `src/weathergen/global.R` trusts R's default
  libPaths so the user-lib install is visible at workflow runtime.
  *Proper fix:* either (a) get weathergenr to compile cleanly against
  conda r-base on Windows (probably needs an upstream conda-forge fix to
  the ncdf4 / r-base mingw build), or (b) vendor weathergenr under
  `vendor/weathergenr/` and install via `R CMD INSTALL` skipping the
  lazy-load test.

- **`setup_constant_pars` short names → CSDMS Standard Names.** hydromt_wflow
  1.x's `setup_constant_pars` rejects the short parameter names from 0.x
  (`Cfmax`, `KsatHorFrac`, `TT`, `TTI`, `TTM`, `WHC`, `G_Cfmax`, `MaxLeakage`,
  `InfiltCapPath`, …) and requires CSDMS Standard Names instead. M2b dropped
  13 of the 14 originally-set constants under the "intentional drift,
  re-baseline aggressively" policy and kept only `KsatHorFrac` (which the
  build errors without). R3 should map the other 13 to CSDMS names and
  decide whether to restore them. CSDMS lookup tables in
  `hydromt_wflow.naming` and `hydromt_wflow.version_upgrade`. Concrete
  remap in `dev/phase-1/m02b/handoff.md` decision #3.

- **CMIP6 `precip` / `temp` `.attrs` lost on `monthly_change_scalar_merge`.**
  Pre-M2b, `annual_change_scalar_stats_summary.nc` carried `cell_measures`,
  `cell_methods`, `comment`, `long_name`, `original_name`, `standard_name`,
  `units` on each data variable; under hydromt 1.3, those are now `{}` on
  the merged output. Documented in `dev/phase-1/m02b/baseline_diffs.md`.
  *Investigation:* identify whether `get_change_climate_proj.py` or hydromt
  drops the attrs during the merge; restore them.

- **Outlet station naming convention decision.** hydromt_wflow 1.x's
  `setup_outlets` uses subcatchment IDs (e.g. `130000086`, `1`, `2`, …) for
  outlet stations rather than the contiguous `1..N` of 0.x. The CSV column
  also renamed `Q_gauges` → `Q_outlets`. M2b's `src/plot_results.py`
  rebuilds `station_name` as `1..N` to keep `hydro_wflow_1.png` visually
  stable; R3 should pick a consistent project-wide convention (real
  subcatchment IDs vs `1..N` rebuild) and document it.

- **Retire the "CMIP6 GCS throughput regression" follow-up.** The original
  M2b mid-flight estimate was ~6 h for the full 3-model × 2-scenario fetch;
  the as-shipped run completed in 24 min after the eager `.load()` patch
  in `src/get_stats_climate_proj.py`. The followup line item was based on
  the slow path and no longer applies. (No file currently lists it
  separately — leaving this here as a reminder if it resurfaces.)
