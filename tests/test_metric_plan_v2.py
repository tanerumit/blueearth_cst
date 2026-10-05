"""Metric sets over a real retained v2 experiment, end to end and unstubbed.

`tests/_v2_experiment.py` builds the experiment with the production WF3/WF4
record producers. Nothing on the reading side is replaced here: planning,
reduction, publication and reading all go through `metric_plan`'s v2 branch.
The live metric-stage environment is presented as `FIXTURE_ENVIRONMENT`
wherever a test plans against it, because publication re-observes it.
"""

import csv
from copy import deepcopy

import numpy as np
import pandas as pd
import pytest
import yaml

from blueearth_cst.experiment.content_identity import (
    canonical_json_bytes,
    content_sha256,
    identity_segment,
    read_canonical_json,
)
from blueearth_cst.experiment.metric_plan import (
    ImmutableMetricSetError,
    MetricPlanStale,
    build_metric_plan,
    current_metric_request,
    publish_metric_set,
    read_metric_set,
    verify_metric_plan,
    write_metric_plan,
)
from tests._v2_experiment import (
    FIXTURE_ENVIRONMENT,
    RUN_IDS,
    Responses,
    build_v2_experiment,
    copy_v2_experiment,
)


def _live(monkeypatch, observed=FIXTURE_ENVIRONMENT):
    from blueearth_cst.experiment import metric_plan

    monkeypatch.setattr(metric_plan, "resolve_metric_environment", lambda: observed)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    return build_v2_experiment(tmp_path_factory.mktemp("v2-experiment"))


@pytest.fixture
def bare(built, tmp_path):
    """A private copy, with the live metric environment left as it really is."""
    return copy_v2_experiment(built, tmp_path)


@pytest.fixture
def experiment(bare, monkeypatch):
    _live(monkeypatch)
    return bare


@pytest.fixture(scope="module")
def _published_once(built, tmp_path_factory):
    """One experiment with its gwr metric set already published.

    The tamper tests only need a ready set to corrupt, and planning plus
    publication is most of their cost, so they share this one and each gets a
    private copy. Every reference inside a set is project-relative.
    """
    experiment = copy_v2_experiment(built, tmp_path_factory.mktemp("published"))
    with pytest.MonkeyPatch.context() as patch:
        from blueearth_cst.experiment import metric_plan

        patch.setattr(
            metric_plan, "resolve_metric_environment", lambda: FIXTURE_ENVIRONMENT
        )
        plan = _plan(experiment.root)
        publish_metric_set(experiment.root, plan)
    return experiment, identity_segment(plan["metric_set_id"], "metric_set_id")


@pytest.fixture
def published(_published_once, tmp_path, monkeypatch):
    """A private copy: (root, engine marker, result directory)."""
    _live(monkeypatch)
    source, short = _published_once
    root = copy_v2_experiment(source, tmp_path).root
    marker = root / "_engine/metric_sets" / short / "metrics.json"
    return root, marker, root / "results/metric_sets" / short


def _plan(root, tokens=("gwr",)):
    return build_metric_plan(root, current_metric_request(root, list(tokens), "YS-JAN"))


def _engine(root, plan):
    short = identity_segment(plan["metric_set_id"], "metric_set_id")
    return root / "_engine/metric_sets" / short


def _result(root, plan):
    short = identity_segment(plan["metric_set_id"], "metric_set_id")
    return root / "results/metric_sets" / short


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
    assert len(plan["expected_result_keys"]) == 2
    assert plan["units"] == [
        {"run_group_id": run, "grain": "run", "run_id": run} for run in RUN_IDS
    ]
    manifest = publish_metric_set(root, plan)
    marker = _engine(root, plan) / "metrics.json"
    assert (_result(root, plan) / "gwr_indicators.csv").is_file()
    files = sorted(
        p for d in (marker.parent, _result(root, plan)) for p in d.rglob("*")
    )
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}
    assert read_metric_set(root, marker) == manifest
    assert publish_metric_set(root, _plan(root)) == manifest
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}


