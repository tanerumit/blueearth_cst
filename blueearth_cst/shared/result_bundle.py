"""Portable WF2 result bundles: explicit export and validated import.

A bundle is one ZIP holding a WF2 product, the exact retained configuration
snapshots that produced it, the basin polygon it was computed over, and a
manifest with every member's size and SHA-256. Source-machine paths survive
only as historical text; nothing in a bundle needs the source project, its
`_shared/` execution inputs, links, locks or `.snakemake/` state.

The working project keeps its one configuration home under `config/`. Bundles
carry snapshots; import never writes the destination's `config/`, spatial
foundation, invocation history or logs. Import supports reading and
interpreting results, not runner adoption: no future no-recompute behaviour
is implied.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from blueearth_cst.shared import product_record

SCHEMA_VERSION = "cst-result-bundle/1"
WORKFLOW = "analyze_projections"
MANIFEST = "manifest.json"
REGION_MEMBER = "dependencies/region.geojson"
# Files without which a WF2 product cannot be read or attributed.
REQUIRED = (
    "report.md",
    "summary/provenance.json",
    "summary/composition.csv",
    "_engine/analysis_record.json",
)
# Scientific settings whose difference changes what the results mean.
CONFIGURATION_FACTS = (
    "ensemble",
    "models",
    "scenarios",
    "members",
    "variables",
    "future_windows",
    "reference_window",
)
_TEXT_SUFFIXES = {".csv", ".json", ".log", ".md", ".tsv", ".txt", ".yml", ".yaml"}


class BundleError(ValueError):
    """A bundle cannot be written or published without a false claim."""


def _now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _payload(path: Path) -> list[Path]:
    """Every file below `path`, refusing links rather than following them."""
    files = []
    for item in sorted(path.rglob("*")):
        if item.is_symlink() or item.is_junction():
            raise BundleError(f"linked path cannot be exported: {item}")
        if item.is_file():
            files.append(item)
    return files


def _region_candidates(project: Path, product: Path) -> list[Path]:
    from blueearth_cst.shared.wf3_science import region_geojson_path

    imported = sorted((product / "_engine/imported").glob("*/" + REGION_MEMBER))
    return [Path(region_geojson_path(project)), *imported]


def _region(project: Path, product: Path, expected: str) -> Path:
    """The polygon the product was computed over, by WKB fingerprint."""
    from blueearth_cst.projections.series_identity import region_fingerprint

    for path in _region_candidates(project, product):
        if path.is_file() and region_fingerprint(path) == expected:
            return path
    raise BundleError(
        "no region.geojson matches summary/provenance.json's region fingerprint; "
        "the product no longer describes the project's current basin polygon"
    )


def _snapshots(project: Path) -> list[Path]:
    root = project / "config/_engine/configuration-snapshots" / WORKFLOW
    if not root.is_dir():
        return []
    return [
        item
        for item in sorted(root.iterdir())
        if item.is_dir() and not item.name.startswith(".")
    ]


def _snapshot_by_digest(project: Path, provenance: Mapping[str, Any]) -> Path:
    """The retained snapshot whose configuration digests produced provenance."""
    from blueearth_cst.shared.workflow_config_snapshot import validate_archive

    wanted = (
        provenance.get("effective_config_sha256"),
        provenance.get("configuration_inputs_sha256"),
    )
    for directory in _snapshots(project):
        projection = validate_archive(directory)["configuration_projection"]
        if (
            projection["effective_config_sha256"],
            projection["configuration_inputs_sha256"],
        ) == wanted:
            return directory
    raise BundleError(
        "no retained configuration snapshot matches summary/provenance.json's "
        "configuration digests; the producing configuration cannot be bundled"
    )


def _snapshot_of(project: Path, generation: Mapping[str, Any]) -> Path:
    from blueearth_cst.shared.provenance import file_sha256

    reference = generation["configuration"]["run_record"]
    if not reference:
        raise BundleError("a producing generation has no configuration reference")
    path = project / reference["path"]
    if not path.is_file() or file_sha256(path) != reference["sha256"]:
        raise BundleError(f"configuration snapshot unavailable: {reference['path']}")
    return path.parent


def _snapshot_files(directory: Path) -> list[str]:
    from blueearth_cst.shared.configuration_archive import _archive_files
    from blueearth_cst.shared.workflow_config_snapshot import validate_archive

    return _archive_files(directory, validate_archive(directory))


def _verified_attribution(
    product: Path, record: Mapping[str, Any] | None, names: list[str]
) -> tuple[dict[str, str | None], dict[str, Any]]:
    """Trust a record's credit only where current bytes still match it."""
    current = product_record.inventory(product)
    if record is None:
        producers = {name: None for name in current}
        summary = {"mode": "legacy-unattributed", "state": "unrecorded"}
    else:
        if record["state"] != "complete":
            raise BundleError(
                "the product is incomplete: its latest changing run failed; rerun WF2 "
                "until it succeeds before exporting"
            )
        producers = {}
        for name, state in current.items():
            entry = record["files"].get(name, {})
            matches = entry.get("sha256") == state["sha256"]
            producers[name] = entry.get("producer") if matches else None
        summary = {
            "mode": "production-record",
            "state": record["state"],
            "missing_recorded_files": sorted(set(record["files"]) - set(current)),
        }
    summary["unattributed_files"] = sum(value is None for value in producers.values())
    missing = [name for name in REQUIRED if name not in names]
    if missing:
        raise BundleError(f"product lacks required files: {', '.join(missing)}")
    return producers, summary


