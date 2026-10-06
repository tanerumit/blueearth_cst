# WF0 integration — proposed project tree

Status: Gate 1 proposal, 2026-10-06. Implementation has not started.
Only changing folders and files are shown. The governing contract is
[design.md](design.md), decisions D1–D6.

This is the task's maintained layout view. Update it alongside every design or
implementation revision affecting paths, names, formats, counts or conditional
outputs; keep proposed and implemented paths explicitly distinguished.

`[new]` and `[edit]` below describe the proposed implementation. `[present]`
identifies the design artifacts already created on the task branch. Proposed
test filenames are implementation planning names, not existing files.

## Toolbox repository

```text
blueearth_cst/                         repository root
├── analyze_climate.smk                [edit] replace 0.04/0.05; add 0.04b and canonical targets
├── blueearth_cst/
│   └── climate_analysis/
│       ├── figure_naming.py           [edit] register new controlled plot contexts
│       ├── diagnostics.py             [new] pure diagnostic calculations
│       ├── diagnostic_settings.py     [new] WF0 settings validation and defaults
│       ├── diagnostic_outputs.py      [new] shared declaration/writer output inventory
│       ├── diagnostic_tables.py       [new] basin series, period calculations, table I/O
│       ├── diagnostic_figures.py      [new] render from plot-ready tables
│       ├── diagnostic_maps.py         [new] native-grid map fields and lab-derived map layout
│       ├── diagnostic_captions.py     [new] reusable scientific captions
│       ├── compute_climate_diagnostics.py  [new] rule 0.04 adapter
│       ├── plot_climate_diagnostics.py     [new] rule 0.04b adapter
│       └── compare_climate_diagnostics.py  [new] rule 0.05 adapter
├── test_case/
│   └── project_config_rapid_analyze_climate.yml
│                                      [edit] diagnostics settings; subbasin_figures defaults to false
├── tests/
│   ├── test_climate_source_plot_contract.py [edit] canonical WF0 wiring; retain WF1 compatibility
│   ├── test_climate_diagnostic_maps.py [new] map aggregation, support, layout and PET caveat
│   ├── test_figure_naming.py           [edit] new controlled contexts
│   ├── test_climate_diagnostics.py     [new] ported numerical known-answer tests
│   ├── test_climate_diagnostic_tables.py   [new] inputs, periods, units, availability
│   ├── test_climate_diagnostic_figures.py  [new] render/output/caption contracts
│   └── test_climate_diagnostic_rules.py    [new] source/comparison DAG declarations
├── docs/
│   └── site/
│       └── toolbox-reference/
│           └── workflow-analyze-climate.qmd
│                                      [edit] outputs, settings, methods, captions, limits
└── dev/
    ├── reference/
    │   ├── wf0-figure-filename-rule.md [edit] new controlled contexts
    │   └── workflows/
    │       └── rule-index.md          [edit] new letter-suffixed WF0 rules
    └── tasks/
        └── wf0-lab-integration/
            ├── design.md             [present] Gate 1 contract; later approval/results log
            └── project-tree.md       [present] this static tree
```

WF0's legacy source/comparison plot producers are replaced. WF1 retains its
existing shared source producer. Other WF0 seed configs receive the documented
settings where relevant; no additional seed is required.

## Generated project outputs

These files are generated under the user's `project_dir`, outside the toolbox
repository in production. `<store-key>` is resolved from the existing climate
store specification; it is not constructed by the new diagnostic code.

```text
<project_dir>/
└── data/
    └── climate/
        └── historical/
            ├── <store-key>/           one existing store per declared source
            │   └── diagnostics/      [new] source diagnostics root D_s
            │       ├── _engine/      retained machine-readable records
            │       │   ├── diagnostics.json
            │       │   └── figure_captions.json
            │       ├── figure_captions.md
            │       ├── tables/       shared table set detailed below
            │       │   ├── daily_basin.csv    source-only addition to shared set
            │       │   ├── annual_climatology.nc source-only map fields
            │       │   └── subbasins/     optional canonical subbasin tables
            │       └── figures/      source figure set detailed below
            │           ├── subbasins/        optional canonical subbasin PNGs
            │           └── captioned/        optional PNG copies, including subbasins/
            └── comparison/           multisource runs only
                └── diagnostics/      [new] comparison diagnostics root D_c
                    ├── _engine/      retained machine-readable records
                    │   ├── diagnostics.json
                    │   └── figure_captions.json
                    ├── figure_captions.md
                    ├── tables/       shared table set detailed below
                    │   ├── agreement.csv     comparison-only addition
                    │   ├── agreement.md      comparison-only addition
                    │   └── subbasins/     optional canonical subbasin tables
                    └── figures/      comparison figure set detailed below
                        ├── subbasins/        optional canonical subbasin PNGs
                        └── captioned/        optional PNG copies, including subbasins/
```

### Shared table subtree

Both diagnostic roots contain these 17 plot-ready tables. Source tables cover
the source analysis period; comparison tables are recomputed for the comparison
display period. Source roots additionally contain `daily_basin.csv`; comparison
roots additionally contain `agreement.csv` and `agreement.md`.

