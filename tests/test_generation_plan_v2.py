"""The WF3 planner emits a reader-checked v2 intent from pinned inputs."""

import os
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from blueearth_cst.experiment import generation_plan
from blueearth_cst.experiment.forcing_descriptor import UnitInterpretation
from blueearth_cst.experiment.scenario_collection_v2 import _profile


def test_candidate_intent_uses_wf3_only_seed_projection(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    config = yaml.safe_load(
        (root / "test_case/project_config_rapid_generate_scenarios.yml").read_text()
    )
    project = tmp_path / "project"
    store = tmp_path / "store"
    store.mkdir()
    (store / "extract_historical.nc").write_bytes(b"historical")
    (store / "basin_cells.csv").write_bytes(b"cells")
    catalog = tmp_path / "catalog.yml"
    catalog.write_bytes(b"catalog")
    monkeypatch.setattr(
        generation_plan,
        "generation_interpretation",
        lambda *_: UnitInterpretation("fixture/1", "fixture", (("temp", "degC"),)),
    )
    monkeypatch.setattr(generation_plan, "_historical_calendar", lambda _: "standard")
    monkeypatch.setattr(generation_plan, "netcdf_content_sha256", lambda _: "c" * 64)
    monkeypatch.setattr(
        generation_plan,
        "stage_environment",
        lambda *_args, **_kwargs: {
            "packages": {"python": "fixture"},
            "locks": {"Manifest.toml": "0" * 64},
        },
    )
    settings = {
        "project_dir": project,
        "store": SimpleNamespace(store_dir=str(store)),
        "template": root / "config/defaults/weathergen_config.yml",
        "catalogs": [catalog],
        "source": "era5",
        "config": config,
        "n_realizations": 2,
        "n_design_points": 4,
        "start": 2046,
        "end": 2054,
        "historical_end": 2016,
        "capacity": 15,
        "request": {"water_year_start": "JAN"},
        "code": [{"path": "provider.py", "sha256": "0" * 64}],
    }
    intent = generation_plan.build_candidate_intent(settings)
    _profile(intent)
    assert intent["documents"]["generation_config"]["seed"] == {
        "requested": 123,
        "resolved": 123,
    }
    assert len(intent["documents"]["source_inventory"]["sources"]) == 4
    assert any(
        item["metadata"].get("unit_interpretation_evidence") == "fixture"
        for item in intent["documents"]["source_inventory"]["sources"]
    )
    catalog.write_bytes(b"catalog\n# comment-only catalog edit\n")
    comment_only = generation_plan.build_candidate_intent(settings)
    assert comment_only["collection_id"] == intent["collection_id"]
    assert (
        comment_only["documents"]["source_inventory"]
        != intent["documents"]["source_inventory"]
    )
    monkeypatch.setattr(
        generation_plan,
        "generation_interpretation",
        lambda *_: UnitInterpretation(
            "fixture/1", "different evidence", (("temp", "degC"),)
        ),
    )
    changed_evidence = generation_plan.build_candidate_intent(settings)
    assert changed_evidence["collection_id"] == intent["collection_id"]
    assert (
        changed_evidence["documents"]["source_inventory"]
        != comment_only["documents"]["source_inventory"]
    )
    copy_template = tmp_path / "weathergen_config.yml"
    copy_template.write_bytes(
        settings["template"].read_bytes() + b"\n# comment-only template edit\n"
    )
    settings["template"] = copy_template
    template_comment = generation_plan.build_candidate_intent(settings)
    assert template_comment["collection_id"] == intent["collection_id"]
    settings["capacity"] = 16
    changed_capacity = generation_plan.build_candidate_intent(settings)
    assert changed_capacity["collection_id"] != intent["collection_id"]
    assert (
        changed_capacity["documents"]["generation_config"]["seed"]["resolved"]
        == intent["documents"]["generation_config"]["seed"]["resolved"]
    )
    settings["capacity"] = 15
    settings["template"] = root / "config/defaults/weathergen_config.yml"
    catalog.write_bytes(b"catalog")
    relocated = tmp_path / "relocated_store"
    relocated.mkdir()
    for name in ("extract_historical.nc", "basin_cells.csv"):
        (relocated / name).write_bytes((store / name).read_bytes())
    settings["store"] = SimpleNamespace(store_dir=str(relocated))
    relocated_intent = generation_plan.build_candidate_intent(settings)
    assert relocated_intent["collection_id"] == intent["collection_id"]
    settings["store"] = SimpleNamespace(store_dir=str(store))
    settings["config"]["seed"] = "auto"
    automatic = generation_plan.build_candidate_intent(settings)
    seed_record = automatic["documents"]["generation_config"]["seed_resolution"]
    automatic_seed = seed_record["resolved_seed"]
    assert automatic_seed == int(seed_record["projection_sha256"], 16) % (2**31 - 1)
    settings["config"]["seed"] = automatic_seed
    matching_explicit = generation_plan.build_candidate_intent(settings)
    assert matching_explicit["collection_id"] == automatic["collection_id"]
    assert (
        matching_explicit["identity_projections"] == automatic["identity_projections"]
    )
    settings["request"] = {
        "schema_version": "generation-request/2",
        "settings": {},
        "provider_code": settings["code"],
        "source": {},
        "water_year_start": "JAN",
        "template": str(settings["template"]),
    }
    request_id = generation_plan.content_sha256(settings["request"])
    request_dir = project / "scenarios/_engine/requests" / request_id[:12]
    settings["request_path"] = request_dir / "request.json"
    plan = generation_plan.build_create_plan(settings, intent)
    path, digest = generation_plan.publish_plan_pointer(settings, plan)
    assert path.name == f"{digest}.json"
    assert plan["outputs"]["temporary_members"] == [
        {
            "run_id": "01",
            "path": f"scenarios/{intent['collection_id'][:12]}/weathergenr/output/run_01.nc",
        },
        {
            "run_id": "06",
            "path": f"scenarios/{intent['collection_id'][:12]}/weathergenr/output/run_06.nc",
        },
    ]
    assert generation_plan.publish_plan_pointer(settings, plan) == (path, digest)
    assert path.read_bytes() == generation_plan.canonical_json_bytes(plan)
    assert generation_plan.read_pinned_plan(path, digest, project) == plan
    (request_dir / "request.json").write_text("{}", encoding="utf-8")
    assert generation_plan.read_pinned_plan(path, digest, project) == plan
    pinned_stat = path.stat()
    path.write_bytes(b"{}\n")
    os.utime(path, ns=(pinned_stat.st_atime_ns, pinned_stat.st_mtime_ns))
    assert path.stat().st_mtime_ns == pinned_stat.st_mtime_ns
    with pytest.raises(ValueError, match="bytes differ"):
        generation_plan.read_pinned_plan(path, digest, project)
    data_root = project / plan["outputs"]["data_root"]
    data_root.mkdir(parents=True)
    with pytest.raises(ValueError, match="partial collection namespace"):
        generation_plan.select_generation_plan(settings, intent)
