"""Native response persistence validates an independent complete request."""

from dataclasses import replace
from shutil import copyfile

import pytest

from blueearth_cst.experiment.content_identity import canonical_json_bytes
from blueearth_cst.experiment.response_inventory import (
    MissingResponseRequirement,
    make_response_request,
    publish_response_inventory,
    read_response_inventory,
)
from blueearth_cst.experiment.simulation_record import (
    freeze_simulation,
    simulation_document,
)
from tests.test_simulation_record import inputs  # noqa: F401
from tests.test_wflow_response_reader import native  # noqa: F401


@pytest.fixture
def frozen(inputs, native):  # noqa: F811 - imported fixtures
    root, record, documents = inputs
    root.mkdir(exist_ok=True)
    temporal = {
        "source_calendar": "noleap",
        "prepared_forcing_calendar": "proleptic_gregorian",
        "response_calendar": "standard",
        "operations": [
            "cftime_to_datetime64",
            "clip_to_configured_window",
            "refresh_toml_endpoints",
        ],
        "prepared_start": "2046-01-01T00:00:00",
        "prepared_end": "2046-01-03T00:00:00",
        "response_start": "2046-01-02 00:00:00",
        "response_end": "2046-01-03 00:00:00",
        "time_label": "interval_end",
    }
    copyfile(native.csv_path, root / "opaque.csv")
    copyfile(native.toml_path, root / "opaque.toml")
    temporal_path = root / "temporal.json"
    temporal_path.write_bytes(canonical_json_bytes(temporal))
    native = replace(
        native,
        csv_path=root / "opaque.csv",
        toml_path=root / "opaque.toml",
        temporal_path=temporal_path,
    )
    declaration = {
        "variable": "q",
        "locations": ["9", "2"],
        "units": "m3 s-1",
        "calendar": "standard",
        "timestep": "P1D",
        "time_label": "interval_end",
        "start": temporal["response_start"],
        "end": temporal["response_end"],
        "missing_value": "NaN",
    }
    documents["response_request"] = make_response_request(["01"], [declaration])
    record = simulation_document(
        root.name,
        record["collection"],
        record["model"]["model_digest"],
        record["simulator"],
        documents,
    )
    freeze_simulation(root, record, documents)
    return root, {"01": native}, temporal


def test_self_contained_coverage_and_immutable_reuse(frozen):
    root, native_runs, temporal = frozen
    inventory = publish_response_inventory(root, native_runs, temporal)
    assert [item["location_id"] for item in inventory["series"]] == ["9", "2"]
    before = {
        p: (p.read_bytes(), p.stat().st_mtime_ns)
        for p in root.rglob("*")
        if p.is_file()
    }
    assert read_response_inventory(root) == inventory
    assert publish_response_inventory(root, native_runs, temporal) == inventory
    assert before == {
        p: (p.read_bytes(), p.stat().st_mtime_ns)
        for p in root.rglob("*")
        if p.is_file()
    }


@pytest.mark.parametrize("replace_header", ["Q_2", "Q_3"])
def test_missing_or_extra_expected_series_refuses_publication(frozen, replace_header):
    root, native_runs, temporal = frozen
    path = native_runs["01"].csv_path
    if replace_header == "Q_2":
        path.write_text("time,Q_9\n2046-01-02,1\n2046-01-03,4\n", encoding="utf-8")
    else:
        path.write_text(
            path.read_text().replace("Q_2", replace_header), encoding="utf-8"
        )
    with pytest.raises(MissingResponseRequirement, match="response keys"):
        publish_response_inventory(root, native_runs, temporal)
    assert not (root / "responses/response_inventory.json").exists()


@pytest.mark.parametrize("artifact", ["csv_path", "toml_path", "temporal_path"])
def test_changed_native_or_reader_dependency_refuses_reopening(frozen, artifact):
    root, native_runs, temporal = frozen
    publish_response_inventory(root, native_runs, temporal)
    path = getattr(native_runs["01"], artifact)
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(MissingResponseRequirement):
        read_response_inventory(root)


def test_temporal_chain_refuses_before_ready_marker(frozen):
    root, native_runs, temporal = frozen
    temporal["response_start"] = "2046-01-01 00:00:00"
    native_runs["01"].temporal_path.write_bytes(canonical_json_bytes(temporal))
    with pytest.raises(MissingResponseRequirement, match="clock"):
        publish_response_inventory(root, native_runs, temporal)


@pytest.mark.parametrize("conversion", ["hydromt_reader_to_datetime64", None])
def test_reader_calendar_conversion_must_be_recorded(frozen, conversion):
    root, native_runs, temporal = frozen
    temporal["operations"].pop(0)
    if conversion is not None:
        temporal["operations"].insert(0, conversion)
    native_runs["01"].temporal_path.write_bytes(canonical_json_bytes(temporal))
    if conversion is None:
        with pytest.raises(
            MissingResponseRequirement, match="temporal preparation chain"
        ):
            publish_response_inventory(root, native_runs, temporal)
    else:
        publish_response_inventory(root, native_runs, temporal)
        assert read_response_inventory(root)["temporal_preparation"] == temporal


def test_corrupt_inventory_digest_refuses_before_native_open(frozen, monkeypatch):
    root, native_runs, temporal = frozen
    inventory = publish_response_inventory(root, native_runs, temporal)
    inventory["series"][0]["units"] = "wrong"
    (root / "responses/response_inventory.json").write_bytes(
        canonical_json_bytes(inventory)
    )

    def forbidden(*args, **kwargs):
        pytest.fail("native reader called before inventory digest validation")

    monkeypatch.setattr(
        "blueearth_cst.experiment.response_inventory.open_responses", forbidden
    )
    with pytest.raises(MissingResponseRequirement, match="before native opening"):
        read_response_inventory(root)