def test_the_metric_environment_changes_only_the_metric_identity(experiment):
    root = experiment.root
    request = current_metric_request(root, ["gwr"], "YS-JAN")
    before = build_metric_plan(root, request)
    changed = deepcopy(request)
    changed["metric_environment"]["packages"]["numpy"] = "another"
    after = build_metric_plan(root, changed)
    assert after["metric_set_id"] != before["metric_set_id"]
    assert after["response_inventory_sha256"] == before["response_inventory_sha256"]
    assert after["request"]["simulation_id"] == before["request"]["simulation_id"]


def test_an_xclim_revision_changes_only_the_metric_identity(bare, monkeypatch):
    from blueearth_cst.experiment import content_identity

    root = bare.root
    revision = "first"

    def environment(roots):
        return {
            "packages": {
                name: revision if name == "xclim" else "fixed" for name in roots
            }
        }

    monkeypatch.setattr(content_identity, "stage_environment", environment)
    before = _plan(root)
    revision = "second"
    after = _plan(root)
    assert before["metric_set_id"] != after["metric_set_id"]
    assert before["request"]["simulation_id"] == after["request"]["simulation_id"]
    assert before["response_inventory_sha256"] == after["response_inventory_sha256"]


def test_a_changed_native_response_byte_refuses_planning(experiment):
    native = experiment.root / f"hydrology/wflow/output/run_{RUN_IDS[0]}.csv"
    original = native.read_bytes()
    native.write_bytes(original.replace(b",3\n", b",4\n"))
    assert native.read_bytes() != original
    with pytest.raises(ValueError, match="bytes differ"):
        _plan(experiment.root)


def test_a_tampered_published_table_is_refused_on_read(published):
    root, marker, result = published
    read_metric_set(root, marker)
    table = result / "gwr_indicators.csv"
    table.write_bytes(table.read_bytes() + b"gwr_mean,9,1,0\n")
    with pytest.raises(ImmutableMetricSetError):
        read_metric_set(root, marker)


def test_tampered_return_level_evidence_is_refused_on_read(published):
    from blueearth_cst.experiment.metric_plan import RETURN_LEVEL_EVIDENCE_FILENAME

    root, marker, _ = published
    evidence = marker.parent / RETURN_LEVEL_EVIDENCE_FILENAME
    assert read_canonical_json(evidence)["bundles"] == [], "gwr fits no return level"
    read_metric_set(root, marker)
    evidence.write_bytes(b'{"bundles": [], "schema_version": "other"}\n')
    with pytest.raises(ImmutableMetricSetError, match="metric artifact differs"):
        read_metric_set(root, marker)


def test_a_set_published_before_evidence_was_retained_stays_readable(published):
    """Sets published before 2026-10-04 carry no evidence key at all."""
    root, marker, _ = published
    manifest = read_canonical_json(marker)
    del manifest["return_level_evidence"]
    manifest["metrics_manifest_sha256"] = content_sha256(
        {k: v for k, v in manifest.items() if k != "metrics_manifest_sha256"}
    )
    marker.write_bytes(canonical_json_bytes(manifest))
    assert read_metric_set(root, marker) == manifest


def test_only_metrics_json_is_read_as_the_engine_marker(published):
    root, marker, _ = published
    renamed = marker.with_name("alternate.json")
    renamed.write_bytes(marker.read_bytes())
    with pytest.raises(ImmutableMetricSetError, match="named metrics.json"):
        read_metric_set(root, renamed)


def test_a_table_renamed_in_the_manifest_is_refused(published):
    root, marker, result = published
    manifest = read_metric_set(root, marker)
    (result / "alternate.csv").write_bytes((result / "gwr_indicators.csv").read_bytes())
    manifest["tables"][0]["file"]["path"] = (
        f"results/metric_sets/{result.name}/alternate.csv"
    )
    manifest["metrics_manifest_sha256"] = content_sha256(
        {k: v for k, v in manifest.items() if k != "metrics_manifest_sha256"}
    )
    marker.write_bytes(canonical_json_bytes(manifest))
    with pytest.raises(ImmutableMetricSetError, match="table reference"):
        read_metric_set(root, marker)


