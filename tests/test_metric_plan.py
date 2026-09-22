"""Independent key planning and immutable metric sets over retained responses."""

import json
from copy import deepcopy
from shutil import copyfile

import pytest

from blueearth_cst.experiment.content_identity import (
    canonical_json_bytes,
    content_sha256,
    identity_segment,
)
from blueearth_cst.experiment.metric_plan import (
    ImmutableMetricSetError,
    MetricPlanStale,
    build_metric_plan,
    metric_request,
    publish_metric_set,
    read_metric_set,
)
from blueearth_cst.experiment.response_inventory import (
    make_response_request,
    publish_response_inventory,
)
from blueearth_cst.experiment.simulation_record import (
    freeze_simulation,
    simulation_document,
)
from blueearth_cst.experiment.wflow_response_reader import NativeRunArtifacts
from tests.test_collection_preparation import retained  # noqa: F401
from tests.test_response_inventory import frozen  # noqa: F401
from tests.test_scenario_collection import planned  # noqa: F401
from tests.test_simulation_record import inputs  # noqa: F401
from tests.test_wflow_response_reader import native  # noqa: F401

# The fixtures below plan against a synthetic stage environment. Publication and
# reduction now RE-OBSERVE the live environment and refuse a mismatch (D5), so a
# test that plans synthetically must also present that same descriptor as the
# live one -- otherwise every publish would fail as stale for the wrong reason.
FIXTURE_ENVIRONMENT = {"packages": {"numpy": "fixture"}}


def _set_dir(root, plan):
    """The metric set's directory.

    Named by the identity's first SHORT_DIGEST_CHARS since t2609152107, not
    by the whole digest. Derived HERE rather than spelled out at seven call
    sites, so this file cannot drift from `metric_plan.py` one site at a time.
    """
    segment = identity_segment(plan["metric_set_id"], "metric_set_id")
    return root / "results/metric_sets" / segment


def fixture_declaration():
    """The real shipped D4 declaration; new requests may carry nothing else."""
    from blueearth_cst.experiment import return_level_validation

    return return_level_validation.build_declaration()


@pytest.fixture
def live_fixture_environment(monkeypatch):
    """Present FIXTURE_ENVIRONMENT as the live metric-stage observation."""
    from blueearth_cst.experiment import metric_plan as plan_module

    monkeypatch.setattr(
        plan_module, "resolve_metric_environment", lambda: FIXTURE_ENVIRONMENT
    )
    return FIXTURE_ENVIRONMENT


@pytest.fixture
def metric_inputs(retained, frozen, tmp_path):  # noqa: F811 - imported fixtures
    collection_root, collection = retained
    frozen_root, native_runs, temporal = frozen
    temporal = {
        **temporal,
        "source_calendar": "proleptic_gregorian",
        "operations": ["clip_to_configured_window", "refresh_toml_endpoints"],
    }
    root = tmp_path / "metric-experiment"
    root.mkdir()
    (root / "config").mkdir()
    copyfile(
        frozen_root / "config/model_reference.yml", root / "config/model_reference.yml"
    )
    from blueearth_cst.experiment.content_identity import read_canonical_json

    model_digest = read_canonical_json(frozen_root / "config/simulation.json")["model"][
        "model_digest"
    ]
    request = make_response_request(
        ["01", "02"],
        [
            {
                "variable": "gwr",
                "locations": ["9"],
                "units": "mm dt-1",
                "calendar": "standard",
                "timestep": "P1D",
                "time_label": "interval_end",
                "start": temporal["response_start"],
                "end": temporal["response_end"],
                "missing_value": "NaN",
            }
        ],
    )
    documents = {
        "settings": {"timestepsecs": 86400},
        "response_request": request,
        "simulator_adapter_code": [{"path": "fixture.py", "sha256": "a" * 64}],
        "environment": {"packages": {"fixture": "1"}},
    }
    record = simulation_document(
        root.name,
        {
            "resolution_mode": "explicit-manifest",
            "manifest_path": str(collection_root / "collection.json"),
            "collection_id": collection["collection_id"],
            "collection_revision": collection["collection_revision"],
        },
        model_digest,
        {"name": "wflow", "revision": "e" * 64},
        documents,
    )
    freeze_simulation(root, record, documents)
    copied = {}
    for run in ("01", "02"):
        for attr, suffix in (
            ("csv_path", "csv"),
            ("toml_path", "toml"),
            ("temporal_path", "json"),
        ):
            copyfile(getattr(native_runs["01"], attr), root / f"{run}.{suffix}")
        copied[run] = NativeRunArtifacts(
            root / f"{run}.csv", root / f"{run}.toml", root / f"{run}.json"
        )
        copied[run].temporal_path.write_bytes(canonical_json_bytes(temporal))
    publish_response_inventory(root, copied, temporal)
    request = metric_request(
        record["simulation_id"],
        ["gwr"],
        "YS-JAN",
        FIXTURE_ENVIRONMENT,
        fixture_declaration(),
    )
    return root, request


