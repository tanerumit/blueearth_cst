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
them directly from WF1's historical model discharge. In `project_config_simulate_system.yml`, use:

```yaml
indicator_sets:
  - set: crop-water
    summer_low_flow_days:
      thresholds:
        baseline_quantile: {}
```

The registered `season: summer` is inherited. WF4 binds the rule to its project's
`models/hydrology/wflow` model and derives source identity from the historical artifacts.
Use `model_root` to select a model directory; relative paths resolve beside the set file.
`source_id` labels the historical discharge in threshold provenance; it does not select another dataset.
If omitted, these use the project's model and the label `wf1-historical-model-discharge`.
Preparation reads `run_default/output.csv` with
`wflow_sbm.toml`, verifies the historical forcing binding (`inmaps_historical.nc`), and refuses missing
or incompatible inputs. With all workflows enabled, startup validates the rule without opening
historical output; preparation happens at the WF4 boundary after upstream execution. A combined
dry-run with WF1 enabled inspects upstream workflows and reports WF4 Q90 preparation as pending
when historical CSV/TOML inputs are missing. Its data-dependent WF4 DAG cannot then be inspected;
no thresholds or calculation identity are invented. A direct WF4 dry-run, or one with WF1 disabled,
requires existing historical inputs and names the required WF1 historical run if they are absent.
Existing malformed inputs remain errors. Neither synthetic observations nor future scenario discharge
supplies this reference. Baseline preparation also works
for indicators-only operations and does not start Wflow. The resolved values are fixed across scenarios.

The default is Q90 exceedance: `quantile: 0.90`, `convention: exceedance` means non-exceedance p=0.10.
Omit `years` (as in this minimal example) or use `years: all` to request every historical calendar
year found in the discharge labels, including partial edge years which are reported and excluded
when their reference period is incomplete. An explicit list such as `years: [1999, 2000, 2001]`
restricts the request; unavailable requested years are also reported as excluded. No reference
period is inferred from the project's climate window.
For Q80 use 0.80 exceedance, or equivalently 0.20 nonexceedance. Probabilities must lie strictly between
0 and 1. `reference_period: summer` pools complete May–October periods; `annual`
pools complete calendar years. This changes the reference distribution only: the indicator still
counts May–October low-flow days. Choose periods for the basin rather than treating this season as a
global crop calendar. Supported quantile methods are linear (default), lower, higher, midpoint and nearest.
The Python helper `prepare_baseline_qcrit` accepts the same rule settings and validated historical Q.

Derived records retain source identity and CSV/TOML SHA-256 digests, baseline run identity, requested
years (`years`), discovered calendar years (`discovered_years`), selection mode (`year_selection`:
`all` or `explicit`), reference period, quantile convention and probability, interpolation method,
included/excluded periods, sample count and per-year expected/finite-day coverage. Incomplete or nonfinite
periods are excluded per location; no complete period is an error. Inspect exclusions before scientific use.
These values and provenance enter calculation identity, so changing inputs or rules changes identity.
Omission and `years: all` have the same resolved identity. An explicit list records explicit intent
even if it happens to match the discovered years.
Explicit threshold records specify `value`, `source_id`, `years`, `used_summers`, `excluded_summers`,
`method: supplied operational` and `units: m3 s-1`.
Do not mix explicit thresholds and a baseline rule. A zero threshold makes a strict low-flow count
uninformative. The bundled registry uses an empty threshold mapping so case preparation must supply it
through a case-specific `selection.registry.overrides.summer_low_flow_days` mapping before a complete
`crop-water` evaluation. Bind the custom file with `indicator_set_definitions.crop-water.config_path`.
`AVAILABILITY` reports an empty mapping, or a retained Q location without a record, as
`missing_parameter:thresholds`: strict WF4 evaluation refuses it, partial evaluation publishes those
locations as unavailable, and `indicator_selection` can exclude the indicator.

`period_values` and `period_summary` diagnostics retain period status, coverage, thresholds, eligible
PET days and AET-above-PET counts. No crop calendar, yield, irrigation demand or damage is inferred.
