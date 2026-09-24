"""WF4 keeps one discharge series per model cell (t2609151118)."""

from __future__ import annotations

import numpy as np
import xarray as xr

from blueearth_cst.experiment.simulator_adapter import coincident_point_headers

COLUMNS = [
    {"header": "Q", "map": "outlets"},
    {"header": "Q", "map": "gauges_locations"},
    {"header": "gwr", "map": "subcatchment"},
]


def _static(tmp_path, gauge_cells):
    shape = (6, 6)
    outlets = np.full(shape, np.nan)
    outlets[4, 0] = 101
    gauges = np.full(shape, np.nan)
    for ident, (row, col) in gauge_cells.items():
        gauges[row, col] = ident
    subcatchment = np.ones(shape)
    subcatchment[:, 3:] = 2
    path = tmp_path / "staticmaps.nc"
    xr.Dataset(
        {
            name: (("y", "x"), values)
            for name, values in (
                ("outlets", outlets),
                ("gauges_locations", gauges),
                ("subcatchment", subcatchment),
            )
        }
    ).to_netcdf(path)
    return path


def test_a_gauge_on_the_outlet_cell_is_dropped_for_the_outlet(tmp_path):
    static = _static(tmp_path, {1010: (4, 0), 1020: (2, 2)})
    headers = ["Q_101", "Q_1010", "Q_1020", "gwr_1", "gwr_2"]
    assert coincident_point_headers(COLUMNS, headers, static) == {"Q_1010": "Q_101"}


def test_the_outlet_wins_whatever_the_header_order(tmp_path):
    static = _static(tmp_path, {1010: (4, 0)})
    headers = ["Q_1010", "Q_101"]
    assert coincident_point_headers(COLUMNS, headers, static) == {"Q_1010": "Q_101"}


def test_distinct_cells_and_area_maps_are_untouched(tmp_path):
    static = _static(tmp_path, {1020: (2, 2), 1030: (0, 5)})
    headers = ["Q_101", "Q_1020", "Q_1030", "gwr_1", "gwr_2"]
    assert coincident_point_headers(COLUMNS, headers, static) == {}