def test_exact_result_keys_and_ready_reuse(metric_inputs, live_fixture_environment):
    root, request = metric_inputs
    plan = build_metric_plan(root, request)
    assert len(plan["expected_result_keys"]) == 2
    assert plan["units"] == [
        {"unit_id": run, "grain": "run", "member_run_id": run} for run in ("01", "02")
    ]
    manifest = publish_metric_set(root, plan)
    marker = _set_dir(root, plan) / "metrics.json"
    before = {
        p: (p.read_bytes(), p.stat().st_mtime_ns) for p in marker.parent.iterdir()
    }
    assert read_metric_set(root, marker) == manifest
    assert publish_metric_set(root, plan) == manifest
    assert before == {
        p: (p.read_bytes(), p.stat().st_mtime_ns) for p in marker.parent.iterdir()
    }


def test_stage3_environment_changes_only_metric_identity(metric_inputs):
    root, request = metric_inputs
    before = build_metric_plan(root, request)
    changed = deepcopy(request)
    changed["metric_environment"]["packages"]["numpy"] = "another"
    after = build_metric_plan(root, changed)
    assert after["metric_set_id"] != before["metric_set_id"]
    assert after["response_inventory_sha256"] == before["response_inventory_sha256"]
    assert after["request"]["simulation_id"] == before["request"]["simulation_id"]


def test_missing_result_key_refuses_even_after_table_digest_is_updated(
    metric_inputs, live_fixture_environment
):
    root, request = metric_inputs
    plan = build_metric_plan(root, request)
    manifest = publish_metric_set(root, plan)
    destination = _set_dir(root, plan)
    table = destination / "gwr_indicators.csv"
    lines = table.read_text().splitlines()
    table.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    from blueearth_cst.shared.provenance import file_sha256

    manifest["indicator_tables"][0]["sha256"] = file_sha256(table)
    manifest["indicator_tables"][0]["row_count"] -= 1
    manifest["metrics_manifest_sha256"] = content_sha256(
        {k: v for k, v in manifest.items() if k != "metrics_manifest_sha256"}
    )
    (destination / "metrics.json").write_bytes(canonical_json_bytes(manifest))
    with pytest.raises(ImmutableMetricSetError, match="exact expected"):
        read_metric_set(root, destination / "metrics.json")


