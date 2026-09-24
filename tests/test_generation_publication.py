"""Reject self-consistent but scientifically wrong WF3 provider arguments."""

import hashlib

import pytest

from blueearth_cst.experiment import generation_publication as publication
from blueearth_cst.experiment.content_identity import atomic_record
from blueearth_cst.experiment.generation_plan import generator_seed_projection
from blueearth_cst.shared.workflow_config_snapshot import file_reference


@pytest.mark.parametrize(
    "text",
    [
        b"a: 1\na: 2\n",
        b"a: &x 1\nb: *x\n",
        b"a: !!int 1\n",
        b"a: .nan\n",
        b"a: yes\n",
    ],
)
def test_installed_generator_rejects_ambiguous_yaml(text):
    with pytest.raises(ValueError):
        publication._decode_generator(text)


@pytest.mark.parametrize("compression", [None, 0, 10, True, "4"])
def test_unsupported_compression_refuses_before_provider(compression):
    with pytest.raises(ValueError, match="unsupported provider compression"):
        publication._validate_supported_execution_choices(
            {
                "write_netcdf": {"compression": compression},
                "run_weather_generator": {"eval_max_grids": 2},
                "generate_weather": {"save_plots": False},
            }
        )


@pytest.mark.parametrize("compression", [1, 9])
def test_supported_compression_values(compression):
    publication._validate_supported_execution_choices(
        {
            "write_netcdf": {"compression": compression},
            "run_weather_generator": {"eval_max_grids": 2},
            "generate_weather": {"save_plots": False},
        }
    )


def test_single_evaluation_grid_is_refused_only_with_plotting():
    data = {
        "write_netcdf": {"compression": 4},
        "run_weather_generator": {"eval_max_grids": 1},
        "generate_weather": {"save_plots": False},
    }
    publication._validate_supported_execution_choices(data)
    data["generate_weather"]["save_plots"] = True
    with pytest.raises(ValueError, match="at least two"):
        publication._validate_supported_execution_choices(data)


