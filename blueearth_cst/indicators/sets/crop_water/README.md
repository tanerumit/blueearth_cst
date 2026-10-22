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

The low-flow declaration requires fixed, location-keyed `thresholds` before evaluation. Each record
contains `value`, `source_id`, `years`, `used_summers`, `excluded_summers`, `method` and `units`. Derive
the fallback as the linear 0.10 non-exceedance quantile of daily Q pooled across complete historical
baseline summers. `prepare_baseline_qcrit(historical_q, source_id=..., years=...)` produces that record
from validated retained daily Q series; inspect the selected years and copy the mapping into the case
selection. A supplied operational threshold is also supported. Thresholds and provenance enter
calculation identity; scenarios never refit them. A zero threshold makes a strict low-flow count
uninformative. The bundled registry uses an empty threshold mapping so case preparation must supply it
through a case-specific `selection.registry.overrides.summer_low_flow_days` mapping before a complete
`crop-water` evaluation. Bind the custom file with `indicator_set_definitions.crop-water.config_path`.
`AVAILABILITY` reports an empty mapping, or a retained Q location without a record, as
`missing_parameter:thresholds`: strict WF4 evaluation refuses it, partial evaluation publishes those
locations as unavailable, and `indicator_selection` can exclude the indicator.

`period_values` and `period_summary` diagnostics retain period status, coverage, thresholds, eligible
PET days and AET-above-PET counts. No crop calendar, yield, irrigation demand or damage is inferred.
