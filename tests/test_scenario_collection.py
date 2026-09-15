"""Synthetic adapter-backed publication, portable reading and immutable reuse."""

import csv
import hashlib
import io
import json
from copy import deepcopy
from pathlib import Path

import pytest

from blueearth_cst.experiment.content_identity import (
    canonical_json_bytes,
    collection_id,
    collection_revision,
    content_sha256,
    scenario_semantics_sha256,
)
from blueearth_cst.experiment.scenario_collection import (
    ImmutableCollectionError,
    ScenarioCollectionNotReady,
    claim_collection,
    collection_size,
    delete_collection,
    list_collections,
    publish_collection,
    read_collection,
    reuse_collection,
    write_collection_payload,
)
from blueearth_cst.experiment.scenario_rows import stochastic_rows


def _reference(path, payload):
    return {"path": path, "sha256": hashlib.sha256(payload).hexdigest()}


def _describe_ancillary(path):
    """Extract a tiny synthetic grid descriptor, without expected metadata."""
    data = json.loads(path.read_bytes())
    return {"grid_sha256": content_sha256(data["grid"]), "units": data["units"]}


def _describe_forcing(path, reader):
    """Fixture-only reader: observations come from bytes, units from context."""
    data = json.loads(path.read_bytes())
    return {
        "source_calendar": data["calendar"],
        "timestep": "P1D",
        "time_label": "interval_end",
        "start": data["start"],
        "end": data["end"],
        "spatial_representation_sha256": content_sha256(data["grid"]),
        "variables": [
            {
                "name": "temp",
                "units": reader["metadata"]["units"],
                "missing_value": None,
            }
        ],
    }


CHECKS = {
    "describe_forcing": _describe_forcing,
    "describe_ancillary": _describe_ancillary,
}


