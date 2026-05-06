# Environment setup notes

Notes on local fixes applied to the `cst` conda environment on Windows. These
are workarounds for upstream packaging issues, not project-specific bugs.

## 2026-05-05 — Windows env repair

### Symptom 1: Graphviz `dot` warnings, fonts fall back to Times

Running `snakemake --dag | dot -Tpng` printed:

```
Warning: Could not load "...\envs\cst\Library\bin\gvplugin_pango.dll" -
It was found, so perhaps one of its dependents was not.  Try ldd.
Warning: no hard-coded metrics for 'sans'.  Falling back to 'Times' metrics
```

The PNG rendered, but with Times instead of `sans`.

### Root cause

Two name-mismatch bugs in conda-forge's Windows graphviz/glib build:

- `gobject-2.0-0.dll` imports `ffi.dll`, but conda-forge libffi 3.5 ships
  `ffi-8.dll`.
- `gvplugin_pango.dll` imports `cairo.dll`, but conda-forge cairo ships
  `cairo-2.dll`.

Diagnosed by walking the PE import table with `pefile`.

### Fix

Created an activation script that recreates the missing alias DLLs every time
the env is activated (so reinstalls of libffi/cairo/graphviz can't silently
break things again):

```
C:\Users\taner\AppData\Local\miniconda3\envs\cst\etc\conda\activate.d\graphviz_dll_shims.bat
```

```bat
@echo off
set "BIN=%CONDA_PREFIX%\Library\bin"
if not exist "%BIN%\ffi.dll"   if exist "%BIN%\ffi-8.dll"   copy /Y "%BIN%\ffi-8.dll"   "%BIN%\ffi.dll"   >nul
if not exist "%BIN%\cairo.dll" if exist "%BIN%\cairo-2.dll" copy /Y "%BIN%\cairo-2.dll" "%BIN%\cairo.dll" >nul
```

The script lives **inside the env**, so it does not survive
`conda env remove` / re-create. After every fresh env build on Windows,
re-create this file.

To verify after a fresh `conda activate cst`:

```powershell
dir $env:CONDA_PREFIX\Library\bin\ffi.dll, $env:CONDA_PREFIX\Library\bin\cairo.dll
```

### Symptom 2: `np.unicode_` AttributeError when running hydromt

```
AttributeError: `np.unicode_` was removed in the NumPy 2.0 release.
Use `np.str_` instead.
```

Triggered by `import xarray` inside hydromt.

### Root cause

The env had `numpy 2.4.3` together with `xarray 0.20.1` (an extremely old
build pulled from anaconda main, not conda-forge). The `xarray<=2024.3.0`
pin in `environment.yml` was satisfied by the ancient main-channel build
because channel priority was not strict and `defaults` was implicitly
included.

### Fix

`environment.yml` updated:

- Added `nodefaults` channel and `channel_priority: strict`.
- Pinned `numpy<2` (xarray 2024.3.0 requires numpy < 2).
- Tightened xarray pin to `>=2023.1,<=2024.3.0` so a working version is
  selected.

In-place repair of the existing env:

```
conda install -n cst -c conda-forge --override-channels "numpy<2" "xarray>=2023.1,<=2024.3.0"
```

Result: `numpy 1.26.4`, `xarray 2024.3.0` (conda-forge build).

### Symptom 4: zarr write errors when staging ERA5 (`Got None instead`, `BytesBytesCodec`)

`xarray.to_zarr` failed with codec / chunk errors (`Expected a BytesBytesCodec`,
`Expected an integer ... Got None instead`) when writing the staged ERA5 zarr
subset.

### Root cause

`xarray 2024.3.0` (March 2024) predates `zarr 3.0` (Nov 2024). The env had
`zarr 3.1.x` installed, and xarray's older zarr backend cannot drive v3
encoding paths cleanly — the source's v2 Blosc codec is unreadable by v3,
and clearing encoding leaves no valid v3 chunk hint.

### Fix

Pin `zarr<3` in `environment.yml` and reinstall:

```
conda install -n cst -c conda-forge --override-channels "zarr<3"
```

Result: `zarr 2.18.7`. The staging script then writes ERA5 cleanly.

### Symptom 3: `RuntimeError: Invalid argument` in netCDF4 during `add_forcing`

Reading ERA5 netCDF/HDF5 files from `p:\wflow_global\hydromt\meteo\...` while
writing `inmaps_historical.nc` raised:

```
File "...\xarray\backends\netCDF4_.py", line 114, in _getitem
    array = getitem(original_array, key)
RuntimeError: Invalid argument
```

### Root cause

HDF5's default Windows behaviour is to take an `flock`-style file lock on the
source file. The Deltares `P:` SMB share rejects that lock call, and netCDF4
fails the read mid-operation.

### Fix

Set `HDF5_USE_FILE_LOCKING=FALSE` for the env. Added to the same activation
script so it follows every shell that activates `cst`:

