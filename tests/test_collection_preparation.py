"""Real NetCDF collection publication and source-independent physical binding."""

from copy import deepcopy

import numpy as np
import pytest
import xarray as xr
import yaml
from pyproj import CRS

from blueearth_cst.climate_analysis.prepare_climate_data_catalog import (
    plan_preparation_payloads,
)
from blueearth_cst.experiment.content_identity import (
    canonical_json_bytes,
    collection_id,
    collection_revision,
    content_sha256,
    read_canonical_json,
)
from blueearth_cst.experiment.downscale_climate_forcing import collection_run_forcing
from blueearth_cst.experiment.forcing_descriptor import (
    UnitInterpretation,
    collection_forcing_descriptor,
    describe_ancillary,
)
from blueearth_cst.experiment.scenario_collection import (
    ScenarioCollectionNotReady,
    claim_collection,
    publish_collection,
    write_collection_payload,
)
from blueearth_cst.shared.provenance import file_sha256
from tests.test_scenario_collection import planned  # noqa: F401


def test_planned_publication_across_separate_workers(retained, tmp_path):
    """Fresh processes share only the initializer's current-invocation receipt."""
    import os
    import subprocess
    import sys
    from pathlib import Path

    from blueearth_cst.experiment.collection_resolution import write_scenario_request
    from blueearth_cst.experiment.legacy_scenario_provider import plan_collection
    from blueearth_cst.experiment.scenario_collection import read_collection

    original, manifest = retained
    intent = read_canonical_json(original / "collection_intent.json")
    documents = {
        key: read_canonical_json(original / intent[key]["path"])
        for key in (
            "generation_config",
            "provider_code",
            "environment",
            "preparation_context",
        )
    }
    project = tmp_path / "worker-project"
    plan = plan_collection(
        project,
        {"seed": 42},
        scenario_spec=intent["scenario_spec"],
        source_inputs={"historical_climate": original / "forcing/run_01.nc"},
        **documents,
    )
    plan_path = write_scenario_request(project, plan)
    invocation = "1" * 32
    program = tmp_path / "worker.py"
    program.write_text(
        """import sys
from pathlib import Path
from blueearth_cst.experiment.content_identity import read_canonical_json
from blueearth_cst.experiment.legacy_scenario_provider import initialize_planned_collection, publish_planned_collection
from blueearth_cst.experiment.scenario_collection import _job_collection_claim, write_collection_payload
project, plan_path, original = map(Path, sys.argv[1:4])
invocation, operation = sys.argv[4:6]
plan = read_canonical_json(plan_path)
if operation == "initialize":
    context = plan["documents"]["preparation_context"]
    initialize_planned_collection(project, plan, invocation,
        lookup_path=original / "stress_test_lookup.csv",
        catalog_bytes=(original / context["catalog"]["path"]).read_bytes(),
        ancillary_sources={entry["path"]: original / entry["path"] for entry in context["ancillary"]})
elif operation == "publish":
    publish_planned_collection(project, plan, invocation)
else:
    claim = _job_collection_claim(project, plan, invocation)
    write_collection_payload(claim, f"forcing/run_{operation}.nc", original / f"forcing/run_{operation}.nc")
""",
        encoding="utf-8",
    )
    environment = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}

    def run(operation, owner=invocation):
        return subprocess.run(
            [
                sys.executable,
                str(program),
                str(project),
                str(plan_path),
                str(original),
                owner,
                operation,
            ],
            env=environment,
            capture_output=True,
            text=True,
        )

    initialized = run("initialize")
    assert initialized.returncode == 0, initialized.stderr
    refused = run("01", "2" * 32)
    assert (
        refused.returncode != 0
        and "no valid collection initialization" in refused.stderr
    )
    for operation in ("01", "02", "publish"):
        result = run(operation)
        assert result.returncode == 0, result.stderr
    ready = read_collection(
        Path(plan["manifest_path"]),
        describe_forcing=collection_forcing_descriptor,
        describe_ancillary=describe_ancillary,
    )
    assert [item["sha256"] for item in ready["forcing"]] == [
        item["sha256"] for item in manifest["forcing"]
    ]
    refused = run("initialize", "2" * 32)
    assert refused.returncode != 0 and "existing ready" in refused.stderr


