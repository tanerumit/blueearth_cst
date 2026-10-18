"""Optional flow-regime formulas, with production annual means."""

from blueearth_cst.metrics.contract import MetricResult
from blueearth_cst.metrics.series import response_frame


def annual_rolling_extreme(metric, series, context) -> MetricResult:
    """Mean water-year extreme of complete trailing N-day means."""
    parameters = metric.calculation_parameters
    blocks = (
        response_frame(series)
        .rolling(parameters["window"])
        .mean()
        .resample(context.anchor)
    )
    return MetricResult(getattr(blocks, parameters["extreme"])().mean())


def annual_daily_change(metric, series, context) -> MetricResult:
    """Mean water-year rise/fall magnitude; zero differences are excluded."""
    change = response_frame(series).diff()
    if metric.calculation_parameters["direction"] == "rise":
        change = change.where(change > 0)
    else:
        change = (-change).where(change < 0)
    return MetricResult(change.resample(context.anchor).mean().mean())


def full_period_mean(metric, series, context) -> MetricResult:
    """Arithmetic mean over retained days, without equal annual block weighting."""
    return MetricResult(response_frame(series).mean())


PARAMETERS = {
    annual_rolling_extreme: {"window": (30, 90), "extreme": ("min", "max")},
    annual_daily_change: {"direction": ("rise", "fall")},
    full_period_mean: {},
}


def validate(function, parameters) -> None:
    """The production flow-regime suite includes only the three reviewed windows."""
    if function is annual_rolling_extreme and parameters == {
        "window": 90,
        "extreme": "max",
    }:
        raise ValueError(
            "window/extreme: accepted combinations: (30,min), (30,max), (90,min)"
        )