def test_q_bundles_and_class_c_use_exact_units_and_shared_reference(
    metric_inputs, tmp_path, live_fixture_environment
):
    """Thirty full years exercise actual GEV fits and independent month means."""
    import csv

    import numpy as np
    import pandas as pd

    from blueearth_cst.experiment.content_identity import read_canonical_json

    old_root, _ = metric_inputs
    root = tmp_path / "q-metric-experiment"
    root.mkdir()
    (root / "config").mkdir()
    copyfile(
        old_root / "config/model_reference.yml", root / "config/model_reference.yml"
    )
    record = read_canonical_json(old_root / "config/simulation.json")
    documents = {
        key: read_canonical_json(old_root / "config" / record[key]["path"])
        for key in (
            "settings",
            "response_request",
            "simulator_adapter_code",
            "environment",
        )
    }
    time = pd.date_range("2046-01-01", "2075-12-31", freq="D")
    temporal = {
        "source_calendar": "proleptic_gregorian",
        "prepared_forcing_calendar": "proleptic_gregorian",
        "response_calendar": "standard",
        "operations": [
            "clip_to_configured_window",
            "refresh_toml_endpoints",
        ],
        "prepared_start": "2045-12-31 00:00:00",
        "prepared_end": str(time[-1]),
        "response_start": str(time[0]),
        "response_end": str(time[-1]),
        "time_label": "interval_end",
    }
    declaration = {
        "variable": "q",
        "locations": ["9", "2"],
        "units": "m3 s-1",
        "calendar": "standard",
        "timestep": "P1D",
        "time_label": "interval_end",
        "start": str(time[0]),
        "end": str(time[-1]),
        "missing_value": "NaN",
    }
    documents["response_request"] = make_response_request(["01", "02"], [declaration])
    record = simulation_document(
        root.name,
        record["collection"],
        record["model"]["model_digest"],
        record["simulator"],
        documents,
    )
    freeze_simulation(root, record, documents)
    rng = np.random.default_rng(12345)
    yearly = rng.uniform(0.8, 1.2, 30)[time.year - 2046]
    base = np.where(time.month == 7, 100.0, np.where(time.month == 1, 5.0, 30.0))
    native_runs, frames = {}, {}
    for run, factor in (("01", 1.0), ("02", 1.5)):
        frame = pd.DataFrame(
            {"Q_9": factor * base * yearly, "Q_2": factor * (120 - base) * yearly},
            index=time,
        )
        frame.to_csv(root / f"{run}.csv", index_label="time")
        (root / f"{run}.toml").write_text(
            '[time]\ncalendar="standard"\ntimestepsecs=86400\n'
            'starttime="2045-12-31T00:00:00"\nendtime="2075-12-31T00:00:00"\n'
            '[[output.csv.column]]\nheader="Q"\n'
            'parameter="river_water__volume_flow_rate"\n',
            encoding="utf-8",
        )
        (root / f"{run}.json").write_bytes(canonical_json_bytes(temporal))
        native_runs[run] = NativeRunArtifacts(
            root / f"{run}.csv", root / f"{run}.toml", root / f"{run}.json"
        )
        frames[run] = frame
    publish_response_inventory(root, native_runs, temporal)
    request = metric_request(
        record["simulation_id"],
        ["q"],
        "YS-JAN",
        FIXTURE_ENVIRONMENT,
        fixture_declaration(),
    )
    plan = build_metric_plan(root, request)
    assert plan["bundle_unit_ids"] == {"": "03", "1": "04"}
    assert plan["units"] == [
        {"unit_id": unit, "grain": grain, "member_run_id": run}
        for unit, grain, run in (
            ("01", "run", "01"),
            ("02", "run", "02"),
            ("03", "bundle", "01"),
            ("04", "bundle", "02"),
        )
    ]
    for which, month in (("wet", 7), ("dry", 1)):
        reference = plan["resolved_references"][which]
        assert reference["month"] == month
        assert reference["reference_location_id"] == "9"
        assert reference["run_ids"] == ["01"]
    manifest = publish_metric_set(root, plan)
    with open(plan["targets"]["q"], encoding="utf-8", newline="") as handle:
        results = list(csv.DictReader(handle))
    assert (
        sorted([row["metric"], row["location"], row["unit_id"]] for row in results)
        == plan["expected_result_keys"]
    )
    assert len(results) == len(
        {(r["metric"], r["location"], r["unit_id"]) for r in results}
    )
    for suffix, month in (("wettest_month_mean", 7), ("driest_month_mean", 1)):
        selected = [row for row in results if row["metric"] == f"q_{suffix}"]
        assert {(r["unit_id"], r["location"]) for r in selected} == {
            (run, location) for run in ("01", "02") for location in ("9", "2")
        }
        for row in selected:
            daily = frames[row["unit_id"]][f"Q_{row['location']}"]
            expected = (
                daily[daily.index.month == month].resample("YS-JAN").mean().mean()
            )
            # The retained CSV contract rounds float32 values to four significant digits.
            assert float(row["value"]) == float(f"{np.float32(expected):.4g}")
    assert manifest["resolved_references"] == plan["resolved_references"]
    assert {item["unit_id"] for item in manifest["return_level_evidence"]} == {
        "03",
        "04",
    }
    for item in manifest["return_level_evidence"]:
        assert all(location["total"] == 30 for location in item["locations"])


