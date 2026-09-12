"""GF31 physical branch comparison; synthetic elevation, real P0 generated forcing."""

# ruff: noqa: E402
import argparse
import csv
import io
import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
import xarray as xr
import yaml

from blueearth_cst.climate_analysis.prepare_climate_data_catalog import (
    resolve_preparation_payloads,
)
from blueearth_cst.experiment.content_identity import (
    canonical_json_bytes,
    collection_id,
    collection_revision,
    content_sha256,
    scenario_semantics_sha256,
)
from blueearth_cst.experiment.downscale_climate_forcing import (
    collection_run_forcing,
    downscale_climate_forcing,
    resolved_unit_interpretation,
)
from blueearth_cst.experiment.forcing_descriptor import (
    collection_forcing_descriptor,
    describe_ancillary,
)
from blueearth_cst.experiment.scenario_collection import (
    claim_collection,
    publish_collection,
    write_collection_payload,
)
from blueearth_cst.experiment.scenario_rows import stochastic_rows
from blueearth_cst.experiment.simulator_adapter import (
    ForcingRequirement,
    ModelReference,
    PreparationSettings,
    prepare,
    validate_forcing,
)
from blueearth_cst.shared.provenance import file_sha256

if len(sys.argv) > 1 and sys.argv[1] == "--old":
    from blueearth_cst.experiment.forcing_descriptor import UnitInterpretation

    arguments = json.loads(Path(sys.argv[2]).read_text())
    binding = arguments.pop("unit_interpretation")
    arguments["unit_interpretation"] = UnitInterpretation(
        binding["revision"],
        binding["evidence"],
        tuple(tuple(p) for p in binding["variables"]),
    )
    downscale_climate_forcing(**arguments)
    sys.exit(0)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--work", type=Path, required=True)
parser.add_argument("--old-root", type=Path, required=True)
args = parser.parse_args()
work = args.work.resolve()
p0 = args.old_root.resolve()
if work.is_relative_to(p0):
    raise ValueError("Probe outputs must be outside P0")
work.mkdir(parents=True, exist_ok=False)
source = p0 / "experiments/experiment/climate/weathergenr/output/rlz_1_st_0.nc"
shutil.copytree(p0 / "models/hydrology/wflow", work / "model")
interpretation = resolved_unit_interpretation(
    ["config/catalogs/deltares_data.yml"], "era5"
)
reports = []


def ref(path, payload):
    import hashlib

    return {"path": path, "sha256": hashlib.sha256(payload).hexdigest()}