def _compatibility(
    product: Path, provenance: Mapping[str, Any], configuration: Mapping[str, Any]
) -> dict[str, Any]:
    analysis = json.loads(
        (product / "_engine/analysis_record.json").read_text(encoding="utf-8")
    )
    section = configuration["loaded_config"]["workflows"][WORKFLOW]
    return {
        "region_fingerprint": provenance["region_fingerprint"],
        "variable_spec": provenance.get("variable_spec"),
        "water_year_start": analysis.get("water_year_start"),
        "reference_window": provenance.get("reference_window"),
        "horizon_windows": provenance.get("horizon_windows"),
        "windows": analysis.get("windows"),
        "composition": provenance.get("composition"),
        "series": [
            {
                key: source.get(key)
                for key in ("series_key", "catalog_entry", "members", "series_digest")
            }
            for source in provenance.get("sources", [])
        ],
        "methods": {
            "provenance_schema_version": provenance.get("schema_version"),
            "analysis_record_schema_version": analysis.get("schema_version"),
            "reducer_module_hash": provenance.get("reducer_module_hash"),
            "weighting_scheme": provenance.get("weighting_scheme"),
            "catalog_crawled_on": provenance.get("catalog_crawled_on"),
        },
        "configuration": {key: section.get(key) for key in CONFIGURATION_FACTS},
    }


def _historical_references(members: Mapping[str, Path], project: Path) -> list[str]:
    """Text payloads naming the source project: history, never dependencies."""
    needles = {str(project), project.as_posix()}
    found = []
    for name, path in members.items():
        if path.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(needle in text for needle in needles):
            found.append(name)
    return found