def test_xclim_revision_changes_only_metric_identity(metric_inputs, monkeypatch):
    from blueearth_cst.experiment import content_identity
    from blueearth_cst.experiment.metric_plan import current_metric_request

    root, _ = metric_inputs
    revision = "first"

    def environment(roots):
        return {
            "packages": {
                name: revision if name == "xclim" else "fixed" for name in roots
            }
        }

    monkeypatch.setattr(content_identity, "stage_environment", environment)
    before = build_metric_plan(root, current_metric_request(root, ["gwr"], "YS-JAN"))
    revision = "second"
    after = build_metric_plan(root, current_metric_request(root, ["gwr"], "YS-JAN"))
    assert before["metric_set_id"] != after["metric_set_id"]
    assert before["request"]["simulation_id"] == after["request"]["simulation_id"]
    assert before["response_inventory_sha256"] == after["response_inventory_sha256"]


@pytest.mark.parametrize(
    "defect", ["renamed-marker", "extra-empty-table", "renamed-table"]
)
def test_metric_marker_and_table_inventory_are_exact(
    metric_inputs, defect, live_fixture_environment
):
    from blueearth_cst.shared.provenance import file_sha256

    root, request = metric_inputs
    plan = build_metric_plan(root, request)
    manifest = publish_metric_set(root, plan)
    destination = _set_dir(root, plan)
    marker = destination / "metrics.json"
    if defect == "renamed-marker":
        marker = destination / "alternate.json"
    elif defect == "extra-empty-table":
        extra = destination / "unknown_indicators.csv"
        extra.write_bytes(b"metric,location,unit_id,value\n")
        manifest["indicator_tables"].append(
            {
                "token": "unknown",
                "path": extra.name,
                "sha256": file_sha256(extra),
                "row_count": 0,
            }
        )
    else:
        alternate = destination / "alternate.csv"
        copyfile(destination / "gwr_indicators.csv", alternate)
        manifest["indicator_tables"][0]["path"] = alternate.name
    manifest["metrics_manifest_sha256"] = content_sha256(
        {
            key: value
            for key, value in manifest.items()
            if key != "metrics_manifest_sha256"
        }
    )
    marker.write_bytes(canonical_json_bytes(manifest))
    with pytest.raises(ImmutableMetricSetError, match="marker|table inventory"):
        read_metric_set(root, marker)