@pytest.fixture
def retained(planned, tmp_path):  # noqa: F811 - explicitly imported pytest fixture
    old_claim, intent, manifest, _, _, _ = planned
    source = tmp_path / "native-elevation.nc"
    ds = xr.Dataset(
        {"temp": (("time", "latitude", "longitude"), np.ones((365, 2, 2)))},
        coords={
            "time": np.arange("2046-01-01", "2047-01-01", dtype="datetime64[D]"),
            "latitude": [1.0, 2.0],
            "longitude": [3.0, 4.0],
        },
    )
    ds["spatial_ref"] = xr.DataArray(0, attrs={"crs_wkt": CRS.from_epsg(4326).to_wkt()})
    ds.temp.attrs["units"] = "K"
    ds.isel(time=0, drop=True).rename({"temp": "elevtn"}).to_netcdf(source)
    entry = {
        "data_type": "RasterDataset",
        "driver": "raster_xarray",
        "metadata": {"crs": 4326},
    }
    context, catalog, ancillary = plan_preparation_payloads(
        entry,
        "era5",
        entry,
        source,
        UnitInterpretation(
            "fixture/1", "synthetic values in degC", (("temp", "degC"),)
        ),
    )
    intent = deepcopy(intent)
    intent["preparation_context"]["sha256"] = content_sha256(context)
    intent["collection_id"] = collection_id(intent)
    claim = claim_collection(tmp_path / "portable-project", intent)
    for path in old_claim.root.iterdir():
        if path.is_file() and path.name not in {
            "collection_intent.json",
            "preparation_context.json",
            "preparation_catalog.yml",
        }:
            write_collection_payload(claim, path.name, path)
    write_collection_payload(
        claim, "preparation_context.json", canonical_json_bytes(context)
    )
    write_collection_payload(claim, "preparation_catalog.yml", catalog)
    for relative, path in ancillary.items():
        write_collection_payload(claim, relative, path)
    manifest = deepcopy(manifest)
    manifest.update(
        collection_id=intent["collection_id"],
        intent_sha256=content_sha256(intent),
        preparation_context=intent["preparation_context"],
    )
    forcing_source = tmp_path / "native-forcing.nc"
    ds.to_netcdf(forcing_source)
    for record in manifest["forcing"]:
        write_collection_payload(claim, record["path"], forcing_source)
        record.update(
            sha256=file_sha256(forcing_source),
            size_bytes=forcing_source.stat().st_size,
            descriptor=collection_forcing_descriptor(
                forcing_source, context["generated_forcing_reader"]
            ),
        )
    manifest["collection_revision"] = collection_revision(manifest)
    publish_collection(
        claim,
        manifest,
        describe_forcing=collection_forcing_descriptor,
        describe_ancillary=describe_ancillary,
    )
    source.unlink()
    forcing_source.unlink()
    return claim.root, manifest


def test_bind_retained_collection_after_original_files_removed(retained, tmp_path):
    root, manifest = retained
    before = {
        str(path): path.read_bytes() for path in root.rglob("*") if path.is_file()
    }
    run = collection_run_forcing(
        root / "collection.json", "01", tmp_path / "run-catalog.yml"
    )
    assert run.collection_revision == manifest["collection_revision"]
    assert run.descriptor.variables[0].units == "degC"
    catalog = yaml.safe_load((tmp_path / "run-catalog.yml").read_text())
    assert set(catalog) == {"elevation", "run_01"}
    assert run.preparation_context.pet_method == "debruin"
    assert before == {
        str(path): path.read_bytes() for path in root.rglob("*") if path.is_file()
    }


def test_changed_ancillary_refuses_before_transient_catalog_write(retained, tmp_path):
    root, _ = retained
    next((root / "ancillary").rglob("*.nc")).write_bytes(b"damaged")
    output = tmp_path / "must-not-exist.yml"
    with pytest.raises(ScenarioCollectionNotReady):
        collection_run_forcing(root / "collection.json", "01", output)
    assert not output.exists()


def test_consumer_refuses_output_inside_immutable_collection(retained):
    root, _ = retained
    with pytest.raises(ValueError, match="outside the collection"):
        collection_run_forcing(
            root / "collection.json", "01", root / "preparation_catalog.yml"
        )


def test_invocation_snapshot_avoids_other_run_scans_but_rechecks_selected_bytes(
    retained, tmp_path, monkeypatch
):
    import blueearth_cst.experiment.scenario_collection as collections

    root, manifest = retained

    def must_not_rescan(*args, **kwargs):
        raise AssertionError("invocation already validated the full collection")

    monkeypatch.setattr(collections, "read_collection", must_not_rescan)
    selected = collection_run_forcing(
        root / "collection.json",
        "01",
        tmp_path / "catalog.yml",
        validated_collection=manifest,
    )
    assert selected.collection_revision == manifest["collection_revision"]
    (root / "forcing/run_01.nc").write_bytes(b"changed since invocation validation")
    output = tmp_path / "must-not-write.yml"
    with pytest.raises(ValueError, match="artifact changed"):
        collection_run_forcing(
            root / "collection.json", "01", output, validated_collection=manifest
        )
    assert not output.exists()


def test_consumer_preserves_marker_confinement_before_resolution(retained, tmp_path):
    root, _ = retained
    other = tmp_path / "other-collection"
    other.mkdir()
    marker = other / "collection.json"
    try:
        marker.symlink_to(root / "collection.json")
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")
    output = tmp_path / "must-not-write.yml"
    with pytest.raises(ScenarioCollectionNotReady, match="outside"):
        collection_run_forcing(marker, "01", output)
    assert not output.exists()
