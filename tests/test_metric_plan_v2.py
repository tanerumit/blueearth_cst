"""Metric sets over a real retained v2 experiment, end to end and unstubbed.

`tests/_v2_experiment.py` builds the experiment with the production WF3/WF4
record producers. Nothing on the reading side is replaced here: planning,
reduction, publication and reading all go through `metric_plan`'s v2 branch.
"""

import pytest

from blueearth_cst.experiment.content_identity import identity_segment
from blueearth_cst.experiment.metric_plan import (
    ImmutableMetricSetError,
    build_metric_plan,
    current_metric_request,
    publish_metric_set,
    read_metric_set,
)
from tests._v2_experiment import (
    FIXTURE_ENVIRONMENT,
    RUN_IDS,
    build_v2_experiment,
    copy_v2_experiment,
)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    return build_v2_experiment(tmp_path_factory.mktemp("v2-experiment"))


@pytest.fixture
def experiment(built, tmp_path, monkeypatch):
    from blueearth_cst.experiment import metric_plan

    monkeypatch.setattr(
        metric_plan, "resolve_metric_environment", lambda: FIXTURE_ENVIRONMENT
    )
    return copy_v2_experiment(built, tmp_path)


def _plan(root):
    return build_metric_plan(root, current_metric_request(root, ["gwr"], "YS-JAN"))


def test_the_fixture_is_a_ready_v2_experiment_wherever_it_is_copied(experiment):
    from blueearth_cst.experiment.response_inventory import read_response_inventory_v2
    from blueearth_cst.experiment.scenario_collection_v2 import read_collection_v2
    from blueearth_cst.experiment.simulation_record import read_simulation_v2

    root = experiment.root
    # metric_plan takes its v1 branch whenever the v2 marker is absent, so a
    # broken fixture would otherwise test the legacy path without saying so.
    assert (root / "_engine/simulation.json").is_file()
    assert not (root / "config/simulation.json").exists()
    assert read_simulation_v2(root)["status"] == "ready"
    assert read_response_inventory_v2(root)["schema_version"] == (
        "response-inventory/2"
    )
    marker = read_collection_v2(experiment.collection_marker)
    assert [item["run_id"] for item in marker["series"]] == list(RUN_IDS)


def test_a_v2_metric_set_publishes_once_and_is_reused_byte_for_byte(experiment):
    root = experiment.root
    plan = _plan(root)
    assert plan["schema_version"] == "metric-request/2"
    manifest = publish_metric_set(root, plan)
    marker = (
        root
        / "_engine/metric_sets"
        / identity_segment(plan["metric_set_id"], "metric_set_id")
        / "metrics.json"
    )
    result = root / "results/metric_sets" / marker.parent.name
    assert (result / "gwr_indicators.csv").is_file()
    files = sorted(p for d in (marker.parent, result) for p in d.rglob("*"))
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}
    assert read_metric_set(root, marker) == manifest
    assert publish_metric_set(root, _plan(root)) == manifest
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}


def test_a_changed_native_response_byte_refuses_planning(experiment):
    native = experiment.root / f"hydrology/wflow/output/run_{RUN_IDS[0]}.csv"
    original = native.read_bytes()
    native.write_bytes(original.replace(b",3\n", b",4\n"))
    assert native.read_bytes() != original
    with pytest.raises(ValueError, match="bytes differ"):
        _plan(experiment.root)


def test_a_tampered_published_table_is_refused_on_read(experiment):
    root = experiment.root
    plan = _plan(root)
    publish_metric_set(root, plan)
    short = identity_segment(plan["metric_set_id"], "metric_set_id")
    table = root / "results/metric_sets" / short / "gwr_indicators.csv"
    table.write_bytes(table.read_bytes() + b"gwr_mean,9,1,0\n")
    with pytest.raises(ImmutableMetricSetError):
        read_metric_set(root, root / "_engine/metric_sets" / short / "metrics.json")
