# Crop-water screening set

`crop-water` selects ten indicators from six methods. Daily input labels denote interval ends. Winter is
1 November through 31 May, labelled by ending year; summer is 1 May through 31 October. The two
seasons overlap in May and are never summed. Annual net recharge uses 1 October through 30 September,
independent of the project's water-year anchor. Each scalar is the arithmetic mean of complete period
values. A missing value in any required daily series invalidates the period; partial edge periods are
reported and excluded. Irregular or absent timestamps are rejected at the response boundary.

| Method | Period calculation | Output |
| --- | --- | --- |
| Climatic deficit | Sum of daily `max(PET - P, 0)` | mm/season |
| Longest dry spell | Longest consecutive run with `P < 1 mm/day` | days |
| Low-flow days | Count of summer `Q < Qcrit` | days/season |
| Annual recharge | Sum of signed daily net `gwr` | mm/year |
| Relative ET deficit | `100 * (1 - sum(AET) / sum(PET))` | percent |
| ET limitation days | Count `AET/PET < 0.5` where `PET >= 1 mm/day` | days/season |

The ET ratio uses Wflow landscape AET and the model's reference PET. Vegetation coefficients and
evaporation components can affect their relationship; these are screening proxies, not calibrated crop
stress or damage estimates. Negative relative deficits are retained when AET exceeds PET. Low PET days
are excluded only from the daily ET count, not from paired completeness. No eligible PET day or zero
seasonal PET makes the corresponding ET period undefined.

Non-discharge inputs are daily subcatchment means before these calculations. This does not establish
agricultural-area or aquifer-specific conditions. `gwr` is signed net saturated-zone recharge, not gross
or pumpable recharge; whether return flows and canal leakage are represented depends on the model setup.
Q is a named outlet/gauge series and may describe drainage rather than irrigation supply.

The low-flow declaration requires fixed, location-keyed `thresholds` before evaluation. WF4 can prepare
them directly from WF1's historical model discharge. In a custom crop-water set file, use:

```yaml
schema_version: 1
id: crop-water
title: Crop-water with historical Qcrit
description: Fixed historical model-discharge thresholds
selection:
  registry:
    set: crop-water
    overrides:
      summer_low_flow_days:
        season: summer
        thresholds:
          baseline_quantile:
            model_root: /absolute/project/models/hydrology/wflow
            source_id: historical-model-era5
            years: [1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005]
            quantile: 0.90
            convention: exceedance
            reference_period: summer
            quantile_method: linear
```

`model_root` resolves against this set file. Preparation reads `run_default/output.csv` with
`wflow_sbm.toml`, verifies the historical forcing binding (`inmaps_historical.nc`), and refuses missing
or incompatible inputs. Run WF1 first; dry-runs also need its historical output. Neither synthetic
observations nor future scenario discharge supplies this reference. Baseline preparation also works
for indicators-only operations and does not start Wflow. The resolved values are fixed across scenarios.

The default is Q90 exceedance: `quantile: 0.90`, `convention: exceedance` means non-exceedance p=0.10.
For Q80 use 0.80 exceedance, or equivalently 0.20 nonexceedance. Probabilities must lie strictly between
0 and 1. `reference_period: summer` pools complete May–October periods for compatibility; `annual`
pools complete calendar years. This changes the reference distribution only: the indicator still
counts May–October low-flow days. Choose periods for the basin rather than treating this season as a
global crop calendar. Supported quantile methods are linear (default), lower, higher, midpoint and nearest.
The Python helper `prepare_baseline_qcrit` accepts the same rule settings and validated historical Q.

Derived records retain source identity and CSV/TOML SHA-256 digests, baseline run identity, requested
years, reference period, quantile convention and probability, interpolation method, included/excluded
periods, sample count and per-year expected/finite-day coverage. Incomplete or nonfinite periods are
excluded per location; no complete period is an error. Inspect exclusions before scientific use.
These values and provenance enter calculation identity, so changing inputs or rules changes identity.
Existing explicit records with `value`, `source_id`, `years`, `used_summers`, `excluded_summers`,
`method: supplied operational` (or legacy `linear p=0.10`) and `units: m3 s-1` remain supported.
Do not mix explicit thresholds and a baseline rule. A zero threshold makes a strict low-flow count
uninformative. The bundled registry uses an empty threshold mapping so case preparation must supply it
through a case-specific `selection.registry.overrides.summer_low_flow_days` mapping before a complete
`crop-water` evaluation. Bind the custom file with `indicator_set_definitions.crop-water.config_path`.
`AVAILABILITY` reports an empty mapping, or a retained Q location without a record, as
`missing_parameter:thresholds`: strict WF4 evaluation refuses it, partial evaluation publishes those
locations as unavailable, and `indicator_selection` can exclude the indicator.

`period_values` and `period_summary` diagnostics retain period status, coverage, thresholds, eligible
PET days and AET-above-PET counts. No crop calendar, yield, irrigation demand or damage is inferred.
