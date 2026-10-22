"""WF4 prepares historical thresholds and seals their numerical provenance."""

import numpy as np
import pandas as pd
import pytest
import yaml

from blueearth_cst.experiment.baseline_qcrit import resolve_thresholds
from blueearth_cst.experiment.indicator_sets import (
    SetSource,
    calculation_records,
    resolve_set,
)


@pytest.fixture
def baseline(tmp_path):
    model = tmp_path / "model"
    (model / "run_default").mkdir(parents=True)
    time = pd.date_range("1999-01-01", "1999-12-31")
    pd.DataFrame({"Q_9": np.arange(365)}, index=time).to_csv(
        model / "run_default/output.csv", index_label="time"
    )
    (model / "wflow_sbm.toml").write_text(
        '[time]\ncalendar="standard"\ntimestepsecs=86400\n'
        'starttime="1998-12-31T00:00:00"\nendtime="1999-12-31T00:00:00"\n'
        '[input]\npath_forcing="forcing/inmaps_historical.nc"\n'
        '[[output.csv.column]]\nheader="Q"\nparameter="river_water__volume_flow_rate"\n',
        encoding="utf-8",
    )
    parameters = {
        "season": "summer",
        "thresholds": {
            "baseline_quantile": {
                "model_root": "model",
                "source_id": "historical-era5",
                "years": [1999],
                "reference_period": "annual",
            }
        },
    }
    return tmp_path / "crop-water.yml", parameters


def source(path, parameters):
    return SetSource(
        "crop-water",
        path,
        False,
        yaml.safe_dump(
            {
                "schema_version": 1,
                "id": "crop-water",
                "title": "Case",
                "description": "Historical Qcrit",
                "selection": {
                    "registry": {
                        "set": "crop-water",
                        "overrides": {"summer_low_flow_days": parameters},
                    }
                },
            }
        ),
    )


def test_owned_set_resolution_prepares_fixed_thresholds_and_changes_identity(baseline):
    path, parameters = baseline
    resolved = resolve_set(source(path, parameters))
    records = calculation_records(resolved.indicators)
    item = next(i for i in resolved.indicators if i.indicator == "summer_low_flow_days")
    threshold = item.declaration.calculation_parameters["thresholds"]["9"]
    assert threshold["value"] == pytest.approx(36.4)
    assert "csv-sha256=" in threshold["source_id"]
    assert "toml-sha256=" in threshold["source_id"]
    parameters["thresholds"]["baseline_quantile"]["quantile"] = 0.8
    assert (
        calculation_records(resolve_set(source(path, parameters)).indicators) != records
    )
    parameters["thresholds"]["baseline_quantile"]["quantile"] = 0.9
    parameters["thresholds"]["baseline_quantile"]["reference_period"] = "summer"
    assert (
        calculation_records(resolve_set(source(path, parameters)).indicators) != records
    )
    parameters["thresholds"]["baseline_quantile"]["reference_period"] = "annual"
    csv_path = path.parent / "model/run_default/output.csv"
    csv_path.write_text(csv_path.read_text().replace(",0", ",0.5", 1), encoding="utf-8")
    assert (
        calculation_records(resolve_set(source(path, parameters)).indicators) != records
    )


@pytest.mark.parametrize(
    "change", ["future", "observations", "missing", "unknown", "bad_years"]
)
def test_baseline_rule_refuses_incompatible_inputs(baseline, change):
    path, parameters = baseline
    rule = parameters["thresholds"]["baseline_quantile"]
    if change in ("future", "observations"):
        toml_path = path.parent / "model/wflow_sbm.toml"
        toml_path.write_text(
            toml_path.read_text().replace("inmaps_historical.nc", f"{change}.nc")
        )
    elif change == "missing":
        rule["model_root"] = "absent"
    elif change == "unknown":
        rule["percentile"] = 90
    else:
        rule["years"] = "1999"
    with pytest.raises((ValueError, FileNotFoundError)):
        resolve_thresholds(parameters, path)
