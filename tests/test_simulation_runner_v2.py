"""WF4 selects a checked v2 marker without invoking WF3 producers."""

from pathlib import Path

import pytest

from blueearth_cst.experiment import collection_resolution, simulation_runner
from blueearth_cst.experiment.content_identity import atomic_record, content_sha256


def test_explicit_selector_uses_v2_reader(tmp_path, monkeypatch):
    marker = tmp_path / "scenarios/_engine/collections/abc/collection.json"
    selection = {
        "resolution_mode": "explicit-manifest",
        "manifest_path": str(marker),
        "collection_id": "a" * 64,
        "collection_revision": "b" * 64,
    }
    monkeypatch.setattr(
        simulation_runner,
        "simulation_settings",
        lambda _: ({}, {"scenario_collection": {"manifest_path": marker}}),
    )
    monkeypatch.setattr(
        simulation_runner, "verify_selected_collection_source", lambda *_: "era5"
    )
    monkeypatch.setattr(
        collection_resolution,
        "resolve_explicit_collection_v2",
        lambda selector: (
            (selection, {"schema_version": "scenario-collection/2"})
            if selector == {"manifest_path": marker}
            else pytest.fail("wrong selector")
        ),
    )
    selected, record = simulation_runner.resolve_selected_collection("unused", tmp_path)
    assert selected == selection
    assert record["schema_version"] == "scenario-collection/2"


def test_project_selector_checks_pinned_candidate(tmp_path, monkeypatch):
    from blueearth_cst.experiment import generation_plan, scenario_collection_v2
    from blueearth_cst.shared import config_composition

    project = tmp_path / "project"
    request = {"schema_version": "generation-request/2", "fixture": "v2"}
    request_id = content_sha256(request)
    request_dir = project / "scenarios/_engine/requests" / request_id[:12]
    request_dir.mkdir(parents=True)
    pointer = request_dir / "request.json"
    atomic_record(
        pointer,
        {
            "schema_version": "scenario-request/2",
            "generation_request_id": request_id,
            "plan_path": f"{'b' * 64}.json",
            "path_base": "request_directory",
            "plan_sha256": "b" * 64,
        },
    )
    marker = project / "scenarios/_engine/collections" / ("c" * 12) / "collection.json"
    marker.parent.mkdir(parents=True)
    marker.write_bytes(b"{}\n")
    settings = {
        "request_path": str(pointer),
        "project_dir": str(project),
        "request": request,
    }
    plan = {
        "generation_request_id": request_id,
        "collection_id": "c" * 64,
        "decision": "create",
        "outputs": {"record_root": f"scenarios/_engine/collections/{'c' * 12}"},
    }
    monkeypatch.setattr(simulation_runner, "simulation_settings", lambda _: ({}, {}))
    monkeypatch.setattr(
        simulation_runner, "verify_selected_collection_source", lambda *_: "era5"
    )
    monkeypatch.setattr(
        config_composition, "compose_config", lambda *_args, **_kwargs: ({}, None)
    )
    monkeypatch.setattr(
        generation_plan, "generation_configuration", lambda *_: settings
    )
    monkeypatch.setattr(generation_plan, "read_pinned_plan", lambda *_: plan)
    monkeypatch.setattr(
        generation_plan,
        "build_candidate_intent",
        lambda _: pytest.fail("WF4 must not capture WF3 source snapshots"),
    )
    monkeypatch.setattr(
        scenario_collection_v2,
        "read_collection_v2",
        lambda path: (
            {"collection_id": "c" * 64, "collection_revision": "d" * 64}
            if Path(path) == marker
            else pytest.fail("wrong marker")
        ),
    )
    selection, collection = simulation_runner.resolve_selected_collection(
        pointer, tmp_path
    )
    assert selection["manifest_path"] == marker.as_posix()
    assert selection["collection_revision"] == collection["collection_revision"]
    settings["request"] = {"schema_version": "generation-request/2", "fixture": "drift"}
    with pytest.raises(ValueError, match="project request pointer differs"):
        simulation_runner.resolve_selected_collection(pointer, tmp_path)


