"""Saved integrity and fresh numerical evidence have different prerequisites."""

import json
import shutil
import subprocess
import sys

import pytest

from blueearth_cst.experiment import metric_plan
from blueearth_cst.experiment.content_identity import atomic_record, content_sha256
from blueearth_cst.experiment.indicator_sets import default_calculations
from blueearth_cst.experiment.metric_artifacts import ImmutableMetricSetError
from blueearth_cst.experiment.metric_inspection import inspect_metric_set
from tests._v2_experiment import (
    FIXTURE_ENVIRONMENT,
    build_v2_experiment,
    copy_v2_experiment,
)


@pytest.fixture(scope="module")
def saved(tmp_path_factory):
    experiment = build_v2_experiment(tmp_path_factory.mktemp("inspection"))
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(
            metric_plan, "resolve_metric_environment", lambda: FIXTURE_ENVIRONMENT
        )
        request = metric_plan.current_metric_request(
            experiment.root, default_calculations(["gwr"]), "YE-DEC"
        )
        plan = metric_plan.build_metric_plan(experiment.root, request)
        metric_plan.publish_metric_set(experiment.root, plan)
    return experiment, plan["metric_set_id"][:12]


@pytest.fixture
def publication(saved, tmp_path, monkeypatch):
    original, short = saved
    experiment = copy_v2_experiment(original, tmp_path)
    monkeypatch.setattr(
        metric_plan, "resolve_metric_environment", lambda: FIXTURE_ENVIRONMENT
    )
    marker = experiment.root / "_engine/metric_sets" / short / "metrics.json"
    return experiment.root, marker


def test_integrity_import_does_not_load_metric_registries():
    code = (
        "import sys; import blueearth_cst.experiment.metric_inspection; "
        "assert 'blueearth_cst.experiment.metric_registry' not in sys.modules; "
        "assert 'blueearth_cst.metrics.loader' not in sys.modules"
    )
    subprocess.run([sys.executable, "-c", code], check=True)


@pytest.mark.parametrize("debug", [False, True])
def test_inspection_cli_missing_completion_has_nonzero_exit(tmp_path, debug):
    from pathlib import Path

    repo = Path(__file__).resolve().parents[1]
    command = [
        sys.executable,
        str(repo / "scripts/inspect_metrics.py"),
        "--experiment",
        str(tmp_path),
        "--manifest",
        str(tmp_path / "metrics.json"),
    ]
    if debug:
        command.append("--traceback")
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode != 0
    assert "missing completion receipt" in result.stderr
    assert ("Traceback" in result.stderr) is debug


def test_fresh_recheck_and_historical_binding(publication):
    root, marker = publication
    result = inspect_metric_set(root, marker, recheck=True)
    assert result["numerical"]["status"] == "passed", result
    history = inspect_metric_set(root, marker)["historical_checks"]
    assert len(history) == 1 and history[0]["label"] == "historical"
    unrelated = dict(history[0]["receipt"], publication={"metric_set_id": "other"})
    atomic_record(marker.parent / "verification/unrelated.json", unrelated)
    comparison = dict(
        history[0]["receipt"], schema_version="comparison/1", kind="comparison"
    )
    atomic_record(marker.parent / "verification/comparison.json", comparison)
    assert len(inspect_metric_set(root, marker)["historical_checks"]) == 1


def test_corruption_and_missing_completion_fail_integrity(publication):
    root, marker = publication
    artifact = marker.parent / "data/gwr_run_indicators.csv"
    artifact.write_bytes(artifact.read_bytes() + b"x")
    with pytest.raises(ImmutableMetricSetError, match="table differs"):
        inspect_metric_set(root, marker)
    marker.unlink()
    with pytest.raises(ImmutableMetricSetError, match="missing completion receipt"):
        inspect_metric_set(root, marker)


@pytest.mark.parametrize(
    "change", ["missing-inventory", "missing-input", "changed-input"]
)
def test_missing_input_keeps_integrity_and_blocks_requested_recheck(
    publication, change
):
    root, marker = publication
    if change == "missing-inventory":
        (root / "_engine/response_inventory.json").unlink()
    else:
        from tests._v2_experiment import native_runs

        native = next(iter(native_runs(root).values())).csv_path
        if change == "missing-input":
            native.unlink()
        else:
            native.write_bytes(native.read_bytes() + b"\n")
    assert inspect_metric_set(root, marker)["integrity"]["status"] == "passed"
    result = inspect_metric_set(root, marker, recheck=True)
    assert result["numerical"]["status"] == "unavailable"


