# CMIP6 source readability

Last updated: 2026-10-20

Use this reference when changing WF2 fetches or diagnosing rejected source combinations.
The generated `config/catalogs/cmip6_store_index.json` is the current source inventory.
Historical crawl counts and staging outcomes are retained separately under R08.

## 1. Grid geometry

HydroMT's regular raster accessor requires uniformly spaced coordinates. Ordered one-dimensional
latitude/longitude axes can still be readable when their spacing is irregular.
`blueearth_cst/projections/fetch_gcm_raw.py::fetch_raw_slice` handles the recognized regular-grid
failure by reopening the same source without a bbox and selecting the bbox in index space.

Keep rename, unit conversion, CRS and nodata handling with HydroMT. The fallback is not a general
unstructured-mesh reader, and successful coordinate probing does not establish successful data staging.
Time coverage and missing data remain separate admission conditions.

## 2. Published-version multiplicity

`blueearth_cst/projections/series_identity.py::pinned_uri` owns source-version selection.
Select the newest indexed path per required variable only when those choices identify the same physical
grid/version location. Refuse competing grid labels or differing newest versions across variables;
do not silently combine published revisions or choose a regridding by lexical ordering.

Version pinning is per member because members can have different publication histories.
Keep the selection in the store-index consumer rather than inventing one catalog-wide version.
The DAG preflight and fetch path must use the same selection policy.

## Verification and evidence

`dev/scripts/probe_cmip6_grids.py` examines coordinate geometry. `dev/scripts/stage_cmip6.py` exercises
readability through actual staging. `tests/test_series_identity.py` owns version-selection checks.
Inspect fetched coverage and diagnostics before interpreting absent ensemble members scientifically.

[Readability measurements](../records/milestones/r08/cmip6-readability-measurements.md) and
[the historical inventory](../records/milestones/r08/wf2-cmip6-store-inventory.md) describe particular
crawls and verification runs. Their model counts are not current acceptance limits or availability claims.
