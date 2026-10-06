# Add WF0 basin diagnostics without replacing existing figures

Status: proposed — Gate 1 owner approval pending
Date: 2026-10-06
Decider: Ümit Taner
Lifecycle: maintained-current body; append-only revision log
Revisions:
- 2026-10-06: Phase 1 inventory and proposed contracts from the lab working tree; read-only cst-architect contract review reconciled.

This task-owned decision record governs implementation after Gate 1. Its extra
length is necessary to review the complete output inventory, source attribution,
and declaration/writer mapping together. No existing ADR covers this diagnostic
integration; ADR 0006 governs the existing shared source figure family.

## Context

The reference is `C:/Users/taner/workspace/wf0-lab` **working tree**, inspected
read-only on 2026-10-06. `git status --short` showed modified handoff docs,
`figures.py`, input/report/runner code and tests; `captions.py` and the caption
snapshot were untracked. A lab commit alone cannot identify the accepted state.
The five requested handoff documents were read in order. Diagnostics, figure,
caption and relevant test implementations were inspected. All 16 standard
compare PNGs were visually inspected; the 16 captioned names were inventoried
and the SPI/annual-series captioned exports inspected as layout references.

BlueEarth lane: `session-2`, `feat/wf0-plotting-improvements`; clean at entry,
HEAD identical to local main (`7704e7e2`), so no synchronization change needed.
The current board was inspected in the primary checkout; its existing
forcing-selection evaluation item concerns observations/Budyko, not this lab
integration. This record creates no board item and changes no main-board state.

Rule 0.04 uses `source_plot_rule.py` and `plot_climate_source.py`, shared with
WF1. Per source it writes maps, annual series and monthly boxes for the genuine
variables from `source_climate_vars`, plus runtime subbasin figures. ERA5 has
precip/temp/PET products; CHIRPS has precipitation products even when its
forcing store contains ERA5 companions. Rule 0.05 writes
`dataset_comparison.csv/.md`, annual series and monthly climatology lines for
variables carried by at least two sources, plus subbasin figures. ERA5/CHIRPS
therefore has two basin comparison PNGs and no temperature comparison.

The existing annual and monthly views are related to three accepted lab forms
but are not equivalents: monthly boxes/mean-only lines differ from percentile
ribbons; annual series have different completeness treatment and no Sen line.
Replacing them would change live contracts and WF1 behavior.

## Decision

Add WF0-only computation and rendering rules beside 0.04/0.05. Use the toolbox's
own extracted daily basin series and mask helper, pure diagnostic functions,
retained plot-ready tables, one output inventory, and separate recoverable
captions. Preserve the paths and content contracts of all pre-existing products.
Adopt the accepted lab visual meanings in the new diagnostic figure family.
Do not change shared `plot_style.py`, extraction, WF1–WF4, or lab files.

### D1. Periods, inputs and scientific conventions

- Read `climate.sources`, `climate.selected`, `climate.window` and
  `climate.water_year_start` through existing composition. Reporting years are
  labelled by their **start year**. Do not reuse end-year labels from existing
  figure aggregation as diagnostic labels.
- Per-source analysis uses the actual extracted span inside the requested
  window. Reindex each series to a complete daily calendar inside that span;
  retain NaNs and partial boundary-year coverage in metadata. Only full
  reporting years qualify for annual diagnostics.
- Reduce raw `precip` and genuine `temp` over equal-weight cells selected by
  `cells_csv_mask`; verify every declared cell matches. Missing, empty or
  partially unmatched masks fail these new diagnostics rather than silently
  averaging the buffered extraction. Use the current toolbox reduction's
  missing-cell convention and record contributing cells. Confirm daily basin
  values against the lab before accepting results.
