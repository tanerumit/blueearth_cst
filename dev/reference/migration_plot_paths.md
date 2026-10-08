# Plot output path migration

WF0 and WF2 now use `plots/` for generated graphics. Generated filenames and directories use
lowercase snake_case. This changes output paths and manifest keys, not climate calculations.

## Directory and record mapping

Paths below are relative to the owning historical store/comparison directory or projection ensemble.

| Workflow | Previous | Current |
| --- | --- | --- |
| WF0 | `figures/` | `plots/` |
| WF0 | `_engine/figure_captions.json` | `plots/_engine/figure_captions.json` |
| WF2 | `plots/full-period/` | `plots/full_period/` |
| WF2 | `plots/period-<start>-<end>/` | `plots/period_<start>_<end>/` |
| WF2 | `analysis/analysis_record.json` | `analysis/_engine/analysis_record.json` |

The configured-horizon helper also emits `<sanitized_name>_<start>_<end>` and sanitizes names with
underscores. The active diagnostic suite uses resolved `period_<start>_<end>` folders rather than these
configured-horizon labels; window IDs in records retain their `start-end` identity spelling.

Optional captioned copies mirror the ordinary directory and filename changes under `plots/captioned/`.
WF0 filenames are unchanged. WF0 diagnostics metadata remains at `_engine/diagnostics.json`.

## WF2 filename mapping

Each pair lists the previous filename followed by its replacement. The authoritative mapping lives
in `blueearth_cst/projections/projection_figures.py` (`FIGURE_FILENAMES`). Internal logical product
keys retain their previous spelling; only canonical filenames are accepted by public render dispatch.

- `availability.png` →
  `cmip6_ensemble_coverage_basin_avg.png`
- `trajectory-temperature.png` →
  `cmip6_temp_annual_anomaly_ts_basin_avg.png`
- `trajectory-precipitation.png` →
  `cmip6_precip_annual_anomaly_ts_basin_avg.png`
- `annual-temperature.png` →
  `cmip6_temp_annual_overview_basin_avg.png`
- `annual-precipitation.png` →
  `cmip6_precip_annual_overview_basin_avg.png`
- `change-temperature.png` →
  `cmip6_temp_annual_seasonal_change_box_basin_avg.png`
- `change-precipitation-pct.png` →
  `cmip6_precip_annual_seasonal_change_pct_box_basin_avg.png`
- `change-precipitation-abs.png` →
  `cmip6_precip_annual_seasonal_change_abs_box_basin_avg.png`
- `seasonal-cycle-temperature.png` →
  `cmip6_temp_monthly_clim_basin_avg.png`
- `seasonal-cycle-precipitation.png` →
  `cmip6_precip_monthly_clim_basin_avg.png`
- `monthly-change-temperature.png` →
  `cmip6_temp_monthly_change_box_basin_avg.png`
- `monthly-change-precipitation.png` →
  `cmip6_precip_monthly_change_pct_box_basin_avg.png`
- `variability-ratio-temperature-sd.png` →
  `cmip6_temp_annual_seasonal_sd_ratio_box_basin_avg.png`
- `variability-ratio-precipitation-sd.png` →
  `cmip6_precip_annual_seasonal_sd_ratio_box_basin_avg.png`
- `variability-ratio-precipitation-cv.png` →
  `cmip6_precip_annual_seasonal_cv_ratio_box_basin_avg.png`
- `variability-member-ratios.png` →
  `cmip6_precip_temp_annual_member_ratio_box_basin_avg.png`
- `change-factor-cloud.png` →
  `cmip6_precip_temp_annual_change_cloud_basin_avg.png`
- `sign-agreement.png` →
  `cmip6_precip_temp_annual_monthly_sign_agreement_basin_avg.png`
- `change-factor-cloud-combined.png` →
  `cmip6_precip_temp_annual_multi_period_change_cloud_basin_avg.png`

## Existing runs and consumers

Existing outputs are neither renamed nor deleted automatically. Regenerate WF0/WF2 plots and
WF2 analysis tables/record into the canonical paths before selecting any obsolete outputs for cleanup.
Update downstream links and scripts using the mapping above. Old figure manifests must not be copied
unchanged because their keys and optional captioned paths describe the previous layout.

Workflow declarations, availability tables, render dispatch, captions, baseline figure targets,
tree-inventory expectations and live documentation have been updated together. Historical sealed
records and the stale numerical baseline manifest remain unchanged.

## JSON placement

Machine plot manifests belong in `plots/_engine/`; internal analysis records in `analysis/_engine/`.
Readable captions remain at `plots/figure_captions.md`. JSON is a format, not a placement rule:
user-facing data and provenance deliverables remain with their owning data products, including
`summary/provenance.json`. Engine records unrelated to plotting retain their existing owners.

## Verification status

Tests, lint, DAG checks and integration gates are deferred until the plotting session concludes,
as requested. The final checks must cover WF0 source/comparison and optional subbasin paths, WF2
availability-to-output mappings, caption manifests, and affected workflow declarations.

A change-cloud figure was rendered through canonical filename dispatch from the retained Gabon lab
model-change table. Its PNG and caption manifest were written under the new `plots/period_2036_2065/`
and `plots/_engine/` paths in session scratch and the exported figure was visually inspected.
