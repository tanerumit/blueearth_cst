"""Shared Snakemake producer; identical scientific inputs for WF0 and WF1."""

from typing import Any

from blueearth_cst.shared.map_reference import (
    build_reference,
    publish_reference,
    reference_arguments,
)


def run(sm: Any) -> None:
    """Prepare independently from candidate stores and atomically publish JSON."""
    expected = reference_arguments(sm.params)
    record = build_reference(**expected)
    publish_reference(sm.output.reference, record, **expected)
    from blueearth_cst.shared.snake_utils import log_row

    log_row("Wrote historical map reference", module="maps")


if "snakemake" in globals():
    from blueearth_cst.shared.snake_utils import tee_to_log

    sm = globals()["snakemake"]
    with tee_to_log(sm.log[0]):
        run(sm)
