"""Location labels shared by climate and spatial map renderers."""

import cmath
import math
from collections.abc import Mapping
from decimal import Decimal
from typing import Any

import numpy as np

# pandas' missing-value sentinels, recognised without importing pandas.
_PANDAS_MISSING = {"NAType", "NaTType"}


def _missing(value: Any) -> bool:
    """None, NaN, NaT or a pandas NA scalar, as ``pandas.isna`` treats scalars."""
    if value is None or type(value).__name__ in _PANDAS_MISSING:
        return True
    if isinstance(value, float):
        return math.isnan(value)
    if isinstance(value, complex):
        return cmath.isnan(value)
    if isinstance(value, Decimal):
        return value.is_nan()
    if isinstance(value, (np.floating, np.complexfloating)):
        return bool(np.isnan(value))
    if isinstance(value, (np.datetime64, np.timedelta64)):
        return bool(np.isnat(value))
    return False


def location_label(properties: Mapping[str, Any], column="station_name") -> str:
    """Prefer the selected label, falling back to the Wflow ID for station names."""
    columns = (
        (column, "wflow_id", "location_code") if column == "station_name" else (column,)
    )
    for key in columns:
        value = properties.get(key)
        if not _missing(value):
            text = str(value).strip()
            if text:
                return text
    return ""
