# Migration: rule 1.11 figure names

Task `t2610061951`, 2026-10-06. Rule 1.11 (`plot_basin_map`) writes its figures to
`data/spatial/plots/` under `<variable>_basin` names. No config key changes; no numeric output changes.

| Old file | New file |
|---|---|
| `basin_area.png` | `elevation_basin.png` |
| `subbasin_delineation.png` | `subbasins.png` |
| `land_cover.png` | `land_cover_basin.png` |
| `leaf_area_index_annual_mean.png` | `lai_clim_basin.png` |
| `soil_clay_topsoil.png` | `soil_clay_basin.png` |
| `soil_silt_topsoil.png` | `soil_silt_basin.png` |
| `soil_sand_topsoil.png` | `soil_sand_basin.png` |
| `soil_organic_carbon_topsoil.png` | `soil_organic_carbon_basin.png` |
| `soil_ph_topsoil.png` | `soil_ph_basin.png` |
| `soil_bulk_density_topsoil.png` | `soil_bulk_density_basin.png` |
| `soil_depth_to_bedrock.png` | `soil_depth_to_bedrock_basin.png` |

Grammar: `<variable>_<spatial_scope>`, a shortened form of the WF0 rule
(`dev/reference/wf0-figure-filename-rule.md`) with the dataset and plot-context tokens dropped: every
rule 1.11 figure has one source and is a map. `lai_clim_basin` keeps `clim` because the layer is a
12-month mean. Soil stems carry no depth token; only the surface slice (`sl1`) is registered, and a
deeper slice would need its depth in the stem.

## Machinery updated

- `blueearth_cst/shared/plot_spatial_maps.py` — `SPATIAL_MAP_FIGURES` stems, `LEGEND_TITLES` keys.
- `blueearth_cst/shared/plot_map.py` — `elevation_basin.png` in both writers.
- `build_model.smk` — rule 1.11 declared outputs.
- `dev/scripts/check_baseline.py` — the `build_model` png target. `dev/baseline/manifest.json`
  records no rule 1.11 figure, so no manifest entry moves.
- `dev/scripts/preview_basin_map.py`, `dev/scripts/semantic_tree_diff.py`, `dev/scripts/stage_data.yml`.
- Tests naming the files; `dev/reference/workflows/{rule-index,model_creation}.md`;
  `docs/notebooks/Model building.ipynb`.

Kept verbatim as history: the dated observations in `blueearth_cst/shared/gauges.py`,
`dev/scripts/check_baseline.py` and `tests/test_check_baseline_provenance.py`.

## Existing projects

A project built before this change keeps its old files; the next rule 1.11 run writes the new names
beside them. Delete the old `data/spatial/plots/*.png` names above by hand if they are not wanted.