def export_bundle(
    project_root: Path, output: Path, *, ensemble: str | None = None
) -> dict[str, Any]:
    """Write one verified WF2 bundle; refuse rather than omit or overclaim."""
    from blueearth_cst.shared.provenance import toolbox_identity
    from blueearth_cst.shared.workflow_config_snapshot import (
        archive_lock,
        validate_archive,
    )

    project = Path(project_root).resolve(strict=True)
    output = Path(output).resolve()
    if output.exists():
        raise BundleError(f"bundle already exists: {output}")
    with archive_lock(project, "project-execution"):
        if ensemble:
            product = project / "data/climate/projections" / _safe_member(ensemble)
        elif (project / "config" / WORKFLOW / "run_record.yml").is_file():
            product = product_record.product_root(project, WORKFLOW)
        else:
            raise BundleError(
                "no captured WF2 configuration names the product; pass --ensemble"
            )
        if product is None or not product.is_dir():
            raise BundleError(f"no WF2 product at {product}")
        files = _payload(product)
        names = [path.relative_to(product).as_posix() for path in files]
        record = product_record.read_record(product)
        producers, attribution = _verified_attribution(product, record, names)
        provenance = json.loads(
            (product / "summary/provenance.json").read_text(encoding="utf-8")
        )
        region = _region(project, product, provenance["region_fingerprint"])
        primary = _snapshot_by_digest(project, provenance)
        directories = {primary}
        if record is not None:
            owners = {value for value in producers.values() if value is not None}
            directories |= {
                _snapshot_of(project, record["generations"][owner]) for owner in owners
            }
        members: dict[str, Path] = {
            f"product/{product.name}/{name}": path for name, path in zip(names, files)
        }
        snapshots = []
        for directory in sorted(directories):
            archive = validate_archive(directory)
            projection = archive["configuration_projection"]
            for name in _snapshot_files(directory):
                members[f"configuration/{directory.name}/{name}"] = directory / name
            snapshots.append(
                {
                    "path": f"configuration/{directory.name}",
                    "effective_config_sha256": projection["effective_config_sha256"],
                    "configuration_inputs_sha256": projection[
                        "configuration_inputs_sha256"
                    ],
                }
            )
        members[REGION_MEMBER] = region
        inventory = []
        for name, path in sorted(members.items()):
            data = path.read_bytes()
            entry = {
                "path": name,
                "sha256": _sha256_bytes(data),
                "size_bytes": len(data),
            }
            relative = name.removeprefix(f"product/{product.name}/")
            if relative in producers:
                entry["producer"] = producers[relative]
            inventory.append(entry)
        bundle_id = _sha256_bytes(
            "\n".join(f"{item['path']} {item['sha256']}" for item in inventory).encode()
        )
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "bundle_id": bundle_id,
            "workflow": WORKFLOW,
            "product": {
                "name": product.name,
                "path": f"product/{product.name}",
                "destination": product.relative_to(project).as_posix(),
            },
            "created_at_utc": _now(),
            "exported_by": toolbox_identity(),
            "source": {"project_root": str(project), "historical_only": True},
            "attribution": attribution,
            "configuration": {
                "provenance_snapshot": f"configuration/{primary.name}",
                "snapshots": snapshots,
            },
            "compatibility": _compatibility(
                product, provenance, validate_archive(primary)
            ),
            "dependencies": {
                "region": {
                    "path": REGION_MEMBER,
                    "fingerprint": provenance["region_fingerprint"],
                }
            },
            "historical_path_references": _historical_references(members, project),
            "files": inventory,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        handle, temporary = tempfile.mkstemp(
            prefix=f".{output.name}.", suffix=".tmp", dir=output.parent
        )
        os.close(handle)
        try:
            with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr(
                    MANIFEST, json.dumps(manifest, indent=2, sort_keys=True) + "\n"
                )
                for name, path in sorted(members.items()):
                    archive.write(path, name)
            os.replace(temporary, output)
        finally:
            Path(temporary).unlink(missing_ok=True)
    return {
        "bundle": str(output),
        "bundle_id": bundle_id,
        "product": manifest["product"]["destination"],
        "files": len(inventory),
        "size_bytes": output.stat().st_size,
        "attribution": attribution,
        "configuration_snapshots": [item["path"] for item in snapshots],
        "historical_path_references": manifest["historical_path_references"],
    }


def _safe_member(name: str) -> str:
    """Accept only relative POSIX member names that stay inside a root."""
    path = PurePosixPath(name)
    if (
        not name
        or "\\" in name
        or ":" in name
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in name.split("/"))
    ):
        raise BundleError(f"unsafe bundle member name: {name!r}")
    return name
