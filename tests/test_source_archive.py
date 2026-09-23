"""P1 source archive: exact captured bytes and recoverable publication."""

import json
import shutil
from pathlib import Path

import pytest
import yaml

from blueearth_cst.shared import config_composition as cc
from blueearth_cst.shared import workflow_config_snapshot as snapshot
from blueearth_cst.shared.workflow_config_snapshot import (
    capture_rerun_predecessor,
    capture_sources,
    file_reference,
    publish_archive,
    read_archive,
    recover_archive,
    resolve_file_reference,
    resolve_rerun_execution,
    run_record_document,
    source_archive_paths,
    validate_archive,
)


def _archive(
    tmp_path: Path, invocation_id: str, data: bytes = b"# comment\r\nx: 1\r\n"
):
    project = tmp_path / "original" / "project_config.yml"
    project.parent.mkdir(exist_ok=True)
    project.write_bytes(data)
    captured = capture_sources([("project", "project_config", project)])
    project.write_bytes(b"# changed after capture\nx: 2\n")
    record, payloads = run_record_document(
        workflow="build_model",
        invocation_id=invocation_id,
        owner_kind="workflow",
        owner_id="build_model",
        loaded_config={"workflows": {"build_model": {"enabled": True}}},
        advanced_settings={},
        projection=["workflows.build_model"],
        toolbox={"commit": None},
        invocation={
            "entry_point": "run_workflow.py",
            "command": [],
            "targets": ["all"],
            "working_directory": str(tmp_path),
            "overrides": {},
        },
        sources=captured,
        environment={},
    )
    return record, payloads


def test_captured_bytes_survive_live_mutation_and_publish(tmp_path):
    record, payloads = _archive(tmp_path, "first")
    root = tmp_path / "output"
    publish_archive(root, "build_model", "config/runs/build_model", record, payloads)
    loaded = read_archive(root, "build_model", "config/runs/build_model")
    entry = loaded["source_files"][0]
    assert entry["archived_path"] == "sources/project_config.yml"
    assert (
        root / "config/runs/build_model" / entry["archived_path"]
    ).read_bytes() == b"# comment\r\nx: 1\r\n"
    assert loaded["schema_version"] == "run-record/2"


def test_first_publication_replaces_empty_target_directory(tmp_path):
    record, payloads = _archive(tmp_path, "first")
    root = tmp_path / "output"
    (root / "config/runs/build_model").mkdir(parents=True)

    publish_archive(root, "build_model", "config/runs/build_model", record, payloads)

    assert (
        read_archive(root, "build_model", "config/runs/build_model")["invocation_id"]
        == "first"
    )


def test_publication_retries_transient_windows_access_denied(tmp_path, monkeypatch):
    root = tmp_path / "output"
    first, first_payloads = _archive(tmp_path, "first")
    publish_archive(
        root, "build_model", "config/runs/build_model", first, first_payloads
    )
    second, second_payloads = _archive(tmp_path, "second", b"second: true\n")
    real_replace = snapshot.os.replace
    attempts = 0

    def replace_with_contention(source, target):
        nonlocal attempts
        if Path(source).name == "build_model" and Path(target).suffix == ".previous":
            attempts += 1
            if attempts < 3:
                error = PermissionError(13, "Access is denied", str(source))
                error.winerror = 5
                raise error
        real_replace(source, target)

    monkeypatch.setattr(snapshot, "_WINDOWS_REPLACE_RETRY", True, raising=False)
    monkeypatch.setattr(snapshot.os, "replace", replace_with_contention)

    publish_archive(
        root, "build_model", "config/runs/build_model", second, second_payloads
    )

    assert attempts == 3
    assert (
        read_archive(root, "build_model", "config/runs/build_model")["invocation_id"]
        == "second"
    )


