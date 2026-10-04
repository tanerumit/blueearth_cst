"""Successor runner target matrix and retained-only operation isolation."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

from blueearth_cst.experiment.metric_plan import (
    build_metric_plan,
    current_metric_request,
)
from tests._v2_experiment import (
    FIXTURE_ENVIRONMENT,
    RUN_IDS,
    build_v2_experiment,
    copy_v2_experiment,
)

REPO = Path(__file__).resolve().parents[1]
HARNESS = REPO / "scripts/simulate_system.py"


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """One retained experiment and its metric plan's gwr target, relative to it.

    Planning is the expensive part of each case and its result is
    project-relative, so it is computed once here rather than on every copy.
    """
    from blueearth_cst.experiment import metric_plan

    experiment = build_v2_experiment(tmp_path_factory.mktemp("carrier"))
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(
            metric_plan, "resolve_metric_environment", lambda: FIXTURE_ENVIRONMENT
        )
        root = experiment.root
        plan = build_metric_plan(root, current_metric_request(root, ["gwr"], "YS-JAN"))
    return experiment, Path(plan["targets"]["gwr"]).relative_to(root)


@pytest.fixture
def carrier_state(built, tmp_path, monkeypatch):
    """A private copy of the retained v2 experiment, declaring metrics-only."""
    from blueearth_cst.experiment import metric_plan

    monkeypatch.setattr(
        metric_plan, "resolve_metric_environment", lambda: FIXTURE_ENVIRONMENT
    )
    source, gwr = built
    experiment = copy_v2_experiment(source, tmp_path)
    root = experiment.root
    return experiment.config, root, {"targets": {"gwr": str(root / gwr)}}


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
        return 0

    monkeypatch.setattr(harness, "run_project_child", launch)
    targets = {
        "all": ["all"],
        "metrics": ["metrics"],
        "selected": [plan["targets"]["gwr"]],
        "wrong-set": [
            str(root / "results/metric_sets" / ("0" * 64) / "gwr_indicators.csv")
        ],
        "wflow": [str(root / f"hydrology/wflow/output/run_{RUN_IDS[0]}.csv")],
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
        invocation_dir = root.parents[1] / "config/runs/_engine/invocations"
        assert not list(invocation_dir.glob("*.json"))
        assert harness.main(argv) == 0
        assert len(calls) == 1
        command, kwargs = calls[0]
        assert command[:3] == [sys.executable, "-m", "snakemake"]
        expected = "all" if target == "default" else targets[target][0]
        # A retired target name reaches Snakemake as its current rule name.
        assert command[3] == {"metrics": "simulations_and_indicators"}.get(
            expected, expected
        )
        assert kwargs["env"]["CST_SIMULATION_OPERATION"] == operation
        records = list(invocation_dir.glob("*.json"))
        assert len(records) == 1
        record = json.loads(records[0].read_text(encoding="utf-8"))
        assert record["status"] == "succeeded"
        assert record["exit_code"] == 0
        assert record["operation"] == operation
    else:
        with pytest.raises(SystemExit) as error:
            harness.main(argv)
        assert error.value.code == 2
        assert calls == []
