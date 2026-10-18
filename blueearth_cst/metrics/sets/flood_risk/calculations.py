"""Opt-in discharge hazard quantiles under the production qualification gate."""

import math

from blueearth_cst.metrics.contract import MetricResult
from blueearth_cst.metrics.extremes import reduce_bundle


def flood_return_level(metric, series, context) -> MetricResult:
    """Fit member-local maxima; never widen the supplied qualification domain."""
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


def _return_period(value) -> bool:
    """must be a finite return period greater than one year"""
    return type(value) in (int, float) and math.isfinite(value) and value > 1


PARAMETERS = {flood_return_level: {"return_period": _return_period}}
