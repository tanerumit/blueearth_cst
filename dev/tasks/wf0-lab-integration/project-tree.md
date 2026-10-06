# WF0 integration — proposed project tree

Status: Gate 1 proposal, 2026-10-06. Implementation has not started.
Only changing folders and files are shown. The governing contract is
[design.md](design.md), decisions D1–D6.

`[new]` and `[edit]` below describe the proposed implementation. `[present]`
identifies the design artifacts already created on the task branch. Proposed
test filenames are implementation planning names, not existing files.

## Toolbox repository

```text
blueearth_cst/                         repository root
├── analyze_climate.smk                [edit] add 0.04b, 0.04c, 0.05b and terminal outputs
├── blueearth_cst/
│   └── climate_analysis/
│       ├── figure_naming.py           [edit] register new controlled plot contexts
│       ├── diagnostics.py             [new] pure diagnostic calculations
│       ├── diagnostic_settings.py     [new] WF0 settings validation and defaults
│       ├── diagnostic_outputs.py      [new] shared declaration/writer output inventory
│       ├── diagnostic_tables.py       [new] basin series, period calculations, table I/O
│       ├── diagnostic_figures.py      [new] render from plot-ready tables
│       ├── diagnostic_captions.py     [new] reusable scientific captions
│       ├── compute_climate_diagnostics.py  [new] rule 0.04b adapter
│       ├── plot_climate_diagnostics.py     [new] rule 0.04c adapter
│       └── compare_climate_diagnostics.py  [new] rule 0.05b adapter
├── test_case/
│   └── project_config_rapid_analyze_climate.yml
│                                      [edit] optional commented diagnostics settings
├── tests/
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

Existing source/comparison figure producers and their outputs retain their
contracts. Other WF0 seed configs may receive the same optional commented
settings if relevant; no additional seed is required by this proposal.

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
            │       ├── diagnostics.json
            │       ├── figure_captions.json
            │       ├── figure_captions.md
            │       ├── tables/       shared table set detailed below
            │       │   └── daily_basin.csv    source-only addition to shared set
            │       └── figures/      source figure set detailed below
            │           └── captioned/        optional PNG/PDF copies
            └── comparison/           multisource runs only
                └── diagnostics/      [new] comparison diagnostics root D_c
                    ├── diagnostics.json
                    ├── figure_captions.json
                    ├── figure_captions.md
                    ├── tables/       shared table set detailed below
                    │   ├── agreement.csv     comparison-only addition
                    │   └── agreement.md      comparison-only addition
                    └── figures/      comparison figure set detailed below
                        └── captioned/        optional PNG/PDF copies
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

### Figure subtree

Every `{png,pdf}` entry represents two explicitly declared files. `<dataset>`
is the source ID for a source figure and `comparison` for a multisource figure.
Each optional captioned copy uses the identical basename under `captioned/`.

```text
<diagnostics-root>/
└── figures/
    ├── <dataset>_precip_monthly_coverage_calendar_basin_avg.{png,pdf}
    ├── <dataset>_precip_monthly_clim_band_basin_avg.{png,pdf}
    ├── <dataset>_temp_monthly_clim_band_basin_avg.{png,pdf}             conditional
    ├── <dataset>_precip_annual_timing_interval_basin_avg.{png,pdf}
    ├── <dataset>_precip_monthly_anomaly_calendar_basin_avg.{png,pdf}
    ├── <dataset>_precip_monthly_spi_calendar_basin_avg.{png,pdf}
    ├── <dataset>_precip_spi_drought_event_scatter_basin_avg.{png,pdf}
    ├── <dataset>_precip_annual_rx1day_ts_basin_avg.{png,pdf}
    ├── <dataset>_precip_annual_rx5day_ts_basin_avg.{png,pdf}
    ├── <dataset>_precip_annual_sdii_ts_basin_avg.{png,pdf}
    ├── <dataset>_precip_annual_wet_days_ts_basin_avg.{png,pdf}
    ├── <dataset>_precip_daily_dry_spell_exceedance_basin_avg.{png,pdf}
    ├── <dataset>_precip_monthly_anomaly_acf_basin_avg.{png,pdf}
    ├── <dataset>_precip_annual_trend_interval_basin_avg.{png,pdf}
    ├── <dataset>_precip_annual_trend_ts_basin_avg.{png,pdf}
    ├── <dataset>_precip_temp_seasonal_anomaly_scatter_basin_avg.{png,pdf} conditional
    ├── <dataset>_precip_monthly_spi_fit_heatmap_basin_avg.{png,pdf}
    ├── <dataset>_precip_annual_trend_start_year_line_basin_avg.{png,pdf}
    └── captioned/                    optional; mirrors the selected basenames above
```

For ERA5 + CHIRPS, the new figure sets are:

| Root | Forms | PNG/PDF files | Temperature behavior |
|---|---:|---:|---|
| ERA5 source | 18 | 36 | Own temperature and own P–T |
| CHIRPS source | 16 | 32 | No temperature or own P–T figure |
| Comparison | 17 | 34 | No single-carrier temperature comparison; explicit P–T pairs use ERA5 temperature |
| Total | 51 | 102 | Optional captioned copies add another 102 files |

A single-source run creates only its source diagnostic subtree. Runtime data
insufficiency produces labelled unavailable panels for declared figures.
Ntoum results remain real-data exercised and **not scientifically qualified**.
