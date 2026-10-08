# -*- coding: utf-8 -*-
"""Pure WF2 suite folder/product contracts and configured-horizon parsing.

Folder declarations use distinct resolved analysis windows. Availability
tables decide which products are drawn; captions retain configured labels.
Scenario is the suite color channel; artists reuse WF0 publication tokens."""

from __future__ import annotations

import re
from collections.abc import Sequence

SCENARIO_COLORS = {
    "ssp126": "#003466",
    "ssp245": "#f69320",
    "ssp370": "#df0000",
    "ssp585": "#980002",
}

SUITE_PRODUCTS = {
    "F3.1": {"folder_kind": "full-period", "filenames": ("availability.png",)},
    "F3.4": {
        "folder_kind": "full-period",
        "filenames": ("trajectory-temperature.png", "trajectory-precipitation.png"),
    },
    "F3.4b": {
        "folder_kind": "full-period",
        "filenames": ("annual-temperature.png", "annual-precipitation.png"),
    },
    "F3.2": {
        "folder_kind": "period",
        "filenames": (
            "change-temperature.png",
            "change-precipitation-pct.png",
            "change-precipitation-abs.png",
        ),
    },
    "F3.3": {
        "folder_kind": "period",
        "filenames": (
            "seasonal-cycle-temperature.png",
            "seasonal-cycle-precipitation.png",
            "monthly-change-temperature.png",
            "monthly-change-precipitation.png",
        ),
    },
    "F3.5a": {
        "folder_kind": "period",
        "filenames": (
            "variability-ratio-temperature-sd.png",
            "variability-ratio-precipitation-cv.png",
        ),
    },
    "F3.5c": {"folder_kind": "period", "filenames": ("variability-member-ratios.png",)},
    "F3.6b": {"folder_kind": "period", "filenames": ("change-factor-cloud.png",)},
    "F5.1": {"folder_kind": "period", "filenames": ("sign-agreement.png",)},
    "combined-cloud": {
        "folder_kind": "full-period",
        "filenames": ("change-factor-cloud-combined.png",),
    },
}


def suite_folders(horizons, water_year_start="Jan", reference_window=(1985, 2014)):
    """One owned folder for each distinct resolved analysis window."""
    from blueearth_cst.projections.get_change_climate_proj import analysis_windows

    records = analysis_windows(horizons, water_year_start, reference_window)
    return [
        "full-period",
        *dict.fromkeys(f"period-{r['window_id']}" for r in records.values()),
    ]


def parse_horizon_period(period: Sequence[int] | str) -> tuple[int, int]:
    """Return one inclusive ``(start_year, end_year)`` horizon pair.

    R01 delivers ``future_horizons`` as lists (``[2070, 2090]``); pre-R01
    configs delivered comma-separated strings (``"2070, 2090"``). Both are
    accepted, because a project config written against either is still valid.
    """
    values = period.split(",") if isinstance(period, str) else list(period)
    if len(values) != 2:
        raise ValueError(f"horizon period must contain two years, got {period!r}")
    try:
        start, end = (int(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"horizon years must be integers, got {period!r}") from exc
    if start > end:
        raise ValueError(f"horizon start must not exceed end, got {start}-{end}")
    return start, end


def sanitize_horizon_name(name: str) -> str:
    """Sanitize a configured horizon name into a portable directory name.

    A horizon name is free text in the config, and it reaches the filesystem
    here. Anything outside ``[a-z0-9]`` collapses to a single hyphen, so a name
    that would otherwise produce an unopenable path on win-64 is caught at parse
    time rather than at the moment a figure is written.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")
    if not slug:
        raise ValueError(f"horizon name has no portable characters: {name!r}")
    return slug


def horizon_directory(name: str, period: Sequence[int] | str) -> str:
    """Return ``<sanitized-name>-<start>-<end>`` for one horizon.

    The years are in the directory name, not only the horizon's label, because
    a project that redefines ``far`` from 2070-2090 to 2060-2080 would otherwise
    overwrite the old figure in place and leave nothing saying the window moved.
    """
    start, end = parse_horizon_period(period)
    return f"{sanitize_horizon_name(name)}-{start}-{end}"