for branch in ("era5", "chirps", "chirps_global", "eobs"):
    root = work / branch
    live = root / "live"
    live.mkdir(parents=True)
    forcing = live / "forcing.nc"
    shutil.copyfile(source, forcing)
    elevation = live / "elevation.nc"
    with xr.open_dataset(forcing) as ds:
        elev = ds[["temp"]].isel(time=0, drop=True).rename({"temp": "elevtn"}).load()
        elev["elevtn"] = elev.elevtn * 0 + 100
        elev.elevtn.attrs["units"] = "m"
        elev["spatial_ref"] = ds.spatial_ref
        elev.to_netcdf(elevation)
    entry = {
        "data_type": "RasterDataset",
        "uri": str(forcing),
        "driver": "raster_xarray",
        "metadata": {"crs": 4326},
    }
    oro_entry = {**entry, "uri": str(elevation)}
    catalog = live / "catalog.yml"
    catalog.write_text(
        yaml.safe_dump({branch: entry, f"{branch}_orography": oro_entry}),
        encoding="utf-8",
    )
    old = root / "old"
    old.mkdir()
    from dataclasses import asdict

    old_arguments = dict(
        config_out_fn=str(old / "run.toml"),
        fn_out=str(old / "forcing.nc"),
        fn_in=str(forcing),
        data_libs=[str(catalog)],
        model_root=str(work / "model"),
        precip_source=branch,
        sim_start=2046,
        sim_end=2054,
        catalog_out=str(old / "reader.yml"),
        oro_path=str(elevation),
        run_id="01",
        unit_interpretation=asdict(interpretation),
        native_output_path=str(old / "run.csv"),
        native_log_path=str(old / "run.log"),
    )
    argument_path = root / "old-arguments.json"
    argument_path.write_text(json.dumps(old_arguments), encoding="utf-8")
    subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--old", str(argument_path)],
        check=True,
    )
    context, catalog_bytes, ancillary = resolve_preparation_payloads(
        [str(catalog)], branch, interpretation, elevation
    )
    inventory = [
        {
            "role": "fixture_forcing",
            "path": str(forcing),
            "sha256": file_sha256(forcing),
            "size_bytes": forcing.stat().st_size,
            "metadata": {
                "fixture": "P0 forcing; synthetic elevation; branch comparison only"
            },
        }
    ]
    documents = {
        "generation_config": (
            "generation_config.json",
            {"seed": {"requested": 123, "resolved": 123}, "unit_id_capacity": 10},
        ),
        "source_inventory": ("source_inventory.json", inventory),
        "provider_code": (
            "provider_code_inventory.json",
            [
                {
                    "path": "probe-portable-preparation.py",
                    "sha256": file_sha256(Path(__file__)),
                }
            ],
        ),
        "environment": (
            "generation_environment.json",
            {
                "packages": {"fixture": "P3"},
                "locks": {"pixi.lock": file_sha256(Path("pixi.lock"))},
            },
        ),
        "preparation_context": ("preparation_context.json", context),
    }
    rows = stochastic_rows(1, 1, unit_id_capacity=10)
    intent = {
        "schema_version": "scenario-collection/1",
        "canonicalization_id": "collection-canon/1",
        "scenario_type": "stochastic",
        "provider": {
            "name": "physical-fixture",
            "revision": file_sha256(Path(__file__)),
        },
        "scenario_spec": {
            "scenario_type": "stochastic",
            "n_realizations": 1,
            "n_design_points": 1,
            "unperturbed_per_realization": 1,
            "expected_run_count": 2,
            "simulation_window": {"start": 2046, "end": 2054},
            "pairing": "paired_across_design_points",
            "row_order": "rlz-major/unperturbed-first/st-id-ascending",
        },
        "scenario_semantics_sha256": scenario_semantics_sha256(rows),
        "unit_id_capacity": 10,
        "unit_id_width": 2,
        "run_count": 2,
        **{
            key: ref(name, canonical_json_bytes(value))
            for key, (name, value) in documents.items()
        },
    }
    intent["collection_id"] = collection_id(intent)
    claim = claim_collection(root / "project", intent)
    for name, value in documents.values():
        write_collection_payload(claim, name, canonical_json_bytes(value))
    write_collection_payload(claim, "preparation_catalog.yml", catalog_bytes)
    for name, path in ancillary.items():
        write_collection_payload(claim, name, path)
    text = io.StringIO(newline="")
    writer = csv.DictWriter(
        text, fieldnames=list(rows[0].as_record()), lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(row.as_record() for row in rows)
    table = text.getvalue().encode()
    lookup = (
        "st_id,month,temp_change,precip_change,precip_variance_change\n"
        + "".join(f"1,{m},0,0,0\n" for m in range(1, 13))
    ).encode()
    write_collection_payload(claim, "scenario_table.csv", table)
    write_collection_payload(claim, "stress_test_lookup.csv", lookup)
    records = []
    for row in rows:
        relative = f"forcing/run_{row.run_id}.nc"
        write_collection_payload(claim, relative, forcing)
        records.append(
            {
                "run_id": row.run_id,
                "path": relative,
                "sha256": file_sha256(forcing),
                "size_bytes": forcing.stat().st_size,
                "descriptor": collection_forcing_descriptor(
                    forcing, context["generated_forcing_reader"]
                ),
            }
        )
    manifest = {
        "schema_version": "scenario-collection/1",
        "status": "ready",
        "collection_id": intent["collection_id"],
        "intent_path": "collection_intent.json",
        "intent_sha256": content_sha256(intent),
        "scenario_table": ref("scenario_table.csv", table),
        "scenario_type_artifacts": [
            {"role": "perturbation_lookup", **ref("stress_test_lookup.csv", lookup)}
        ],
        "preparation_context": intent["preparation_context"],
        "forcing": records,
    }
    manifest["collection_revision"] = collection_revision(manifest)
    publish_collection(
        claim,
        manifest,
        describe_forcing=collection_forcing_descriptor,
        describe_ancillary=describe_ancillary,
    )
    # These are disposable probe-owned sources. Retain them under a new name so
    # every original locator is unavailable while the consumer executes.
    destination = (root / "unavailable-originals").resolve()
    if not live.resolve().is_relative_to(work) or not destination.is_relative_to(work):
        raise ValueError("Fixture relocation leaves probe workspace")
    live.rename(destination)
    new = root / "new"
    new.mkdir()
    run = collection_run_forcing(
        claim.root / "collection.json", "01", new / "reader.yml"
    )
    if run.preparation_context.forcing_entry != "run_01":
        raise ValueError("Final run selector not exercised")
    variables = (
        ("precip", "mm/day"),
        ("temp", "degC"),
        ("press_msl", "hPa"),
        ("kin", "W/m2"),
    )
    if branch != "eobs":
        variables += (("kout", "W/m2"),)
    req = ForcingRequirement(
        variables,
        "EPSG:4326",
        ("longitude", "latitude", "time"),
        ("noleap", "standard", "proleptic_gregorian"),
        86400,
        "interval_end",
        "2046-01-01T00:00:00",
        "2054-12-31T00:00:00",
        False,
    )
    settings = PreparationSettings(
        new / "run.toml",
        new / "forcing.nc",
        new / "run.csv",
        new / "run.log",
        req.first_time,
        req.last_time,
    )
    prepare(
        "01", validate_forcing(run, req), ModelReference(work / "model", req), settings
    )
    with (
        xr.open_dataset(old / "forcing.nc") as left,
        xr.open_dataset(new / "forcing.nc") as right,
    ):
        # The accepted catalog selector migration changes these provenance
        # attributes only. Validate their exact spelling before excluding them
        # in memory; every other attribute, coordinate and value remains exact.
        selector_relocations = {}
        for variable in ("precip", "pet", "temp"):
            attribute = f"{variable}_fn"
            observed = [
                left[variable].attrs.get(attribute),
                right[variable].attrs.get(attribute),
            ]
            if observed != ["forcing", "run_01"]:
                raise ValueError(
                    f"Unexpected {variable}.{attribute} relocation: {observed}"
                )
            selector_relocations[f"{variable}.{attribute}"] = observed
            left[variable].attrs.pop(attribute)
            right[variable].attrs.pop(attribute)
        xr.testing.assert_identical(left, right)
        changed = right.load().copy(deep=True)
        changed["precip"].data = changed["precip"].data + 1.0
        try:
            xr.testing.assert_identical(left, changed)
        except AssertionError:
            pass
        else:
            raise ValueError("Forcing comparator failed to detect +1 precipitation")
    left = tomllib.loads((old / "run.toml").read_text())
    right = tomllib.loads((new / "run.toml").read_text())
    complete_toml_identical = left == right
    paths = {}
    for section, key in [("input", "path_forcing")]:
        paths[f"{section}.{key}"] = [left[section].pop(key), right[section].pop(key)]
    assert left == right, (branch, left, right)
    reports.append(
        {
            "branch": branch,
            "fixture": "P0 ERA5 generated values; constant synthetic elevation",
            "pet_method": context["pet_method"],
            "original_paths_unavailable": not live.exists(),
            "forcing_identical_except_declared_selectors": True,
            "selector_attribute_relocations": selector_relocations,
            "positive_perturbation_rejected": True,
            "complete_toml_identical": complete_toml_identical,
            "final_generated_catalog_key": run.preparation_context.forcing_entry,
            "toml_identical_excluding_reported_paths": True,
            "paths": paths,
            "collection_manifest": str(claim.root / "collection.json"),
            "prepared_old": str(old / "forcing.nc"),
            "prepared_new": str(new / "forcing.nc"),
        }
    )
    (work / "comparison.json").write_text(
        json.dumps(reports, indent=2), encoding="utf-8"
    )
    print(branch, "PASS", flush=True)