def test_selected_collection_climate_source_matches_creator(tmp_path, monkeypatch):
    from blueearth_cst.shared import workflow_config_snapshot

    marker_path = (
        tmp_path / "scenarios/_engine/collections" / ("a" * 12) / "collection.json"
    )
    marker_path.parent.mkdir(parents=True)
    marker_path.write_bytes(b"{}\n")
    selection = {"manifest_path": str(marker_path)}
    marker = {"collection_id": "a" * 64, "archive": {"path": "unused"}}
    archive_path = tmp_path / "archive/run_record.yml"
    monkeypatch.setattr(
        workflow_config_snapshot,
        "resolve_file_reference",
        lambda *_args: archive_path,
    )
    monkeypatch.setattr(
        workflow_config_snapshot,
        "validate_archive",
        lambda _: {
            "owner": {"kind": "scenario_collection", "id": "a" * 64},
            "loaded_config": {"climate": {"selected": "era5"}},
        },
    )
    assert (
        simulation_runner.verify_selected_collection_source(
            {
                "project": {"project_dir": str(tmp_path)},
                "climate": {"selected": "era5"},
            },
            selection,
            marker,
        )
        == "era5"
    )
    with pytest.raises(ValueError, match="differs from collection creator"):
        simulation_runner.verify_selected_collection_source(
            {
                "project": {"project_dir": str(tmp_path)},
                "climate": {"selected": "chirps"},
            },
            selection,
            marker,
        )
    with pytest.raises(ValueError, match="outside the WF4 project root"):
        simulation_runner.verify_selected_collection_source(
            {
                "project": {"project_dir": str(tmp_path / "other")},
                "climate": {"selected": "era5"},
            },
            selection,
            marker,
        )


def test_p6_target_matrix_uses_v2_contract(monkeypatch, tmp_path):
    monkeypatch.setattr(
        simulation_runner,
        "simulation_settings",
        lambda _: ({}, {"operation": "simulate-and-metrics"}),
    )
    assert (
        simulation_runner.validate_targets("unused", ["all"]) == "simulate-and-metrics"
    )
    assert (
        simulation_runner.validate_targets("unused", ["responses"])
        == "simulate-and-metrics"
    )
    with pytest.raises(ValueError, match="UnsupportedOperationTarget"):
        simulation_runner.validate_targets("unused", ["metrics"])

    selected = tmp_path / "_engine/metric_sets/abc123/metrics.json"
    monkeypatch.setattr(
        simulation_runner,
        "simulation_settings",
        lambda _: ({}, {"operation": "metrics-only"}),
    )
    monkeypatch.setattr(
        "blueearth_cst.experiment.metric_plan.metrics_only_configuration",
        lambda _: (tmp_path, ["gwr"], "YS-JAN"),
    )
    monkeypatch.setattr(
        "blueearth_cst.experiment.metric_plan.current_metric_request",
        lambda *_: {"request": "v2"},
    )
    monkeypatch.setattr(
        "blueearth_cst.experiment.metric_plan.build_metric_plan",
        lambda *_: {"targets": {"manifest": selected.as_posix()}},
    )
    assert simulation_runner.validate_targets("unused", ["metrics"]) == "metrics-only"
    assert (
        simulation_runner.validate_targets("unused", [selected.as_posix()])
        == "metrics-only"
    )
    monkeypatch.setattr(
        "blueearth_cst.experiment.metric_plan.build_metric_plan",
        lambda *_: {
            "targets": {
                "manifest": (
                    tmp_path / "_engine/metric_sets/other/metrics.json"
                ).as_posix()
            }
        },
    )
    with pytest.raises(ValueError, match="UnsupportedOperationTarget"):
        simulation_runner.validate_targets("unused", [selected.as_posix()])


def test_metrics_only_reads_v2_collection_from_simulation_intent(tmp_path, monkeypatch):
    from blueearth_cst.experiment import metric_plan

    project = tmp_path / "project"
    root = project / "experiments/experiment_rapid"
    (root / "_engine").mkdir(parents=True)
    (root / "_engine/simulation.json").write_bytes(b"{}\n")
    workflow = tmp_path / "metrics.yml"
    workflow.write_text(
        "experiment_name: experiment_rapid\noperation: metrics-only\n",
        encoding="utf-8",
    )
    config = tmp_path / "project.yml"
    config.write_text(
        "project:\n"
        f"  project_dir: {project.as_posix()}\n"
        "workflows:\n"
        "  simulate_system:\n"
        "    enabled: true\n"
        "    config_path: metrics.yml\n",
        encoding="utf-8",
    )
    intent = {
        "collection": {
            "collection_id": "a" * 64,
            "collection_revision": "b" * 64,
            "manifest": {"path": "scenarios/_engine/collections/a/collection.json"},
        },
        "documents": {"response_request": {"variables": [{"variable": "q"}]}},
    }
    monkeypatch.setattr(
        metric_plan,
        "read_simulation_v2",
        lambda path: {"schema_version": "simulation/2"},
    )
    monkeypatch.setattr(metric_plan, "read_simulation_intent_v2", lambda path: intent)

    actual_root, tokens, anchor = metric_plan.metrics_only_configuration(config)

    assert actual_root == root
    assert tokens == ["q"]
    assert anchor == "YS-JAN"
