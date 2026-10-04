"""Versioned native inventory binds science while retaining exact evidence.

Every case starts from a real v2 experiment frozen by the production producers
(`tests/_v2_experiment.py`) with its native runs retained and nothing yet
published -- the state rule 4.06 publishes from.
"""

from dataclasses import replace
from shutil import copyfile

import pytest

from blueearth_cst.experiment.content_identity import (
    canonical_json_bytes,
    content_sha256,
)
from blueearth_cst.experiment.response_inventory import (
    MissingResponseRequirement,
    publish_response_inventory_v2,
    read_response_inventory_v2,
)
from tests._v2_experiment import (
    RUN_IDS,
    TEMPORAL,
    build_v2_experiment,
    copy_v2_experiment,
    native_runs,
)

FIRST = RUN_IDS[0]
#: The requested variable's Wflow parameter; the fixture's request asks for gwr.
RECHARGE = "soil_water_saturated_zone_top__net_recharge_volume_flux"


@pytest.fixture(scope="module")
def unpublished(tmp_path_factory):
    return build_v2_experiment(tmp_path_factory.mktemp("frozen"), publish=False)


@pytest.fixture
def v2(unpublished, tmp_path):
    root = copy_v2_experiment(unpublished, tmp_path).root
    assert not (root / "_engine/response_inventory.json").exists()
    return root, native_runs(root), dict(TEMPORAL)


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
    native_runs[FIRST].temporal_path.unlink()
    assert read_response_inventory_v2(root) == inventory


def test_toml_path_change_preserves_response_identity_but_changes_full_evidence(v2):
    root, native_runs, temporal = v2
    first = publish_response_inventory_v2(root, native_runs, temporal)
    copyfile(native_runs[FIRST].toml_path, root / "moved.toml")
    moved = {
        **native_runs,
        FIRST: replace(native_runs[FIRST], toml_path=root / "moved.toml"),
    }
    from blueearth_cst.experiment.response_inventory import build_response_inventory_v2

    second = build_response_inventory_v2(root, moved, temporal)
    assert first["response_identity_sha256"] == second["response_identity_sha256"]
    assert first["response_inventory_sha256"] != second["response_inventory_sha256"]


def test_path_bearing_toml_change_keeps_scientific_identity(v2):
    root, native_runs, temporal = v2
    first = publish_response_inventory_v2(root, native_runs, temporal)
    toml = native_runs[FIRST].toml_path
    toml.write_text(toml.read_text() + '\n[input]\npath_forcing="elsewhere.nc"\n')
    from blueearth_cst.experiment.response_inventory import build_response_inventory_v2

    second = build_response_inventory_v2(root, native_runs, temporal)
    assert first["response_identity_sha256"] == second["response_identity_sha256"]
    assert first["response_inventory_sha256"] != second["response_inventory_sha256"]


def test_clock_change_refuses_native_reopening(v2):
    root, native_runs, temporal = v2
    publish_response_inventory_v2(root, native_runs, temporal)
    toml = native_runs[FIRST].toml_path
    toml.write_text(toml.read_text().replace("timestepsecs=86400", "timestepsecs=3600"))
    with pytest.raises(MissingResponseRequirement):
        read_response_inventory_v2(root)


def test_time_units_are_nonsemantic_native_clock_metadata(v2):
    root, native_runs, temporal = v2
    toml = native_runs[FIRST].toml_path
    toml.write_text(
        toml.read_text().replace(
            'calendar="standard"\n',
            'calendar="standard"\ntime_units="days since 1900-01-01 00:00:00"\n',
        )
    )

    inventory = publish_response_inventory_v2(root, native_runs, temporal)

    assert inventory["identity_projection"]["series"][0]["native_selector"][
        "clock"
    ] == {
        "calendar": "standard",
        "starttime": "2046-01-01 00:00:00",
        "endtime": "2046-01-03 00:00:00",
        "timestepsecs": 86400,
    }


def test_output_routing_metadata_is_not_response_selector_semantics(v2):
    root, native_runs, temporal = v2
    toml = native_runs[FIRST].toml_path
    toml.write_text(
        toml.read_text().replace(
            f'parameter="{RECHARGE}"\n',
            f'parameter="{RECHARGE}"\nmap="outlets"\nreducer="mean"\n',
        )
    )

    inventory = publish_response_inventory_v2(root, native_runs, temporal)

    assert inventory["identity_projection"]["series"][0]["native_selector"][
        "output_declarations"
    ] == [{"header": "gwr", "parameter": RECHARGE}]


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
    native_runs[FIRST].temporal_path.write_bytes(
        canonical_json_bytes({**temporal, "source_calendar": "standard"})
    )
    with pytest.raises(MissingResponseRequirement, match="inconsistent temporal"):
        publish_response_inventory_v2(root, native_runs, temporal)
    assert not (root / "_engine/response_inventory.json").exists()
