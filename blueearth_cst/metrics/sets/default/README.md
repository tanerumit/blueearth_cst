# Default metrics

`registry.py` retains the production default metric names and declares fixed `ASSUMPTIONS`.
`calculations.py` owns formulas and callable-keyed `PARAMETERS`; `checks.py` computes independent expected
values. The complete authoring/input/result contract is in [the module README](../../README.md).

Annual means, maxima, minima, p95, basin totals, rolling-seven-day extrema, baseflow ratio and reference
month means retain native pandas missingness and partial-block weighting. The configured water-year anchor
defines blocks; January–December applies only to a January water year. Rolling windows cross water-year
boundaries, never member boundaries, and require seven nonmissing days. Reference months use pooled monthly
sums and explicit reference membership/location. No new warm-up is removed.

Return levels retain member-local annual maxima / rolling-seven-day annual minima, finite-block filtering,
max(ceil(T),10) sample screening, qualified estimator source verification and supplied probability-domain
gating. `rolling_annual_min` accurately describes the fixed seven-day calculation; the old
`rolling7_annual_min` selector remains a declarative compatibility alias. Annual maximum fits have no unused
rolling-window parameter. Fit-block counts differ from retained daily-input counts.

Run metrics support equal-weight member means with NaN propagation. Return levels pool blocks instead.
Units, reference behavior and accepted parameters appear next to each registration and formula.
