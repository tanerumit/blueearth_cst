"""Default formulas with native pandas missingness and explicit water years."""

from blueearth_cst.metrics.contract import MetricResult
from blueearth_cst.metrics.extremes import reduce_bundle
from blueearth_cst.metrics.series import response_frame


def annual_summary(metric, series, context) -> MetricResult:
    """Average the declared water-year summary, retaining partial blocks."""
    frame = response_frame(series)
    statistic = metric.calculation_parameters["statistic"]
    annual = frame.resample(context.anchor)
    blocks = (
        annual.quantile(0.95) if statistic == "p95" else getattr(annual, statistic)()
    )
    return MetricResult(blocks.mean())


def annual_rolling7_extreme(metric, series, context) -> MetricResult:
    """Reduce complete trailing seven-day windows, including across blocks."""
    blocks = response_frame(series).rolling(7).mean().resample(context.anchor)
    return MetricResult(
        getattr(blocks, metric.calculation_parameters["extreme"])().mean()
    )


def annual_min7_mean_ratio(metric, series, context) -> MetricResult:
    """Average each water year's minimum-seven-day / mean-flow ratio."""
    frame = response_frame(series)
    minimum = frame.rolling(7).mean().resample(context.anchor).min()
    return MetricResult((minimum / frame.resample(context.anchor).mean()).mean())


def reference_month_mean(metric, series, context) -> MetricResult:
    """Use one explicitly resolved reference month, never select per response."""
    which = metric.calculation_parameters["which"]
    reference = context.reference
    if (
        reference is None
        or reference.which != which
        or reference.month not in range(1, 13)
    ):
        raise ValueError("explicit resolved wet/dry month reference required")
    frame = response_frame(series)
    return MetricResult(
        frame[frame.index.month == reference.month]
        .resample(context.anchor)
        .mean()
        .mean()
    )


def pooled_return_level(metric, series, context) -> MetricResult:
    """Use the qualified estimator and preserve screening/refusal exceptions."""
    values, evidence = reduce_bundle(
        metric,
        series,
        expected_run_ids=context.expected_run_ids,
        anchor=context.anchor,
        validation=context.validation,
    )
    return MetricResult(
        values, metadata={"evidence": evidence, "estimator": "gf15-lmoments-c/1"}
    )


PARAMETERS = {
    annual_summary: {
        "variable": ("q", "aet", "gwr", "precip", "snow", "overland_flow"),
        "statistic": ("mean", "sum", "max", "min", "p95"),
    },
    annual_rolling7_extreme: {"extreme": ("min", "max")},
    annual_min7_mean_ratio: {},
    reference_month_mean: {"which": ("wet", "dry")},
    pooled_return_level: {"kind": ("annual_max", "rolling_annual_min")},
}


def validate(function, parameters) -> None:
    """Conditional variable controls remain owned by the formula's set."""
    if function is annual_summary:
        accepted = {
            "q": ("mean", "max", "min", "p95"),
            "aet": ("sum",),
            "gwr": ("sum",),
            "precip": ("sum",),
            "snow": ("max",),
            "overland_flow": ("mean",),
        }
        if parameters["statistic"] not in accepted[parameters["variable"]]:
            raise ValueError(
                f"statistic: accepted for {parameters['variable']}: {accepted[parameters['variable']]}"
            )


def normalize_parameters(function, parameters):
    """Keep the historic fixed-seven-day selector as a local declarative alias."""
    if function is pooled_return_level and parameters == {
        "kind": "rolling7_annual_min"
    }:
        return {"kind": "rolling_annual_min"}
    return parameters
