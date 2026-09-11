"""Frozen simulation identity excludes metrics, execution facts and completion."""

from copy import deepcopy

import pytest

from blueearth_cst.experiment.content_identity import (
    canonical_json_bytes,
    content_sha256,
)
from blueearth_cst.experiment.simulation_record import (
    MetricsOnlySimulationUnavailable,
    SimulationFrozenError,
    complete_simulation,
    freeze_simulation,
    read_simulation,
    simulation_document,
    simulation_id,
)


@pytest.mark.parametrize("wflow_available", [True, False])
def test_live_input_planner_applies_prepared_clock_once(
    tmp_path, monkeypatch, wflow_available
):
    """Exercise the real live-helper/planner seam with only external reads stubbed."""
    import subprocess
    from pathlib import Path
    from types import SimpleNamespace

    from blueearth_cst.experiment import content_identity, write_model_reference
    from blueearth_cst.experiment.simulation_record import live_simulation_inputs

    model = tmp_path / "model"
    model.mkdir()
    toml = model / "wflow_sbm.toml"
    toml.write_text(
        '[time]\ncalendar="proleptic_gregorian"\ntimestepsecs=86400\n'
        '[[output.csv.column]]\nheader="Q"\n'
        'parameter="river_water__volume_flow_rate"\n',
        encoding="utf-8",
    )
    original = toml.read_bytes()
    monkeypatch.setattr(
        write_model_reference,
        "build_model_reference",
        lambda *args: {
            "model_toml": toml.name,
            "digest": "a" * 64,
        },
    )
    monkeypatch.setattr(
        content_identity,
        "repository_code_inventory",
        lambda *args: [{"path": "fixture.py", "sha256": "b" * 64}],
    )
    monkeypatch.setattr(
        content_identity,
        "stage_environment",
        lambda *args, **kwargs: {
            "packages": {"julia:Wflow": "1.0.2:fixture"} if wflow_available else {},
            "locks": {},
        },
    )
    calls = []

    def native_headers(command, *, check):
        assert check is True
        assert command[-2] == str(toml.resolve())
        Path(command[-1]).write_text("Q_9\nQ_2\n", encoding="utf-8")
        calls.append(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(subprocess, "run", native_headers)
    kwargs = {
        "project_dir": tmp_path,
        "model_root": model,
        "collection": {
            "collection_id": "c" * 64,
            "collection_revision": "d" * 64,
            "forcing": [{"run_id": "01"}, {"run_id": "02"}],
        },
        "settings": {
            "simulation_window": {"start": 2046, "end": 2054},
            "resolution_mode": "explicit-manifest",
            "manifest_path": "retained/collection.json",
        },
        "julia_command": ["fixture-julia"],
        "header_path": tmp_path / "headers.txt",
    }
    if not wflow_available:
        with pytest.raises(KeyError, match="julia:Wflow"):
            live_simulation_inputs(tmp_path / "experiment", **kwargs)
    else:
        _, documents = live_simulation_inputs(tmp_path / "experiment", **kwargs)
        request = documents["response_request"]
        assert request["variables"][0]["start"] == "2046-01-02 00:00:00"
        assert request["variables"][0]["end"] == "2054-12-31 00:00:00"
        assert request["variables"][0]["calendar"] == "standard"
        assert request["variables"][0]["locations"] == ["9", "2"]
        assert request["expected_series"] == [
            [run, "q", location] for run in ("01", "02") for location in ("9", "2")
        ]
    assert len(calls) == 1
    assert toml.read_bytes() == original


@pytest.fixture
def inputs(tmp_path):
    root = tmp_path / "experiment"
    import yaml

    from blueearth_cst.shared.model_digest import (
        DIGEST_VERSION,
        model_digest_from_entries,
    )

    entries = {"wflow_sbm.toml": "a" * 64}
    digest = model_digest_from_entries(sorted(entries.items()))
    (root / "config").mkdir(parents=True)
    (root / "config/model_reference.yml").write_text(
        yaml.safe_dump(
            {
                "digest_version": DIGEST_VERSION,
                "model_path": "models/hydrology/wflow",
                "model_toml": "wflow_sbm.toml",
                "digest": digest,
                "inputs": entries,
            }
        ),
        encoding="utf-8",
    )
    documents = {
        "settings": {"timestepsecs": 86400},
        "simulator_adapter_code": [{"path": "adapter.py", "sha256": "a" * 64}],
        "environment": {"packages": {"wflow": "1.0.2"}},
        "response_request": {
            "variables": ["q"],
            "expected_series": [["01", "q", "101"]],
        },
    }
    record = simulation_document(
        root.name,
        {
            "resolution_mode": "project-generation",
            "manifest_path": "/project/collection.json",
            "collection_id": "b" * 64,
            "collection_revision": "c" * 64,
        },
        digest,
        {"name": "wflow", "revision": "e" * 64},
        documents,
    )
    return root, record, documents


def test_freeze_and_reuse_preserve_all_recorded_bytes(inputs):
    root, record, documents = inputs
    assert freeze_simulation(root, record, documents) == record
    before = {
        p: (p.read_bytes(), p.stat().st_mtime_ns)
        for p in root.rglob("*")
        if p.is_file()
    }
    assert freeze_simulation(root, record, documents) == record
    assert before == {
        p: (p.read_bytes(), p.stat().st_mtime_ns)
        for p in root.rglob("*")
        if p.is_file()
    }


@pytest.mark.parametrize(
    "field", ["settings", "response_request", "environment", "simulator_adapter_code"]
)
def test_stale_reuse_refuses_changed_immutable_document(inputs, field):
    root, record, documents = inputs
    freeze_simulation(root, record, documents)
    changed = deepcopy(documents)
    changed[field] = {"changed": True}
    proposed = simulation_document(
        root.name,
        record["collection"],
        record["model"]["model_digest"],
        record["simulator"],
        changed,
    )
    with pytest.raises(SimulationFrozenError, match="simulation_id"):
        freeze_simulation(root, proposed, changed)
    assert read_simulation(root) == record


def test_retained_input_tampering_refuses_without_live_model(inputs):
    root, record, documents = inputs
    freeze_simulation(root, record, documents)
    (root / "config/simulator_settings.json").write_bytes(
        canonical_json_bytes({"timestepsecs": 3600})
    )
    with pytest.raises(SimulationFrozenError, match="settings.*expected=.*observed="):
        read_simulation(root)


def test_self_hashed_incomplete_inventory_cannot_mark_completion(inputs):
    root, record, documents = inputs
    freeze_simulation(root, record, documents)
    with pytest.raises(
        MetricsOnlySimulationUnavailable, match="no response completion"
    ):
        read_simulation(root, require_complete=True)
    inventory = {
        "simulation_id": record["simulation_id"],
        "fixture": "completion digest only",
    }
    digest = content_sha256(inventory)
    inventory["response_inventory_sha256"] = digest
    (root / "responses").mkdir()
    (root / "responses/response_inventory.json").write_bytes(
        canonical_json_bytes(inventory)
    )
    from blueearth_cst.experiment.response_inventory import MissingResponseRequirement

    with pytest.raises(MissingResponseRequirement):
        complete_simulation(root, digest)
    assert read_simulation(root)["response_inventory_sha256"] is None


def test_experiment_name_and_completion_do_not_enter_identity(inputs):
    _, record, _ = inputs
    changed = deepcopy(record)
    changed["experiment_name"] = "another"
    changed["response_inventory_sha256"] = "f" * 64
    assert simulation_id(changed) == simulation_id(record)
