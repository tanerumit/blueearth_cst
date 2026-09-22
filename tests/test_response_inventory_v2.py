"""Versioned native inventory binds science while retaining exact evidence."""

from dataclasses import replace
from shutil import copyfile

import pytest

from blueearth_cst.experiment.content_identity import (
    canonical_json_bytes,
    content_sha256,
    read_canonical_json,
)
from blueearth_cst.experiment.response_inventory import (
    MissingResponseRequirement,
    publish_response_inventory_v2,
    read_response_inventory_v2,
)
from tests.test_response_inventory import frozen  # noqa: F401
from tests.test_simulation_record import inputs  # noqa: F401
from tests.test_wflow_response_reader import native  # noqa: F401


@pytest.fixture
def v2(frozen, monkeypatch):  # noqa: F811 - imported fixture
    root, native_runs, temporal = frozen
    old = read_canonical_json(root / "config/simulation.json")
    request = read_canonical_json(root / "config/response_request.json")
    intent = {
        "simulation_id": old["simulation_id"],
        "collection": old["collection"],
        "documents": {
            "model_reference": {"digest": old["model"]["model_digest"]},
            "response_request": request,
        },
        "simulator": old["simulator"],
        "identity_digests": {
            "settings": content_sha256(
                {"simulation_window": {"start": 2046, "end": 2046}}
            ),
            "response_request": content_sha256(request),
        },
    }
    engine = root / "_engine"
    engine.mkdir(exist_ok=True)
    (engine / "simulation_intent.json").write_bytes(canonical_json_bytes(intent))
    monkeypatch.setattr(
        "blueearth_cst.experiment.simulation_record.read_simulation_intent_v2",
        lambda path: intent,
    )
    return root, native_runs, temporal


def test_common_temporal_and_path_neutral_scientific_projection(v2):
    root, native_runs, temporal = v2
    inventory = publish_response_inventory_v2(root, native_runs, temporal)
    assert inventory["schema_version"] == "response-inventory/2"
    assert inventory["response_request"]["section"] == "/documents/response_request"
    assert inventory["series"][0]["native_selector"]["temporal"] == {
        "schema_version": "local-section-reference/1",
        "section": "/temporal_preparation",
        "section_sha256": inventory["temporal_preparation_sha256"],
    }
    assert inventory["identity_projection"]["series"][0]["native_selector"][
        "clock"
    ] == {
        "calendar": "standard",
        "starttime": "2046-01-01 00:00:00",
        "endtime": "2046-01-03 00:00:00",
        "timestepsecs": 86400,
    }
    native_runs["01"].temporal_path.unlink()
    assert read_response_inventory_v2(root) == inventory


def test_toml_path_change_preserves_response_identity_but_changes_full_evidence(v2):
    root, native_runs, temporal = v2
    first = publish_response_inventory_v2(root, native_runs, temporal)
    copyfile(native_runs["01"].toml_path, root / "moved.toml")
    moved = {"01": replace(native_runs["01"], toml_path=root / "moved.toml")}
    from blueearth_cst.experiment.response_inventory import build_response_inventory_v2

    second = build_response_inventory_v2(root, moved, temporal)
    assert first["response_identity_sha256"] == second["response_identity_sha256"]
    assert first["response_inventory_sha256"] != second["response_inventory_sha256"]


def test_path_bearing_toml_change_keeps_scientific_identity(v2):
    root, native_runs, temporal = v2
    first = publish_response_inventory_v2(root, native_runs, temporal)
    toml = native_runs["01"].toml_path
    toml.write_text(toml.read_text() + '\n[input]\npath_forcing="elsewhere.nc"\n')
    from blueearth_cst.experiment.response_inventory import build_response_inventory_v2

    second = build_response_inventory_v2(root, native_runs, temporal)
    assert first["response_identity_sha256"] == second["response_identity_sha256"]
    assert first["response_inventory_sha256"] != second["response_inventory_sha256"]


def test_clock_change_refuses_native_reopening(v2):
    root, native_runs, temporal = v2
    publish_response_inventory_v2(root, native_runs, temporal)
    toml = native_runs["01"].toml_path
    toml.write_text(toml.read_text().replace("timestepsecs=86400", "timestepsecs=3600"))
    with pytest.raises(MissingResponseRequirement):
        read_response_inventory_v2(root)


def test_local_temporal_pointer_tamper_refuses_before_native_open(v2, monkeypatch):
    root, native_runs, temporal = v2
    inventory = publish_response_inventory_v2(root, native_runs, temporal)
    inventory["series"][0]["native_selector"]["temporal"]["section"] = "/other"
    inventory["response_inventory_sha256"] = content_sha256(
        {
            key: value
            for key, value in inventory.items()
            if key != "response_inventory_sha256"
        }
    )
    (root / "_engine/response_inventory.json").write_bytes(
        canonical_json_bytes(inventory)
    )

    def forbidden(*args, **kwargs):
        pytest.fail("native reader called before local section validation")

    monkeypatch.setattr(
        "blueearth_cst.experiment.response_inventory.open_responses", forbidden
    )
    with pytest.raises(MissingResponseRequirement, match="local temporal section"):
        read_response_inventory_v2(root)


def test_per_run_temporal_difference_refuses_publication(v2):
    root, native_runs, temporal = v2
    native_runs["01"].temporal_path.write_bytes(
        canonical_json_bytes({**temporal, "source_calendar": "standard"})
    )
    with pytest.raises(MissingResponseRequirement, match="inconsistent temporal"):
        publish_response_inventory_v2(root, native_runs, temporal)
    assert not (root / "_engine/response_inventory.json").exists()
