"""Successor runner target matrix and retained-only operation isolation."""

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from blueearth_cst.experiment.indicator_sets import default_calculations
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
    """One retained experiment and its scoped gwr targets, relative to it.

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
        plan = build_metric_plan(
            root, current_metric_request(root, default_calculations(["gwr"]), "YS-JAN")
        )
    return experiment, {
        name: Path(plan["tables"][name]).relative_to(root)
        for name in ("gwr_run", "gwr_group")
    }


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
    return (
        experiment.config,
        root,
        {"targets": {name: str(root / path) for name, path in gwr.items()}},
    )


@pytest.mark.parametrize("operation", ["simulate-and-metrics", "metrics-only"])
@pytest.mark.parametrize(
    "target",
    [
        "default",
        "all",
        "simulations_only",
        "metrics",
        "selected",
        "selected-run",
        "wrong-set",
        "wflow",
        "mixed",
        "unknown",
    ],
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
    from blueearth_cst.experiment import metric_export

    exports = []
    monkeypatch.setattr(
        metric_export, "export_selected_metrics", lambda *args: exports.append(args)
    )
    if operation == "simulate-and-metrics":
        # This launch-target matrix has no producer catalog. Real admission is
        # covered by the context tests and the fresh all-five execution.
        from blueearth_cst.experiment import reservation_context

        monkeypatch.setattr(
            reservation_context,
            "admit_context_owned",
            lambda *args, **kwargs: SimpleNamespace(
                name=root.name,
                bind_selection=lambda: None,
                environment=lambda: {"CST_EXPERIMENT_NAME": root.name},
            ),
        )
    targets = {
        "all": ["all"],
        "simulations_only": ["simulations_only"],
        "metrics": ["metrics"],
        "selected": [plan["targets"]["gwr_group"]],
        "selected-run": [plan["targets"]["gwr_run"]],
        "wrong-set": [
            str(root / "results/metric_sets" / ("0" * 64) / "gwr_group_indicators.csv")
        ],
        "wflow": [str(root / f"hydrology/wflow/output/{RUN_IDS[0]}.csv")],
        "mixed": ["metrics", plan["targets"]["gwr_group"]],
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
        operation == "simulate-and-metrics"
        and target in {"default", "all", "simulations_only"}
    ) or (
        operation == "metrics-only"
        and target in {"metrics", "selected", "selected-run"}
    )
    if allowed:
        invocation_dir = root.parents[1] / "config/_engine/invocations"
        assert not list(invocation_dir.glob("*.json"))
        assert harness.main(argv) == 0
        assert len(calls) == 1
        if target == "simulations_only":
            assert exports == []
        else:
            assert len(exports) == 1
            assert exports[0][0] == root
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
        assert exports == []
