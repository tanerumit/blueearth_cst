# WF0 design reference

Status: Gate 1 approved; implementation in progress. Approval covers design revision
`9bed3e05`; see [the gate record](design.md#8-gate-1-review).

This companion serves implementers and reviewers who need exact scientific
conventions, schemas, rule contracts and validation details. The user-facing
proposal and authoritative tree are in [design.md](design.md). D1–D6 remain
the technical contract. The decision history and inspection evidence at the
end record how the proposal developed; they are not additional instructions.

## Contents

- [Technical decisions](#technical-decisions)
- [Validation and acceptance](#validation-and-acceptance-after-gate-1)
- [Scientific limitations](#scientific-status-and-required-limitations)
- [Decision history](#session-decision-process-record--2026-10-06)
- [Inspection evidence](#inspection-evidence)

## Technical decisions

### D1. Periods, inputs and scientific conventions

- Read `climate.sources`, `climate.selected`, `climate.window` and
  `climate.water_year_start` through existing composition. Reporting years are labelled
  by their **start year**. Do not reuse end-year labels from existing figure aggregation
  as diagnostic labels.
- Per-source analysis uses the actual extracted span inside the requested window.
  Reindex each series to a complete daily calendar inside that span; retain NaNs and
  partial boundary-year coverage in metadata. Only full reporting years qualify for
  annual diagnostics.
- Reduce raw `precip` and genuine `temp` over equal-weight cells selected by
  `cells_csv_mask`; verify every declared cell matches. Missing, empty or partially
  unmatched masks fail these new diagnostics rather than silently averaging the buffered
  extraction. Use the current toolbox reduction's missing-cell convention and record
  contributing cells. Confirm daily basin values against the lab before accepting
  results.
- Do not invoke source-grid PET/parity transformations for temporal diagnostics;
  source PET maps retain the existing derivation.
  Precipitation is mm/day and extracted temperature values are Celsius under the
  existing extraction/catalog transform. The ERA5 Zarr catalog already applies -273.15.
  Retained Ntoum extracts may label Celsius values as K: record both the original label
  and effective Celsius contract, with a diagnostic warning, without subtracting 273.15
  again or rewriting the store. Check extraction lineage and value plausibility before
  accepting temperature; unresolved units make temperature diagnostics unavailable with
  a reason.
- CHIRPS dates already incorporate catalog `unit_add: time: 86400`. Never add a second
  time shift or port the lab input loader.
- The reference period is distinct from the display period. Default reference is the
  requested `climate.window` in reporting-year labels, recorded as in-sample when
  appropriate. Explicit references are not silently shortened or substituted. Record
  actual usable years and fit sample counts, including internal gaps and source-specific
  reference coverage.
- Comparison display defaults to the reference period, matching the lab. If
  `comparison_period` is set, use that interval instead. Its displayed axis is that
  interval for every source, with unavailable cells gray; never silently fall back to
  different per-source windows. Agreement uses the exact intersection of valid reporting
  years, not merely overlapping endpoints.
- Fit SPI and establish reference monthly/seasonal means from the full retained source
  series **before** display clipping. Retain accumulations across display boundaries
  where preceding extracted months exist. Drought/spell boundaries are censored at the
  displayed interval; seasonal P–T uses complete DJF/MAM/ JJA/SON, with December
  assigned to the following DJF year as in the lab.
- Completeness is ≤3 missing days/month and ≤15/year. Fill tolerated gaps with that
  month's observed mean for amounts only. Extremes, SDII and dry spells retain observed
  values; wet-day counts scale to full-year length. Wet day is ≥1 mm. Rx5day windows
  cannot cross a reporting-year boundary.
- Gamma SPI includes point-mass zeros; scales 3/6/12, fit checks by calendar month.
  McKee events use SPI-3/12, negative runs reaching ≤-1, unmerged across non-drought
  months. Fewer than five fitting accumulations, degenerate positive samples or failed
  fits produce unavailable cells with reasons. Fewer than 30 usable reference years is
  exploratory, never qualified calibration.
- Theil–Sen slopes/95% Sen intervals and two-sided Mann–Kendall p use the lab's Yue–Wang
  lag-1 variance inflation, bias correction and floor of one. Record n, r1 and factor;
  document that dropping missing annual values compresses the dependence sequence.
  Sensitivity uses at least 15 valid years.
- Port Pettitt and seeded SNHT helpers and tests. Homogeneity tables are exploratory,
  not a qualification gate. Source tests cover total/wet_days/ SDII/Rx1day/Rx5day;
  comparison adds each source pair's annual differences over common valid years. Record
  seed 0 and 20,000 SNHT simulations.

### D2. Configuration proposed for approval

New settings belong in the **WF0-owned workflow file** (e.g.
`project_config_rapid_analyze_climate.yml`), since WF0 alone consumes them. They are not
new project `climate:` keys or toolbox-wide advanced settings. The composed location is
`workflows.analyze_climate.diagnostics`.

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

`reference_period` also accepts `{start: Y, end: Y}`. Validate the closed block, integer
periods/tolerances, positive finite wet threshold, distribution, boolean and genuine
temperature binding at parse time. An omitted default ERA5 binding when ERA5 is absent
yields unavailable P–T; an explicitly named non-carrier/source outside the declared set
is a configuration error. Unknown keys fail rather than silently retaining defaults.

No lab display-period arrays, input-path/unit overrides, `time_shift_days`, HTML output
or synthetic CLI enter the toolbox. This block adds outputs and cost to WF0 by default
but preserves extracted climate inputs. Approval includes documenting these T2 keys and
adding optional commented examples in WF0 seed configs. No config-composition default
injection or new advanced-settings schema entries are proposed.

### D3. Accepted figure inventory and exact proposed names

`S` below is the actual single-source dataset ID. `comparison` is used only when
multiple precipitation sources/explicit source pairs are plotted. All new files have the
four semantic fields `<dataset_scope>_<variable>_<plot_context>_<spatial_scope>`;
underscores inside controlled fields are permitted by the existing grammar. The variable
tokens are `precip`, `temp`, `pet`, and combined `precip_temp`.

The following views are the canonical temporal figures. Rows 2, 3 and 15 replace the
related old views; those old views are not also rendered. New diagnostic figures are
PNG-only; no PDF twins are declared.

**Figure 1**

- **Lab accepted form:** coverage
- **Existing 0.04 / 0.05 relationship:** absent
- **New comparison basename / source behavior:**
  `comparison_precip_monthly_coverage_basin_avg.png`; also S
- **Input table:** coverage

**Figure 2**

- **Lab accepted form:** seasonal
- **Existing 0.04 / 0.05 relationship:** monthly boxes / mean-only line; no equivalent
  band
- **New comparison basename / source behavior:**
  `comparison_precip_monthly_clim_band_basin_avg.png`; also S
- **Input table:** precip_climatology

**Figure 3**

- **Lab accepted form:** temperature
- **Existing 0.04 / 0.05 relationship:** temp boxes; comparison unavailable for
  ERA5/CHIRPS
- **New comparison basename / source behavior:**
  `S_temp_monthly_clim_band_basin_avg.png`; only genuine temp carriers
- **Input table:** temp_climatology

**Figure 4**

- **Lab accepted form:** timing
- **Existing 0.04 / 0.05 relationship:** absent
- **New comparison basename / source behavior:**
  `comparison_precip_annual_timing_basin_avg.png`; also S
- **Input table:** rainfall_timing

**Figure 5**

- **Lab accepted form:** anomaly
- **Existing 0.04 / 0.05 relationship:** absent
- **New comparison basename / source behavior:**
  `comparison_precip_monthly_anomaly_basin_avg.png`; also S
- **Input table:** monthly_values

**Figure 6**

- **Lab accepted form:** spi
- **Existing 0.04 / 0.05 relationship:** absent
- **New comparison basename / source behavior:**
  `comparison_precip_monthly_spi_basin_avg.png`; also S
- **Input table:** spi

**Figure 7**

- **Lab accepted form:** drought-events
- **Existing 0.04 / 0.05 relationship:** absent
- **New comparison basename / source behavior:**
  `comparison_precip_spi_events_basin_avg.png`; also S
- **Input table:** drought_events

**Figure 8**

- **Lab accepted form:** extreme-Rx1day
- **Existing 0.04 / 0.05 relationship:** absent
- **New comparison basename / source behavior:**
  `comparison_precip_annual_rx1day_ts_basin_avg.png`; also S
- **Input table:** annual_indices

**Figure 9**

- **Lab accepted form:** extreme-Rx5day
- **Existing 0.04 / 0.05 relationship:** absent
- **New comparison basename / source behavior:**
  `comparison_precip_annual_rx5day_ts_basin_avg.png`; also S
- **Input table:** annual_indices

**Figure 10**

- **Lab accepted form:** extreme-SDII
- **Existing 0.04 / 0.05 relationship:** absent
- **New comparison basename / source behavior:**
  `comparison_precip_annual_sdii_ts_basin_avg.png`; also S
- **Input table:** annual_indices

**Figure 11**

- **Lab accepted form:** extreme-Wet days
- **Existing 0.04 / 0.05 relationship:** absent
- **New comparison basename / source behavior:**
  `comparison_precip_annual_wet_days_ts_basin_avg.png`; also S
- **Input table:** annual_indices

**Figure 12**

- **Lab accepted form:** spell
- **Existing 0.04 / 0.05 relationship:** absent
- **New comparison basename / source behavior:**
  `comparison_precip_dry_spell_exceedance_basin_avg.png`; also S
- **Input table:** dry_spell_exceedance

**Figure 13**

- **Lab accepted form:** acf
- **Existing 0.04 / 0.05 relationship:** absent
- **New comparison basename / source behavior:**
  `comparison_precip_monthly_anomaly_acf_basin_avg.png`; also S
- **Input table:** anomaly_acf

**Figure 14**

- **Lab accepted form:** slopes
- **Existing 0.04 / 0.05 relationship:** absent
- **New comparison basename / source behavior:**
  `comparison_precip_annual_trend_interval_basin_avg.png`; also S; panels identify
  total/wet days/Rx1day
- **Input table:** trends

**Figure 15**

- **Lab accepted form:** series
- **Existing 0.04 / 0.05 relationship:** existing annual series lacks completeness/Sen
  overlay
- **New comparison basename / source behavior:**
  `comparison_precip_annual_trend_ts_basin_avg.png`; also S
- **Input table:** annual_indices + trends

**Figure 16**

- **Lab accepted form:** pt
- **Existing 0.04 / 0.05 relationship:** absent; CHIRPS own temperature/P–T unavailable
- **New comparison basename / source behavior:**
  `comparison_precip_temp_seasonal_anomaly_basin_avg.png`; source-only form for genuine
  own P+T
- **Input table:** pt_anomalies

Two additional diagnostic figure forms expose important methods already in the lab,
beyond the accepted 16 PNG inventory: fit checks and start-year sensitivity.
`spi_checks` and `sensitivity` functions exist in the lab but are not in its current
CHARTS export set. These are proposed additions, not claimed accepted visual references:

| Form | New basename (comparison or S) | Input |
|---|---|---|
| Gamma/Pearson III fit checks | `comparison_precip_monthly_spi_fit_basin_avg.png` | spi_fit_checks |
| Total/Rx1day start-year sensitivity | `comparison_precip_annual_trend_sensitivity_basin_avg.png` | trend_sensitivity |

Extend `figure_naming.PLOT_CONTEXTS` with exactly the contexts in these tables; keep
`annual_ts`, `monthly_box`, `monthly_clim_line`, maps and all old names. No new spatial
scope; basin diagnostics are the default; optional subbasin temporal views are defined
below. Update the controlled-context reference with implementation.

For ERA5/CHIRPS: ERA5 has 21 source forms; CHIRPS has 17 (no own temp/P–T); comparison
has 17 (no one-carrier temperature climatology). The accepted compare reference set maps
to 15 comparison views plus ERA5's source temperature view. The other two comparison
views are the proposed fit/sensitivity additions. If at least two genuine temperature
carriers are supported in future, the inventory permits a
`comparison_temp_monthly_clim_band_basin_avg` form.

P–T in source diagnostics uses only that source's genuine own temperature. In
comparisons, use each precipitation source against the explicitly bound temperature
source over complete shared seasons. Legend entries identify `P: ERA5` / `P: CHIRPS
v2.0`; axis and caption identify `T: ERA5`, and table columns preserve both source IDs.
This reproduces the accepted lab P–T meaning without representing ERA5 temperature as a
CHIRPS measurement. If no declared temperature source exists, omit P–T at parse time and
record its unavailability.

### Canonical spatial maps

Add `S_precip_annual_clim_map_basin_ext.png`, `S_temp_annual_clim_map_basin_ext.png` and
`S_pet_annual_clim_map_basin_ext.png` for supported source variables. ERA5 supplies all
three; CHIRPS supplies precipitation only. Use the structure of lab
`figures/era5/era5-precip-annual-climatology.png` and its temperature counterpart:
native-grid cells, basin boundary, dashed subbasin boundaries, river/gauge overlays,
discrete colourbar, geographic axes and complete-year annotation. No interpolation or
cellwise cross-source difference map. Subbasin boundary overlays are independent of
optional subbasin plot fan-out. Use complete reporting-year totals for precipitation/PET
and complete-year means for temperature, consistent with D1's start-year convention.
Shared per-variable colour bounds cover the configured sources over their displayed
basin extent. PET retains the existing source-grid derivation and its caveat; the lab
has no PET map reference, so this is a layout extension requiring review. Retain map
fields in source `tables/annual_climatology.nc` with units, valid-year counts and
unavailable-cell masks. Source computation declares this additional file; rendering
receives it plus declared spatial overlays. Maps use the same caption inventory as
temporal figures. Default source counts become ERA5 21, CHIRPS 17; comparison stays 17:
55 PNGs, plus 55 optional captioned copies.

### D4. Table, metadata, figure and caption output contracts

Roots (resolved from existing specs, never guessed from source names):

- Source `D_s = CLIMATE_STORES[source].store_dir + '/diagnostics'`.
- Comparison `D_c = COMPARISON_DIR + '/diagnostics'`.
- Tables `D/tables/`; standard figures `D/figures/`; optional captioned figures
  `D/figures/captioned/` with the **same four-field basename**. Directory placement, not
  a fifth `_captioned` field, identifies the variant.
- Metadata `D/_engine/diagnostics.json`; captions `D/_engine/figure_captions.json` and
  `D/figure_captions.md`. These are declared files, not incidental side effects.

All CSVs have fixed headers, including when empty/unavailable. `source` and
`period_start/period_end` accompany the keys below; dates are ISO, units and column
definitions are in diagnostics.json. NaN is empty, never numerical zero. No diagnostic
table is `temp()`.

**Declared filename under tables/: `daily_basin.csv`**

- **Row keys and required values:** date; observed precip, genuine temp (NaN otherwise),
  contributing-cell counts
- **Source / comparison:** source only; gap-preserving handoff to 0.05

**Declared filename under tables/: `coverage.csv`**

- **Row keys and required values:** reporting_year, calendar_month; fraction,
  missing_days, class 0/1/2
- **Source / comparison:** both

**Declared filename under tables/: `valid_years.csv`**

- **Row keys and required values:** reporting_year; full_year, valid_precip, valid_temp,
  missing_days, reason
- **Source / comparison:** both; includes invalid years

**Declared filename under tables/: `annual_indices.csv`**

- **Row keys and required values:** reporting_year; total, wet_days, SDII, Rx1day,
  Rx5day
- **Source / comparison:** both

**Declared filename under tables/: `monthly_values.csv`**

- **Row keys and required values:** date, reporting_year, calendar_month; total,
  reference_mean, anomaly, temp_mean, usable flags
- **Source / comparison:** both

**Declared filename under tables/: `precip_climatology.csv`**

- **Row keys and required values:** calendar_month; mean, p10, p90, n
- **Source / comparison:** both

**Declared filename under tables/: `temp_climatology.csv`**

- **Row keys and required values:** calendar_month; mean, p10, p90, n
- **Source / comparison:** both; empty for absent temperature

**Declared filename under tables/: `rainfall_timing.csv`**

- **Row keys and required values:** reporting_year, fraction; day, valid flag
- **Source / comparison:** both; fractions .25/.5/.75

**Declared filename under tables/: `spi.csv`**

- **Row keys and required values:** date, scale; value, distribution, available, reason
- **Source / comparison:** both; scales 3/6/12

**Declared filename under tables/: `spi_fit_checks.csv`**

- **Row keys and required values:** calendar_month, scale; n, zeros, sw_gamma,
  sw_pearson3, skew, max_abs, mom_diff, p3_bound_hits, reason
- **Source / comparison:** both; reference fit retained

**Declared filename under tables/: `drought_events.csv`**

- **Row keys and required values:** scale, event_id; start, end, duration, severity,
  intensity, censored
- **Source / comparison:** both; scales 3/12

**Declared filename under tables/: `dry_spells.csv`**

- **Row keys and required values:** spell_id; complete spell length_days
- **Source / comparison:** both; dropped censored counts in metadata

**Declared filename under tables/: `dry_spell_exceedance.csv`**

- **Row keys and required values:** length_days; probability, n_complete_spells
- **Source / comparison:** both

**Declared filename under tables/: `anomaly_acf.csv`**

- **Row keys and required values:** lag_months; r, pairs
- **Source / comparison:** both; lags 1–12

**Declared filename under tables/: `trends.csv`**

- **Row keys and required values:** metric; slope, lo, hi, intercept, p, r1, factor, n,
  correction
- **Source / comparison:** both; total/wet_days/Rx1day

**Declared filename under tables/: `trend_sensitivity.csv`**

- **Row keys and required values:** metric, start_year; end_year, slope, lo, hi, p, n
- **Source / comparison:** both; total/Rx1day, minimum 15

**Declared filename under tables/: `pt_anomalies.csv`**

- **Row keys and required values:** precip_source, temperature_source, season,
  season_year; p, t, p_anom_pct, t_anom
- **Source / comparison:** both; empty when unavailable

**Declared filename under tables/: `homogeneity.csv`**

- **Row keys and required values:** series_kind, source_pair, metric, method;
  break_after, stat, p, n, seed, n_sim, reason
- **Source / comparison:** both; guarded insufficient/constant samples

**Declared filename under tables/: `agreement.csv`**

- **Row keys and required values:** source; mean_total, mean_wet_days, mean_sdii,
  n_common_valid_years
- **Source / comparison:** comparison only

**Declared filename under tables/: `agreement.md`**

- **Row keys and required values:** same agreement table, common valid year list,
  support and qualification caveats
- **Source / comparison:** comparison only

`diagnostics.json` has schema_version 1; resolved settings; input paths and content
hashes; source IDs/labels; extraction span and catalogue lineage; reported/effective
units; basin cell counts; reporting/calendar conventions; requested/actual
display/reference periods; exact valid/common years; reference fit counts; qualification
notices; unavailable products/reasons; spell/event censoring counts; anomaly colour
bounds; and every produced relative path. Its six families start as prototype-tested
only after ported tests pass; Ntoum exercise and qualification status are separate
fields, never inferred from run success. Include the scientific limitations below.

`figure_captions.json` has schema_version 1 and entries keyed by relative standard PNG
basename/path, with optional captioned PNG paths, unnumbered caption text, contributing
source IDs, period, reference, support, encoding, method details, availability and
caveats. Markdown exposes the same text for a report author, with filename headings.
`diagnostic_captions.py` is the sole caption formatter; JSON, Markdown and captioned
exports reuse its text. New standard figures have no bottom descriptive paragraph.
Existing figure footers remain unchanged; their support/resolution warning is carried
once in each new caption/metadata entry, not duplicated in the optional caption band.

Both JSON files are retained machine-readable records under `D/_engine/`, not disposable
cache. All recorded output paths and caption keys resolve from the diagnostic root `D`,
not the JSON file's parent directory. Writers and Snakemake declarations use the same
paths. `D/figure_captions.md` remains the user-facing reference and includes each
figure's periods, data support, availability, method caveats and scientific
qualification notice, so users can interpret figures without opening JSON. The Markdown
is generated from the same caption records and is not maintained independently.

### D5. Single declaration source and Snakemake mapping

All new modules live under `blueearth_cst/climate_analysis/`:

**Module: `diagnostics.py`**

- **Responsibility:** selected pure numerical functions, adapted and tested; no
  Snakemake objects

**Module: `diagnostic_outputs.py`**

- **Responsibility:** closed table/figure inventory, capability predicates, and exact
  paths used by declaration and writers

**Module: `diagnostic_settings.py`**

- **Responsibility:** pure closed settings parser; resolved defaults without mutating
  composed config

**Module: `diagnostic_tables.py`**

- **Responsibility:** gap-preserving basin adapter, period-specific compute, CSV/JSON
  I/O

**Module: `diagnostic_figures.py`**

- **Responsibility:** figures from retained plot-ready tables; family-local layout/style

**Module: `diagnostic_maps.py`**

- **Responsibility:** native-grid annual fields and lab-derived spatial-map rendering

**Module: `diagnostic_captions.py`**

- **Responsibility:** recoverable scientific captions independent of figures

**Module: `compute_climate_diagnostics.py`**

- **Responsibility:** 0.04 script glue

**Module: `plot_climate_diagnostics.py`**

- **Responsibility:** 0.04b script glue

**Module: `compare_climate_diagnostics.py`**

- **Responsibility:** 0.05 script glue and common-period table/figure production

Use `diagnostic_source_outputs(store_dir, source, settings)` and
`diagnostic_comparison_outputs(comparison_dir, sources, settings)` returning named
compute/render path sets. Derive every figure basename through `figure_filename`.
Writers receive these path sets, never rebuild stems. Tests assert exact recursive
output-file equality and rule declaration equality.

**Rule number/name: 0.04 `compute_climate_diagnostics_<source>`**

- **Declared inputs:** own extracted climate_nc + basin_cells; source orography for
  derived PET; subbasins when enabled; settings in params
- **Declared outputs / writer:** daily_basin + 17 plot-ready CSVs +
  annual_climatology.nc + diagnostics.json; optional subbasin tables; compute script

**Rule number/name: 0.04b `plot_climate_diagnostics_<source>`**

- **Declared inputs:** own 0.04 table/metadata outputs; all candidates'
  monthly_values/metadata and map fields for pooled bounds; spatial overlays
- **Declared outputs / writer:** capability-selected source PNGs + both caption files +
  optional captioned/subbasin PNGs; plot script

**Rule number/name: 0.05 `compare_climate_diagnostics`**

- **Declared inputs:** each source's daily_basin + diagnostics.json (full native
  series/lineage)
- **Declared outputs / writer:** 17 common-period plot-ready CSVs + agreement.csv/.md +
  diagnostics.json + selected comparison PNGs + captions/optional variants; compare
  script

0.05 recomputes **period-dependent** climatologies, trends, sensitivity, ACF, spells and
event tables using the same pure computation functions; it does not filter full-record
aggregates. SPI/reference means are computed from the full series before display
clipping. A read-only specialist suggested computing both full/common sets in 0.04; this
design instead keeps the single-source job independent, retaining daily data so the
comparison owns its period. This costs some repeated fits but avoids coupling every
source job to every other store. Only the source rendering jobs wait for all candidates'
monthly anomaly tables to establish the shared colour scale; single-source computation
stays independent.

Replace the WF0 0.04/0.05 producer registrations and add 0.04b through the current
RuleRegistry; keep other rule numbers unchanged. Register 0.05 only for >1 declared
source. Add all new terminal output paths to WF0_TERMINALS so gathers await tables,
captions and figures; no logs are stranded. WF0_TARGETS includes the new terminals. No
one-source comparison directory/job or agreement table is introduced.

Capability absence known at parse time omits its figure (CHIRPS temp/own P–T) and
records the reason. Data insufficiency known only at execution produces a clearly
labelled unavailable panel for every declared PNG, with identical availability notices
in captions/JSON. No common valid years means no numerical agreement claim; no temporal
overlap means unavailable comparison panels, not an own-period overlay. Empty events
mean "no events", distinct from failed SPI.

For default ERA5/CHIRPS this declares 55 canonical standard forms, 55 PNG files;
captioned_figures=true adds another 55 files. Source compute: 20 files/source; source
render: 2 caption files plus selected images. Comparison: 20 table/ metadata files, 2
caption files plus selected images. Counts are verification consequences of the
inventory, not hardcoded caps.

### D6. Visual contract

Use local `rc_context`, retain the shared unit conversion/600-DPI PNG export. Shared
typography currently starts at 8 pt/7 pt ticks/6.5 pt legend; the new family
deliberately uses the accepted 7 pt axes/titles and 6 pt ticks/legends/captions. No
shared rcParams or style constant changes.

| Layout | Physical canvas |
|---|---|
| One panel | 140 × 80 mm |
| Two vertical source panels (coverage/anomaly/SPI) | 180 × 110 mm |
| Two side-by-side panels (events/sensitivity) | 180 × 86 mm |
| Three interval panels (slopes) | 180 × 80 mm |
| Four seasonal panels (P–T) | 180 × 142 mm |

Outer constrained-layout padding starts at 4 mm horizontal/3 mm vertical. All four plot
boundaries are #c6d2d8 at 0.9 pt; grid #e6edef at 0.6 pt. Use horizontal x labels,
labelled five-year heatmap ticks plus intervening-year ticks, panel letters, short
legends/axes, bottom-aligned short right colourbars with horizontal title, and direct
in-axes series slopes with no trend legend key. ERA5/CHIRPS labels are ERA5/CHIRPS v2.0;
identity colors #236b8e/#bf6a3c. Use seven-class RdBu dry-red/wet-blue and gray
unavailable cells. Anomaly bounds are computed once from pooled full-series anomalies of
declared sources and recorded; source/comparison/caption variants share them.
Single-source renders derive the same rule locally. No silent source-count cap;
supported configured sources all render, with extra stacked panels sized and reviewed
explicitly.

Preserve mean/10–90% bands, timing mean dots/day labels + white median ticks, observed
annual extremes, censored event tint, log dry-spell exceedance, no ACF significance
band, and filled/hollow trend evidence. Caption variants reserve an added bottom band
and preserve the plotting canvas/type scale; review final exports for clipping.
Fit-check canvas is a declared density exception with one row/source/distribution; panel
letters and short titles, detailed tests in caption. Sensitivity has panel letters (the
lab function's older titles lack them).

## Validation and acceptance after Gate 1

1. Port known-answer tests: completeness/infill, reporting labels, Rx5day boundaries,
   observed extremes, censoring, SPI moments/zeros/fit failures, McKee events, Sen vs
   scipy, Yue–Wang AR(1), sensitivity/P–T, break tests. Add adapter/contract tests for
   absent temp, source order, short/empty reference, all-zero/constant data, no overlap,
   internal gaps, non-January SPI axes, exact mask matching, single-source declarations,
   and declaration/writer equality.
2. Focused existing figure naming/source/comparison tests; target rule-registry
   log/benchmark and config-snapshot tests affected by new rules/settings.
3. Ntoum regression once per diagnostics change. Re-measure lab retained tables
   read-only; compare exact yearly totals/daily basin series under matched data, masks,
   year convention, settings and spans. 2000–2016 mean annual P reference: ERA5 2721.9
   mm, CHIRPS 2524.8 mm. 1990–2020 Rx1day slope/p reference: ERA5 +7.1 mm/decade / .006;
   CHIRPS +10.0 / .002. Slope tolerance .1 mm/decade, p .001; daily float32 rounding
   about 1e-4 mm/day. The accepted PNG set displays 1991–2020: do not confuse it with
   the 1990 trend regression.
4. Value-neutral check uses matched fresh rapid cases and existing numerical products,
   without the stale baseline manifest. Render agreed new source/ comparison PNGs and
   approved captioned variants, inspect intended size, unavailable cases, margins and
   bar placement. Expose local PNG artifacts for owner inspection; do not publish them
   externally. Report paths against the declaration. Document every difference from lab
   values/layout/availability in a Results delta (including source-only P–T policy).
5. Before implementation commit: `pixi run pytest tests/test_cli.py`, `pixi run lint`,
   `pixi run format-check`; rapid WF0 DAG dry-run and targeted execution from this
   BlueEarth lane. Gate logs go to .tmp/scratchpad after confirming ignore. No BlueEarth
   workflow runs from the lab.
6. Commit verified work on this branch. Landing requires separate approval, then the
   live batch ladder's test-fast and applicable test-full/test-e2e gates; no
   landing/push/publication in this task. The design-only commit uses a diff check, not
   workflow tests.

Acceptance requires Gate 1 recorded, every declared output written, source temperature
honesty, falsifiers passing, documented method/status/limits, changed-file inventory,
rung-by-rung report, lab/toolbox regression table and Results delta. If matched old
numerical outputs change, stop and diagnose; rollback is a branch revert after
preserving evidence.

## Scientific status and required limitations

The lab families are prototype-tested and real-data exercised on Ntoum; **not
scientifically qualified**. Integration does not improve that status. Toolbox docs must
carry the following lab section unchanged:

- Input homogeneity is unverified. CHIRPS gauge density and ERA5's assimilated
  observations change over time, which can create spurious trends in extremes. The
  Rx1day increase of about 7–10 mm/decade over 1990–2020 in both products survives
  start-year, leave-one-out and multiple-testing checks, but the products disagree on
  which years are extreme (r = 0.29). Treat it as provisional until compared with a
  homogeneous station record or other products (MSWEP, GPCC).
- Relative homogeneity (`pettitt`, `snht` on ERA5 − CHIRPS differences, 1990–2020) finds
  no break in annual P, wet days, SDII, Rx1day or Rx5day (p = 0.26–0.73). The test is
  weak here: the Rx1day difference has an SD of 35 mm, so a step equal to the whole
  trend (about 22 mm) is detected only about 26% of the time (80% power needs about
  45–50 mm). The absence of a break therefore does not rule out an artefact of trend
  size. Each product alone shows an Rx1day change point near 2005–2006 (Pettitt p =
  0.035 ERA5, 0.008 CHIRPS); two differently built products agreeing on its timing
  weakly supports a real change, but does not separate a step from a gradual trend.
- No station data are available, and the toolbox catalog has no other daily
  precipitation product for this region (SM2RAIN-ASCAT is monthly, 2007–2020). An
  independent check needs an approved download (IMERG from 2000, MSWEP from 1979).
- ERA5 short-scale SPI misfit (negative skew) overstates dry extremes in flagged months.
- CHIRPS is staged only from 1990; a 1981–2020 window needs a wider clip.
- Source agreement is not accuracy; no independent observations were used.

## Additional output contracts and revision notes

### Owner-directed output revision

The proposed new diagnostic family uses PNG only, including captioned copies. Shortened
contexts match the [proposed tree/layout](design.md#5-proposed-tree). The four-field grammar is preserved;
existing WF0 plot outputs are retired; new contexts identify the diagnostic while
registered definitions and captions specify its visual form. Update the controlled
vocabulary and its plot-form requirement for this new family at implementation. Gate 1
approval of the full design was recorded after these revisions; see the gate record.

Keep the [proposed tree/layout](design.md#5-proposed-tree) current whenever this task changes file
placement, output names, formats, counts or conditional availability. Update it in the
same revision as the design or implementation, distinguishing proposed paths from
implemented paths so the owner can inspect the current layout quickly.

### Owner-directed optional subbasin figures

WF0-owned T2 boolean `subbasin_figures` defaults to `false`. When enabled, the canonical
source and multisource comparison renderers produce precipitation `monthly_clim_band`
and `annual_trend_ts` views per subbasin, plus genuine temperature `monthly_clim_band`
views where supported. Use the four-field grammar with `subbasin_<id>_avg`, under
`D/figures/subbasins/`; optional captioned copies live under
`D/figures/captioned/subbasins/`. Declare runtime directories because delineation
supplies the IDs. Retain corresponding subbasin plot-ready tables under
`D/tables/subbasins/`, declared by computation/comparison rules only when enabled. Never
revive old monthly-box or annual_ts renderers.

With the option off, omit these directories from declarations and targets and skip their
calculations/rendering. Spatial-foundation products and map overlays remain available.
Previously generated plots are not deleted. WF1 keeps its existing behavior. Test
default/false and true declarations and renders, single-source behavior, and unchanged
WF1 source-plot behavior.

### Owner-directed canonical replacement revision

The owner superseded the additive design: only the new system plots WF0. The lab spatial
references were inspected read-only; lab `git status --short` was clean at this
inspection (no lab commit is cited). The complete revised design and output inventory
received Gate 1 approval after these revisions; implementation is now authorized.

## Session decision-process record — 2026-10-06

This sequence records owner direction and its consequences, not approval of the complete
implementation. The current normative contracts are D1–D6 and the owner-directed
revisions above.

**Sequence: 1**

- **Decision and reason:** Provide a static affected project tree for quick inspection.
- **Consequence / superseded proposal:** Added `project-tree.md`; layout becomes a
  concrete review surface beside the prose design.

**Sequence: 2**

- **Decision and reason:** Make layout/tree and explicit user-facing changes part of
  generic Gate 1.
- **Consequence / superseded proposal:** Canonical design guidance now requires
  annotated paths, new artifacts, naming and compatibility changes, and the owner's
  recorded review.

**Sequence: 3**

- **Decision and reason:** Shorten verbose figure contexts while preserving the
  toolbox's four-field syntax.
- **Consequence / superseded proposal:** Replace descriptive context stems with
  controlled diagnostic names; retain canonical variable names, `comparison`, and
  spatial scope. Register visual meaning in definitions and captions.

**Sequence: 4**

- **Decision and reason:** Produce PNG only; PDF is unnecessary for current use.
- **Consequence / superseded proposal:** Remove PDF declarations and caption paths,
  recalculate output counts, and align tree and design.

**Sequence: 5**

- **Decision and reason:** Keep the tree continuously updated.
- **Consequence / superseded proposal:** Treat it as the current inspection view; update
  it with relevant design/implementation revisions and distinguish proposed from
  implemented paths.

**Sequence: 6**

- **Decision and reason:** Make subbasin figure fan-out optional, off by default.
- **Consequence / superseded proposal:** Add WF0 opt-in setting and conditional
  declarations. After canonical replacement, the opt-in renders new views; it does not
  revive the old system. Map boundary overlays remain independent.

**Sequence: 7**

- **Decision and reason:** Explain the three metadata/caption files before settling
  placement.
- **Consequence / superseded proposal:** Establish contents, consumers and purpose:
  diagnostic provenance/status, machine caption records, and readable report captions.

**Sequence: 8**

- **Decision and reason:** Review `_engine/` precedents and place both JSON files there.
  Users find JSON harder to use.
- **Consequence / superseded proposal:** Retain machine records under each diagnostic
  root's `_engine/`; keep `figure_captions.md` at the root with interpretation and
  scientific caveats. This supersedes root-level JSON placement.

**Sequence: 9**

- **Decision and reason:** Explain the proposed rules and inventory existing 0.04 plots.
- **Consequence / superseded proposal:** Exposed the additive proposal's duplicate
  old/new plotting families and its execution organization. Source compute/render
  separation supports rerendering; comparison remains combined.

**Sequence: 10**

- **Decision and reason:** Make the new system WF0's only plotting system; adopt the lab
  spatial map structure.
- **Consequence / superseded proposal:** Retire old WF0 plotting producers, monthly
  boxes and plain annual/comparison lines. Replace source maps; preserve WF1's separate
  contracts. Revised proposal uses 0.04 compute, 0.04b render, 0.05 comparison and 55
  default PNGs. PET map styling is a proposed extension, not a lab-qualified reference.

**Sequence: 11**

- **Decision and reason:** Improve generic design-scoping and design-document from this
  process.
- **Consequence / superseded proposal:** Surface replacement scope, artifact
  audience/placement, naming/formats/defaults and execution/rule changes early; keep
  review surfaces synchronized and preserve decision rationale/status.

The initial proposal assumed additive preservation of old WF0 figure contracts. The
owner later explicitly authorized their replacement. This material scope change belongs
in the revised Gate 1 framing; agreement on its components does not establish scientific
qualification or approve the complete design.

### Owner-directed single-document layout revision

The proposed tree is embedded in [design.md](design.md#5-proposed-tree). The separate
`project-tree.md` is removed; maintain that section with the design.
This supersedes the earlier separate-tree decision, retaining its quick-review
purpose and all proposed layout/output details.

## Inspection evidence

The reference is `C:/Users/taner/workspace/wf0-lab` **working tree**, inspected
read-only on 2026-10-06. `git status --short` showed modified handoff docs,
`figures.py`, input/report/runner code and tests; `captions.py` and the caption snapshot
were untracked. A lab commit alone cannot identify the accepted state. The five
requested handoff documents were read in order. Diagnostics, figure, caption and
relevant test implementations were inspected. All 16 standard compare PNGs were visually
inspected; the 16 captioned names were inventoried and the SPI/annual-series captioned
exports inspected as layout references.

BlueEarth lane: `session-2`, `feat/wf0-plotting-improvements`; clean at entry, HEAD
identical to local main (`7704e7e2`), so no synchronization change needed. The current
board was inspected in the primary checkout; its existing forcing-selection evaluation
item concerns observations/Budyko, not this lab integration. This record creates no
board item and changes no main-board state.

Rule 0.04 uses `source_plot_rule.py` and `plot_climate_source.py`, shared with WF1. Per
source it writes maps, annual series and monthly boxes for the genuine variables from
`source_climate_vars`, plus runtime subbasin figures. ERA5 has precip/temp/PET products;
CHIRPS has precipitation products even when its forcing store contains ERA5 companions.
Rule 0.05 writes `dataset_comparison.csv/.md`, annual series and monthly climatology
lines for variables carried by at least two sources, plus subbasin figures. ERA5/CHIRPS
therefore has two basin comparison PNGs and no temperature comparison.

The owner has directed replacement of WF0's existing plotting system. Old monthly boxes,
annual time series and comparison climatology lines are retired from WF0 targets. The
newer percentile-band and trend-series views supersede them. Existing source maps are
replaced by the lab spatial-map structure.


## Related

- `C:/Users/taner/workspace/wf0-lab/docs/blueearth-integration-brief.md`
- `C:/Users/taner/workspace/wf0-lab/docs/integration-notes.md`
- `C:/Users/taner/workspace/wf0-lab/docs/figure-rules.md`, Current figure polish
- `C:/Users/taner/workspace/wf0-lab/docs/compare-figure-captions.md`
- `C:/Users/taner/workspace/wf0-lab/docs/diagnostic-notes.md`
- `dev/reference/wf0-figure-filename-rule.md`; `dev/reference/workflows/rule-index.md`
- `dev/records/decisions/0006-retire-subcatchment-climate-plots.md`
- `AGENTS.md`, validation ladder and task-lane rules

