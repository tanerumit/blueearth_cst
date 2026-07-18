# Followups

Issues surfaced during pre-M1 cleanup that belong to later milestones.
Per the roadmap's "no milestone touches the next milestone's territory" rule,
captured here and resolved in passing when the relevant milestone starts.

Convention: one bullet per item. Keep the diagnosis date and reproducible
context so future-you can confirm the issue still applies before fixing.

---

## Cross-cutting — baseline manifest integrity

- **[RESOLVED 2026-07-18] Baseline rebuilt from a tracked seed config.**
  `dev/baseline/manifest.json` was re-recorded from the now-tracked
  `config/snake_config_model_test.yml` (project_dir `examples/test_local`,
  3 models, single `far` horizon, current libraries), after a fresh run of
  all three workflows. `record` → `check` round-trips clean (14/14). The
  untracked `snake_config_model_test_local.yml` that seeded the stale M2b
  baseline is retired, so the divergence cannot recur. The model-independent
  workflow-1 PNG drift noted below was not separately investigated — it is
  moot now that the whole baseline is re-recorded from a known, tracked
  config; revisit only if a future `check` shows unexplained PNG drift.
  Original diagnosis retained below for provenance.

- **Rebuild `dev/baseline/manifest.json` against current libraries with a
  tracked seed config.** *Surfaced 2026-07-18 during R01 Task 5.* The M2b
  manifest (last recorded 2026-05-08, commit `159e197`) was recorded from
  an **untracked, 3-model local config**, while the tracked canonical
  (`config/snake_config_model_test.yml`) has used an **8-model** list since
  before `pre-r01`. The two have been silently divergent since M2b — the
  workflow smoke tests never compare against the manifest, so nobody caught
  it. R01 Task 5 was the first `check_baseline check` against the canonical
  model set and exposed the mismatch (see `dev/r01/baseline_diffs.md`).

  A fresh 8-model canonical run also shows **model-independent** drift on
  workflow-1 plots (`basin_area/hydro_wflow_1/precip.png`, 19–32% size) —
  workflow 1 never reads the climate model list, so the M2b local config
  must have differed from the canonical in ways beyond model count, and
  **cannot be reconstructed**.

  *Fix:* choose a deliberate model set, commit a **tracked** seed config
  (or parameterize `check_baseline` with one) so the baseline is
  reproducible, run all three workflows on current libraries, and record a
  fresh manifest. Investigate whether the workflow-1 PNG drift is
  rendering-only (matplotlib) or real content before blessing it. Until
  then the M2b manifest remains the contract of record, with R01 sealed on
  invariance-by-construction rather than a re-record.

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

- **[RESOLVED 2026-07-17] weathergenr crashed loading on Windows —
  root cause was conda-forge's r45 `r-waveslim` build, not `ncdf4`.**
  `library(weathergenr)` (and the install's lazy-load step) died with
  `Mingw-w64 runtime failure: 32 bit pseudo relocation ... out of range`.
  Isolated by loading each Import in turn: the first 15 loaded fine and
  only `waveslim` overflowed — its Fortran DLL carries a 32-bit
  pseudo-relocation to libgfortran that lands ~2.7 GB away (past the
  signed 2 GB range), so load order can't dodge it. The earlier "likely
  ncdf4" and "user lib on Windows" notes were both wrong: under pixi
  `Rscript --vanilla` the only libPath is the conda site-lib, and ncdf4
  is fine. The bug is specific to the **r45** (R 4.5) waveslim build; the
  **r44** build loads and runs `modwt` cleanly.
  *Fix applied:* pin `r-base = "4.4.*"` in `pixi.toml` so the solver picks
  the working r44 waveslim (and r44 builds of the other Fortran deps).
  Also switched `install_weathergenr.R` from `pak` (conda-forge `r-pak` is
  separately broken on win-64 — "Wrong OS or architecture") to
  `remotes::install_github(dependencies=FALSE, upgrade="never")`, which
  touches nothing but weathergenr itself. Verified: `pixi run install-rdeps`
  installs and `library(weathergenr)` loads.
  *Revisit when:* conda-forge ships a fixed r45 `r-waveslim` (or R 4.6)
  Fortran build — then the `r-base` pin can move forward again.

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