def test_provider_binding_rejects_wrong_seed_rows_and_member_mapping(
    tmp_path, monkeypatch
):
    root = tmp_path
    data_root = root / "scenarios/collection"
    output_dir = data_root / "weathergenr/output"
    output_dir.mkdir(parents=True)
    series_dir = data_root / "series"
    historical = root / "historical.nc"
    cells = root / "cells.csv"
    generator_yaml = data_root / "weathergenr/weather_generation_input.yml"
    lookup = data_root / "perturbation_lookup.csv"
    for path, content in (
        (historical, b"climate"),
        (cells, b"cells"),
        (generator_yaml, b"generator"),
        (lookup, b"lookup"),
        (series_dir / "run_01.nc", b"root"),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    generator = {
        "run_weather_generator": {},
        "generate_weather": {"seed": 123, "n_realizations": 1},
        "apply_climate_perturbations": {"diagnostic": False},
        "write_netcdf": {},
        "temp": {},
        "precip": {},
    }
    rows = [
        {
            "st_id": "1",
            "month": 1,
            "temp_change": 0.0,
            "precip_change": 0.0,
            "precip_variance_change": 0.0,
        }
    ]
    sources = [
        {
            "role": role,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "size_bytes": path.stat().st_size,
        }
        for role, path in (("basin_cells", cells), ("historical_climate", historical))
    ]
    plan = {
        "intent": {
            "identity_projections": {
                "generation_config": {
                    "schema_version": "generation-config-identity/2",
                    "resolved_seed": 123,
                    "generator_settings": generator_seed_projection(generator),
                },
                "source_inventory": {"sources": sources},
            },
            "scenario_semantics_sha256": "0" * 64,
        },
        "rows": [
            {"run_id": "01", "rlz": "1", "st_id": None},
            {"run_id": "02", "rlz": "1", "st_id": "1"},
        ],
        "outputs": {
            "data_root": "scenarios/collection",
            "series": [
                {
                    "run_id": run_id,
                    "path": f"scenarios/collection/series/run_{run_id}.nc",
                }
                for run_id in ("01", "02")
            ],
        },
    }
    monkeypatch.setattr(
        publication,
        "_source_paths",
        lambda *_: {"historical_climate": historical, "basin_cells": cells},
    )
    monkeypatch.setattr(
        publication,
        "_paths",
        lambda *_: {"generator_input": generator_yaml, "perturbation_lookup": lookup},
    )
    monkeypatch.setattr(
        publication, "validate_installed_generator", lambda *_: generator
    )
    monkeypatch.setattr(publication, "_perturbation_rows", lambda *_: rows)
    observed_rows = list(rows)
    monkeypatch.setattr(
        publication, "_observed_perturbation_rows", lambda *_: observed_rows
    )
    arguments = dict(
        historical=historical,
        cells=cells,
        generator_yaml=generator_yaml,
        lookup=lookup,
        root_run_ids=["01"],
        output_dir=output_dir,
    )
    assert (
        publication.validate_provider_inputs(plan, root, **arguments)["schema_version"]
        == "provider-input-identity/1"
    )
    with pytest.raises(ValueError, match="pinned snapshot"):
        publication.validate_provider_inputs(
            plan, root, **{**arguments, "historical": cells}
        )
    with pytest.raises(ValueError, match="root argument"):
        publication.validate_provider_inputs(
            plan, root, **{**arguments, "root_run_ids": ["02"]}
        )
    with pytest.raises(ValueError, match="root argument"):
        publication.validate_provider_inputs(
            plan, root, **{**arguments, "output_dir": root}
        )
    observed_rows[0] = {**rows[0], "precip_change": 1.0}
    with pytest.raises(ValueError, match="monthly perturbation"):
        publication.validate_provider_inputs(plan, root, **arguments)
    observed_rows[:] = rows
    generator["generate_weather"]["seed"] = 124
    with pytest.raises(ValueError, match="resolved seed"):
        publication.validate_provider_inputs(plan, root, **arguments)
    generator["generate_weather"]["seed"] = 123
    generator["generate_weather"]["n_realizations"] = 2
    with pytest.raises(ValueError, match="input identity"):
        publication.validate_provider_inputs(plan, root, **arguments)
    generator["generate_weather"]["n_realizations"] = 1
    derived = {
        **arguments,
        "root_run_ids": None,
        "output_dir": None,
        "ancestor": series_dir / "run_01.nc",
        "row_id": "02",
        "output": series_dir / "run_02.nc",
    }
    publication.validate_provider_inputs(plan, root, **derived)
    with pytest.raises(ValueError, match="member mapping"):
        publication.validate_provider_inputs(
            plan, root, **{**derived, "output": series_dir / "run_03.nc"}
        )
    # A perturbed member is written once, to its retained series path; the
    # generator's own output directory is no longer an accepted target.
    with pytest.raises(ValueError, match="member mapping"):
        publication.validate_provider_inputs(
            plan, root, **{**derived, "output": output_dir / "run_02.nc"}
        )


@pytest.mark.parametrize(
    "field,bad",
    [
        ("generation_request_id", "wrong"),
        ("candidate_intent_sha256", "wrong"),
        ("decision", "reuse_ready"),
        ("collection_revision", "wrong"),
        ("workspace_path", "elsewhere"),
        ("claim_token", "not-a-valid-claim"),
    ],
)
def test_publication_rejects_forged_receipt_before_marker(
    tmp_path, monkeypatch, field, bad
):
    root = tmp_path
    archive_path = root / "scenarios/collection/config/run_record.yml"
    archive_path.parent.mkdir(parents=True)
    archive_path.write_bytes(b"archive")
    plan = {
        "outputs": {
            "archive_root": "scenarios/collection/config",
            "record_root": "scenarios/_engine/collections/collection",
            "data_root": "scenarios/collection",
        },
        "generation_request_id": "request",
        "collection_id": "collection",
        "intent_sha256": "intent",
        "candidate_intent_sha256": "candidate",
        "decision": "create",
        "collection_revision": None,
    }
    plan_path = root / "scenarios/_engine/requests/request/plan.json"
    receipt_path = plan_path.parent / "initializations/invocation.json"
    receipt = {
        "schema_version": "generation-initialization/2",
        "invocation_id": "invocation",
        "generation_request_id": "request",
        "plan_sha256": "digest",
        "collection_id": "collection",
        "intent_sha256": "intent",
        "candidate_intent_sha256": "candidate",
        "creator_archive": file_reference(archive_path, "project_root", root),
        "decision": "create",
        "collection_revision": None,
        "workspace_path": "scenarios/collection/weathergenr",
        "claim_token": "0" * 32,
    }
    receipt[field] = bad
    receipt_path.parent.mkdir(parents=True)
    atomic_record(receipt_path, receipt)
    monkeypatch.setattr(publication, "read_pinned_plan", lambda *_: plan)
    monkeypatch.setattr(
        publication,
        "_paths",
        lambda *_: {
            "data_root": root / plan["outputs"]["data_root"],
            "record_root": root / plan["outputs"]["record_root"],
        },
    )
    with pytest.raises(ValueError, match="receipt differs"):
        publication.publish_generation(root, plan_path, "digest", "invocation")
    assert not (root / plan["outputs"]["record_root"] / "collection.json").exists()


def test_initialization_refuses_partial_namespace(tmp_path, monkeypatch):
    root = tmp_path
    plan = {
        "decision": "create",
        "outputs": {
            "data_root": "scenarios/collection",
            "record_root": "scenarios/_engine/collections/collection",
        },
    }
    data_root = root / plan["outputs"]["data_root"]
    data_root.mkdir(parents=True)
    monkeypatch.setattr(publication, "read_pinned_plan", lambda *_: plan)
    monkeypatch.setattr(
        publication,
        "_paths",
        lambda *_: {
            "data_root": data_root,
            "record_root": root / plan["outputs"]["record_root"],
        },
    )
    with pytest.raises(ValueError, match="namespace appeared"):
        publication.initialize_generation(
            root,
            root / "plan.json",
            "digest",
            config_path=root / "config.yml",
            loaded_config={},
            invocation_id="invocation",
            lookup_path=root / "lookup.csv",
            command=[],
        )


def test_competing_initialization_cannot_replace_receipt(tmp_path, monkeypatch):
    root = tmp_path
    plan_path = root / "requests/request/plan.json"
    receipt = plan_path.parent / "initializations/invocation.json"
    receipt.parent.mkdir(parents=True)
    receipt.write_bytes(b"first owner")
    monkeypatch.setattr(publication, "read_pinned_plan", lambda *_: {})
    monkeypatch.setattr(publication, "_paths", lambda *_: {})
    with pytest.raises(ValueError, match="receipt already exists"):
        publication.initialize_generation(
            root,
            plan_path,
            "digest",
            config_path=root / "config.yml",
            loaded_config={},
            invocation_id="invocation",
            lookup_path=root / "lookup.csv",
            command=[],
        )
    assert receipt.read_bytes() == b"first owner"