```text
<diagnostics-root>/
└── tables/
    ├── coverage.csv
    ├── valid_years.csv
    ├── annual_indices.csv
    ├── monthly_values.csv
    ├── precip_climatology.csv
    ├── temp_climatology.csv
    ├── rainfall_timing.csv
    ├── spi.csv
    ├── spi_fit_checks.csv
    ├── drought_events.csv
    ├── dry_spells.csv
    ├── dry_spell_exceedance.csv
    ├── anomaly_acf.csv
    ├── trends.csv
    ├── trend_sensitivity.csv
    ├── pt_anomalies.csv
    └── homogeneity.csv
```

Unavailable table products retain their headers and have reasons in metadata.

### User-facing changes in this revision

- Both JSON records live under each diagnostic root's `_engine/` folder.
  `figure_captions.md` remains at the root as the readable caption and
  interpretation reference. JSON output paths resolve from the diagnostic root.
- New diagnostic figures use PNG only, including optional captioned copies.
  No PDF files are created by the proposed diagnostic rules.
- WF0's old `plots/` figures are retired from workflow declarations and
  targets. Monthly boxes, plain annual series and old comparison lines are
  superseded by the new views. No legacy WF0 plot producer remains active.
- Source climatology maps use the lab native-grid map layout, including
  precipitation, genuine temperature and derived source-grid PET where supported.
  Their four-field basenames remain `annual_clim_map_basin_ext`, under
  `diagnostics/figures/`. Old files are not automatically deleted.
- `subbasin_figures` defaults to `false`. Opt-in produces canonical precipitation
  monthly-band and annual-trend views, and genuine temperature monthly-band
  views, using `subbasin_<id>_avg` under `figures/subbasins/`. Corresponding tables
  live under `tables/subbasins/`; captioned copies use
  `figures/captioned/subbasins/`. No old box/annual_ts plots are revived.
- WF1 retains its existing plotting contracts. Old WF0 plot consumers must use
  the canonical diagnostic paths; old comparison summaries are superseded by
  `tables/agreement.csv` and `tables/agreement.md` with matched-period semantics.
- Proposed contexts are shortened: `monthly_coverage`, `annual_timing`,
  `monthly_anomaly`, `monthly_spi`, `spi_events`, `dry_spell_exceedance`,
  `seasonal_anomaly`, `monthly_spi_fit`, and `annual_trend_sensitivity`.
- The four-field grammar, canonical variables, `comparison` token and
  `basin_avg` scope are retained. Contexts identify the diagnostic; their
  registered definitions, titles and captions specify the visual form. This
  revises the requirement to include plot form in every context for the new
  family and requires a controlled-vocabulary documentation update.
### Figure subtree

Every `.png` entry represents one explicitly declared file. `<dataset>`
is the source ID for a source figure and `comparison` for a multisource figure.
Each optional captioned copy uses the identical basename under `captioned/`.

```text
<diagnostics-root>/
└── figures/
    ├── <dataset>_precip_annual_clim_map_basin_ext.png    source only
    ├── <dataset>_temp_annual_clim_map_basin_ext.png      source only, conditional
    ├── <dataset>_pet_annual_clim_map_basin_ext.png       source only, conditional
    ├── <dataset>_precip_monthly_coverage_basin_avg.png
    ├── <dataset>_precip_monthly_clim_band_basin_avg.png
    ├── <dataset>_temp_monthly_clim_band_basin_avg.png             conditional
    ├── <dataset>_precip_annual_timing_basin_avg.png
    ├── <dataset>_precip_monthly_anomaly_basin_avg.png
    ├── <dataset>_precip_monthly_spi_basin_avg.png
    ├── <dataset>_precip_spi_events_basin_avg.png
    ├── <dataset>_precip_annual_rx1day_ts_basin_avg.png
    ├── <dataset>_precip_annual_rx5day_ts_basin_avg.png
    ├── <dataset>_precip_annual_sdii_ts_basin_avg.png
    ├── <dataset>_precip_annual_wet_days_ts_basin_avg.png
    ├── <dataset>_precip_dry_spell_exceedance_basin_avg.png
    ├── <dataset>_precip_monthly_anomaly_acf_basin_avg.png
    ├── <dataset>_precip_annual_trend_interval_basin_avg.png
    ├── <dataset>_precip_annual_trend_ts_basin_avg.png
    ├── <dataset>_precip_temp_seasonal_anomaly_basin_avg.png conditional
    ├── <dataset>_precip_monthly_spi_fit_basin_avg.png
    ├── <dataset>_precip_annual_trend_sensitivity_basin_avg.png
    ├── subbasins/                    optional canonical temporal views
    └── captioned/                    optional; mirrors the selected basenames above
```

For ERA5 + CHIRPS, the new figure sets are:

| Root | Forms | PNG files | Temperature behavior |
|---|---:|---:|---|
| ERA5 source | 21 | 21 | Own temperature and own P–T |
| CHIRPS source | 17 | 17 | No temperature or own P–T figure |
| Comparison | 17 | 17 | No single-carrier temperature comparison; explicit P–T pairs use ERA5 temperature |
| Total | 55 | 55 | Optional captioned copies add another 55 files |

A single-source run creates only its source diagnostic subtree. Runtime data
insufficiency produces labelled unavailable panels for declared figures.
Ntoum results remain real-data exercised and **not scientifically qualified**.
