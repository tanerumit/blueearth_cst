"""Fixture proof for the additive scenario-collection/2 reader and identity."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from shutil import copy2

import pytest

from blueearth_cst.experiment.collection_resolution import (
    discover_collections_v2,
    resolve_explicit_collection_v2,
)
from blueearth_cst.experiment.content_identity import (
    atomic_record,
    automatic_seed_v2,
    collection_id_v2,
    collection_revision_v2,
    content_sha256,
    generation_seed_material_v2,
    identity_segment,
    repository_code_inventory,
)
from blueearth_cst.experiment.generation_plan import (
    GENERATOR_SEED_FIELDS,
    generator_seed_projection,
)
from blueearth_cst.experiment.scenario_collection_v2 import (
    _profile,
    read_collection_v2,
)
from blueearth_cst.shared.workflow_config_snapshot import file_reference


def _intent() -> dict:
    """Construct one complete two-member scientific intent without a producer."""
    digest = sha256(b"x").hexdigest()
    sources = [
        {"role": role, "sha256": digest, "size_bytes": 1}
        for role in ("basin_cells", "historical_climate")
    ]
    code = [{"path": "blueearth_cst/experiment/scenario_provider.py", "sha256": digest}]
    month = [0.0] * 12
    range12 = {"min": month, "max": month}
    perturbations = {
        "temp": {"n_levels": 1, "trajectory": "constant", "mean": range12},
        "precip": {
            "n_levels": 1,
            "trajectory": "constant",
            "mean": range12,
            "variance": range12,
        },
        "spell_factors": {"dry": [1.0] * 12, "wet": [1.0] * 12},
    }
    window = {"start": 2046, "end": 2054}
    generator = {
        section: {key: 1 for key in included | excluded}
        for section, (included, excluded) in GENERATOR_SEED_FIELDS.items()
    }
    generator["apply_climate_perturbations"]["diagnostic"] = False
    generator["generate_weather"]["out_dir"] = None
    for section, keys in (
        ("generate_weather", ("plot_dpi", "plot_device")),
        ("write_netcdf", ("file_suffix", "out_dir")),
    ):
        for key in keys:
            generator[section][key] = {"present": False, "value": None}
    generator_settings = generator_seed_projection(generator)
    material = generation_seed_material_v2(
        n_realizations=1,
        simulation_window=window,
        climate_perturbations=perturbations,
        water_year_start="JAN",
        provider_revision=content_sha256(code),
        sources=sources,
        generator_settings=generator_settings,
    )
    seed = automatic_seed_v2(material)
    generator["generate_weather"]["seed"] = seed
    resolution = {
        "seed_request": "auto",
        "resolved_seed": seed,
        "projection": material,
        "projection_sha256": content_sha256(material),
    }
    resolution["seed_resolution_id"] = content_sha256(resolution)
    generation = {
        "seed": {"requested": "auto", "resolved": seed},
        "seed_resolution": resolution,
        "run_group_id_capacity": 2,
        "weathergen": generator,
        "climate_perturbations": perturbations,
    }
    source_inventory = {
        "sources": [
            {
                "role": role,
                "original_path": role,
                "file": {
                    "schema_version": "artifact-reference/1",
                    "path_base": "project_root",
                    "path": f"data/{role}.dat",
                    "sha256": digest,
                    "size_bytes": 1,
                },
                "metadata": {},
            }
            for role in ("basin_cells", "historical_climate")
        ],
        "interpretation": {
            "revision": "fixture/1",
            "variables": [{"name": "temp", "units": "degC"}],
            "calendar": "standard",
            "time_label": "interval_end",
        },
    }
    documents = {
        "generation_config": generation,
        "source_inventory": source_inventory,
        "provider_code": code,
        "environment": {
            "packages": {"python": "fixture"},
            "locks": {"Manifest.toml": digest},
        },
    }
    projections = {
        "generation_config": {
            "schema_version": "generation-config-identity/2",
            "resolved_seed": seed,
            "generator_settings": material["generator_settings"],
            "climate_perturbations": perturbations,
            "simulation_window": window,
            "n_realizations": 1,
            "water_year_start": "JAN",
        },
        "source_inventory": {
            "schema_version": "generation-sources-identity/2",
            "sources": sources,
            "interpretation": source_inventory["interpretation"],
        },
    }
    intent = {
        "schema_version": "scenario-collection-intent/2",
        "canonicalization_id": "collection-canon/1",
        "collection_id": digest,
        "provider": {"name": "weathergenr", "revision": content_sha256(code)},
        "scenario_type": "stochastic",
        "scenario_spec": {
            "scenario_type": "stochastic",
            "n_realizations": 1,
            "n_design_points": 1,
            "unperturbed_per_realization": 1,
            "expected_run_count": 2,
            "simulation_window": window,
            "pairing": "paired_across_design_points",
            "row_order": "rlz-major/unperturbed-first/st-id-ascending",
        },
        "scenario_semantics_sha256": content_sha256(
            [
                {"evaluate": "true", "type": "stochastic", "rlz": "1", "st_id": ""},
                {"evaluate": "true", "type": "stochastic", "rlz": "1", "st_id": "1"},
            ]
        ),
        "run_count": 2,
        "run_group_id_capacity": 2,
        "run_group_id_width": 1,
        "documents": documents,
        "document_digests": {
            name: content_sha256(value) for name, value in documents.items()
        },
        "identity_projections": projections,
        "identity_digests": {
            name: content_sha256(projections[name] if name in projections else value)
            for name, value in documents.items()
        },
    }
    intent["collection_id"] = collection_id_v2(intent)
    return intent


def test_wf4_only_evidence_does_not_enter_seed_or_collection_identity():
    intent = _intent()
    _profile(intent)
    original_seed = intent["documents"]["generation_config"]["seed"]["resolved"]
    original_id = intent["collection_id"]
    assert intent["documents"]["generation_config"]["seed_resolution"][
        "projection_sha256"
    ] == ("4098d5a35ab1178648d6c20c1e662d84d38ef1c3bff957b6d34e04b81a1bf78a")
    assert original_seed == 1459665732
    assert (
        original_id
        == "e129e7f83e925771dc8d9cfbf1553b615a01c39f5561876c81f29f6e6f870a92"
    )
    wf4_only = {"elevation": "changed", "settings": "changed", "code": "changed"}
    wf4_only["elevation"] = "changed again"
    assert intent["collection_id"] == original_id
    assert (
        automatic_seed_v2(
            intent["documents"]["generation_config"]["seed_resolution"]["projection"]
        )
        == original_seed
    )
    changed = deepcopy(intent)
    changed["documents"]["source_inventory"]["sources"][0]["file"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="document digest"):
        _profile(changed)


def test_wf3_code_closure_ignores_wf4_only_source_bytes(tmp_path):
    root = Path(__file__).resolve().parents[1]
    entries = [
        "blueearth_cst/experiment/generation_plan.py",
        "blueearth_cst/experiment/scenario_provider.py",
        "blueearth_cst/experiment/prepare_weathergen_config.py",
        "blueearth_cst/experiment/prepare_cst_parameters.py",
        *(
            f"blueearth_cst/weathergen/{name}"
            for name in (
                "generate_weather.R",
                "impose_climate_change.R",
                "global.R",
                "read_member_grid.R",
            )
        ),
    ]
    inventory = repository_code_inventory(root, entries)
    paths = {item["path"] for item in inventory}
    forbidden = {
        "blueearth_cst/climate_analysis/prepare_climate_data_catalog.py",
        "blueearth_cst/experiment/downscale_climate_forcing.py",
        "blueearth_cst/experiment/simulation_record.py",
        "blueearth_cst/experiment/metric_groups.py",
    }
    assert not paths & forbidden
    for relative in paths | forbidden:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        copy2(root / relative, target)
    original = repository_code_inventory(tmp_path, entries)
    for relative in forbidden:
        path = tmp_path / relative
        path.write_bytes(path.read_bytes() + b"\n# WF4-only mutation\n")
    assert repository_code_inventory(tmp_path, entries) == original
    changed = tmp_path / "blueearth_cst/experiment/scenario_provider.py"
    changed.write_bytes(changed.read_bytes() + b"\n# WF3 mutation\n")
    assert repository_code_inventory(tmp_path, entries) != original


def test_collection_v2_refuses_unknown_nested_document_key():
    intent = _intent()
    intent["documents"]["generation_config"]["unclassified"] = True
    intent["document_digests"]["generation_config"] = content_sha256(
        intent["documents"]["generation_config"]
    )
    with pytest.raises(ValueError, match="generation_config"):
        _profile(intent)


def test_explicit_and_auto_requests_with_same_seed_share_collection_identity():
    intent = _intent()
    changed = deepcopy(intent)
    generation = changed["documents"]["generation_config"]
    resolved = generation["seed"]["resolved"]
    generation["seed"]["requested"] = resolved
    resolution = generation["seed_resolution"]
    resolution["seed_request"] = resolved
    resolution["seed_resolution_id"] = content_sha256(
        {key: value for key, value in resolution.items() if key != "seed_resolution_id"}
    )
    changed["document_digests"]["generation_config"] = content_sha256(generation)
    _profile(changed)
    assert changed["collection_id"] == intent["collection_id"]


def test_collection_v2_requires_marker_and_matching_data(tmp_path, monkeypatch):
    intent = _intent()
    segment = identity_segment(intent["collection_id"], "collection_id")
    record = tmp_path / "scenarios" / "_engine" / "collections" / segment
    data = tmp_path / "scenarios" / segment
    record.mkdir(parents=True)
    (data / "config").mkdir(parents=True)
    (data / "series").mkdir()
    (data / "weathergenr" / "output").mkdir(parents=True)
    for role in ("basin_cells", "historical_climate"):
        path = tmp_path / "data" / f"{role}.dat"
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(b"x")
    atomic_record(record / "collection_intent.json", intent)
    archive_path = data / "config" / "run_record.yml"
    archive_path.write_bytes(b"fixture archive")
    monkeypatch.setattr(
        "blueearth_cst.experiment.scenario_collection_v2.validate_archive",
        lambda path: {
            "owner": {"kind": "scenario_collection", "id": intent["collection_id"]},
            "workflow": "generate_scenarios",
            "generated_inputs": [products[2]],
        },
    )
    lookup = data / "scenario_run_lookup.csv"
    lookup.write_text(
        "run_id,evaluate,type,rlz,st_id\n1,true,stochastic,1,\n2,true,stochastic,1,1\n",
        encoding="utf-8",
    )
    perturbation = data / "perturbation_lookup.csv"
    perturbation.write_text(
        "st_id,month,temp_change,precip_change,precip_variance_change\n"
        + "".join(f"1,{month},0,0,0\n" for month in range(1, 13)),
        encoding="utf-8",
    )
    series = []
    for run_id in ("1", "2"):
        path = data / "series" / f"run_{run_id}.nc"
        path.write_bytes(run_id.encode())
        series.append(
            {
                "run_id": run_id,
                "file": file_reference(path, "project_root", tmp_path),
                "descriptor": {
                    "source_calendar": "standard",
                    "timestep": "daily",
                    "time_label": "interval_end",
                    "start": "2046-01-01",
                    "end": "2054-12-31",
                    "spatial_representation_sha256": sha256(b"spatial").hexdigest(),
                    "variables": [
                        {"name": "temp", "units": "degC", "missing_value": None}
                    ],
                },
            }
        )
    products = []
    for role, name in (
        ("sim_dates", "output/sim_dates.csv"),
        ("resampled_dates", "output/resampled_dates.csv"),
        ("weather_generation_input", "weather_generation_input.yml"),
    ):
        path = data / "weathergenr" / name
        path.write_bytes(role.encode())
        products.append(
            {"role": role, "file": file_reference(path, "project_root", tmp_path)}
        )
    marker = {
        "schema_version": "scenario-collection/2",
        "canonicalization_id": "collection-canon/1",
        "status": "ready",
        "collection_id": intent["collection_id"],
        "collection_revision": "0" * 64,
        "data_root": f"scenarios/{segment}",
        "intent": file_reference(
            record / "collection_intent.json", "record_directory", record
        ),
        "archive": file_reference(archive_path, "project_root", tmp_path),
        "scenario_run_lookup": file_reference(lookup, "project_root", tmp_path),
        "perturbation_lookup": file_reference(perturbation, "project_root", tmp_path),
        "series": series,
        "provider_products": products,
        "diagnostics": [],
    }
    marker["collection_revision"] = collection_revision_v2(marker, intent)
    # Readiness is never inferred from the data directory alone.
    with pytest.raises(FileNotFoundError):
        read_collection_v2(record / "collection.json")
    atomic_record(record / "collection.json", marker)
    before = (record / "collection.json").read_bytes()
    assert read_collection_v2(record / "collection.json") == marker
    assert read_collection_v2(record / "collection.json") == marker
    assert discover_collections_v2(tmp_path) == [marker]
    selection, selected = resolve_explicit_collection_v2(
        {"manifest_path": record / "collection.json"}
    )
    assert selection["collection_id"] == intent["collection_id"]
    assert selected == marker
    assert (record / "collection.json").read_bytes() == before
    (data / "series" / "run_2.nc").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="artifact reference bytes differ"):
        read_collection_v2(record / "collection.json")
    assert (record / "collection.json").read_bytes() == before
