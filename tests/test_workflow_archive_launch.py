"""WF0--WF2 exact capture before Snakefile parsing."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from blueearth_cst.shared.workflow_archive_launch import (
    CONTEXT_ENV,
    prepare_workflow,
    require_capture,
    split_config_overrides,
)
from blueearth_cst.shared.workflow_config_snapshot import (
    read_archive,
    resolve_file_reference,
)
from scripts import run_workflows

ROOT = Path(__file__).resolve().parents[1]


def test_preparse_capture_survives_source_edit(tmp_path, capsys):
    project = yaml.safe_load((ROOT / "test_case/project_config_rapid.yml").read_text())
    source_workflow = ROOT / "test_case/project_config_rapid_analyze_climate.yml"
    workflow = tmp_path / source_workflow.name
    workflow.write_bytes(source_workflow.read_bytes())
    catalog = tmp_path / "catalog.yml"
    catalog.write_text("meta:\n  roots: [C:/data]\nera5:\n  uri: meteo/data.nc\n")
    project_root = tmp_path / "output"
    project["project"]["project_dir"] = str(project_root)
    project["project"]["catalog"] = [str(catalog)]
    project["workflows"]["analyze_climate"]["config_path"] = str(workflow)
    project_file = tmp_path / "project_config_test.yml"
    project_file.write_text(yaml.safe_dump(project), encoding="utf-8")
    source_bytes = workflow.read_bytes()

    execution, context = prepare_workflow(
        "analyze_climate",
        project_file,
        project_root,
        command=["snakemake", "all"],
        targets=["all"],
    )
    workflow.write_bytes(source_bytes + b"\n# late comment\n")
    record = read_archive(
        project_root, "analyze_climate", "config/runs/analyze_climate"
    )
    assert record["schema_version"] == "run-record/2"
    archived = next(
        entry
        for entry in record["source_files"]
        if entry["role"] == "workflow_config_analyze_climate"
    )
    assert (
        project_root / "config/runs/analyze_climate" / archived["archived_path"]
    ).read_bytes() == source_bytes
    execution_project = yaml.safe_load(execution.read_bytes())
    for name, stanza in execution_project["workflows"].items():
        if name != "analyze_climate":
            assert "config_path" not in stanza
    assert yaml.safe_load(
        Path(
            execution_project["workflows"]["analyze_climate"]["config_path"]
        ).read_bytes()
    ) == yaml.safe_load(source_bytes)
    assert json.loads(context.read_text())["archive_id"] == record["archive_id"]
    assert "[config_composition] skipped unreadable" not in capsys.readouterr().out


def test_shared_dependency_stages_once_across_workflows(tmp_path):
    """A dependency shared by two workflows resolves to one execution path.

    Regression for the bug where each workflow staged its own copy of the same
    data catalog under its own bundle digest: WF0/WF1/WF2 declare byte-identical
    shared-foundation rules (delineate_region and friends) over that catalog,
    so a per-workflow staging path made Snakemake see a changed input set --
    and rebuild the whole foundation -- every time a different workflow last
    ran, even with nothing to redo.
    """
    project = yaml.safe_load((ROOT / "test_case/project_config_rapid.yml").read_text())
    project_root = tmp_path / "output"
    project["project"]["project_dir"] = str(project_root)
    project["project"]["catalog"] = [str((ROOT / "config/catalogs/deltares_data.yml"))]
    for name, stanza in project["workflows"].items():
        if "config_path" in stanza:
            stanza["config_path"] = str(
                (ROOT / "test_case" / stanza["config_path"]).resolve()
            )
    project_file = tmp_path / "project_config_test.yml"
    project_file.write_text(yaml.safe_dump(project), encoding="utf-8")

    execution_a, _ = prepare_workflow(
        "analyze_climate",
        project_file,
        project_root,
        command=["snakemake", "all"],
        targets=["all"],
    )
    execution_b, _ = prepare_workflow(
        "build_model",
        project_file,
        project_root,
        command=["snakemake", "all"],
        targets=["all"],
    )
    catalog_a = yaml.safe_load(execution_a.read_bytes())["project"]["catalog"][0]
    catalog_b = yaml.safe_load(execution_b.read_bytes())["project"]["catalog"][0]
    assert catalog_a == catalog_b
    assert Path(catalog_a).is_relative_to(
        project_root / "config/runs/_engine/execution-configs/_shared"
    )


def test_raw_execution_refuses_without_capture(monkeypatch, tmp_path):
    monkeypatch.delenv(CONTEXT_ENV, raising=False)
    with pytest.raises(ValueError, match="pre-parse source capture"):
        require_capture("build_model", str(tmp_path / "project.yml"))
    require_capture("build_model", str(tmp_path / "project.yml"), dry_run=True)


def test_config_overrides_are_captured_before_forwarding():
    overrides, forwarded = split_config_overrides(
        ["--config", "debug=true", "--keep-going"]
    )
    assert overrides == {"debug": True}
    assert forwarded == ["--keep-going"]
    with pytest.raises(ValueError, match="--configfile"):
        split_config_overrides(["--configfile", "other.yml"])


def test_all_workflow_wrapper_routes_wf0_through_capture(tmp_path, monkeypatch):
    project = yaml.safe_load((ROOT / "test_case/project_config_rapid.yml").read_text())
    output = tmp_path / "output"
    project["project"]["project_dir"] = str(output)
    for name, stanza in project["workflows"].items():
        stanza["enabled"] = name == "analyze_climate"
        if "config_path" in stanza:
            stanza["config_path"] = str(
                (ROOT / "test_case" / stanza["config_path"]).resolve()
            )
    config = tmp_path / "project_config_test.yml"
    config.write_text(yaml.safe_dump(project), encoding="utf-8")
    commands = []

    def fake_run(command, **kwargs):
        if command[0] == "git":
            return SimpleNamespace(returncode=0, stdout="a" * 40 + "\n", stderr="")
        commands.append((command, kwargs))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(
        run_workflows,
        "run_project_child",
        lambda cmd, **kwargs: fake_run(cmd, **kwargs).returncode,
    )
    assert run_workflows.run(str(config), cores=1, extra=[]) == 0
    assert len(commands) == 1
    command, kwargs = commands[0]
    assert command[command.index("--configfile") + 1] != str(config)
    assert CONTEXT_ENV in kwargs["env"]
    record = read_archive(output, "analyze_climate", "config/runs/analyze_climate")
    assert record["schema_version"] == "run-record/2"
    assert record["invocation"]["entry_point"] == "scripts/run_workflows.py"
    invocation_paths = (output / "config/runs/_engine/invocations").glob("*.json")
    invocations = [
        json.loads(path.read_text(encoding="utf-8")) for path in invocation_paths
    ]
    parent = next(item for item in invocations if item["workflow"] is None)
    child = next(item for item in invocations if item["workflow"] == "analyze_climate")
    assert child["invocation_id"] == record["invocation_id"]
    assert child["parent_invocation_id"] == parent["invocation_id"]
    assert (
        resolve_file_reference(
            child["configuration"]["run_record"], {"project_root": output}
        )
        == output / "config/runs/analyze_climate/run_record.yml"
    )