def test_experiment_owner_is_an_archive_owner_kind(tmp_path):
    project = tmp_path / "project.yml"
    project.write_text("project: {}\n", encoding="utf-8")
    record, _ = run_record_document(
        workflow="simulate_system",
        invocation_id="simulation",
        owner_kind="experiment",
        owner_id="a" * 64,
        loaded_config={"workflows": {"simulate_system": {"enabled": True}}},
        advanced_settings={},
        projection=["workflows.simulate_system"],
        toolbox={"commit": None},
        invocation={
            "entry_point": "simulate_system.py",
            "command": [],
            "targets": ["all"],
            "working_directory": str(tmp_path),
            "overrides": {},
        },
        sources=capture_sources([("project", "project_config", project)]),
        environment={},
    )
    assert record["owner"] == {"kind": "experiment", "id": "a" * 64}


@pytest.mark.parametrize(
    "failure_after,expected",
    [
        ("prepared", "rolled_back"),
        ("old_detached", "rolled_back"),
        ("new_installed", "committed"),
    ],
)
def test_recovery_and_next_writer(tmp_path, failure_after, expected):
    root = tmp_path / "output"
    first, first_payloads = _archive(tmp_path, "first")
    publish_archive(
        root, "build_model", "config/runs/build_model", first, first_payloads
    )
    second, second_payloads = _archive(tmp_path, "second", b"new: true\n")
    with pytest.raises(RuntimeError, match="injected failure"):
        publish_archive(
            root,
            "build_model",
            "config/runs/build_model",
            second,
            second_payloads,
            failure_after=failure_after,
        )
    assert recover_archive(root, "build_model") == expected
    assert read_archive(root, "build_model", "config/runs/build_model")[
        "invocation_id"
    ] == ("second" if expected == "committed" else "first")
    assert recover_archive(root, "build_model") == expected
    third, third_payloads = _archive(tmp_path, "third", b"third: true\n")
    publish_archive(
        root, "build_model", "config/runs/build_model", third, third_payloads
    )
    assert (
        read_archive(root, "build_model", "config/runs/build_model")["invocation_id"]
        == "third"
    )
    assert list(
        (root / "config/runs/_engine/archive-transactions/completed").glob("*.json")
    )


def test_first_publication_failure_stays_unpublished(tmp_path):
    root = tmp_path / "output"
    first, payloads = _archive(tmp_path, "first")
    with pytest.raises(RuntimeError):
        publish_archive(
            root,
            "build_model",
            "config/runs/build_model",
            first,
            payloads,
            failure_after="prepared",
        )
    assert recover_archive(root, "build_model") == "unpublished"
    assert not (root / "config/runs/build_model").exists()
    publish_archive(root, "build_model", "config/runs/build_model", first, payloads)
    assert (
        read_archive(root, "build_model", "config/runs/build_model")["invocation_id"]
        == "first"
    )


@pytest.mark.parametrize(
    "failure_after,candidate",
    [
        ("prepared", "staged"),
        ("old_detached", "previous"),
        ("new_installed", "previous"),
    ],
)
def test_contradictory_candidate_refuses_recovery_reader_and_next_writer(
    tmp_path, failure_after, candidate
):
    root = tmp_path / "output"
    first, first_payloads = _archive(tmp_path, "first")
    publish_archive(
        root, "build_model", "config/runs/build_model", first, first_payloads
    )
    second, second_payloads = _archive(tmp_path, "second", b"second: true\n")
    with pytest.raises(RuntimeError):
        publish_archive(
            root,
            "build_model",
            "config/runs/build_model",
            second,
            second_payloads,
            failure_after=failure_after,
        )
    journal = root / "config/runs/_engine/archive-transactions/build_model.json"
    transaction = json.loads(journal.read_text(encoding="utf-8"))
    path = root / transaction[candidate] / "run_record.yml"
    path.write_bytes(b"corrupt")
    for action in (
        lambda: recover_archive(root, "build_model"),
        lambda: read_archive(root, "build_model", "config/runs/build_model"),
        lambda: publish_archive(
            root, "build_model", "config/runs/build_model", second, second_payloads
        ),
    ):
        with pytest.raises(ValueError, match="contradicts"):
            action()
    assert path.read_bytes() == b"corrupt"