def test_dependency_drift_keeps_integrity_and_blocks_recheck(publication, monkeypatch):
    root, marker = publication
    monkeypatch.setattr(
        metric_plan,
        "resolve_metric_environment",
        lambda: {"packages": {"numpy": "changed"}},
    )
    result = inspect_metric_set(root, marker, recheck=True)
    assert result["integrity"]["status"] == "passed"
    assert "dependency versions differ" in result["numerical"]["reason"]


def test_checker_sources_do_not_enter_execution_identity(publication):
    _, marker = publication
    saved = json.loads(marker.read_text(encoding="utf-8"))
    assert (
        "configured water-year anchor"
        in saved["execution_context"]["set_assumptions"]["default"]["annual_blocks"]
    )
    paths = {
        row["path"] for row in saved["execution_context"]["request"]["code_inventory"]
    }
    assert any(path.endswith("sets/default/calculations.py") for path in paths)
    assert not any(path.endswith(("checks.py", "checking.py")) for path in paths)


def test_failed_numerical_check_is_distinct_from_ineligibility(
    publication, monkeypatch
):
    from blueearth_cst.metrics import loader

    root, marker = publication

    def wrong_answer(*args, **kwargs):
        raise ValueError(
            "default/gwr_annual_total/location=9: deliberate numerical mismatch"
        )

    monkeypatch.setattr(loader, "check", wrong_answer)
    result = inspect_metric_set(root, marker, recheck=True)
    assert result["integrity"]["status"] == "passed"
    assert result["numerical"]["status"] == "failed"
    with pytest.raises(ValueError, match="deliberate numerical mismatch"):
        inspect_metric_set(root, marker, recheck=True, traceback=True)


def test_changed_execution_source_blocks_numerical_only(
    publication, tmp_path, monkeypatch
):
    from pathlib import Path

    from blueearth_cst.experiment import metric_inspection

    root, marker = publication
    document = json.loads(marker.read_text(encoding="utf-8"))
    repo = Path(metric_inspection.__file__).resolve().parents[2]
    copied_repo = tmp_path / "execution-copy"
    for source in document["execution_context"]["request"]["code_inventory"]:
        destination = copied_repo / source["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo / source["path"], destination)
    changed = copied_repo / "blueearth_cst/metrics/sets/default/calculations.py"
    changed.write_bytes(changed.read_bytes() + b"\n# deliberate execution edit\n")
    monkeypatch.setattr(
        metric_inspection,
        "__file__",
        str(copied_repo / "blueearth_cst/experiment/metric_inspection.py"),
    )
    result = inspect_metric_set(root, marker, recheck=True)
    assert result["integrity"]["status"] == "passed"
    assert "execution source changed" in result["numerical"]["reason"]


def test_changed_checker_gets_fresh_attribution(publication, monkeypatch):
    from pathlib import Path

    from blueearth_cst.metrics.sets.default import checks

    root, marker = publication
    first = inspect_metric_set(root, marker, recheck=True)
    assert first["numerical"]["status"] == "passed", first
    checker = Path(checks.__file__)
    original_read = Path.read_bytes

    def changed_bytes(path):
        data = original_read(path)
        return data + b"\n# changed checker evidence\n" if path == checker else data

    monkeypatch.setattr(Path, "read_bytes", changed_bytes)
    second = inspect_metric_set(root, marker, recheck=True)
    assert second["numerical"]["status"] == "passed", second
    before = json.loads(Path(first["numerical"]["receipt"]).read_text(encoding="utf-8"))
    after = json.loads(Path(second["numerical"]["receipt"]).read_text(encoding="utf-8"))
    assert before["checker_sources"] != after["checker_sources"]


def test_old_publication_inspection_without_rewriting_inputs(publication):
    root, marker = publication
    document = json.loads(marker.read_text(encoding="utf-8"))
    document.pop("execution_context")
    document["schema_version"] = "metric-set/4"
    document["identity_projection"]["schema_version"] = "metric-set-identity/4"
    document["metric_set_id"] = content_sha256(document["identity_projection"])
    old_engine = marker.parent.with_name(document["metric_set_id"][:12])
    old_engine_relative = old_engine.relative_to(root).as_posix()
    original_root = document["engine_root"]
    # Re-identify only this disposable fixture to exercise the genuine old schema.
    document = json.loads(
        json.dumps(document).replace(original_root, old_engine_relative)
    )
    document.pop("metrics_manifest_sha256")
    document["metrics_manifest_sha256"] = content_sha256(document)
    marker.parent.rename(old_engine)
    old_marker = old_engine / "metrics.json"
    atomic_record(old_marker, document, replace=True)
    before = old_marker.read_bytes()
    report = inspect_metric_set(root, old_marker, recheck=True)
    assert report["integrity"]["status"] == "passed"
    assert "legacy publication" in report["numerical"]["reason"]
    assert old_marker.read_bytes() == before
