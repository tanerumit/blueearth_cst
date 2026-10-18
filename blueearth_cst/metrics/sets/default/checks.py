"""Independent expected values; never call production calculations."""

import numpy as np

from blueearth_cst.metrics.checking import member_expectation, return_level_expected


def expected(metric, series, context, *, group=False):
    """Check declared water-year statistics using independent scalar locations."""
    method = metric.calculation_method
    if method == "pooled_return_level/1":
        return return_level_expected(metric, series, context)
    if method not in {
        "annual_summary/1",
        "annual_rolling7_extreme/1",
        "annual_min7_mean_ratio/1",
        "reference_month_mean/1",
    }:
        raise ValueError(f"missing independent check for calculation {method!r}")

    def scalar(daily):
        parameters = metric.calculation_parameters
        method = metric.calculation_method
        if method == "reference_month_mean/1":
            if context.reference is None:
                raise ValueError("check requires explicit reference month")
            daily = daily[daily.index.month == context.reference.month]
        if method == "annual_min7_mean_ratio/1":
            rolling = daily.rolling(7).mean()
            ratios = []
            means = daily.resample(context.anchor).mean()
            for label, block in rolling.resample(context.anchor):
                with np.errstate(divide="ignore", invalid="ignore"):
                    ratios.append(float(np.divide(block.min(), means.loc[label])))
            usable = [value for value in ratios if not np.isnan(value)]
            return float(np.mean(usable)) if usable else np.nan
        if method == "annual_rolling7_extreme/1":
            daily = daily.rolling(7).mean()
        values = []
        if method == "annual_summary/1":
            statistic = parameters["statistic"]
        elif method == "annual_rolling7_extreme/1":
            statistic = parameters["extreme"]
        else:
            statistic = "mean"  # reference-month arithmetic is fixed by this method
        for _, block in daily.resample(context.anchor):
            values.append(
                block.quantile(0.95)
                if statistic == "p95"
                else getattr(block, statistic)()
            )
        usable = [value for value in values if not np.isnan(value)]
        return float(np.mean(usable)) if usable else np.nan

    return member_expectation(metric, series, context, scalar, group=group)


def check_result(metric, series, result, context, *, group=False):
    """Verify estimator attribution separately from matching numerical values."""
    if (
        metric.grain == "bundle"
        and result.metadata.get("estimator") != "gf15-lmoments-c/1"
    ):
        raise ValueError("estimator metadata must identify gf15-lmoments-c/1")