def test_the_published_set_carries_and_verifies_its_benchmark_report(published):
    from blueearth_cst.experiment import return_level_validation

    root, marker, _ = published
    manifest = read_canonical_json(marker)
    report = marker.parent / return_level_validation.REPORT_FILENAME
    assert report.read_bytes() == return_level_validation.load_report_bytes()
    assert manifest["return_level_benchmark"]["path"] == report.name
    assert read_metric_set(root, marker) == manifest
    # A tampered copy must fail the reader rather than downgrade silently.
    report.write_bytes(b"{}\n")
    with pytest.raises(ImmutableMetricSetError, match="metric artifact differs"):
        read_metric_set(root, marker)


def test_a_stale_live_environment_refuses_reduction_before_any_fit(
    experiment, monkeypatch
):
    """D5: drift between planning and execution aborts before fitting."""
    from blueearth_cst.experiment import gev_lmoments
    from blueearth_cst.experiment import metric_plan as plan_module

    root = experiment.root
    plan = _plan(root)
    _live(monkeypatch, {"packages": {"numpy": "moved"}})
    calls = []
    real = gev_lmoments.fit_case
    monkeypatch.setattr(
        gev_lmoments, "fit_case", lambda *a, **k: (calls.append(a), real(*a, **k))[1]
    )
    with pytest.raises(MetricPlanStale, match="live metric-stage environment"):
        plan_module.reduce_metric_plan(root, plan)
    assert calls == [], "the estimator ran despite a stale environment"


def test_a_stale_live_environment_leaves_no_ready_marker(experiment, monkeypatch):
    root = experiment.root
    plan = _plan(root)
    _live(monkeypatch, {"packages": {"numpy": "moved"}})
    with pytest.raises(MetricPlanStale):
        publish_metric_set(root, plan)
    assert not (_engine(root, plan) / "metrics.json").exists()


def _moved_plan(experiment, tmp_path_factory):
    """Write the gwr plan, then copy the experiment to another project root."""
    request = current_metric_request(experiment.root, ["gwr"], "YS-JAN")
    write_metric_plan(experiment.root, request)
    moved = copy_v2_experiment(experiment, tmp_path_factory.mktemp("moved")).root
    (stored,) = (moved / "_engine/metric_requests").glob("*.json")
    return moved, request, stored


def test_a_plan_copied_from_another_root_verifies_at_the_new_root(
    experiment, tmp_path_factory
):
    """t2610042152: a stored plan's targets name the root it was written at."""
    moved, request, stored = _moved_plan(experiment, tmp_path_factory)
    assert experiment.root.as_posix() in stored.read_text(encoding="utf-8")
    plan = verify_metric_plan(moved, request)
    assert plan == build_metric_plan(moved, request)
    assert all(
        target.startswith(moved.as_posix() + "/") for target in plan["targets"].values()
    )


def _other_field(plan, origin):
    plan["expected_result_keys"] = plan["expected_result_keys"][:1]


def _mixed_roots(plan, origin):
    """One target keeps its tail but under a third root."""
    target = plan["targets"]["gwr"]
    plan["targets"]["gwr"] = "C:/elsewhere" + target[len(origin.as_posix()) :]


@pytest.mark.parametrize(
    "tamper, redigest",
    [(_other_field, True), (_mixed_roots, True), (lambda plan, origin: None, False)],
    ids=["another-field", "mixed-roots", "stale-self-digest"],
)
def test_a_moved_plan_still_refuses_any_other_difference(
    experiment, tmp_path_factory, tamper, redigest
):
    moved, request, stored = _moved_plan(experiment, tmp_path_factory)
    plan = read_canonical_json(stored)
    tamper(plan, experiment.root)
    body = {key: value for key, value in plan.items() if key != "request_sha256"}
    plan["request_sha256"] = content_sha256(body) if redigest else "0" * 64
    stored.write_bytes(canonical_json_bytes(plan))
    with pytest.raises(MetricPlanStale):
        verify_metric_plan(moved, request)


