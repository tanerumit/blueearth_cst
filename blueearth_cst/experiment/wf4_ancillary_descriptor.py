"""WF4 physical description of retained preparation ancillary data."""

from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr

from blueearth_cst.experiment.content_identity import content_sha256
from blueearth_cst.experiment.forcing_descriptor import (
    _metadata_value,
    _missing_encoding,
    _spatial_description,
)


def describe_ancillary(path: Path) -> dict[str, Any]:
    """Observe a packaged NetCDF ancillary without a live catalog."""
    with xr.open_dataset(path) as ds:
        spatial = _spatial_description(ds, require_crs=False)
        variables = []
        for name in sorted(set(ds.data_vars) - {"spatial_ref"}):
            variable = ds[name]
            variables.append(
                {
                    "name": name,
                    "units": variable.attrs.get("units"),
                    "dimensions": list(variable.dims),
                    "attributes": _metadata_value(variable.attrs),
                    "missing_value": _missing_encoding(variable),
                    "missing_count": int((~np.isfinite(variable)).sum().item()),
                }
            )
        if not variables:
            raise ValueError("ancillary has no physical variables")
        return {
            "crs": spatial["crs"],
            "spatial_representation_sha256": content_sha256(spatial),
            "variables": variables,
        }
