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


def test_open_responses_drops_the_duplicate_before_numbering(tmp_path):
    """Every reader of a native CSV sees one series per cell, ordinals contiguous."""
    import pandas as pd

    from blueearth_cst.experiment.wflow_response_reader import (
        NativeRunArtifacts,
        ResponseRequest,
        open_responses,
    )

    static = _static(tmp_path, {1010: (4, 0), 1020: (2, 2)})
    toml = tmp_path / "run_01.toml"
    toml.write_text(
        '[time]\ncalendar = "standard"\ntimestepsecs = 86400\n'
        'starttime = "2000-01-01T00:00:00"\nendtime = "2000-01-03T00:00:00"\n'
        f'[input]\npath_static = "{static.name}"\n'
        "[[output.csv.column]]\n"
        'header = "Q"\nmap = "outlets"\n'
        'parameter = "river_water__volume_flow_rate"\n'
        "[[output.csv.column]]\n"
        'header = "Q"\nmap = "gauges_locations"\n'
        'parameter = "river_water__volume_flow_rate"\n',
        encoding="utf-8",
    )
    csv = tmp_path / "run_01.csv"
    frame = pd.DataFrame(
        {"Q_101": [1.0, 2.0], "Q_1010": [1.0, 2.0], "Q_1020": [3.0, 4.0]},
        index=pd.to_datetime(["2000-01-02", "2000-01-03"]),
    )
    frame.index.name = "time"
    frame.to_csv(csv)
    series = open_responses(
        "01", NativeRunArtifacts(csv, toml), ResponseRequest(("q",))
    )
    assert [(s.location_id, s.location_ordinal) for s in series] == [
        ("101", 0),
        ("1020", 1),
    ]
