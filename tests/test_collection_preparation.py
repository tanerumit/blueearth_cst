"""Real NetCDF collection publication and source-independent physical binding."""

from copy import deepcopy

import numpy as np
import pytest
import xarray as xr
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
from blueearth_cst.experiment.forcing_descriptor import (
    UnitInterpretation,
    collection_forcing_descriptor,
)
from blueearth_cst.experiment.scenario_collection import (
    claim_collection,
    publish_collection,
    write_collection_payload,
)
from blueearth_cst.experiment.wf4_ancillary_descriptor import describe_ancillary
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
