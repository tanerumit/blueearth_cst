# weathergenr bugs

Upstream bugs found in `tanerumit/weathergenr@master` while running
`Snakefile_climate_experiment` on the test config. Captured here so they
can be filed as GitHub issues in the weathergenr repo independent of
this project's milestone tracking.

Cross-reference: project-side workarounds for these bugs are recorded in
`dev/followups.md` under M5 (Workflow 3: climate experiment).

---

## Bug 1 — `write_netcdf` does not propagate `spatial_ref` attributes from `template_path`

**Discovered:** 2026-05-07
**Affected file:** `R/io_netcdf.R` (`write_netcdf`)
**Severity:** High — breaks any downstream use of the output as a template.

**Symptom.** The output netCDF written by `write_netcdf` contains a
`spatial_ref` variable with an *empty* attribute list, even when the
template passed via `template_path` has fully populated attributes
(`x_dim`, `y_dim`, `crs_wkt`, `grid_mapping_name`, etc.). When a
downstream caller uses the output as its own template, every attribute
lookup fails.

**Reproduction.**

1. Open a hydromt-produced netCDF with a populated `spatial_ref`
   variable, e.g.
   ```
   x_dim          = 'longitude'
   y_dim          = 'latitude'
   crs_wkt        = 'GEOGCRS["WGS 84"...'
   grid_mapping_name = 'latitude_longitude'
   ```
2. Use it as `template_path` in a `write_netcdf` call.
3. Inspect the output's `spatial_ref` attributes — observed empty list.

Confirmed via:
```python
from netCDF4 import Dataset
with Dataset("rlz_1_cst_0.nc") as ds:
    print(ds.variables["spatial_ref"].ncattrs())   # []
```

**Suspected cause.** The attribute-copy loop in `write_netcdf` reads
attributes via `nc_in$var[[spatial_ref]]$att`, which may return the
wrong shape or empty data depending on the ncdf4 representation. The
`ncatt_put` calls are wrapped in `try(..., silent = TRUE)`, so any
copy failure is swallowed without warning.

**Suggested fix.** Use `ncdf4::ncatt_get(nc_in, spatial_ref)` (no
attribute name → returns named list of all attributes) instead of
indexing into `$var[[spatial_ref]]$att`. Drop the `silent = TRUE` from
the `try`, or replace `try` with explicit error handling so silent
failures cannot mask a half-copied output.

**Project-side workaround:** in
`src/weathergen/generate_weather.R`, after each `write_netcdf` call,
manually copy `spatial_ref` attributes from the historical input to
the just-written realization file via `ncatt_get` / `ncatt_put`. To
remove when this bug is fixed.

---

## Bug 2 — `write_netcdf`'s missing-attribute check accepts numeric `0`

**Discovered:** 2026-05-07
**Affected file:** `R/io_netcdf.R` (`write_netcdf`)
**Severity:** Medium — turns a clear missing-template-attribute error
into a cryptic indexing error one line later.

**Symptom.** When the template's `spatial_ref` variable is missing the
`x_dim` or `y_dim` attribute, the user sees:
```
Error in nc_in$dim[[x_dim_name]] :
  attempt to select less than one element in get1index <real>
```
…instead of the documented
```
Template spatial_ref must have attributes 'x_dim' and 'y_dim'.
```

**Cause.** The current check is

```r
x_dim_name <- ncdf4::ncatt_get(nc_in, spatial_ref, "x_dim")$value
y_dim_name <- ncdf4::ncatt_get(nc_in, spatial_ref, "y_dim")$value
if (is.null(x_dim_name) || is.null(y_dim_name) || anyNA(c(x_dim_name, y_dim_name))) {
  stop("Template spatial_ref must have attributes 'x_dim' and 'y_dim'.", call. = FALSE)
}
x_vals <- nc_in$dim[[x_dim_name]]$vals
```

When the attribute is missing, `ncatt_get(...)$value` returns the
numeric `0`, not `NULL` or `NA`. So the validation passes, and the
next line evaluates `nc_in$dim[[0]]`, which raises the cryptic
`get1index` error.

**Suggested fix.** Test `hasatt`, not the value:

```r
x_att <- ncdf4::ncatt_get(nc_in, spatial_ref, "x_dim")
y_att <- ncdf4::ncatt_get(nc_in, spatial_ref, "y_dim")
if (!isTRUE(x_att$hasatt) || !isTRUE(y_att$hasatt)) {
  stop("Template spatial_ref must have attributes 'x_dim' and 'y_dim'.", call. = FALSE)
}
x_dim_name <- x_att$value
y_dim_name <- y_att$value
```

This is independent of Bug 1 and worth fixing on its own — even after
Bug 1 is resolved, a malformed third-party template could still
trigger the missing-attribute path, and the error message should be
useful.

---

## Bug 3 — Cryptic error when historical period is below the wavelet minimum

**Discovered:** 2026-05-07
**Affected file:** `R/wavelet_cwt.R`
**Severity:** Medium — error message does not name the cause.

**Symptom.** Running `generate_weather` with a historical period
shorter than 16 years yields:
```
Error: 'series' must have at least 16 observations.
```
The user has no way to tell from the message that:
- The 16-observation constraint applies to the *annual* aggregate
  (one observation per year), not the daily input.
- The constraint comes from a wavelet-decomposition depth assumption
  inside the WARM step.
- The remedy is to extend the historical period or shorten the
  wavelet decomposition.

**Reproduction.** Pass any historical period of fewer than 16 years
to `generate_weather`. Daily input length is irrelevant; only the
number of historical *years* matters.

**Suggested fix.** Replace the bare check with a contextual message:

```r
if (length(series) < 16) {
  stop(
    sprintf(
      "Historical period (%d years) is below weathergenr's wavelet minimum of 16 years. ",
      length(series)
    ),
    "Extend the historical range, or reduce the wavelet decomposition depth.",
    call. = FALSE
  )
}
```

(Or wrap the bare check in a higher-level function and translate the
bare error there; either way, surface the user-meaningful framing.)

---

## When to file these upstream

After M1 ships and the workarounds in this repo are stable. Filing
earlier risks a weathergenr release that breaks the workarounds in
unexpected ways. After M1, snapshot the workarounds to a tag, then
file the issues with reproductions linked to that tag.