@pytest.mark.parametrize("mismatch", [False, True])
def test_metrics_only_project_anchor_and_collection_assertion(
    metric_inputs, tmp_path, monkeypatch, capsys, mismatch
):
    from pathlib import Path
    from shutil import copytree

    import yaml

    from blueearth_cst.experiment import metric_plan
    from blueearth_cst.experiment.content_identity import read_canonical_json

    root, _ = metric_inputs
    record = read_canonical_json(root / "config/simulation.json")
    selector = {"manifest_path": record["collection"]["manifest_path"]}
    original_manifest = Path(selector["manifest_path"])
    relocated = tmp_path / "relocated" / original_manifest.parent.name
    copytree(original_manifest.parent, relocated)
    selector["manifest_path"] = str(relocated / "collection.json")
    if mismatch:
        record["collection"]["collection_revision"] = "0" * 64
    monkeypatch.setattr(metric_plan, "read_simulation", lambda *args, **kwargs: record)
    workflow = tmp_path / "metrics-only.yml"
    workflow.write_text(
        yaml.safe_dump(
            {
                "experiment_name": "retained",
                "metrics": ["gwr"],
                "scenario_collection": selector,
                "seed": 123,
                "simulation_window": {"start": 9990, "end": 9999},
            }
        ),
        encoding="utf-8",
    )
    config = tmp_path / "metrics-project.yml"
    config.write_text(
        yaml.safe_dump(
            {
                "project": {
                    "project_dir": str(tmp_path / "no-live-inputs"),
                    "catalog": "missing.yml",
                },
                "climate": {"water_year_start": "oct"},
                "model": {"name": "unavailable-model"},
                "workflows": {
                    "simulate_system": {"enabled": True, "config_path": workflow.name}
                },
            }
        ),
        encoding="utf-8",
    )
    if mismatch:
        with pytest.raises(ValueError, match="collection_revision"):
            metric_plan.metrics_only_configuration(config)
    else:
        _, tokens, anchor = metric_plan.metrics_only_configuration(config)
        assert tokens == ["gwr"]
        assert anchor == "YS-OCT"
        output = capsys.readouterr().out
        assert "seed" in output and "simulation_window" in output
        assert "model.name" in output and "config/simulation.json" in output


def test_stale_live_environment_refuses_reduction_before_any_fit(
    metric_inputs, monkeypatch
):
    """D5: drift between planning and execution aborts before fitting."""
    from blueearth_cst.experiment import metric_plan as plan_module

    root, request = metric_inputs
    monkeypatch.setattr(
        plan_module, "resolve_metric_environment", lambda: FIXTURE_ENVIRONMENT
    )
    plan = build_metric_plan(root, request)

    calls = []
    monkeypatch.setattr(
        plan_module,
        "resolve_metric_environment",
        lambda: {"packages": {"numpy": "moved"}},
    )
    from blueearth_cst.experiment import gev_lmoments

    real = gev_lmoments.fit_case
    monkeypatch.setattr(
        gev_lmoments,
        "fit_case",
        lambda *a, **k: (calls.append(a), real(*a, **k))[1],
    )
    with pytest.raises(MetricPlanStale, match="live metric-stage environment"):
        plan_module.reduce_metric_plan(root, plan)
    assert calls == [], "the estimator ran despite a stale environment"


def test_stale_live_environment_leaves_no_ready_marker(metric_inputs, monkeypatch):
    """A drifted environment must not produce a published set."""
    from blueearth_cst.experiment import metric_plan as plan_module

    root, request = metric_inputs
    monkeypatch.setattr(
        plan_module, "resolve_metric_environment", lambda: FIXTURE_ENVIRONMENT
    )
    plan = build_metric_plan(root, request)
    monkeypatch.setattr(
        plan_module,
        "resolve_metric_environment",
        lambda: {"packages": {"numpy": "moved"}},
    )
    with pytest.raises(MetricPlanStale):
        publish_metric_set(root, plan)
    destination = _set_dir(root, plan)
    assert not (destination / "metrics.json").exists()


def test_late_environment_drift_leaves_an_unready_destination(
    metric_inputs, monkeypatch
):
    """Switching the observation only at the final pre-marker check (D5)."""
    from blueearth_cst.experiment import metric_plan as plan_module

    root, request = metric_inputs
    observations = []

    def drifting():
        observations.append(len(observations))
        # Stale only on the LAST check, after payloads are already flushed.
        return (
            FIXTURE_ENVIRONMENT
            if len(observations) < 3
            else {"packages": {"numpy": "moved"}}
        )

    monkeypatch.setattr(
        plan_module, "resolve_metric_environment", lambda: FIXTURE_ENVIRONMENT
    )
    plan = build_metric_plan(root, request)
    monkeypatch.setattr(plan_module, "resolve_metric_environment", drifting)
    with pytest.raises(MetricPlanStale):
        publish_metric_set(root, plan)
    destination = _set_dir(root, plan)
    assert not (destination / "metrics.json").exists()
    assert destination.exists() and any(destination.iterdir()), (
        "payloads were flushed, so the destination should be partial, not absent"
    )


