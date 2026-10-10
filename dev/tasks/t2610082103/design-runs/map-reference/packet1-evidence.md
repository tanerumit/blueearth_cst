# Packet 1 — unused portable artist and source preparation

Owned writes only:
`blueearth_cst/plotting/prepared_maps.py`,
`blueearth_cst/climate_analysis/source_map_fields.py` and named scratch probes/evidence.
`diagnostic_maps.py` and all active callers remain unchanged.

## Interfaces

`MapFrame(extent, longitude_ticks, latitude_ticks, aspect)` retains common display settings.
`MapScale(units, boundaries, ticks, colors, under_color, over_color, missing_color, status)` supports
`degC`/`mm/year` and status `available`/`unavailable`. Available ticks equal all boundaries; unavailable
scales contain no colors, boundaries or numerical ticks. Colors are already resolved by the producer.
`RasterMap(values, longitude_edges, latitude_edges, inside=None, cell_edges=True)` requires a nonempty
latitude × longitude numeric array, regular monotonic cell edges and an exactly matching boolean mask.
`draw_raster_map(raster, frame, scale, overlays) -> matplotlib.figure.Figure` takes loaded feature lists
keyed by `subbasins`, `rivers`, `basins`, `locations`. No filesystem IO/backend/style selection occurs.
Adapters own their existing style context and prepend existing variable names to the units-only colorbar
title when needed. Endpoint normalization keeps equality with the final boundary in the final class;
strict excess uses explicit extension colors. Available colorbars always show rectangular extensions.

`SourceMapSpec(source, climate_nc, basin_cells, catalogs, requested_window, orography_nc=None,
orography_inputs=())` uses Paths and an ordered tuple of catalog Paths. `requested_window` is a normalized
pair of date strings for later identity construction; it does not change the extraction period.
`orography_nc` is the existing optional sidecar; `orography_inputs` is the concrete catalog-backed file
dependency list. Actual DEM loading continues through HydroMT's existing catalog adapter.
`prepare_source_map_fields(spec, m0, completeness: Mapping[str,int]) -> PreparedSourceMapFields`
returns eager `fields: xr.Dataset` and the current `lineage: dict[str,Any]`. Completeness contains the
two existing `max_missing_days_month`/`max_missing_days_year` keys. Calls existing `daily_series`,
temperature-role gate, `load_source_orography`, `source_grid_climate` and `annual_fields` unchanged.
It preserves existing reporting-year/period attrs, raw precipitation/temperature policy, derived source
PET and CHIRPS raw auxiliary arrays. Packet 2 must attach real preparation identity/payload sealing;
this unused intermediate interface has no identity placeholders or dummy hashes.

## Focused verification

Budget: rapid with numerical behavior guarded by unchanged preparation methods and later exact science
comparisons. No permanent plotting tests, repository-wide lint, suite or workflows.

Commands actually run:

```text
pixi run ruff format blueearth_cst/plotting/prepared_maps.py blueearth_cst/climate_analysis/source_map_fields.py
pixi run python .tmp/scratchpad/shared-rendering/map-reference/packet1-probe.py
pixi run ruff check blueearth_cst/plotting/prepared_maps.py blueearth_cst/climate_analysis/source_map_fields.py
pixi run ruff format --check blueearth_cst/plotting/prepared_maps.py blueearth_cst/climate_analysis/source_map_fields.py
```

All exit 0. Probe output retained in `packet1-probe.log`:
inert backend and NumPy/Matplotlib-only third-party import closure; supplied aspect; strict under/over
and every boundary including adjacent representable value above the final endpoint; masked normalization;
all missing with common colorbar; unavailable reference with finite hatch/missing gray/outside white and
no colorbar; single-class scale; descending one-cell edge arrays; shape/regularity/mask refusal before
creating figures; values and edges unchanged. Scope does not claim independent science validation.

Opened `packet1-boundaries.png` and `packet1-unscaled.png`: discrete colors and both rectangular extensions
visible; hatched finite cell, gray missing cell and white outside cell distinguish correctly; coordinate
ticks and labels render. These deliberately synthetic previews use default Matplotlib style to keep the
core import probe independent; final workflow renders must use existing CST style.

## Remaining acceptance

Identity integration, configuration validation and geographic frame/scale construction belong to packet 2.
Common frame classes/ticks/aspect are supplied, never computed from the drawn field. Core only checks a
positive finite aspect; producer must construct/reject singular geographic frames per the approved policy.
Scientific parity against retained/fresh real fields, final workflow visual renders and numerical known
answers remain later gates. The legacy artist remains intentionally present until consumer migration.