@pytest.mark.parametrize("mismatch", [False, True])
def test_metrics_only_reads_the_anchor_and_asserts_the_retained_collection(
    experiment, capsys, mismatch
):
    from blueearth_cst.experiment import metric_plan
    from blueearth_cst.experiment.simulation_record import read_simulation_intent_v2

    retained = read_simulation_intent_v2(experiment.root)["collection"]
    asserted = {
        "collection_id": retained["collection_id"],
        "collection_revision": "0" * 64
        if mismatch
        else retained["collection_revision"],
    }
    config = experiment.config
    workflow = config.parent / "simulate_system.yml"
    workflow.write_text(
        yaml.safe_dump(
            {
                "experiment_name": experiment.root.name,
                "metrics": ["gwr"],
                "scenario_collection": asserted,
                "seed": 123,
                "simulation_window": {"start": 9990, "end": 9999},
            }
        ),
        encoding="utf-8",
    )
    project = yaml.safe_load(config.read_text(encoding="utf-8"))
    project["climate"] = {"water_year_start": "oct"}
    project["model"] = {"name": "unavailable-model"}
    config.write_text(yaml.safe_dump(project), encoding="utf-8")
    if mismatch:
        with pytest.raises(ValueError, match="collection_revision"):
            metric_plan.metrics_only_configuration(config)
        return
    root, tokens, anchor = metric_plan.metrics_only_configuration(config)
    assert root == experiment.root
    assert tokens == ["gwr"]
    assert anchor == "YS-OCT"
    output = capsys.readouterr().out
    assert "seed" in output and "simulation_window" in output
    assert "model.name" in output and "_engine/simulation.json" in output


# --- thirty years of discharge: real GEV fits and class-C month means --------

_TIME = pd.date_range("2046-01-01", "2075-12-31", freq="D")
_FACTORS = {"1": 1.0, "2": 1.5}


def _discharge_frames():
    rng = np.random.default_rng(12345)
    yearly = rng.uniform(0.8, 1.2, 30)[_TIME.year - 2046]
    base = np.where(_TIME.month == 7, 100.0, np.where(_TIME.month == 1, 5.0, 30.0))
    return {
        run: pd.DataFrame(
            {"Q_9": f * base * yearly, "Q_2": f * (120 - base) * yearly}, index=_TIME
        )
        for run, f in _FACTORS.items()
    }


def _discharge_responses(frames):
    temporal = {
        "source_calendar": "proleptic_gregorian",
        "prepared_forcing_calendar": "proleptic_gregorian",
        "response_calendar": "standard",
        "operations": ["clip_to_configured_window", "refresh_toml_endpoints"],
        "prepared_start": "2045-12-31 00:00:00",
        "prepared_end": str(_TIME[-1]),
        "response_start": str(_TIME[0]),
        "response_end": str(_TIME[-1]),
        "time_label": "interval_end",
    }
    return Responses(
        csv={
            run: frame.to_csv(index_label="time", lineterminator="\n").encode()
            for run, frame in frames.items()
        },
        toml=(
            '[time]\ncalendar="standard"\ntimestepsecs=86400\n'
            'starttime="2045-12-31T00:00:00"\nendtime="2075-12-31T00:00:00"\n'
            '[[output.csv.column]]\nheader="Q"\n'
            'parameter="river_water__volume_flow_rate"\n'
        ),
        temporal=temporal,
        variables=[
            {
                "variable": "q",
                "locations": ["9", "2"],
                "units": "m3 s-1",
                "calendar": "standard",
                "timestep": "P1D",
                "time_label": "interval_end",
                "start": str(_TIME[0]),
                "end": str(_TIME[-1]),
                "missing_value": "NaN",
            }
        ],
    )


