# Followups

Issues surfaced during pre-M1 cleanup that belong to later milestones.
Per the roadmap's "no milestone touches the next milestone's territory" rule,
captured here and resolved in passing when the relevant milestone starts.

Convention: one bullet per item. Keep the diagnosis date and reproducible
context so future-you can confirm the issue still applies before fixing.

---

## M3 — Workflow 1: model builder

- **Redo M1 warnings triage exhaustively.** M1 closed with an incomplete
  triage (`dev/m01_warnings.md`) because most rules don't write stderr
  to disk. Once M3's cross-cutting deliverable adds `log:` directives
  to every non-trivial rule across all three Snakefiles, re-run all
  three workflows, sweep the captured logs, and fix any bucket-2
  (config/data-catalog) or bucket-3 (our-code) warnings that surface.
  Update `dev/m01_warnings.md` (or supersede it with an `m03_*` doc).

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

## M5 — Workflow 3: climate experiment

- **`extract_climate_grid` ignores the `historical:` config and hardcodes
  the date range.** Pre-M5 unblocking edit on 2026-05-07 changed the
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

  *Also touches the M3 followup:* this is the same shape as the
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
  in M5 deliverables if M5 is also touching the R layer; otherwise track as
  a separate weathergenr issue.