- Do not invoke source-grid PET/parity transformations for the new diagnostics.
  Precipitation is mm/day and extracted temperature values are Celsius under
  the existing extraction/catalog transform. The ERA5 Zarr catalog already
  applies -273.15. Retained Ntoum extracts may label Celsius values as K:
  record both the original label and effective Celsius contract, with a
  diagnostic warning, without subtracting 273.15 again or rewriting the store.
  Check extraction lineage and value plausibility before accepting temperature;
  unresolved units make temperature diagnostics unavailable with a reason.
- CHIRPS dates already incorporate catalog `unit_add: time: 86400`.
  Never add a second time shift or port the lab input loader.
- The reference period is distinct from the display period. Default reference
  is the requested `climate.window` in reporting-year labels, recorded as
  in-sample when appropriate. Explicit references are not silently shortened
  or substituted. Record actual usable years and fit sample counts, including
  internal gaps and source-specific reference coverage.
- Comparison display defaults to the reference period, matching the lab.
  If `comparison_period` is set, use that interval instead. Its displayed axis
  is that interval for every source, with unavailable cells gray; never silently
  fall back to different per-source windows. Agreement uses the exact
  intersection of valid reporting years, not merely overlapping endpoints.
- Fit SPI and establish reference monthly/seasonal means from the full retained
  source series **before** display clipping. Retain accumulations across display
  boundaries where preceding extracted months exist. Drought/spell boundaries
  are censored at the displayed interval; seasonal P–T uses complete DJF/MAM/
  JJA/SON, with December assigned to the following DJF year as in the lab.
- Completeness is ≤3 missing days/month and ≤15/year. Fill tolerated gaps with
  that month's observed mean for amounts only. Extremes, SDII and dry spells
  retain observed values; wet-day counts scale to full-year length. Wet day
  is ≥1 mm. Rx5day windows cannot cross a reporting-year boundary.
- Gamma SPI includes point-mass zeros; scales 3/6/12, fit checks by calendar
  month. McKee events use SPI-3/12, negative runs reaching ≤-1, unmerged across
  non-drought months. Fewer than five fitting accumulations, degenerate positive
  samples or failed fits produce unavailable cells with reasons. Fewer than
  30 usable reference years is exploratory, never qualified calibration.
- Theil–Sen slopes/95% Sen intervals and two-sided Mann–Kendall p use the lab's
  Yue–Wang lag-1 variance inflation, bias correction and floor of one. Record
  n, r1 and factor; document that dropping missing annual values compresses
  the dependence sequence. Sensitivity uses at least 15 valid years.
- Port Pettitt and seeded SNHT helpers and tests. Homogeneity tables are
  exploratory, not a qualification gate. Source tests cover total/wet_days/
  SDII/Rx1day/Rx5day; comparison adds each source pair's annual differences
  over common valid years. Record seed 0 and 20,000 SNHT simulations.

### D2. Configuration proposed for approval

New settings belong in the **WF0-owned workflow file** (e.g.
`project_config_rapid_analyze_climate.yml`), since WF0 alone consumes them.
They are not new project `climate:` keys or toolbox-wide advanced settings.
The composed location is `workflows.analyze_climate.diagnostics`.

```yaml
# Optional block; omitted values resolve only in the new diagnostic adapter.
diagnostics:
  reference_period: null       # null -> requested climate.window start/end
  comparison_period: null      # null -> reference_period; {start: Y, end: Y}
  max_missing_days_month: 3
  max_missing_days_year: 15
  wet_day_threshold_mm: 1.0
  spi_distribution: gamma     # gamma or pearson3; both fit-checked
  captioned_figures: false
  pt_temperature_source: era5  # explicit binding; unavailable if not declared
```

`reference_period` also accepts `{start: Y, end: Y}`. Validate the closed block,
integer periods/tolerances, positive finite wet threshold, distribution,
boolean and genuine temperature binding at parse time. An omitted default ERA5
binding when ERA5 is absent yields unavailable P–T; an explicitly named
non-carrier/source outside the declared set is a configuration error.
Unknown keys fail rather than silently retaining defaults.

