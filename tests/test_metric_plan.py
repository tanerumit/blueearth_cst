"""Metric requests and the v2 metric-plan seams, tested without an experiment.

Planning, reduction, publication and reading over a real retained experiment
live in `test_metric_plan_v2.py`; this module keeps the request-level rules and
the unit seams that need no experiment at all.
"""

import pytest

from blueearth_cst.experiment.content_identity import content_sha256, identity_segment
from blueearth_cst.experiment.metric_plan import metric_request
from tests._v2_experiment import FIXTURE_ENVIRONMENT

SIMULATION_ID = "a" * 64


def fixture_declaration():
    """The real shipped D4 declaration; new requests may carry nothing else."""
    from blueearth_cst.experiment import return_level_validation

    return return_level_validation.build_declaration()


def test_new_requests_refuse_the_legacy_validation_record():
    """D6: legacy acceptance is read compatibility, not a write escape hatch."""
    with pytest.raises(ValueError, match="readable, not writable"):
        metric_request(
            SIMULATION_ID,
            ["gwr"],
            "YS-JAN",
            FIXTURE_ENVIRONMENT,
            {"status": "provisional_operational", "benchmark": "not assessed"},
        )


def test_new_requests_refuse_an_unsupported_declaration():
    from blueearth_cst.experiment import return_level_validation

    altered = dict(fixture_declaration(), screening_policy_validated=True)
    with pytest.raises(return_level_validation.ReturnLevelValidationError):
        metric_request(SIMULATION_ID, ["gwr"], "YS-JAN", FIXTURE_ENVIRONMENT, altered)


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
    assert marker["metric_run_lookup"]["path"] == (
        f"results/metric_sets/{short}/metric_run_lookup.csv"
    )
    assert [item["file"]["path"] for item in marker["tables"]] == [
        f"results/metric_sets/{short}/gwr_indicators.csv"
    ]
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
