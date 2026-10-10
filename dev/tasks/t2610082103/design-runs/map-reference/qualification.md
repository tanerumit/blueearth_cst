# Map reference implementation qualification — packet 0

Read-only source qualification against approved design-v2, SHA-256
`4e3175e4b79e0856bbd5c4705b7e81e5a2c6aa9b9602462dd49c5a87ee26f278`.
Source candidate: `22fbe441`, session-1. No source, Git or workflow changes. No installs or raster loads.

## Result

Current rapid inputs qualify for concrete local PET/orography dependencies. No G1 interface blocker for
ERA5's shipped NetCDF descriptor. P-drive reads require sandbox escalation; ordinary sandbox catalog
construction incorrectly presents denied roots as absent. Escalated qualification succeeds.
Environment version/build checks below pass for the relevant active Conda packages. This is qualification,
not proof that annual fields or paired workflow products match; baseline capture and implementation remain.

## Concrete consumed inputs

Rapid project catalogs, in precedence order: `config/catalogs/deltares_data_pdrive.yml`, then
`config/catalogs/deltares_era5_daily_zarr.yml`. Sources are selected-first `era5`, `chirps`, 2000–2016.
The second catalog replaces ERA5 climate, not `era5_orography`.

Existing files under `test_case/test_rapid/data/climate/historical/`:

| Store-relative path | Exists | Bytes |
|---|---|---|
| `era5_20000101_20161231/extract_historical.nc` | yes | 1,931,250 |
| `era5_20000101_20161231/basin_cells.csv` | yes | 41 |
| `chirps_20000101_20161231/extract_historical.nc` | yes | 2,439,004 |
| `chirps_20000101_20161231/basin_cells.csv` | yes | 508 |
| `chirps_20000101_20161231/orography.nc` | yes | 18,877 |

Actual ERA5 source PET DEM: `P:/wflow_global/hydromt/meteo/era5/meta/era5_orography_2018.nc`, exists,
2,086,436 bytes. This concrete path belongs in executable inputs; semantic identity uses logical role
`era5_orography`, its root-relative URI `meteo/era5/meta/era5_orography_2018.nc`, and streamed byte SHA-256.
Its absolute root must not enter identity. Size above is inventory evidence, never a hash substitute.

`load_source_orography()` reads the declared CHIRPS sidecar with Xarray, or constructs HydroMT DataCatalog
and reads `era5_orography` using raw extraction bbox, buffer 2 and `elevtn`. It strips nonspatial coordinates
and uses the existing average reprojection. Source PET delegates to `shared/climate_parity.py` and HydroMT
meteo, passing the same DEM on both branches. No new loading or reprojection algorithm is required.
Current extra CHIRPS preparation has no genuine temperature and consumes no DEM for source PET. Preserve
declared optional sidecars and raw auxiliary arrays rather than deleting them.

## Qualified descriptor interface

HydroMT 1.3.1:

1. Instantiate `DataCatalog(data_libs=ordered_catalogs)` and `get_source("era5_orography")`.
2. Obtain `source.full_uri`; this correctly combines HydroMT's selected catalog root and declared URI.
3. Call `source.uri_resolver.resolve(source.full_uri, variables=["z"], metadata=source.metadata)`.
   This returned the single concrete P-drive file above, without calling the driver or loading raster data.
4. Declare that exact local regular file on both producer specs and adapter validation; hash its bytes.

Installed `RasterDatasetSource.read_data()` performs adapter variable translation before resolution;
`elevtn` becomes `z`. It passes metadata, mask, optional source time range and zoom into the resolver.
For this static URI, no placeholders/overview/tile selection exist, so those absent optional arguments
do not alter the resolved file list. The descriptor uses `convention` URI resolver and `raster_xarray`
driver. Adapter rename is `{z: elevtn}` and multiplier is `0.10197162129779283`.
The resolver expands URIs and filesystem globs. The driver opens the resolved NetCDF with
`xr.open_mfdataset`; its mask is unused at driver level and clipping occurs in the adapter. Dependency
resolution can therefore avoid opening the whole global raster, while ordinary preparation stays intact.

Do not generalize the qualification to every possible HydroMT descriptor. If another source uses a remote
URI, Zarr directory, VRT with transitive tiles, custom resolver, opaque preprocessor or unsupported driver,
reject qualification with a concrete source/driver reason until its consumed local file closure is known.
`source.model_dump()` omits its root; hashing serialized descriptor alone cannot establish consumed bytes.

## Local preparation code closure