def test_duplicate_basenames_keep_relative_directories(tmp_path):
    first = tmp_path / "a" / "settings.yml"
    second = tmp_path / "b" / "settings.yml"
    first.parent.mkdir()
    second.parent.mkdir()
    first.write_bytes(b"one\n")
    second.write_bytes(b"two\n")
    sources = capture_sources([("a", "catalog_a", first), ("b", "catalog_b", second)])
    assert source_archive_paths(sources) == {
        "a": "sources/a/settings.yml",
        "b": "sources/b/settings.yml",
    }


def test_file_reference_refuses_tampered_bytes_and_unbound_paths(tmp_path):
    path = tmp_path / "source.yml"
    path.write_bytes(b"one\n")
    reference = file_reference(path, "record_directory", tmp_path)
    assert resolve_file_reference(reference, {"record_directory": tmp_path}) == path
    path.write_bytes(b"two\n")
    with pytest.raises(ValueError, match="bytes differ"):
        resolve_file_reference(reference, {"record_directory": tmp_path})
    with pytest.raises(ValueError, match="unbound"):
        resolve_file_reference(reference, {"project_root": tmp_path})


@pytest.mark.parametrize(
    "mutation",
    [
        lambda r: r.update({"extra": 1}),
        lambda r: r["source_files"][0].update({"extra": 1}),
        lambda r: r.update({"source_config": "missing"}),
        lambda r: r["generated_inputs"].append(
            {
                "role": "input",
                "file": {
                    "schema_version": "artifact-reference/1",
                    "path_base": "arbitrary",
                    "path": "x",
                    "sha256": "0" * 64,
                    "size_bytes": 1,
                },
            }
        ),
    ],
)
def test_closed_record_rejects_unknown_fields_and_bad_pointers(tmp_path, mutation):
    root = tmp_path / "output"
    record, payloads = _archive(tmp_path, "first")
    publish_archive(root, "build_model", "config/runs/build_model", record, payloads)
    directory = root / "config/runs/build_model"
    loaded = yaml.safe_load((directory / "run_record.yml").read_bytes())
    mutation(loaded)
    (directory / "run_record.yml").write_text(yaml.safe_dump(loaded), encoding="utf-8")
    with pytest.raises(ValueError):
        validate_archive(directory)


def test_builder_refuses_unclassified_rerun_overlay(tmp_path):
    source = tmp_path / "project.yml"
    source.write_text("x: 1\n", encoding="utf-8")
    captured = capture_sources([("project", "project_config", source)])
    with pytest.raises(ValueError, match="resolver-overlay"):
        run_record_document(
            workflow="build_model",
            invocation_id="first",
            owner_kind="workflow",
            owner_id="build_model",
            loaded_config={"workflows": {"build_model": {}}},
            advanced_settings={},
            projection=["workflows.build_model"],
            toolbox={"commit": None},
            environment={},
            sources=captured,
            invocation={
                "entry_point": "x",
                "command": [],
                "targets": [],
                "working_directory": str(tmp_path),
                "overrides": {},
            },
            rerun_adjustments=[{"schema_version": "resolver-overlay/1", "extra": 1}],
        )


def test_rerun_retains_predecessor_after_original_is_removed(tmp_path):
    first_root = tmp_path / "A"
    first, payloads = _archive(tmp_path, "first")
    publish_archive(
        first_root, "build_model", "config/runs/build_model", first, payloads
    )
    predecessor = first_root / "config/runs/build_model"
    second_root = tmp_path / "B"
    sources, retained, overlay = capture_rerun_predecessor(
        predecessor,
        predecessor_project_root=first_root,
        new_project_root=second_root,
        output_project_dir=str(second_root),
    )
    second, second_payloads = run_record_document(
        workflow="build_model",
        invocation_id="second",
        owner_kind="workflow",
        owner_id="build_model",
        loaded_config={"workflows": {"build_model": {"enabled": True}}},
        advanced_settings={},
        projection=["workflows.build_model"],
        toolbox={"commit": None},
        invocation={
            "entry_point": "run_workflow.py",
            "command": [],
            "targets": ["all"],
            "working_directory": str(tmp_path),
            "overrides": {},
        },
        sources=sources,
        rerun_adjustments=[overlay],
        environment={},
    )
    publish_archive(
        second_root,
        "build_model",
        "config/runs/build_model",
        second,
        second_payloads | retained,
    )
    (tmp_path / "original" / "project_config.yml").unlink()
    moved = tmp_path / "C"
    second_root.rename(moved)
    assert (
        read_archive(moved, "build_model", "config/runs/build_model")["invocation_id"]
        == "second"
    )


