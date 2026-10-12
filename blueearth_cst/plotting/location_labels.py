"""Location labels shared by climate and spatial map renderers."""

from collections.abc import Mapping
from typing import Any

import pandas as pd


def location_label(properties: Mapping[str, Any], column="station_name") -> str:
    """Prefer the selected label, falling back to the Wflow ID for station names."""
    columns = (
        (column, "wflow_id", "location_code") if column == "station_name" else (column,)
    )
    for key in columns:
        value = properties.get(key)
        if value is not None and not pd.isna(value):
            text = str(value).strip()
            if text:
                return text
    return ""