The design's seed list misses these reachable local dependencies: `climate_analysis/climate_figures.py`
(`carries_temp` calls `source_climate_vars`), `shared/snake_utils.py` (`PRECIP_ONLY_SOURCES`, grid logging),
and `shared/variable_registry.py` (`CLIMATE_VARS` controls genuine variable membership).
Module import dependencies add `climate_analysis/figure_naming.py`, `shared/plot_style.py`,
`shared/advanced_settings.py`, `shared/run_log_core.py`, `shared/wf3_science.py`, and
`plotting/fundamentals.py` (currently imported by `diagnostic_maps.py`). Include these conservatively when
hashing whole modules, despite some being nonnumerical imports. No `dev/` import is needed.

Explicit local closure, paths relative to `blueearth_cst/`:

```text
climate_analysis/source_map_fields.py                       # new preparation owner
climate_analysis/diagnostic_maps.py
climate_analysis/diagnostics.py
climate_analysis/diagnostic_tables.py
climate_analysis/diagnostic_settings.py
climate_analysis/plot_climate_source.py
climate_analysis/climate_figures.py
climate_analysis/figure_naming.py
shared/climate_parity.py
shared/grid_cells.py
shared/map_reference.py                                    # new identity/dependency owner
shared/snake_utils.py
shared/variable_registry.py
shared/advanced_settings.py
shared/run_log_core.py
shared/wf3_science.py
shared/plot_style.py
plotting/fundamentals.py
__init__.py
climate_analysis/__init__.py
shared/__init__.py
plotting/__init__.py
```

Existing package initializers are empty except plotting's docstring. Include their bytes so future import
behavior cannot change unnoticed. Preparation call closure does not include unused figure functions'
deferred artist imports or temporal-table compute paths. Recheck imports after the source extraction;
adding any local preparation import adds its transitive module dependencies to the explicit list.
Reference identity additionally includes new producer/resolver and portable scale/frame modules.

## Loaded environment and lock qualification

Probe interpreter is the session Pixi default Python 3.12.13. Relevant installed distribution versions:
HydroMT 1.3.1, NumPy 2.4.6, Pandas 3.0.3, Xarray 2026.4.0, SciPy 1.18.0, Rasterio 1.5.0,
PyProj 3.7.2, Dask 2026.3.0, netCDF4 1.7.4, Matplotlib 3.11.0, PyYAML 6.0.3,
Shapely 2.1.2, GeoPandas 1.1.3. h5netcdf is absent, and must not be made a mandatory package check.

`pixi.lock` is schema version 7: `environments.default.packages.win-64` holds URL references; top-level
`packages` holds records keyed by `conda`/`pypi` URL, not universally explicit name/version keys. Conda
name/version/build are in archive filenames; installed metadata is under interpreter-prefix `conda-meta`.
The probe joined active-platform URL references to top-level records and compared relevant installed
Conda name/version/build, including `dask-core`, `geopandas-base` and `matplotlib-base`. All matched.
Do not mistake distribution name `netCDF4` for Conda record `netcdf4`, or metapackages for loaded modules.
`Manifest.toml` declares Julia 1.11.7 and format 2.0. Include its byte digest as approved, but Julia does not
execute source PET/annual preparation, so a loaded Julia version check is not justified here.

Implementation recommendation: canonical identity contains both approved lock byte digests, active
platform/environment and actual loaded numerical/geospatial/backend versions, qualified against active
lock package records. Runtime implementations must inspect loaded module versions as well as distribution
metadata; this probe establishes installed metadata/Conda consistency and imported HydroMT location only.
Normalize identifiers and use an explicit package list. Include GDAL/PROJ backend identities as exposed by
Rasterio/PyProj if qualifying binary runtime, with their locked Conda records. Never include environment
prefix, sys.executable or installed absolute module paths in semantic identity. Hash the complete lock
bytes; do not require Linux packages to be installed on Windows.

## Evidence and limits

Final successful command, with read-only P-drive escalation:
`pixi run python -u .tmp/scratchpad/shared-rendering/map-reference/qualify-inputs.py`
redirected to `qualify-inputs-final.log`; exit 0. The log contains concrete descriptor, installed resolver,
source and driver methods, resolved URI, installed versions and relevant active-lock build matches.
`qualify-inputs-elevated.log` is an earlier descriptor success interrupted by absent optional h5netcdf;
`qualify-inputs.log` retains sandbox denial diagnostics. Final script handles that optional absence.
No tests, full workflows, raster loads, installation or network research ran. Baseline capture, scientific
equality, hashing costs, actual loaded-module versions and producer/adapter stale rejection remain for
implementation acceptance. Logs/probe are retained as packet evidence for root integration.