@pytest.fixture
def planned(tmp_path):
    """A complete stochastic table; physical payloads are explicit test doubles."""
    rows = stochastic_rows(1, 1, unit_id_capacity=10)
    table = io.StringIO(newline="")
    writer = csv.DictWriter(
        table, fieldnames=list(rows[0].as_record()), lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(row.as_record() for row in rows)
    lookup = "st_id,month,temp_change,precip_change,precip_variance_change\n"
    lookup += "".join(f"1,{month},0,0,0\n" for month in range(1, 13))
    live_source = tmp_path / "original.nc"
    live_source.write_bytes(b"original source bytes")
    live_code = tmp_path / "provider.py"
    live_code.write_bytes(b"immutable provider")
    ancillary = canonical_json_bytes({"grid": [0, 1], "units": "m"})
    ancillary_path = tmp_path / "ancillary.nc"
    ancillary_path.write_bytes(ancillary)
    catalog = b"elevation:\n  data_type: RasterDataset\n  uri: ancillary/elevation/grid.nc\n  driver:\n    name: raster_xarray\n    options:\n      preprocess: harmonise_dims\n  metadata:\n    crs: 4326\n"
    context = {
        "schema_version": "forcing-preparation/1",
        "generated_forcing_reader": {
            "data_type": "RasterDataset",
            "driver": {"name": "raster_xarray"},
            "metadata": {"crs": 4326, "units": "degC"},
        },
        "pet_method": "debruin",
        "forcing_elevation": {"catalog_key": "elevation", "artifact_id": "elevation"},
        "catalog": _reference("preparation_catalog.yml", catalog),
        "ancillary": [
            {
                "id": "elevation",
                "role": "forcing_elevation",
                **_reference("ancillary/elevation/grid.nc", ancillary),
                "size_bytes": len(ancillary),
                "descriptor": _describe_ancillary(ancillary_path),
            }
        ],
    }
    documents = {
        "generation_config": {
            "seed": {"requested": 42, "resolved": 42},
            "unit_id_capacity": 10,
        },
        "source_inventory": [
            {
                "role": "historical_climate",
                "path": "original.nc",
                "size_bytes": live_source.stat().st_size,
                "sha256": hashlib.sha256(live_source.read_bytes()).hexdigest(),
                "metadata": {"source": "fixture"},
            }
        ],
        "provider_code": [
            {
                "path": "provider.py",
                "sha256": hashlib.sha256(live_code.read_bytes()).hexdigest(),
            }
        ],
        "environment": {
            "packages": {"fixture": "1.0"},
            "locks": {"fixture.lock": "c" * 64},
        },
        "preparation_context": context,
    }
    filenames = {
        "generation_config": "generation_config.json",
        "source_inventory": "source_inventory.json",
        "provider_code": "provider_code_inventory.json",
        "environment": "generation_environment.json",
        "preparation_context": "preparation_context.json",
    }
    payloads = {
        filenames[key]: canonical_json_bytes(value) for key, value in documents.items()
    }
    payloads.update(
        {
            "scenario_table.csv": table.getvalue().encode(),
            "stress_test_lookup.csv": lookup.encode(),
            "preparation_catalog.yml": catalog,
            "ancillary/elevation/grid.nc": ancillary,
        }
    )
    intent = {
        "schema_version": "scenario-collection/1",
        "canonicalization_id": "collection-canon/1",
        "scenario_type": "stochastic",
        "provider": {"name": "fixture", "revision": "b" * 64},
        "scenario_spec": {
            "scenario_type": "stochastic",
            "n_realizations": 1,
            "n_design_points": 1,
            "unperturbed_per_realization": 1,
            "expected_run_count": 2,
            "simulation_window": {"start": 2046, "end": 2046},
            "pairing": "paired_across_design_points",
            "row_order": "rlz-major/unperturbed-first/st-id-ascending",
        },
        "scenario_semantics_sha256": scenario_semantics_sha256(rows),
        "unit_id_capacity": 10,
        "unit_id_width": 2,
        "run_count": 2,
        **{
            key: _reference(filenames[key], payloads[filenames[key]])
            for key in documents
        },
    }
    intent["collection_id"] = collection_id(intent)
    claim = claim_collection(tmp_path / "project", intent)
    for relative, payload in payloads.items():
        write_collection_payload(claim, relative, payload)
    forcing = []
    for row in rows:
        payload = canonical_json_bytes(
            {
                "calendar": "proleptic_gregorian",
                "start": "2046-01-01 00:00:00",
                "end": "2046-12-31 00:00:00",
                "grid": [0, 1],
                "values": [1, 2],
            }
        )
        relative = f"forcing/run_{row.run_id}.nc"
        write_collection_payload(claim, relative, payload)
        forcing.append(
            {
                "run_id": row.run_id,
                **_reference(relative, payload),
                "size_bytes": len(payload),
                "descriptor": _describe_forcing(
                    claim.root / relative, context["generated_forcing_reader"]
                ),
            }
        )
    manifest = {
        "schema_version": "scenario-collection/1",
        "status": "ready",
        "collection_id": intent["collection_id"],
        "intent_path": "collection_intent.json",
        "intent_sha256": content_sha256(intent),
        "scenario_table": _reference(
            "scenario_table.csv", payloads["scenario_table.csv"]
        ),
        "scenario_type_artifacts": [
            {
                "role": "perturbation_lookup",
                **_reference(
                    "stress_test_lookup.csv", payloads["stress_test_lookup.csv"]
                ),
            }
        ],
        "preparation_context": intent["preparation_context"],
        "forcing": forcing,
    }
    manifest["collection_revision"] = collection_revision(manifest)
    return (
        claim,
        intent,
        manifest,
        {"original.nc": live_source},
        {"provider.py": live_code},
        documents["environment"],
    )


def _snapshot(root):
    return {
        path.relative_to(root).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in root.rglob("*")
        if path.is_file()
    }


def test_publish_portable_read_and_exact_producer_reuse(planned):
    claim, intent, manifest, sources, code, environment = planned
    assert not (claim.root / "collection.json").exists()
    result = publish_collection(claim, manifest, **CHECKS)
    assert result == manifest
    before = _snapshot(claim.root)
    assert (
        reuse_collection(
            claim.root / "collection.json",
            intent,
            live_sources=sources,
            live_code=code,
            live_environment=environment,
            **CHECKS,
        )
        == manifest
    )
    assert publish_collection(claim, manifest, **CHECKS) == manifest
    assert _snapshot(claim.root) == before
    for path in [*sources.values(), *code.values()]:
        path.unlink()
    assert read_collection(claim.root / "collection.json", **CHECKS) == manifest
    assert _snapshot(claim.root) == before
    assert collection_size(claim.root) == (
        len(before),
        sum(len(value[0]) for value in before.values()),
    )


def test_partial_claim_and_duplicate_payload_refuse_without_mutation(planned):
    claim, intent, *_ = planned
    before = _snapshot(claim.root)
    with pytest.raises(ImmutableCollectionError, match="partial"):
        claim_collection(claim.root.parent.parent, intent)
    with pytest.raises(ImmutableCollectionError):
        write_collection_payload(claim, "scenario_table.csv", b"overwrite")
    with pytest.raises(ScenarioCollectionNotReady):
        read_collection(claim.root / "collection.json", **CHECKS)
    assert _snapshot(claim.root) == before


@pytest.mark.parametrize(
    "defect",
    [
        "missing_forcing",
        "extra_forcing",
        "duplicate_forcing",
        "forcing_order",
        "wrong_size",
        "wrong_digest",
        "calendar",
        "endpoint",
        "grid",
        "units",
        "revision",
        "extra_table_column",
        "missing_table_row",
    ],
)
def test_publication_refuses_incomplete_or_falsified_inventory(planned, defect):
    claim, intent, manifest, *_ = planned
    if defect == "missing_forcing":
        manifest["forcing"].pop()
    elif defect in {"extra_forcing", "duplicate_forcing"}:
        entry = deepcopy(manifest["forcing"][0])
        if defect == "extra_forcing":
            entry["run_id"] = "03"
        manifest["forcing"].append(entry)
    elif defect == "forcing_order":
        manifest["forcing"].reverse()
    elif defect == "wrong_size":
        manifest["forcing"][0]["size_bytes"] += 1
    elif defect == "wrong_digest":
        manifest["forcing"][0]["sha256"] = "f" * 64
    elif defect in {"calendar", "endpoint", "grid", "units"}:
        descriptor = manifest["forcing"][0]["descriptor"]
        if defect == "calendar":
            descriptor["source_calendar"] = "360_day"
        elif defect == "endpoint":
            descriptor["end"] = "2046-12-30 00:00:00"
        elif defect == "grid":
            descriptor["spatial_representation_sha256"] = "a" * 64
        else:
            descriptor["variables"][0]["units"] = "K"
    elif defect.startswith("extra_table") or defect.startswith("missing_table"):
        path = claim.root / "scenario_table.csv"
        lines = path.read_text().splitlines()
        if defect == "extra_table_column":
            lines = [line + ",extra" for line in lines]
        else:
            lines.pop()
        path.write_bytes(("\n".join(lines) + "\n").encode())
        manifest["scenario_table"] = _reference("scenario_table.csv", path.read_bytes())
    manifest["collection_revision"] = collection_revision(manifest)
    if defect == "revision":
        manifest["collection_revision"] = "e" * 64
    before = _snapshot(claim.root)
    with pytest.raises(ScenarioCollectionNotReady):
        publish_collection(claim, manifest, **CHECKS)
    assert _snapshot(claim.root) == before
    assert not (claim.root / "collection.json").exists()


def test_extraction_failure_and_publication_failure_leave_no_ready_marker(
    planned, monkeypatch
):
    claim, _, manifest, *_ = planned

    def broken(path, reader):
        raise ValueError("cannot extract calendar")

    with pytest.raises(ScenarioCollectionNotReady, match="calendar"):
        publish_collection(
            claim,
            manifest,
            describe_forcing=broken,
            describe_ancillary=_describe_ancillary,
        )
    assert not (claim.root / "collection.json").exists()

    def failed_replace(source, destination):
        raise OSError("injected publication failure")

    monkeypatch.setattr(
        "blueearth_cst.experiment.scenario_collection.os.replace", failed_replace
    )
    before = _snapshot(claim.root)
    with pytest.raises(OSError, match="publication failure"):
        publish_collection(claim, manifest, **CHECKS)
    assert _snapshot(claim.root) == before


@pytest.mark.parametrize(
    "changed", ["source", "code", "environment", "ready", "intent"]
)
def test_producer_reuse_refuses_drift_without_repair(planned, changed):
    claim, intent, manifest, sources, code, environment = planned
    publish_collection(claim, manifest, **CHECKS)
    if changed == "source":
        next(iter(sources.values())).write_bytes(b"changed")
    elif changed == "code":
        next(iter(code.values())).write_bytes(b"changed")
    elif changed == "environment":
        environment["packages"]["fixture"] = "2.0"
    elif changed == "intent":
        intent["run_count"] = 99
    else:
        (claim.root / "forcing/run_01.nc").write_bytes(b"corrupt")
    before = _snapshot(claim.root)
    with pytest.raises(ImmutableCollectionError):
        reuse_collection(
            claim.root / "collection.json",
            intent,
            live_sources=sources,
            live_code=code,
            live_environment=environment,
            **CHECKS,
        )
    assert _snapshot(claim.root) == before
    with pytest.raises(ImmutableCollectionError):
        write_collection_payload(claim, "new-file", b"no")


def test_descriptor_callbacks_are_mandatory(planned):
    claim, _, manifest, *_ = planned
    with pytest.raises(TypeError):
        publish_collection(claim, manifest)
    assert not (claim.root / "collection.json").exists()


def _changed_preparation(planned, defect):
    """Build a new internally hashed intent so physical/closure checks must act."""
    old_claim, old_intent, old_manifest, *_ = planned
    payloads = {name: raw for name, (raw, _) in _snapshot(old_claim.root).items()}
    context = json.loads(payloads["preparation_context.json"])
    catalog = payloads["preparation_catalog.yml"]
    if defect == "descriptor":
        context["ancillary"][0]["descriptor"]["units"] = "km"
    elif defect == "size":
        context["ancillary"][0]["size_bytes"] += 1
    elif defect == "missing_artifact":
        payloads.pop("ancillary/elevation/grid.nc")
    elif defect == "duplicate_id":
        context["ancillary"].append(deepcopy(context["ancillary"][0]))
    elif defect == "missing_array":
        del context["ancillary"]
    elif defect == "wrong_elevation":
        context["forcing_elevation"]["artifact_id"] = "absent"
    elif defect == "reader_root":
        context["generated_forcing_reader"]["root"] = "/external"
    elif defect == "nested_uri":
        context["generated_forcing_reader"]["driver"]["options"] = {
            "uri": "external.nc"
        }
    elif defect == "empty_driver":
        context["generated_forcing_reader"]["driver"] = {}
    elif defect == "empty_driver_name":
        context["generated_forcing_reader"]["driver"] = ""
    elif defect == "bad_options":
        context["generated_forcing_reader"]["driver"]["options"] = []
    elif defect == "unknown_io_option":
        context["generated_forcing_reader"]["driver"]["options"] = {
            "unreviewed_loader": "external.nc"
        }
    elif defect == "descriptive_metadata":
        context["generated_forcing_reader"]["metadata"]["url"] = (
            "https://example.invalid/provenance"
        )
    elif defect in {"empty_absent_reason", "empty_explicit_reason"}:
        context["ancillary"] = []
        context["forcing_elevation"] = None
        catalog = b"{}\n"
        if defect == "empty_explicit_reason":
            context["ancillary_absence_reason"] = (
                "test-only reader requires no elevation"
            )
    else:
        if defect == "remote_uri":
            catalog = catalog.replace(
                b"ancillary/elevation/grid.nc", b"https://example.invalid/elevation.nc"
            )
        elif defect == "unlisted_uri":
            catalog = catalog.replace(
                b"ancillary/elevation/grid.nc",
                b"ancillary/elevation/not-in-inventory.nc",
            )
        elif defect == "duplicate_yaml":
            catalog += catalog
        elif defect == "catalog_root":
            catalog += b"  root: /external\n"
        elif defect == "driver_filename":
            catalog = catalog.replace(
                b"preprocess: harmonise_dims", b"filename: external.nc"
            )
        elif defect == "catalog_bad_driver":
            catalog = catalog.replace(b"name: raster_xarray", b"name: ''")
        else:
            raise AssertionError(defect)
    context["catalog"] = _reference("preparation_catalog.yml", catalog)
    payloads["preparation_catalog.yml"] = catalog
    payloads["preparation_context.json"] = canonical_json_bytes(context)
    intent = deepcopy(old_intent)
    intent["preparation_context"] = _reference(
        "preparation_context.json", payloads["preparation_context.json"]
    )
    intent["collection_id"] = collection_id(intent)
    # Missing-byte defects leave the intent unchanged but need a distinct project.
    claim = claim_collection(old_claim.root.parent.parent / "changed", intent)
    for name, payload in payloads.items():
        if name != "collection_intent.json":
            write_collection_payload(claim, name, payload)
    manifest = deepcopy(old_manifest)
    manifest.update(
        collection_id=intent["collection_id"],
        intent_sha256=content_sha256(intent),
        preparation_context=intent["preparation_context"],
    )
    manifest["collection_revision"] = collection_revision(manifest)
    return claim, manifest


@pytest.mark.parametrize(
    "defect",
    [
        "descriptor",
        "size",
        "missing_artifact",
        "duplicate_id",
        "missing_array",
        "wrong_elevation",
        "reader_root",
        "nested_uri",
        "empty_absent_reason",
        "remote_uri",
        "unlisted_uri",
        "duplicate_yaml",
        "catalog_root",
        "driver_filename",
        "empty_driver",
        "empty_driver_name",
        "bad_options",
        "unknown_io_option",
        "catalog_bad_driver",
    ],
)
def test_preparation_closure_refuses_with_self_consistent_hashes(planned, defect):
    claim, manifest = _changed_preparation(planned, defect)
    before = _snapshot(claim.root)
    with pytest.raises(ScenarioCollectionNotReady):
        publish_collection(claim, manifest, **CHECKS)
    assert _snapshot(claim.root) == before


def test_explicit_empty_ancillary_contract_is_supported(planned):
    claim, manifest = _changed_preparation(planned, "empty_explicit_reason")
    assert publish_collection(claim, manifest, **CHECKS) == manifest


def test_descriptive_metadata_does_not_become_an_io_dependency(planned):
    claim, manifest = _changed_preparation(planned, "descriptive_metadata")
    assert publish_collection(claim, manifest, **CHECKS) == manifest


def test_reserved_marker_case_alias_refuses_on_windows(planned):
    claim, *_ = planned
    if Path("COLLECTION.JSON") != Path("collection.json"):
        pytest.skip("case alias is specific to Windows paths")
    with pytest.raises(ImmutableCollectionError, match="reserved"):
        write_collection_payload(claim, "COLLECTION.JSON", b"unvalidated")
    assert not (claim.root / "collection.json").exists()


def test_reserved_marker_symlink_alias_refuses(planned):
    claim, *_ = planned
    try:
        (claim.root / "alias").symlink_to(claim.root / "collection.json")
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")
    with pytest.raises(ImmutableCollectionError, match="reserved"):
        write_collection_payload(claim, "alias", b"unvalidated")
    assert not (claim.root / "collection.json").exists()


def test_ready_marker_symlink_escape_refuses(planned, tmp_path):
    claim, _, manifest, *_ = planned
    outside = tmp_path / "outside.json"
    outside.write_bytes(canonical_json_bytes(manifest))
    marker = claim.root / "collection.json"
    try:
        marker.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")
    with pytest.raises(ScenarioCollectionNotReady, match="outside"):
        read_collection(marker, **CHECKS)


def test_distinct_intent_gets_distinct_directory(planned):
    claim, intent, *_ = planned
    changed = deepcopy(intent)
    changed["provider"]["revision"] = "d" * 64
    changed["collection_id"] = collection_id(changed)
    other = claim_collection(claim.root.parent.parent, changed)
    assert other.root != claim.root
    assert other.root.name == changed["collection_id"]


def test_referenced_collection_requires_explicit_force_for_deletion(planned):
    claim, intent, manifest, *_ = planned
    publish_collection(claim, manifest, **CHECKS)
    project = claim.root.parent.parent
    simulation = project / "experiments" / "retained" / "config" / "simulation.json"
    simulation.parent.mkdir(parents=True)
    simulation.write_bytes(
        canonical_json_bytes({"collection": {"collection_id": intent["collection_id"]}})
    )
    records = list_collections(project)
    assert records[0]["simulation_references"] == [
        "experiments/retained/config/simulation.json"
    ]
    before = _snapshot(claim.root)
    with pytest.raises(ImmutableCollectionError, match="force required"):
        delete_collection(project, intent["collection_id"])
    assert _snapshot(claim.root) == before
    deleted = delete_collection(project, intent["collection_id"], force=True)
    assert deleted["size_bytes"] == records[0]["size_bytes"]
    assert not claim.root.exists()
    assert simulation.exists()


def test_unreadable_simulation_blocks_reference_aware_delete(planned):
    claim, intent, *_ = planned
    project = claim.root.parent.parent
    simulation = project / "experiments" / "broken" / "config" / "simulation.json"
    simulation.parent.mkdir(parents=True)
    simulation.write_bytes(b"broken record")
    with pytest.raises(ImmutableCollectionError, match="cannot establish references"):
        delete_collection(project, intent["collection_id"], force=True)
    assert claim.root.exists()


def test_same_invocation_workers_and_later_partial_refusal(planned, tmp_path):
    from blueearth_cst.experiment.collection_resolution import scenario_plan
    from blueearth_cst.experiment.content_identity import read_canonical_json
    from blueearth_cst.experiment.scenario_collection import (
        _job_collection_claim,
        initialize_collection_jobs,
    )

    original, intent, manifest, *_ = planned
    project = tmp_path / "multi-job-project"
    plan = scenario_plan(
        project,
        {"fixture": "same-invocation"},
        intent,
        read_canonical_json(original.root / "source_inventory.json"),
    )
    payloads = {
        path.relative_to(original.root).as_posix(): path
        for path in original.root.rglob("*")
        if path.is_file()
        and path.name != "collection_intent.json"
        and "forcing" not in path.relative_to(original.root).parts
    }
    initialize_collection_jobs(project, plan, "1" * 32, payloads)
    with pytest.raises(ImmutableCollectionError):
        _job_collection_claim(project, plan, "2" * 32)
    with pytest.raises(ImmutableCollectionError):
        initialize_collection_jobs(project, plan, "2" * 32, payloads)
    for entry in manifest["forcing"]:
        worker = _job_collection_claim(project, plan, "1" * 32)
        write_collection_payload(worker, entry["path"], original.root / entry["path"])
    publisher = _job_collection_claim(project, plan, "1" * 32)
    publish_collection(publisher, manifest, **CHECKS)
    assert read_collection(publisher.root / "collection.json", **CHECKS) == manifest
    with pytest.raises(ImmutableCollectionError, match="writer authorization"):
        initialize_collection_jobs(project, plan, "1" * 32, payloads)


def test_initializer_crash_before_receipt_cannot_resume(planned, tmp_path):
    from blueearth_cst.experiment.collection_resolution import scenario_plan
    from blueearth_cst.experiment.content_identity import read_canonical_json
    from blueearth_cst.experiment.scenario_collection import initialize_collection_jobs

    original, intent, *_ = planned
    project = tmp_path / "crashed-initializer"
    plan = scenario_plan(
        project,
        {"fixture": "crash"},
        intent,
        read_canonical_json(original.root / "source_inventory.json"),
    )
    with pytest.raises(FileNotFoundError):
        initialize_collection_jobs(
            project, plan, "1" * 32, {"missing.nc": tmp_path / "absent.nc"}
        )
    with pytest.raises(ImmutableCollectionError):
        initialize_collection_jobs(project, plan, "1" * 32, {})
