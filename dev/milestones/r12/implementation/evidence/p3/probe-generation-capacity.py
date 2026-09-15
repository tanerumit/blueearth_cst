"""Stage GF27 auto-seed configs or compare three explicitly selected collections.

This probe never invokes Snakemake. Stage against an existing project so all
variants share the same historical source bytes. Execute the emitted generation
commands separately, then pass their exact ready manifests to compare.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import xarray as xr
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[6]))

from blueearth_cst.experiment.forcing_descriptor import (  # noqa: E402
    collection_forcing_descriptor,
    describe_ancillary,
)
from blueearth_cst.experiment.scenario_collection import read_collection  # noqa: E402


def require(condition: bool, message: str) -> None:
    """Refuse mismatches without depending on Python assertion settings."""
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    """Hash an evidence artifact."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def stage(config: Path, work: Path) -> dict[str, Any]:
    """Write three generation-only variants without changing source configs."""
    config, work = config.resolve(), work.resolve()
    project = yaml.safe_load(config.read_text(encoding="utf-8"))
    generation_path = (
        config.parent / project["workflows"]["generate_scenarios"]["config_path"]
    ).resolve()
    generation = yaml.safe_load(generation_path.read_text(encoding="utf-8"))
    require(generation["n_realizations"] == 2, "GF27 fixture needs two realizations")
    perturb = generation["climate_perturbations"]
    require(
        perturb["temp"]["n_levels"] * perturb["precip"]["n_levels"] == 6,
        "GF27 fixture needs six design points",
    )
    work.mkdir(parents=True, exist_ok=False)
    for stanza in project["workflows"].values():
        stanza["enabled"] = False
        if "config_path" in stanza:
            stanza["config_path"] = str(
                (config.parent / stanza["config_path"]).resolve()
            )
    commands = []
    for capacity in (21, 22, 100):
        current = copy.deepcopy(project)
        settings = copy.deepcopy(generation)
        settings.update(seed="auto", unit_id_capacity=capacity)
        settings_path = work / f"project_config_capacity_{capacity}_generate.yml"
        path = work / f"project_config_capacity_{capacity}.yml"
        settings_path.write_text(
            yaml.safe_dump(settings, sort_keys=False), encoding="utf-8"
        )
        current["workflows"]["generate_scenarios"] = {
            "enabled": True,
            "config_path": settings_path.name,
        }
        path.write_text(yaml.safe_dump(current, sort_keys=False), encoding="utf-8")
        commands.append(
            {
                "capacity": capacity,
                "config": str(path),
                "config_sha256": digest(path),
                "argv_after_pixi_run": [
                    "snakemake",
                    "all",
                    "-c",
                    "3",
                    "-s",
                    "generate_scenarios.smk",
                    "--configfile",
                    str(path),
                ],
            }
        )
    result = {
        "status": "staged_not_executed",
        "source_config": str(config),
        "commands": commands,
    }
    (work / "matrix.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    return result


def compare(markers: list[Path], report: Path) -> dict[str, Any]:
    """Require exact auto-seed and forcing preservation across namespace widths."""
    reports, baseline, base_rows, base_forcing = [], None, None, None
    identities = set()
    for capacity, marker in zip((21, 22, 100), markers, strict=True):
        marker = marker.resolve()
        require(
            not report.resolve().is_relative_to(marker.parent),
            "Report must be outside collection",
        )
        manifest = read_collection(
            marker,
            describe_forcing=collection_forcing_descriptor,
            describe_ancillary=describe_ancillary,
        )
        root = marker.parent
        generation = json.loads((root / "generation_config.json").read_text())
        require(generation["unit_id_capacity"] == capacity, "Wrong capacity manifest")
        require(
            generation["seed"]["requested"] == "auto", "Auto seed must actually execute"
        )
        with (root / "scenario_table.csv").open(encoding="utf-8", newline="") as handle:
            raw_rows = list(csv.DictReader(handle))
        rows = {(row["rlz"], row["st_id"]): row for row in raw_rows}
        require(len(rows) == len(raw_rows) == 14, "Expected 14 unique scenario members")
        require(
            all(row["evaluated"] == "true" for row in raw_rows), "Unevaluated member"
        )
        require(
            all(len(row["run_id"]) == len(str(capacity)) for row in raw_rows),
            "Incorrect namespace width",
        )
        forcing = {item["run_id"]: root / item["path"] for item in manifest["forcing"]}
        require(
            set(forcing) == {row["run_id"] for row in raw_rows},
            "Forcing coverage mismatch",
        )
        scientific = copy.deepcopy(generation)
        scientific.pop("unit_id_capacity")
        if baseline is None:
            baseline, base_rows, base_forcing = scientific, rows, forcing
        require(scientific == baseline, "Seed or scientific generation settings drift")
        require(set(rows) == set(base_rows), "Scenario crosswalk coverage drift")
        comparisons = []
        for key, row in rows.items():
            base_run = base_rows[key]["run_id"]
            current_run = row["run_id"]
            before, after = base_forcing[base_run], forcing[current_run]
            with xr.open_dataset(before) as left, xr.open_dataset(after) as right:
                xr.testing.assert_identical(left, right)
                if not comparisons:
                    changed = right.load().copy(deep=True)
                    changed["precip"] = changed["precip"] + 1.0
                    try:
                        xr.testing.assert_identical(left, changed)
                    except AssertionError:
                        pass
                    else:
                        raise ValueError(
                            "Forcing comparison failed positive perturbation"
                        )
            comparisons.append(
                {
                    "rlz": key[0],
                    "st_id": key[1],
                    "base_run": base_run,
                    "run_id": current_run,
                    "arrays_attributes_exact": True,
                    "sha256": digest(after),
                    "base_sha256": digest(before),
                }
            )
        identities.add(manifest["collection_id"])
        reports.append(
            {
                "capacity": capacity,
                "width": len(str(capacity)),
                "manifest": str(marker),
                "manifest_sha256": digest(marker),
                "collection_id": manifest["collection_id"],
                "collection_revision": manifest["collection_revision"],
                "resolved_seed": generation["seed"]["resolved"],
                "seed_resolution": generation["seed_resolution"],
                "forcing": comparisons,
            }
        )
    require(
        len(identities) == 3, "Capacity changes must create three collection namespaces"
    )
    result = {
        "status": "passed_pending_named_review",
        "comparator_sha256": digest(Path(__file__)),
        "variants": reports,
        "positive_perturbation_rejected": True,
        "scope": "Actual auto-seed capacity/width generation only; no simulation or GF15",
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return {"status": result["status"], "report": str(report)}


def main() -> None:
    """Dispatch staging or explicit-manifest comparison."""
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    staging = modes.add_parser("stage")
    staging.add_argument("--config", type=Path, required=True)
    staging.add_argument("--work", type=Path, required=True)
    checking = modes.add_parser("compare")
    for capacity in (21, 22, 100):
        checking.add_argument(f"--capacity-{capacity}", type=Path, required=True)
    checking.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "stage":
        result = stage(args.config, args.work)
    else:
        result = compare(
            [getattr(args, f"capacity_{c}") for c in (21, 22, 100)], args.report
        )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