def test_a_to_b_to_relocated_c_composes_without_a(tmp_path):
    root_a = tmp_path / "A"
    source_dir = root_a / "inputs"
    source_dir.mkdir(parents=True)
    project_path = source_dir / "project_config.yml"
    workflow_path = source_dir / "project_config_build_model.yml"
    project_path.write_text(
        yaml.safe_dump(
            {
                "schema_version": cc.SCHEMA_VERSION,
                "project": {"project_dir": str(root_a)},
                "basin": {"region": "x"},
                "climate": {"sources": ["era5"], "selected": "era5"},
                "workflows": {
                    "build_model": {"enabled": True, "config_path": workflow_path.name}
                },
            }
        ),
        encoding="utf-8",
    )
    workflow_bytes = b"# retained\r\nengine:\r\n  build_config: old.yml\r\n"
    workflow_path.write_bytes(workflow_bytes)
    sources = cc.capture_configuration_sources(project_path, "build_model")
    composed, _ = cc.compose_captured_config(sources[0], sources, "build_model")
    invocation = {
        "entry_point": "run_workflow.py",
        "command": [],
        "targets": ["all"],
        "working_directory": str(tmp_path),
        "overrides": {},
    }
    first, payloads = run_record_document(
        workflow="build_model",
        invocation_id="first",
        owner_kind="workflow",
        owner_id="build_model",
        loaded_config=composed,
        advanced_settings={},
        projection=["workflows.build_model"],
        toolbox={"commit": None},
        invocation=invocation,
        sources=sources,
        environment={},
    )
    publish_archive(root_a, "build_model", "config/runs/build_model", first, payloads)
    root_b = tmp_path / "B"
    captured, retained, overlay = capture_rerun_predecessor(
        root_a / "config/runs/build_model",
        predecessor_project_root=root_a,
        new_project_root=root_b,
        output_project_dir=str(root_b),
    )
    second, second_payloads = run_record_document(
        workflow="build_model",
        invocation_id="second",
        owner_kind="workflow",
        owner_id="build_model",
        loaded_config=composed,
        advanced_settings={},
        projection=["workflows.build_model"],
        toolbox={"commit": None},
        invocation=invocation,
        sources=captured,
        rerun_adjustments=[overlay],
        environment={},
    )
    publish_archive(
        root_b,
        "build_model",
        "config/runs/build_model",
        second,
        second_payloads | retained,
    )
    shutil.rmtree(root_a)
    root_c = tmp_path / "C"
    root_b.rename(root_c)
    resolved = resolve_rerun_execution(root_c, "build_model", "config/runs/build_model")
    assert (
        resolved.composed_config["workflows"]["build_model"]["engine"]["build_config"]
        == "old.yml"
    )
    assert resolved.composed_config["project"]["project_dir"] == str(root_c)
    assert (
        Path(resolved.workflow_config_paths["build_model"]).read_bytes()
        == workflow_bytes
    )
    assert resolved.resolve_path(project_path).is_file()
    assert (
        resolved.resolve_path(root_a / "data" / "input.nc")
        == root_c / "data" / "input.nc"
    )
    with pytest.raises(ValueError, match="unmapped external"):
        resolved.resolve_path(tmp_path / "unmapped.nc")
