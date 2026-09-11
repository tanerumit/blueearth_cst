"""Independent key planning and immutable metric sets over retained responses."""

from copy import deepcopy
from shutil import copyfile

import pytest

from blueearth_cst.experiment.content_identity import (
    canonical_json_bytes,
    content_sha256,
)
from blueearth_cst.experiment.metric_plan import (
    ImmutableMetricSetError,
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
        {"packages": {"numpy": "fixture"}},
        {"status": "provisional_operational", "benchmark": "not assessed"},
    )
    return root, request


def test_exact_result_keys_and_ready_reuse(metric_inputs):
    root, request = metric_inputs
    plan = build_metric_plan(root, request)
    assert len(plan["expected_result_keys"]) == 2
    assert plan["units"] == [
        {"unit_id": run, "grain": "run", "member_run_id": run} for run in ("01", "02")
    ]
    manifest = publish_metric_set(root, plan)
    marker = root / "results/metric_sets" / plan["metric_set_id"] / "metrics.json"
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


def test_missing_result_key_refuses_even_after_table_digest_is_updated(metric_inputs):
    root, request = metric_inputs
    plan = build_metric_plan(root, request)
    manifest = publish_metric_set(root, plan)
    destination = root / "results/metric_sets" / plan["metric_set_id"]
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
    metric_inputs, tmp_path
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
        {"packages": {"numpy": "fixture"}},
        {"status": "provisional_operational", "benchmark": "not assessed"},
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
def test_metric_marker_and_table_inventory_are_exact(metric_inputs, defect):
    from blueearth_cst.shared.provenance import file_sha256

    root, request = metric_inputs
    plan = build_metric_plan(root, request)
    manifest = publish_metric_set(root, plan)
    destination = root / "results/metric_sets" / plan["metric_set_id"]
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
                    "run_stress_test": {"enabled": True, "config_path": workflow.name}
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
