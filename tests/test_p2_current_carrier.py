"""Successor runner target matrix and retained-only operation isolation."""

import importlib.util
import subprocess
import sys
from pathlib import Path
from shutil import copytree
from types import SimpleNamespace

import pytest
import yaml

from blueearth_cst.experiment.content_identity import (
    canonical_json_bytes,
    read_canonical_json,
)
from blueearth_cst.experiment.metric_plan import (
    build_metric_plan,
    current_metric_request,
)
from tests.test_collection_preparation import retained  # noqa: F401
from tests.test_metric_plan import metric_inputs  # noqa: F401
from tests.test_response_inventory import frozen  # noqa: F401
from tests.test_scenario_collection import planned  # noqa: F401
from tests.test_simulation_record import inputs  # noqa: F401
from tests.test_wflow_response_reader import native  # noqa: F401

REPO = Path(__file__).resolve().parents[1]
HARNESS = REPO / "scripts/simulate_system.py"


@pytest.fixture
def carrier_state(metric_inputs, tmp_path):  # noqa: F811
    original, _ = metric_inputs
    project = tmp_path / "retained-project"
    root = project / "experiments" / "metric_experiment"
    copytree(original, root)
    # The lower-level fixture uses a name outside the production namespace grammar.
    record_path = root / "config/simulation.json"
    record = read_canonical_json(record_path)
    record["experiment_name"] = root.name
    record_path.write_bytes(canonical_json_bytes(record))
    workflow = tmp_path / "wf3.yml"
    workflow.write_text(
        yaml.safe_dump(
            {
                "experiment_name": root.name,
                "operation": "metrics-only",
                "metrics": ["gwr"],
                "water_year_start": "jan",
                "seed": "ignored",
                "n_realizations": "ignored",
            }
        ),
        encoding="utf-8",
    )
    config = tmp_path / "project.yml"
    config.write_text(
        yaml.safe_dump(
            {
                "project": {
                    "project_dir": str(project),
                    "catalog": str(tmp_path / "missing-generation.yml"),
                },
                "workflows": {
                    "simulate_system": {"enabled": True, "config_path": workflow.name},
                    "build_model": {
                        "enabled": True,
                        "config_path": "missing-model.yml",
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    request = current_metric_request(root, ["gwr"], "YS-JAN")
    plan = build_metric_plan(root, request)
    assert not (project / "models").exists()
    assert not (tmp_path / "missing-generation.yml").exists()
    return config, root, plan


@pytest.mark.parametrize("operation", ["simulate-and-metrics", "metrics-only"])
@pytest.mark.parametrize(
    "target",
    ["default", "all", "metrics", "selected", "wrong-set", "wflow", "mixed", "unknown"],
)
def test_current_carrier_operation_target_matrix(
    carrier_state, monkeypatch, operation, target
):
    config, root, plan = carrier_state
    spec = importlib.util.spec_from_file_location("p2_current_carrier_runner", HARNESS)
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    calls = []

    def launch(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(harness.subprocess, "run", launch)
    targets = {
        "all": ["all"],
        "metrics": ["metrics"],
        "selected": [plan["targets"]["gwr"]],
        "wrong-set": [
            str(root / "results/metric_sets" / ("0" * 64) / "gwr_indicators.csv")
        ],
        "wflow": [str(root / "hydrology/wflow/output/run_01.csv")],
        "mixed": ["metrics", plan["targets"]["gwr"]],
        "unknown": ["unknown"],
    }
    source = yaml.safe_load(config.read_text())
    workflow_path = (
        config.parent / source["workflows"]["simulate_system"]["config_path"]
    )
    settings = yaml.safe_load(workflow_path.read_text())
    settings["operation"] = operation
    workflow_path.write_text(yaml.safe_dump(settings), encoding="utf-8")
    argv = ["--config", str(config)]
    if target != "default":
        argv += ["--target", *targets[target]]
    allowed = (
        operation == "simulate-and-metrics" and target in {"default", "all"}
    ) or (operation == "metrics-only" and target in {"metrics", "selected"})
    if allowed:
        invocation_dir = root.parents[1] / "config/runs/invocations"
        assert not invocation_dir.exists()
        assert harness.main(argv) == 0
        assert len(calls) == 1
        command, kwargs = calls[0]
        assert command[:3] == [sys.executable, "-m", "snakemake"]
        assert command[3] == ("all" if target == "default" else targets[target][0])
        assert kwargs["env"]["CST_SIMULATION_OPERATION"] == operation
        records = list(invocation_dir.glob("simulation-*.json"))
        assert len(records) == 1
        record = read_canonical_json(records[0])
        assert record["status"] == "succeeded"
        assert record["exit_code"] == 0
        assert record["operation"] == operation
    else:
        with pytest.raises(SystemExit) as error:
            harness.main(argv)
        assert error.value.code == 2
        assert calls == []


def test_current_carrier_metrics_only_dry_run_without_live_inputs(
    carrier_state, tmp_path
):
    config, _, _ = carrier_state
    result = subprocess.run(
        [
            sys.executable,
            str(HARNESS),
            "--config",
            str(config),
            "--target",
            "metrics",
            "--dry-run",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    output = result.stdout + result.stderr
    (tmp_path / "current-carrier-dry-run.log").write_text(output, encoding="utf-8")
    assert result.returncode == 0, output
    assert "simulate_system: metrics" in output
    assert "prepare_metric_plan" in output
    for producer in (
        "generate_weather_realizations",
        "downscale_climate_realization",
        "run_wflow_batch_",
        "extract_historical_climate",
    ):
        assert producer not in output