No lab display-period arrays, input-path/unit overrides, `time_shift_days`,
HTML output or synthetic CLI enter the toolbox. This block adds outputs and
cost to WF0 by default but leaves all pre-existing numerical artifacts neutral.
Approval includes documenting these T2 keys and adding optional commented
examples in WF0 seed configs. No config-composition default injection or new
advanced-settings schema entries are proposed.

### D3. Accepted figure inventory and exact proposed names

`S` below is the actual single-source dataset ID. `comparison` is used only
when multiple precipitation sources/explicit source pairs are plotted.
All new files have the four semantic fields
`<dataset_scope>_<variable>_<plot_context>_<spatial_scope>`; underscores inside
controlled fields are permitted by the existing grammar.
The variable tokens remain `precip`, `temp`, and combined `precip_temp`.

Every row below adds a new diagnostic view. **None is an existing exact
equivalent.** Rows 2, 3 and 15 retain the related old view alongside the new one.
Each name shown as `.png` also has a declared `.pdf` twin.

| # | Lab accepted form | Existing 0.04 / 0.05 relationship | New comparison basename / source behavior | Input table |
|---|---|---|---|---|
| 1 | coverage | absent | `comparison_precip_monthly_coverage_calendar_basin_avg.png`; also S | coverage |
| 2 | seasonal | monthly boxes / mean-only line; no equivalent band | `comparison_precip_monthly_clim_band_basin_avg.png`; also S | precip_climatology |
| 3 | temperature | temp boxes; comparison unavailable for ERA5/CHIRPS | `S_temp_monthly_clim_band_basin_avg.png`; only genuine temp carriers | temp_climatology |
| 4 | timing | absent | `comparison_precip_annual_timing_interval_basin_avg.png`; also S | rainfall_timing |
| 5 | anomaly | absent | `comparison_precip_monthly_anomaly_calendar_basin_avg.png`; also S | monthly_values |
| 6 | spi | absent | `comparison_precip_monthly_spi_calendar_basin_avg.png`; also S | spi |
| 7 | drought-events | absent | `comparison_precip_spi_drought_event_scatter_basin_avg.png`; also S | drought_events |
| 8 | extreme-Rx1day | absent | `comparison_precip_annual_rx1day_ts_basin_avg.png`; also S | annual_indices |
| 9 | extreme-Rx5day | absent | `comparison_precip_annual_rx5day_ts_basin_avg.png`; also S | annual_indices |
| 10 | extreme-SDII | absent | `comparison_precip_annual_sdii_ts_basin_avg.png`; also S | annual_indices |
| 11 | extreme-Wet days | absent | `comparison_precip_annual_wet_days_ts_basin_avg.png`; also S | annual_indices |
| 12 | spell | absent | `comparison_precip_daily_dry_spell_exceedance_basin_avg.png`; also S | dry_spell_exceedance |
| 13 | acf | absent | `comparison_precip_monthly_anomaly_acf_basin_avg.png`; also S | anomaly_acf |
| 14 | slopes | absent | `comparison_precip_annual_trend_interval_basin_avg.png`; also S; panels identify total/wet days/Rx1day | trends |
| 15 | series | existing annual series lacks completeness/Sen overlay | `comparison_precip_annual_trend_ts_basin_avg.png`; also S | annual_indices + trends |
| 16 | pt | absent; CHIRPS own temperature/P–T unavailable | `comparison_precip_temp_seasonal_anomaly_scatter_basin_avg.png`; source-only form for genuine own P+T | pt_anomalies |

Two additional diagnostic figure forms expose important methods already in
the lab, beyond the accepted 16 PNG inventory: fit checks and start-year
sensitivity. `spi_checks` and `sensitivity` functions exist in the lab but are
not in its current CHARTS export set. These are proposed additions, not claimed
accepted visual references:

| Form | New basename (comparison or S) | Input |
|---|---|---|
| Gamma/Pearson III fit checks | `comparison_precip_monthly_spi_fit_heatmap_basin_avg.png` | spi_fit_checks |
| Total/Rx1day start-year sensitivity | `comparison_precip_annual_trend_start_year_line_basin_avg.png` | trend_sensitivity |

Extend `figure_naming.PLOT_CONTEXTS` with exactly the contexts in these tables;
keep `annual_ts`, `monthly_box`, `monthly_clim_line`, maps and all old names.
No new spatial scope; this integration is **basin only**, with no diagnostic
subbasin fan-out. Update the controlled-context reference with implementation.

For ERA5/CHIRPS: ERA5 has 18 new source forms; CHIRPS has 16 (no own temp/P–T);
comparison has 17 (no one-carrier temperature climatology). The accepted
compare reference set maps to 15 comparison views plus ERA5's source temperature
view. The other two comparison views are the proposed fit/sensitivity additions.
If at least two genuine temperature carriers are supported in future, the
inventory permits a `comparison_temp_monthly_clim_band_basin_avg` form.

P–T in source diagnostics uses only that source's genuine own temperature.
In comparisons, use each precipitation source against the explicitly bound
temperature source over complete shared seasons. Legend entries identify
`P: ERA5` / `P: CHIRPS v2.0`; axis and caption identify `T: ERA5`, and table
columns preserve both source IDs. This reproduces the accepted lab P–T meaning
without representing ERA5 temperature as a CHIRPS measurement. If no declared
temperature source exists, omit P–T at parse time and record its unavailability.

### D4. Table, metadata, figure and caption output contracts

Roots (resolved from existing specs, never guessed from source names):

- Source `D_s = CLIMATE_STORES[source].store_dir + '/diagnostics'`.
- Comparison `D_c = COMPARISON_DIR + '/diagnostics'`.
- Tables `D/tables/`; standard figures `D/figures/`; optional captioned
  figures `D/figures/captioned/` with the **same four-field basename**.
  Directory placement, not a fifth `_captioned` field, identifies the variant.
- Metadata `D/diagnostics.json`; captions `D/figure_captions.json` and
  `D/figure_captions.md`. These are declared files, not incidental side effects.

All CSVs have fixed headers, including when empty/unavailable. `source` and
`period_start/period_end` accompany the keys below; dates are ISO, units and
column definitions are in diagnostics.json. NaN is empty, never numerical zero.
No diagnostic table is `temp()`.

| Declared filename under tables/ | Row keys and required values | Source / comparison |
|---|---|---|
| `daily_basin.csv` | date; observed precip, genuine temp (NaN otherwise), contributing-cell counts | source only; gap-preserving handoff to 0.05b |
| `coverage.csv` | reporting_year, calendar_month; fraction, missing_days, class 0/1/2 | both |
| `valid_years.csv` | reporting_year; full_year, valid_precip, valid_temp, missing_days, reason | both; includes invalid years |
| `annual_indices.csv` | reporting_year; total, wet_days, SDII, Rx1day, Rx5day | both |
| `monthly_values.csv` | date, reporting_year, calendar_month; total, reference_mean, anomaly, temp_mean, usable flags | both |
| `precip_climatology.csv` | calendar_month; mean, p10, p90, n | both |
| `temp_climatology.csv` | calendar_month; mean, p10, p90, n | both; empty for absent temperature |
| `rainfall_timing.csv` | reporting_year, fraction; day, valid flag | both; fractions .25/.5/.75 |
| `spi.csv` | date, scale; value, distribution, available, reason | both; scales 3/6/12 |
| `spi_fit_checks.csv` | calendar_month, scale; n, zeros, sw_gamma, sw_pearson3, skew, max_abs, mom_diff, p3_bound_hits, reason | both; reference fit retained |
| `drought_events.csv` | scale, event_id; start, end, duration, severity, intensity, censored | both; scales 3/12 |
| `dry_spells.csv` | spell_id; complete spell length_days | both; dropped censored counts in metadata |
| `dry_spell_exceedance.csv` | length_days; probability, n_complete_spells | both |
| `anomaly_acf.csv` | lag_months; r, pairs | both; lags 1–12 |
| `trends.csv` | metric; slope, lo, hi, intercept, p, r1, factor, n, correction | both; total/wet_days/Rx1day |
| `trend_sensitivity.csv` | metric, start_year; end_year, slope, lo, hi, p, n | both; total/Rx1day, minimum 15 |
| `pt_anomalies.csv` | precip_source, temperature_source, season, season_year; p, t, p_anom_pct, t_anom | both; empty when unavailable |
| `homogeneity.csv` | series_kind, source_pair, metric, method; break_after, stat, p, n, seed, n_sim, reason | both; guarded insufficient/constant samples |
| `agreement.csv` | source; mean_total, mean_wet_days, mean_sdii, n_common_valid_years | comparison only |
| `agreement.md` | same agreement table, common valid year list, support and qualification caveats | comparison only |

