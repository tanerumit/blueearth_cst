# eflow-erfa

This independent indicator set ports the fixed defaults of `eflowrisk`'s `calculate_flow_metrics()`
and `summarize_flow_metrics()` from `eflow-risk-tool`. Its 35 annual metrics yield 70 indicators:
`q_<R metric key>_med` and `q_<R metric key>_iqr`. The callable is
`erfa_annual_statistic/1`, with explicit `metric` and `statistic` parameters.

Source revision: `16ad6f424bfa5425ce0c0403471482b5e7a5cdb4`.
The [R oracle provenance](../../../../tests/data/eflow-erfa-r-oracle.md) records the independent
reference calculations and reproducible numerical checks.

The five groups are high flow (8 metrics), monthly flow (12), low flow (8), rate/frequency of change
(4), and intermittency (3). Registrations contain descriptions, group labels and units. This is the
package's IHA-style metric set, not a claim of exact reproduction of every IHA/ERFA implementation.
Ecological risk classification is outside this set.

The configured water-year anchor controls annual blocks. Years require 90% finite calendar days and
monthly means require 80%, with leap days included. Each result carries `erfa_year_coverage`
diagnostics with run, location, year, finite and expected days, and retained status. No retained year
raises an error, matching the R summary rejection. Missing values are excluded separately by metric;
all-missing metrics remain undefined. Group reductions average run summaries with equal weights and
propagate undefined members.

High and low pulses use strict comparisons against per-record global 0.9 and 0.1 type-7 quantiles.
Threshold estimation includes the full supplied record, including dropped years, and requires ten
finite observations. Baseline and scenario records therefore estimate their own thresholds. Zero
sequences use discharge <= 0. Runs split at water-year boundaries and missing values; absent runs
have zero count and duration, and absent zero runs have undefined timing.

Trailing complete 3/7/30/90-day means and daily differences cross water-year boundaries. No smoothing
or deadband is applied; fall rates are positive magnitudes. Timing uses one-based water-year days and
the first occurrence of an extreme or longest zero run. Timing medians and IQRs are linear, not
circular. Annual summaries use the median and type-7 IQR. Counts are dimensionless, timing/duration
use days, discharge uses m3 s-1, and change rates use m3 s-1 d-1.

The neutral response contract requires a complete daily Gregorian grid with NaNs for missing values.
Unlike the R package's gap warning, omitted dates are rejected before calculation. Optional R modes
(alternative threshold scopes, zero cutoffs, smoothing, deadbands and completeness fractions) are
not exposed. `checks.py` independently reconstructs scalar windows, runs and order statistics;
it does not invoke production calculations.