def test_new_requests_refuse_the_legacy_validation_record(metric_inputs):
    """D6: legacy acceptance is read compatibility, not a write escape hatch."""
    root, request = metric_inputs
    with pytest.raises(ValueError, match="readable, not writable"):
        metric_request(
            request["simulation_id"],
            ["gwr"],
            "YS-JAN",
            FIXTURE_ENVIRONMENT,
            {"status": "provisional_operational", "benchmark": "not assessed"},
        )


def test_new_requests_refuse_an_unsupported_declaration(metric_inputs):
    from blueearth_cst.experiment import return_level_validation

    root, request = metric_inputs
    altered = dict(fixture_declaration(), screening_policy_validated=True)
    with pytest.raises(return_level_validation.ReturnLevelValidationError):
        metric_request(
            request["simulation_id"], ["gwr"], "YS-JAN", FIXTURE_ENVIRONMENT, altered
        )


def test_published_set_carries_and_verifies_its_benchmark_report(
    metric_inputs, live_fixture_environment
):
    """D5: the checked report bytes travel with the set and gate the reader."""
    from blueearth_cst.experiment import return_level_validation

    root, request = metric_inputs
    plan = build_metric_plan(root, request)
    manifest = publish_metric_set(root, plan)
    destination = _set_dir(root, plan)
    report = destination / return_level_validation.REPORT_FILENAME
    assert report.is_file()
    assert report.read_bytes() == return_level_validation.load_report_bytes()
    assert manifest["return_level_benchmark"]["path"] == report.name
    assert (
        manifest["return_level_validation"]["benchmark_record"]["sha256"]
        == manifest["return_level_benchmark"]["sha256"]
    )
    marker = destination / "metrics.json"
    assert read_metric_set(root, marker) == manifest

    # A tampered copy must fail the reader rather than downgrade silently.
    report.write_bytes(b"{}\n")
    with pytest.raises(ImmutableMetricSetError):
        read_metric_set(root, marker)


def test_reader_accepts_a_legacy_set_without_the_report(
    metric_inputs, live_fixture_environment, monkeypatch
):
    """D6: a retained pre-C set stays readable, and needs no benchmark."""
    from blueearth_cst.experiment import metric_plan as plan_module
    from blueearth_cst.experiment import return_level_validation

    root, request = metric_inputs
    plan = build_metric_plan(root, request)
    publish_metric_set(root, plan)
    destination = _set_dir(root, plan)
    marker = destination / "metrics.json"

    # Rewrite the published set as a legacy one: legacy validation, no report.
    manifest = json.loads(marker.read_text(encoding="utf-8"))
    manifest["return_level_validation"] = dict(
        return_level_validation.LEGACY_VALIDATION
    )
    manifest["metric_definition"]["return_level_validation"] = dict(
        return_level_validation.LEGACY_VALIDATION
    )
    del manifest["return_level_benchmark"]
    (destination / return_level_validation.REPORT_FILENAME).unlink()
    legacy = plan_module._validated_benchmark(
        destination.resolve(), manifest, manifest["return_level_validation"]
    )
    assert legacy is None, "a legacy set must resolve to no benchmark reference"


def test_reader_refuses_an_unknown_validation_shape(metric_inputs):
    from blueearth_cst.experiment import metric_plan as plan_module

    root, _ = metric_inputs
    with pytest.raises(ImmutableMetricSetError, match="unknown return-level"):
        plan_module._validated_benchmark(root, {}, {"schema_version": "other/9"})
    with pytest.raises(ImmutableMetricSetError, match="unknown return-level"):
        plan_module._validated_benchmark(root, {}, {"status": "something"})