`diagnostics.json` has schema_version 1; resolved settings; input paths and
content hashes; source IDs/labels; extraction span and catalogue lineage;
reported/effective units; basin cell counts; reporting/calendar conventions;
requested/actual display/reference periods; exact valid/common years; reference
fit counts; qualification notices; unavailable products/reasons; spell/event
censoring counts; anomaly colour bounds; and every produced relative path.
Its six families start as prototype-tested only after ported tests pass;
Ntoum exercise and qualification status are separate fields, never inferred
from run success. Include the scientific limitations below.

`figure_captions.json` has schema_version 1 and entries keyed by relative
standard PNG basename/path, with PDF and optional captioned paths, unnumbered
caption text, contributing source IDs, period, reference, support, encoding,
method details, availability and caveats. Markdown exposes the same text for a
report author, with filename headings. `diagnostic_captions.py` is the sole
caption formatter; JSON, Markdown and captioned exports reuse its text.
New standard figures have no bottom descriptive paragraph. Existing figure
footers remain unchanged; their support/resolution warning is carried once in
each new caption/metadata entry, not duplicated in the optional caption band.

### D5. Single declaration source and Snakemake mapping

All new modules live under `blueearth_cst/climate_analysis/`:

| Module | Responsibility |
|---|---|
| `diagnostics.py` | selected pure numerical functions, adapted and tested; no Snakemake objects |
| `diagnostic_outputs.py` | closed table/figure inventory, capability predicates, and exact paths used by declaration and writers |
| `diagnostic_settings.py` | pure closed settings parser; resolved defaults without mutating composed config |
| `diagnostic_tables.py` | gap-preserving basin adapter, period-specific compute, CSV/JSON I/O |
| `diagnostic_figures.py` | figures from retained plot-ready tables; family-local layout/style |
| `diagnostic_captions.py` | recoverable scientific captions independent of figures |
| `compute_climate_diagnostics.py` | 0.04b script glue |
| `plot_climate_diagnostics.py` | 0.04c script glue |
| `compare_climate_diagnostics.py` | 0.05b script glue and common-period table/figure production |

Use `diagnostic_source_outputs(store_dir, source, settings)` and
`diagnostic_comparison_outputs(comparison_dir, sources, settings)` returning
named compute/render path sets. Derive every figure basename through
`figure_filename`. Writers receive these path sets, never rebuild stems.
Tests assert exact recursive output-file equality and rule declaration equality.