```bat
set "HDF5_USE_FILE_LOCKING=FALSE"
```

(Same recovery rule applies: re-create the activation script after a fresh
env build.)

### Symptom 5: `Invalid value kinematic-wave in the TOML` from Wflow.jl

`run_wflow` failed with errors like

```
ArgumentError: Invalid value kinematic-wave in the TOML,
  must be one of ("kinematic_wave", "local_inertial").
```

plus warnings that fields `time_units`, `starttime`, `glacier`, `reinit`,
`kw_river_tstep`, `kin_wave_iteration`, `masswasting`, `lakes`, ... are
"not recognized as a valid field of the [input] section".

### Root cause

`hydromt_wflow 0.5.0` (pinned in `environment.yml` as `<0.6`) emits the
pre-1.0 Wflow.jl TOML format. The locally installed Wflow.jl had upgraded
to 1.0.x, which renamed everything to snake_case and rejects unknown
fields strictly.

### Fix

Pin Wflow.jl to 0.8.1 in the user's Julia environment:

```
julia -e 'using Pkg; Pkg.add(name="Wflow", version="0.8.1")'
```

This matches what `hydromt_wflow 0.5.0` was developed and tested against.
Re-run snakemake; the wflow run step should clear without TOML rewrites.

A future migration option is to upgrade `hydromt_wflow` to 1.x and adopt
Wflow.jl 1.x; that would touch the build configs and likely the Snakefile
script signatures, so it is out of scope here.

## Local data staging (P-drive bypass)

To eliminate the SMB read failures entirely (and speed up runs), stage a
bbox-clipped subset of the Deltares data onto the local SSD.

### What gets staged

Each spatial dataset the model_creation workflow reads is clipped to the bbox
and mirrored under a local root. Default bbox is
`[8.5, -0.5, 11.0, 1.5]` (~1.5° pad around the test point at `(9.666, 0.4476)`).
Default destination is `C:\data\wflow_global\hydromt`.

Datasets covered:

| Dataset                         | Method                  |
|---------------------------------|-------------------------|
| `topography/merit_hydro_ihu/30sec/*.tif` | rasterio window read |
| `topography/merit_hydro/basin_index.gpkg` | geopandas bbox filter |
| `hydrography/rivers_lin2019/rivers_ge30m.gpkg` | geopandas bbox filter |
| `landuse/vito/ProbaV_LC100_*.tif` | rasterio window read |
| `landuse/modis/MODIS_MCD15A3H_LAI/*.tif` | rasterio window read |
| `soil/soilgrids_v1.0/*.tif` | rasterio window read |
| `meteo/era5_daily.zarr` | xarray.sel + to_zarr |
| `meteo/era5/meta/era5_orography_2018.nc` | xarray.sel + to_netcdf |

### Run it

The staging script reads its inputs (source root, destination root, bbox,
list of datasets) from `dev/scripts/stage_data.yml`. Edit that file to add or
remove datasets, change paths, or shift the bbox.

```powershell
conda activate cst
python dev/scripts/stage_data.py                    # uses dev/scripts/stage_data.yml
python dev/scripts/stage_data.py --config <path>    # alternate config
python dev/scripts/stage_data.py --bbox 8 -1 12 2   # one-off bbox override
```

Supported dataset `type` values:

| type          | clipped via                                   |
|---------------|-----------------------------------------------|
| `raster`      | `rasterio` window read on a single GeoTIFF    |
| `raster_glob` | iterate `pattern` (default `*.tif`) in a dir  |
| `vector`      | `geopandas.read_file(..., bbox=...)`          |
| `zarr`        | `xarray.open_zarr` + `sel` + `to_zarr`        |
| `netcdf`      | `xarray.open_dataset` + `sel` + `to_netcdf`   |

The script is idempotent — it skips files that already exist at the
destination. On failure it removes the partial output so the next run can
retry cleanly, and continues past errors so one bad dataset does not block
the rest.

### Switch the workflow to the local catalog

Use `config/deltares_data_local.yml` (a copy of `deltares_data.yml` with
`root:` pointing at `C:/data/wflow_global/hydromt`) by either:

- pointing the snake config's data catalog key at it, or
- passing `--config data_catalog=config/deltares_data_local.yml` to snakemake
  if your Snakefile reads it from `config`.

### Limits

The script only stages spatial datasets the **model_creation** workflow
touches. CMIP6 data used by `Snakefile_climate_projections` /
`Snakefile_climate_experiment` lives in `cmip6_data.yml` and is not yet
mirrored — extend the script when you need those flows.

## Recovering from a fresh env build

After `conda env create -f environment.yml` on Windows:

1. Recreate `etc/conda/activate.d/graphviz_dll_shims.bat` (see above).
2. Deactivate and reactivate the env so the script runs once.
3. Sanity-check: `python -c "import xarray, numpy; print(xarray.__version__, numpy.__version__)"`
   should report `2024.3.0` and `1.26.x`.