def test_legacy_set_must_not_carry_a_benchmark_report(metric_inputs):
    from blueearth_cst.experiment import metric_plan as plan_module
    from blueearth_cst.experiment import return_level_validation

    root, _ = metric_inputs
    with pytest.raises(ImmutableMetricSetError, match="must not carry"):
        plan_module._validated_benchmark(
            root,
            {"return_level_benchmark": {"path": "x", "sha256": "y"}},
            dict(return_level_validation.LEGACY_VALIDATION),
        )


def test_metric_environment_records_the_estimator_source():
    """D5: the resolver binds D7's verified source hashes, not just versions."""
    from blueearth_cst.experiment import gev_lmoments
    from blueearth_cst.experiment.metric_plan import resolve_metric_environment

    observed = resolve_metric_environment()
    estimator = observed["return_level_estimator"]
    assert estimator["estimator_id"] == "gf15-lmoments-c/1"
    assert estimator["version"] == gev_lmoments.DEPENDENCY_VERSION
    assert estimator["source_sha256"] == gev_lmoments.SOURCE_SHA256
    assert "lmoments3" in observed["packages"] or any(
        "lmoments3" in key for key in observed["packages"]
    )


def test_metric_set_v2_publishes_paired_paths_and_headers(tmp_path, monkeypatch):
    """The v2 marker and user-facing tables use one short-ID identity."""
    import csv
    from dataclasses import asdict

    from blueearth_cst.experiment import metric_plan
    from blueearth_cst.experiment.metric_registry import declarations

    declaration = asdict(declarations(("gwr",))[0])
    environment = {"packages": {"fixture": "1"}}
    simulation = {"schema_version": "simulation/2", "simulation_id": "a" * 64}
    inventory = {
        "response_inventory_sha256": "b" * 64,
        "response_identity_sha256": "c" * 64,
    }
    projection = {
        "simulation_id": simulation["simulation_id"],
        "response_identity_sha256": inventory["response_identity_sha256"],
        "metric_definition_sha256": "d" * 64,
        "metric_environment_sha256": content_sha256(environment),
    }
    plan = {
        "schema_version": "metric-request/2",
        "metric_set_id": content_sha256(projection),
        "request": {
            "declarations": [declaration],
            "metric_environment": environment,
            "return_level_validation": {"schema_version": "fixture/1"},
        },
        "identity_projection": projection,
        "metric_definition_sha256": projection["metric_definition_sha256"],
        "metric_environment_sha256": projection["metric_environment_sha256"],
        "response_inventory_sha256": inventory["response_inventory_sha256"],
        "groups": {},
        "units": [{"run_group_id": "01", "grain": "run", "run_id": "01"}],
        "expected_result_keys": [[declaration["name"], "9", "01"]],
    }
    monkeypatch.setattr(metric_plan, "check_live_metric_environment", lambda _: None)
    monkeypatch.setattr(metric_plan, "read_simulation_v2", lambda _: simulation)
    monkeypatch.setattr(metric_plan, "read_response_inventory_v2", lambda _: inventory)
    monkeypatch.setattr(
        metric_plan,
        "reduce_metric_plan",
        lambda *_: (
            {
                "gwr": [
                    {
                        "metric": declaration["name"],
                        "location": "9",
                        "run_group_id": "01",
                        "value": "1",
                    }
                ]
            },
            (),
        ),
    )
    monkeypatch.setattr(
        metric_plan.return_level_validation,
        "load_report_bytes",
        lambda: b"fixture benchmark",
    )
    monkeypatch.setattr(
        metric_plan.return_level_validation,
        "verify_declaration",
        lambda *_: None,
    )
    marker = metric_plan._publish_metric_set_v2(tmp_path, plan)
    short = identity_segment(plan["metric_set_id"], "metric_set_id")
    engine = tmp_path / "_engine/metric_sets" / short
    result = tmp_path / "results/metric_sets" / short
    assert marker["schema_version"] == "metric-set/2"
    assert engine.joinpath("metrics.json").is_file()
    assert result.joinpath("metric_run_lookup.csv").is_file()
    with result.joinpath("metric_run_lookup.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        assert csv.DictReader(handle).fieldnames == ["run_group_id", "grain", "run_id"]
    with result.joinpath("gwr_indicators.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        assert csv.DictReader(handle).fieldnames == [
            "metric",
            "location",
            "run_group_id",
            "value",
        ]
    assert metric_plan.read_metric_set(tmp_path, engine / "metrics.json") == marker


def test_v2_metric_plan_reads_collection_from_intent(tmp_path, monkeypatch):
    from blueearth_cst.experiment import metric_plan

    root = tmp_path / "experiment"
    (root / "_engine").mkdir(parents=True)
    (root / "_engine/simulation.json").write_bytes(b"{}\n")
    request = {
        "schema_version": "metric-request/2",
        "simulation_schema_version": "simulation/2",
        "simulation_id": "a" * 64,
        "tokens": ["gwr"],
        "water_year_anchor": "YS-JAN",
        "metric_environment": {},
        "return_level_validation": {},
    }
    collection = {
        "collection_id": "b" * 64,
        "collection_revision": "c" * 64,
        "manifest": {"path": "scenarios/_engine/collections/b/collection.json"},
    }
    monkeypatch.setattr(
        metric_plan,
        "read_simulation_v2",
        lambda path: {"schema_version": "simulation/2", "simulation_id": "a" * 64},
    )
    monkeypatch.setattr(
        metric_plan,
        "read_simulation_intent_v2",
        lambda path: {"collection": collection},
    )
    monkeypatch.setattr(metric_plan, "metric_request", lambda *args: dict(request))
    monkeypatch.setattr(metric_plan, "read_response_inventory_v2", lambda path: {})
    seen = {}

    def stop_after_collection(simulation):
        seen.update(simulation)
        raise RuntimeError("stop after collection selection")

    monkeypatch.setattr(metric_plan, "_collection", stop_after_collection)

    with pytest.raises(RuntimeError, match="stop after collection"):
        metric_plan.build_metric_plan(root, request)

    assert seen["collection"] == collection


def test_v2_scenario_lookup_preserves_member_ancestry():
    from blueearth_cst.experiment.metric_plan import _v2_scenario_rows

    rows = _v2_scenario_rows(
        [
            {
                "run_id": "01",
                "evaluate": "true",
                "type": "stochastic",
                "rlz": "1",
                "st_id": "",
            },
            {
                "run_id": "02",
                "evaluate": "true",
                "type": "stochastic",
                "rlz": "1",
                "st_id": "1",
            },
        ]
    )

    assert [(row.run_id, row.derived_from, dict(row.payload)) for row in rows] == [
        ("01", "", {"rlz": "1", "st_id": ""}),
        ("02", "01", {"rlz": "1", "st_id": "1"}),
    ]


def test_v2_native_run_references_resolve_from_inventory(tmp_path):
    from blueearth_cst.experiment.metric_plan import _native_runs_v2
    from blueearth_cst.shared.workflow_config_snapshot import file_reference

    csv_path = tmp_path / "output.csv"
    toml_path = tmp_path / "run.toml"
    csv_path.write_text("time,Q_1\n2046-01-02,1\n", encoding="utf-8")
    toml_path.write_text("[time]\n", encoding="utf-8")
    inventory = {
        "artifacts": [
            {
                "run_id": "01",
                "file": file_reference(csv_path, "experiment_root", tmp_path),
            }
        ],
        "series": [
            {
                "run_id": "01",
                "native_selector": {
                    "toml": file_reference(toml_path, "experiment_root", tmp_path)
                },
            }
        ],
    }

    native_runs = _native_runs_v2(tmp_path, inventory)

    assert native_runs["01"].csv_path == csv_path
    assert native_runs["01"].toml_path == toml_path
    assert native_runs["01"].temporal_path is None


def test_v2_run_groups_replace_legacy_unit_keys():
    from blueearth_cst.experiment.metric_plan import _v2_run_groups

    assert _v2_run_groups(
        [{"unit_id": "01", "grain": "run", "member_run_id": "01"}]
    ) == [{"run_group_id": "01", "grain": "run", "run_id": "01"}]