| Rule number/name | Declared inputs | Declared outputs / writer |
|---|---|---|
| 0.04 `plot_climate_datasets_<source>` | current SourcePlotRule inputs | existing plots/subbasins only; current writer |
| 0.04b `compute_climate_diagnostics_<source>` | own extracted climate_nc + basin_cells; settings in params | daily_basin + 17 plot-ready CSVs + diagnostics.json; compute script |
| 0.04c `plot_climate_diagnostics_<source>` | own 0.04b table/metadata outputs; all candidates' monthly_values/metadata for pooled anomaly bounds | capability-selected source PNG/PDFs + both caption files + optional captioned PNG/PDFs; plot script |
| 0.05 `compare_climate_datasets` | current extracted stores/cells/subbasins | current comparison files/subbasins only; current writer |
| 0.05b `compare_climate_diagnostics` | each source's daily_basin + diagnostics.json (full native series/lineage) | 17 common-period plot-ready CSVs + agreement.csv/.md + diagnostics.json + selected comparison PNG/PDFs + captions/optional variants; compare script |

0.05b recomputes **period-dependent** climatologies, trends, sensitivity, ACF,
spells and event tables using the same pure computation functions; it does not
filter full-record aggregates. SPI/reference means are computed from the full
series before display clipping. A read-only specialist suggested computing both
full/common sets in 0.04b; this design instead keeps the single-source job
independent, retaining daily data so the comparison owns its period. This costs
some repeated fits but avoids coupling every source job to every other store.
Only the source rendering jobs wait for all candidates' monthly anomaly tables
to establish the shared colour scale; single-source computation stays independent.

Register letter-suffixed rules through the current RuleRegistry without
renumbering 0.01–0.07. Register 0.05b only for >1 declared source. Add all new
terminal output paths to WF0_TERMINALS so gathers await tables, captions and
figures; no logs are stranded. WF0_TARGETS includes the new terminals.
No one-source comparison directory/job or agreement table is introduced.

Capability absence known at parse time omits its figure (CHIRPS temp/own P–T)
and records the reason. Data insufficiency known only at execution produces
a clearly labelled unavailable panel for every declared PNG/PDF, with identical
availability notices in captions/JSON. No common valid years means no numerical
agreement claim; no temporal overlap means unavailable comparison panels, not
an own-period overlay. Empty events mean "no events", distinct from failed SPI.

For default ERA5/CHIRPS this declares 51 new standard forms, 102 PNG/PDF files;
captioned_figures=true adds another 102 files. Source compute: 19 files/source;
source render: 2 caption files plus selected images. Comparison: 20 table/
metadata files, 2 caption files plus selected images. Counts are verification
consequences of the inventory, not hardcoded caps.

### D6. Visual contract

Use local `rc_context`, retain the shared unit conversion/600-DPI PNG export and
PDF font type 42. Shared typography currently starts at 8 pt/7 pt ticks/6.5 pt
legend; the new family deliberately uses the accepted 7 pt axes/titles and
6 pt ticks/legends/captions. No shared rcParams or style constant changes.

| Layout | Physical canvas |
|---|---|
| One panel | 140 × 80 mm |
| Two vertical source panels (coverage/anomaly/SPI) | 180 × 110 mm |
| Two side-by-side panels (events/sensitivity) | 180 × 86 mm |
| Three interval panels (slopes) | 180 × 80 mm |
| Four seasonal panels (P–T) | 180 × 142 mm |

Outer constrained-layout padding starts at 4 mm horizontal/3 mm vertical.
All four plot boundaries are #c6d2d8 at 0.9 pt; grid #e6edef at 0.6 pt.
Use horizontal x labels, labelled five-year heatmap ticks plus intervening-year
ticks, panel letters, short legends/axes, bottom-aligned short right colourbars
with horizontal title, and direct in-axes series slopes with no trend legend key.
ERA5/CHIRPS labels are ERA5/CHIRPS v2.0; identity colors #236b8e/#bf6a3c.
Use seven-class RdBu dry-red/wet-blue and gray unavailable cells. Anomaly bounds
are computed once from pooled full-series anomalies of declared sources and
recorded; source/comparison/caption variants share them. Single-source renders
derive the same rule locally. No silent source-count cap; supported configured
sources all render, with extra stacked panels sized and reviewed explicitly.

