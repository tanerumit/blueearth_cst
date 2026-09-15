"""Native response binding preserves values and refuses misleading metadata."""

from dataclasses import replace

import numpy as np
import pytest

from blueearth_cst.experiment.wflow_response_reader import (
    NativeRunArtifacts,
    ResponseRequest,
    open_responses,
)


@pytest.fixture
def native(tmp_path):
    csv_path = tmp_path / "opaque.csv"
    csv_path.write_text(
        "time,Q_9,Q_2,gwr_9\n2046-01-02,1,2,3\n2046-01-03,4,,6\n",
        encoding="utf-8",
    )
    toml_path = tmp_path / "unrelated.toml"
    toml_path.write_text(
        '[time]\ncalendar="standard"\ntimestepsecs=86400\n'
        'starttime="2046-01-01T00:00:00"\nendtime="2046-01-03T00:00:00"\n'
        '[[output.csv.column]]\nheader="Q"\n'
        'parameter="river_water__volume_flow_rate"\n'
        '[[output.csv.column]]\nheader="gwr"\n'
        'parameter="soil_water_saturated_zone_top__net_recharge_volume_flux"\n',
        encoding="utf-8",
    )
    return NativeRunArtifacts(csv_path, toml_path)


def test_native_order_values_and_explicit_physical_metadata(native):
    before = native.csv_path.read_bytes()
    series = open_responses("opaque-id", native, ResponseRequest(("q", "gwr")))
    assert [
        (item.variable, item.location_id, item.location_ordinal) for item in series
    ] == [
        ("q", "9", 0),
        ("q", "2", 1),
        ("gwr", "9", 0),
    ]
    assert {item.run_id for item in series} == {"opaque-id"}
    assert series[0].units == "m3 s-1"
    assert series[2].units == "mm dt-1"
    assert series[0].calendar == "standard"
    assert series[0].time_label == "interval_end"
    np.testing.assert_array_equal(series[0].values, [1.0, 4.0])
    np.testing.assert_array_equal(series[1].missing, [False, True])
    assert native.csv_path.read_bytes() == before


@pytest.mark.parametrize(
    "old,new,match",
    [
        ('calendar="standard"', 'calendar="noleap"', "calendar"),
        ("timestepsecs=86400", "timestepsecs=3600", "coverage"),
        ("river_water__volume_flow_rate", "river_water__depth", "parameter"),
    ],
)
def test_native_metadata_mismatch_refuses(native, old, new, match):
    native.toml_path.write_text(native.toml_path.read_text().replace(old, new))
    with pytest.raises(ValueError, match=match):
        open_responses("01", native, ResponseRequest(("q",)))


def test_missing_request_and_duplicate_columns_refuse(native, tmp_path):
    with pytest.raises(ValueError, match="parameter"):
        open_responses("01", native, ResponseRequest(("snow",)))
    duplicate = tmp_path / "duplicate.csv"
    duplicate.write_text(native.csv_path.read_text().replace("Q_2", "Q_9"))
    with pytest.raises(ValueError, match="duplicate"):
        open_responses(
            "01", replace(native, csv_path=duplicate), ResponseRequest(("q",))
        )
