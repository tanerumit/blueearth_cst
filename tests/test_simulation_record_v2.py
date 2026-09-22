"""Simulation v2 freezes exact sources and the closed scientific intent."""

import pytest
import yaml

from blueearth_cst.experiment.content_identity import content_sha256
from blueearth_cst.experiment.response_inventory import make_response_request
from blueearth_cst.experiment.simulation_record import (
    SimulationFrozenError,
    capture_simulation_sources_v2,
    read_simulation_sources_v2,
    simulation_intent_v2,
)
from blueearth_cst.shared.model_digest import model_digest_from_entries


def test_preparse_wf4_sources_refuse_comment_mutation(tmp_path):
    config = tmp_path / "project_config.yml"
    workflow = tmp_path / "simulate_system.yml"
    workflow.write_text("operation: simulate-and-metrics\n", encoding="utf-8")
    config.write_text(
        yaml.safe_dump(
            {
                "project": {"project_dir": str(tmp_path / "project")},
                "workflows": {
                    "simulate_system": {
                        "enabled": True,
                        "config_path": workflow.name,
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    project = tmp_path / "project"
    invocation = "a" * 32
    capture_simulation_sources_v2(config, project, invocation)
    sources = read_simulation_sources_v2(project, invocation)
    assert [source.id for source in sources] == ["project", "workflow_simulate_system"]
    workflow.write_text(workflow.read_text() + "# revised\n", encoding="utf-8")
    with pytest.raises(SimulationFrozenError, match="changed after preparse"):
        read_simulation_sources_v2(project, invocation)


def test_simulation_intent_binds_prep_and_selected_runs():
    entries = {"wflow_sbm.toml": "a" * 64, "output.csv": "<absent>"}
    reference = {
        "digest_version": 1,
        "model_path": "models/hydrology/wflow",
        "model_toml": "wflow_sbm.toml",
        "digest": model_digest_from_entries(sorted(entries.items())),
        "inputs": entries,
    }
    request = make_response_request(
        ["01"],
        [
            {
                "variable": "q",
                "locations": ["outlet"],
                "units": "m3/s",
                "calendar": "standard",
                "timestep": "P1D",
                "time_label": "interval_end",
                "start": "2046-01-02 00:00:00",
                "end": "2054-12-31 00:00:00",
                "missing_value": "NaN",
            }
        ],
    )
    documents = {
        "model_reference": reference,
        "settings": {"simulation_window": {"start": 2046, "end": 2054}},
        "environment": {"packages": {}},
        "simulator_adapter_code": [],
        "response_request": request,
        "preparation": {"schema_version": "forcing-preparation/2"},
    }
    identity = {
        "schema_version": "forcing-preparation-identity/2",
        "ancillary": [],
        "catalog": {},
        "forcing_elevation": {},
        "generated_forcing_reader": {},
        "pet_method": "debruin",
    }
    selection = {
        "resolution_mode": "explicit-manifest",
        "manifest": {"path": "scenarios/_engine/collections/a/collection.json"},
        "collection_id": "a" * 64,
        "collection_revision": "b" * 64,
        "run_ids": ["01"],
    }
    intent = simulation_intent_v2(
        "experiment",
        selection,
        {"name": "wflow", "revision": "c" * 64},
        documents,
        identity,
    )
    assert intent["identity_digests"]["preparation"] == content_sha256(identity)
    identity["pet_method"] = "makkink"
    changed = simulation_intent_v2(
        "experiment",
        selection,
        {"name": "wflow", "revision": "c" * 64},
        documents,
        identity,
    )
    assert changed["simulation_id"] != intent["simulation_id"]