Preserve mean/10–90% bands, timing mean dots/day labels + white median ticks,
observed annual extremes, censored event tint, log dry-spell exceedance, no ACF
significance band, and filled/hollow trend evidence. Caption variants reserve
an added bottom band and preserve the plotting canvas/type scale; review final
exports for clipping. Fit-check canvas is a declared density exception with one
row/source/distribution; panel letters and short titles, detailed tests in caption.
Sensitivity has panel letters (the lab function's older titles lack them).

## Consequences

Positive: WF0 has auditable six-family source diagnostics, genuine comparisons,
recoverable captions, and independent figure reruns from retained tables.

Negative: additive plots overlap some older views, produce 102 additional
default images for ERA5/CHIRPS, and add compute/storage even in a single-source
WF0 run. Comparison recomputation repeats some fits. New exports remain
exploratory scientific products.

Neutral: no existing output migration; no new dependency expected (numpy,
pandas, scipy, xarray and Matplotlib already exist). New controlled contexts,
WF0 T2 settings, rule wiring and docs require focused verification.

## Alternatives considered

1. Extend existing 0.04/0.05 figures in place. Preferable if the owner approves
   changing both WF0/WF1 source figures and old comparison content contracts.
   Rejected here because the accepted percentile/trend/completeness views change
   scientific meaning and the shared source producer affects WF1.
2. Compute full/common tables in every per-source job. Preferable if comparison
   periods are fixed independently of other sources or avoiding repeated fits
   dominates. Not chosen because mutual availability/reference choices would
   couple otherwise independent source jobs. Retained daily basin tables give
   the comparison the exact input needed for faithful recomputation.
3. Only output comparisons. Preferable for a comparison-only review report;
   rejected because a single-source WF0 must retain useful diagnostics.
4. Only metadata captions, no captioned export option. Lower artifact count;
   preferable for a single established report pipeline. Optional captioned
   PNG/PDFs are proposed because the reviewed lab supports standalone sharing.

## Validation and acceptance after Gate 1

1. Port known-answer tests: completeness/infill, reporting labels, Rx5day
   boundaries, observed extremes, censoring, SPI moments/zeros/fit failures,
   McKee events, Sen vs scipy, Yue–Wang AR(1), sensitivity/P–T, break tests.
   Add adapter/contract tests for absent temp, source order, short/empty reference,
   all-zero/constant data, no overlap, internal gaps, non-January SPI axes, exact
   mask matching, single-source declarations, and declaration/writer equality.
2. Focused existing figure naming/source/comparison tests; target rule-registry
   log/benchmark and config-snapshot tests affected by new rules/settings.
3. Ntoum regression once per diagnostics change. Re-measure lab retained tables
   read-only; compare exact yearly totals/daily basin series under matched data,
   masks, year convention, settings and spans. 2000–2016 mean annual P reference:
   ERA5 2721.9 mm, CHIRPS 2524.8 mm. 1990–2020 Rx1day slope/p reference:
   ERA5 +7.1 mm/decade / .006; CHIRPS +10.0 / .002. Slope tolerance .1
   mm/decade, p .001; daily float32 rounding about 1e-4 mm/day. The accepted
   PNG set displays 1991–2020: do not confuse it with the 1990 trend regression.
4. Value-neutral check uses matched fresh rapid cases and existing numerical
   products, without the stale baseline manifest. Render agreed new source/
   comparison PNG/PDFs and approved captioned variants, inspect intended size,
   unavailable cases, margins and bar placement. Expose local PNG artifacts for
   owner inspection; do not publish them externally. Report paths against the
   declaration. Document every difference from lab values/layout/availability
   in a Results delta (including source-only P–T policy).
5. Before implementation commit: `pixi run pytest tests/test_cli.py`,
   `pixi run lint`, `pixi run format-check`; rapid WF0 DAG dry-run and targeted
   execution from this BlueEarth lane. Gate logs go to .tmp/scratchpad after
   confirming ignore. No BlueEarth workflow runs from the lab.
6. Commit verified work on this branch. Landing requires separate approval,
   then the live batch ladder's test-fast and applicable test-full/test-e2e
   gates; no landing/push/publication in this task. The design-only commit
   uses a diff check, not workflow tests.

Acceptance requires Gate 1 recorded, every declared output written, source
temperature honesty, falsifiers passing, documented method/status/limits,
changed-file inventory, rung-by-rung report, lab/toolbox regression table and
Results delta. If matched old numerical outputs change, stop and diagnose;
rollback is a branch revert after preserving evidence.

## Scientific status and required limitations

The lab families are prototype-tested and real-data exercised on Ntoum;
**not scientifically qualified**. Integration does not improve that status.
Toolbox docs must carry the following lab section unchanged:

- Input homogeneity is unverified. CHIRPS gauge density and ERA5's assimilated observations change over time,
  which can create spurious trends in extremes. The Rx1day increase of about 7–10 mm/decade over 1990–2020 in both
  products survives start-year, leave-one-out and multiple-testing checks, but the products disagree on which
  years are extreme (r = 0.29). Treat it as provisional until compared with a homogeneous station record or other
  products (MSWEP, GPCC).
- Relative homogeneity (`pettitt`, `snht` on ERA5 − CHIRPS differences, 1990–2020) finds no break in annual P, wet
  days, SDII, Rx1day or Rx5day (p = 0.26–0.73). The test is weak here: the Rx1day difference has an SD of 35 mm, so
  a step equal to the whole trend (about 22 mm) is detected only about 26% of the time (80% power needs about
  45–50 mm). The absence of a break therefore does not rule out an artefact of trend size. Each product alone shows
  an Rx1day change point near 2005–2006 (Pettitt p = 0.035 ERA5, 0.008 CHIRPS); two differently built products
  agreeing on its timing weakly supports a real change, but does not separate a step from a gradual trend.
- No station data are available, and the toolbox catalog has no other daily precipitation product for this region
  (SM2RAIN-ASCAT is monthly, 2007–2020). An independent check needs an approved download (IMERG from 2000, MSWEP
  from 1979).
- ERA5 short-scale SPI misfit (negative skew) overstates dry extremes in flagged months.
- CHIRPS is staged only from 1990; a 1981–2020 window needs a wider clip.
- Source agreement is not accuracy; no independent observations were used.

## Gate 1 decision requested

Approve D1–D6, including the complete 16-form reconciliation, two additional
fit/sensitivity views, additive paths and table schemas, PNG/PDF plus optional
captioned output contract, WF0-owned T2 configuration, explicit common-period
and P–T source binding, unavailable-panel behavior, and local visual style.
There are no proposed existing-output renames/content changes, project climate
keys, advanced settings changes, or shared plotting-style changes.

Owner approval: pending. Implementation is paused at the integration brief's
explicit **Phase 1 item 5, Gate 1** boundary. The design-document skill supplies
the record format; the pause is required by the user-invoked integration brief.

## Related

- `C:/Users/taner/workspace/wf0-lab/docs/blueearth-integration-brief.md`
- `C:/Users/taner/workspace/wf0-lab/docs/integration-notes.md`
- `C:/Users/taner/workspace/wf0-lab/docs/figure-rules.md`, Current figure polish
- `C:/Users/taner/workspace/wf0-lab/docs/compare-figure-captions.md`
- `C:/Users/taner/workspace/wf0-lab/docs/diagnostic-notes.md`
- `dev/reference/wf0-figure-filename-rule.md`; `dev/reference/workflows/rule-index.md`
- `dev/records/decisions/0006-retire-subcatchment-climate-plots.md`
- `AGENTS.md`, validation ladder and task-lane rules