def test_q_bundles_and_class_c_use_exact_units_and_shared_reference(
    tmp_path, monkeypatch
):
    """Thirty full years exercise actual GEV fits and independent month means."""
    _live(monkeypatch)
    frames = _discharge_frames()
    root = build_v2_experiment(tmp_path, _discharge_responses(frames), capacity=9).root
    plan = _plan(root, ("q",))
    assert plan["bundle_run_group_ids"] == {"": "3", "1": "4"}
    assert plan["units"] == [
        {"run_group_id": unit, "grain": grain, "run_id": run}
        for unit, grain, run in (
            ("1", "run", "1"),
            ("2", "run", "2"),
            ("3", "bundle", "1"),
            ("4", "bundle", "2"),
        )
    ]
    for which, month in (("wet", 7), ("dry", 1)):
        reference = plan["resolved_references"][which]
        assert reference["month"] == month
        assert reference["reference_location_id"] == "9"
        assert reference["run_ids"] == ["1"]
    publish_metric_set(root, plan)
    with open(
        _result(root, plan) / "q_indicators.csv", encoding="utf-8", newline=""
    ) as handle:
        results = list(csv.DictReader(handle))
    keys = [[r["metric"], r["location"], r["run_group_id"]] for r in results]
    assert sorted(keys) == plan["expected_result_keys"]
    assert len(keys) == len({tuple(key) for key in keys})
    for suffix, month in (("wettest_month_mean", 7), ("driest_month_mean", 1)):
        selected = [row for row in results if row["metric"] == f"q_{suffix}"]
        assert {(r["run_group_id"], r["location"]) for r in selected} == {
            (run, location) for run in RUN_IDS for location in ("9", "2")
        }
        for row in selected:
            daily = frames[row["run_group_id"]][f"Q_{row['location']}"]
            expected = (
                daily[daily.index.month == month].resample("YS-JAN").mean().mean()
            )
            # The retained CSV contract rounds float32 values to four digits.
            assert float(row["value"]) == float(f"{np.float32(expected):.4g}")
    # Return levels are fitted per bundle, never per run.
    fitted = {
        r["run_group_id"] for r in results if r["metric"].startswith("q_return_level")
    }
    assert fitted == {"3", "4"}
    manifest = read_canonical_json(_engine(root, plan) / "metrics.json")
    assert manifest["run_groups"] == plan["units"]
    # Every fitted return level keeps its provenance: one record per bundle and
    # metric, each location with its usable-block total and fitted parameters.
    from blueearth_cst.experiment.metric_plan import RETURN_LEVEL_EVIDENCE_FILENAME

    assert manifest["return_level_evidence"]["path"] == RETURN_LEVEL_EVIDENCE_FILENAME
    evidence = read_canonical_json(_engine(root, plan) / RETURN_LEVEL_EVIDENCE_FILENAME)
    assert evidence["schema_version"] == "return-level-evidence/1"
    assert {item["run_group_id"] for item in evidence["bundles"]} == {"3", "4"}
    for item in evidence["bundles"]:
        assert {loc["location_id"] for loc in item["locations"]} == {"9", "2"}
        for location in item["locations"]:
            assert location["total"] == 30
            assert location["total"] >= location["required"]
            assert location["parameters"], "the fitted parameters are retained"


def test_a_pre_release_v1_experiment_is_refused_by_name(tmp_path):
    """No release wrote v1 records; one is named as such, not read as missing."""
    from blueearth_cst.experiment.simulation_record import (
        MetricsOnlySimulationUnavailable,
    )

    root = tmp_path / "project/experiments/old_experiment"
    (root / "config").mkdir(parents=True)
    (root / "config/simulation.json").write_bytes(b"{}\n")
    with pytest.raises(MetricsOnlySimulationUnavailable, match="pre-release v1"):
        current_metric_request(root, ["gwr"], "YS-JAN")
    with pytest.raises(MetricsOnlySimulationUnavailable, match="pre-release v1"):
        build_metric_plan(root, {})
