"""Immutable stochastic collections with adapter-backed physical validation.

This is P2 storage infrastructure, not a production provider binding. Required
descriptor readers extract observations from confined files; no default reader
can turn checksum-only validation into readiness. Consumers use persisted inputs
only. Producer reuse separately verifies live source, code and environment inputs.
"""

import csv
import math
import os
import re
import shutil
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from blueearth_cst.experiment.content_identity import (
    canonical_json_bytes,
    collection_id,
    collection_revision,
    confined_path,
    content_sha256,
    read_canonical_json,
    scenario_semantics_sha256,
)
from blueearth_cst.experiment.scenario_rows import ScenarioRow, validate_stochastic
from blueearth_cst.shared.interchange_contracts import validate_wg2
from blueearth_cst.shared.provenance import file_sha256

ForcingReader = Callable[[Path, dict[str, Any]], dict[str, Any]]
AncillaryReader = Callable[[Path], dict[str, Any]]

_DOCUMENT_PATHS = {
    "generation_config": "generation_config.json",
    "source_inventory": "source_inventory.json",
    "provider_code": "provider_code_inventory.json",
    "environment": "generation_environment.json",
    "preparation_context": "preparation_context.json",
}


class ScenarioCollectionNotReady(ValueError):
    """Persisted collection state cannot establish complete readiness."""


class ImmutableCollectionError(ValueError):
    """An existing collection cannot be overwritten, resumed or silently repaired."""


@dataclass(frozen=True)
class CollectionClaim:
    """Writer handle returned after exclusive directory initialization.

    Workflow jobs may reconstruct it only through a verified receipt belonging
    to the same initialization invocation. A later invocation cannot resume a
    partial collection; the owner must explicitly delete it before starting again.
    """

    root: Path
    intent_sha256: str


def _fields(
    value: Any, required: set[str], field: str, *, optional: set[str] = frozenset()
) -> None:
    """Require explicit record shape rather than discard misspelled fields."""
    if type(value) is not dict:
        raise ValueError(f"{field}: expected object; observed {type(value).__name__}")
    if not required <= value.keys() or value.keys() - required - optional:
        raise ValueError(
            f"{field}: expected keys {sorted(required)}, optional {sorted(optional)}; observed {sorted(value)}"
        )


def _equal(field: str, expected: Any, observed: Any) -> None:
    """Use canonical comparison so a boolean cannot alias an integer."""
    if canonical_json_bytes(expected) != canonical_json_bytes(observed):
        raise ValueError(f"{field}: expected {expected!r}; observed {observed!r}")


def _integer(value: Any, field: str, minimum: int = 1) -> None:
    """Check stored counts without accepting coercions or boolean aliases."""
    if type(value) is not int or value < minimum:
        raise ValueError(f"{field}: expected integer >= {minimum}; observed {value!r}")


def _text(value: Any, field: str) -> None:
    """Require a nonempty string for an explicit descriptor or identifier."""
    if type(value) is not str or not value:
        raise ValueError(f"{field}: expected nonempty string; observed {value!r}")


def _sha256(value: Any, field: str) -> None:
    """Require a full lowercase content digest."""
    if type(value) is not str or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError(f"{field}: expected lowercase SHA-256; observed {value!r}")


def _intent(intent: dict[str, Any]) -> None:
    """Validate the currently bound stochastic intent and configured domain."""
    _fields(
        intent,
        {
            "schema_version",
            "canonicalization_id",
            "collection_id",
            "scenario_type",
            "provider",
            "generation_config",
            "scenario_spec",
            "source_inventory",
            "provider_code",
            "environment",
            "preparation_context",
            "scenario_semantics_sha256",
            "unit_id_capacity",
            "unit_id_width",
            "run_count",
        },
        "intent",
    )
    _fields(intent["provider"], {"name", "revision"}, "provider")
    _equal("collection_id", collection_id(intent), intent["collection_id"])
    _equal("scenario_type", "stochastic", intent["scenario_type"])
    spec = intent["scenario_spec"]
    _fields(
        spec,
        {
            "scenario_type",
            "n_realizations",
            "n_design_points",
            "unperturbed_per_realization",
            "expected_run_count",
            "simulation_window",
            "pairing",
            "row_order",
        },
        "scenario_spec",
    )
    for field in (
        "n_realizations",
        "n_design_points",
        "unperturbed_per_realization",
        "expected_run_count",
    ):
        _integer(spec[field], f"scenario_spec.{field}")
    for field in ("unit_id_capacity", "unit_id_width", "run_count"):
        _integer(intent[field], field)
    _equal(
        "scenario_spec.scenario_type", intent["scenario_type"], spec["scenario_type"]
    )
    _equal("unperturbed_per_realization", 1, spec["unperturbed_per_realization"])
    _equal("pairing", "paired_across_design_points", spec["pairing"])
    _equal(
        "row_order", "rlz-major/unperturbed-first/st-id-ascending", spec["row_order"]
    )
    _equal(
        "expected_run_count",
        spec["n_realizations"] * (spec["n_design_points"] + 1),
        spec["expected_run_count"],
    )
    _equal("run_count", spec["expected_run_count"], intent["run_count"])
    _equal(
        "unit_id_width", len(str(intent["unit_id_capacity"])), intent["unit_id_width"]
    )
    if intent["run_count"] > intent["unit_id_capacity"]:
        raise ValueError(
            "unit_id_capacity: expected >= run_count; observed insufficient capacity"
        )
    window = spec["simulation_window"]
    _fields(window, {"start", "end"}, "simulation_window")
    for field in ("start", "end"):
        _integer(window[field], f"simulation_window.{field}")
    if window["end"] < window["start"]:
        raise ValueError(
            "simulation_window: expected end >= start; observed reversed years"
        )
    for field, relative in _DOCUMENT_PATHS.items():
        _fields(intent[field], {"path", "sha256"}, field)
        _equal(f"{field}.path", relative, intent[field]["path"])
        _sha256(intent[field]["sha256"], f"{field}.sha256")


def claim_collection(project_dir: Path, intent: dict[str, Any]) -> CollectionClaim:
    """Exclusively create a new collection, refusing both partial and ready roots.

    Ready reuse has a separate read-only API. Failed initialization leaves the
    claimed directory in place so a later producer cannot resume it implicitly.
    """
    _intent(intent)
    parent = (project_dir / "scenario_collections").resolve()
    parent.mkdir(parents=True, exist_ok=True)
    root = parent / intent["collection_id"]
    try:
        root.mkdir()
    except FileExistsError as exc:
        state = (
            "ready; use reuse_collection"
            if (root / "collection.json").exists()
            else "partial; explicit owner deletion is required"
        )
        raise ImmutableCollectionError(f"collection {root}: existing {state}") from exc
    raw = canonical_json_bytes(intent)
    with (root / "collection_intent.json").open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    return CollectionClaim(root, content_sha256(intent))


def _check_claim(claim: CollectionClaim) -> None:
    """Keep the handle bound to its original immutable intent and real directory."""
    if claim.root.is_symlink() or claim.root.resolve() != claim.root:
        raise ImmutableCollectionError(f"collection {claim.root}: claim root changed")
    intent_path = claim.root / "collection_intent.json"
    marker = claim.root / "collection.json"
    if intent_path.is_symlink() or marker.is_symlink():
        raise ImmutableCollectionError(
            f"collection {claim.root}: aliased control record"
        )
    observed = file_sha256(confined_path(claim.root, "collection_intent.json"))
    if observed != claim.intent_sha256:
        raise ImmutableCollectionError(
            f"collection {claim.root}: intent expected {claim.intent_sha256}; observed {observed}"
        )


def write_collection_payload(
    claim: CollectionClaim, relative: str, source: bytes | Path
) -> None:
    """Copy a new payload without replacing existing bytes or following sources twice.

    A failed copy deliberately remains partial. Only publish_collection may write
    the ready marker, after validating the complete inventory.
    """
    _check_claim(claim)
    if not isinstance(source, (bytes, Path)):
        raise TypeError("source must be bytes or Path")
    target = confined_path(claim.root, relative)
    reserved = {
        (claim.root / name).resolve()
        for name in ("collection.json", "collection_intent.json")
    }
    if (claim.root / "collection.json").exists() or target in reserved:
        raise ImmutableCollectionError(
            f"collection {claim.root}: reserved or ready payload {relative!r}"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open("xb") as destination:
            if isinstance(source, Path):
                with source.open("rb") as origin:
                    shutil.copyfileobj(origin, destination)
            elif isinstance(source, bytes):
                destination.write(source)
            destination.flush()
            os.fsync(destination.fileno())
    except FileExistsError as exc:
        raise ImmutableCollectionError(
            f"collection {claim.root}: payload already exists: {relative}"
        ) from exc


def _artifact(root: Path, record: dict[str, Any], field: str) -> Path:
    """Verify confined file bytes and the optional authoritative size assertion."""
    target = confined_path(root, record["path"])
    _sha256(record["sha256"], f"{field}.sha256")
    if not target.is_file():
        raise ValueError(f"{field}: expected file {record['path']!r}; observed missing")
    if "size_bytes" in record:
        _integer(record["size_bytes"], f"{field}.size_bytes", 0)
        _equal(f"{field}.size_bytes", record["size_bytes"], target.stat().st_size)
    _equal(f"{field}.sha256", record["sha256"], file_sha256(target))
    return target


def _documents(root: Path, intent: dict[str, Any]) -> dict[str, Any]:
    """Reopen canonical identity inputs without touching original provider inputs."""
    docs = {}
    paths = []
    for field in (
        "generation_config",
        "source_inventory",
        "provider_code",
        "environment",
        "preparation_context",
    ):
        target = _artifact(root, intent[field], field)
        paths.append(target)
        docs[field] = read_canonical_json(target)
    if len(set(paths)) != len(paths):
        raise ValueError(
            "identity documents: expected distinct paths; observed aliases"
        )
    config = docs["generation_config"]
    if (
        type(config) is not dict
        or {"seed", "unit_id_capacity"} - config.keys()
        or {"compute", "console"} & config.keys()
    ):
        raise ValueError(
            "generation_config: expected scientific projection with seed/capacity and no compute/console"
        )
    _fields(config["seed"], {"requested", "resolved"}, "generation_config.seed")
    _integer(config["seed"]["resolved"], "seed.resolved", 0)
    _equal(
        "generation_config.unit_id_capacity",
        intent["unit_id_capacity"],
        config["unit_id_capacity"],
    )
    for field in ("source_inventory", "provider_code"):
        entries = docs[field]
        if type(entries) is not list or not entries:
            raise ValueError(
                f"{field}: expected nonempty inventory; observed {entries!r}"
            )
        keys = []
        for entry in entries:
            required = (
                {"path", "sha256"}
                if field == "provider_code"
                else {"role", "path", "sha256", "size_bytes", "metadata"}
            )
            _fields(entry, required, field)
            _text(entry["path"], f"{field}.path")
            _sha256(entry["sha256"], f"{field}.sha256")
            if field == "source_inventory":
                _text(entry["role"], "source.role")
                _integer(entry["size_bytes"], "source.size_bytes", 0)
                if type(entry["metadata"]) is not dict:
                    raise ValueError("source.metadata: expected object")
                keys.append((entry["role"], entry["path"]))
            else:
                confined_path(root, entry["path"])
                keys.append(entry["path"])
        if keys != sorted(set(keys)):
            raise ValueError(
                f"{field}: expected unique sorted entries; observed {keys}"
            )
    environment = docs["environment"]
    _fields(environment, {"packages", "locks"}, "environment")
    for field in ("packages", "locks"):
        if type(environment[field]) is not dict or not environment[field]:
            raise ValueError(f"environment.{field}: expected nonempty revisions object")
        for key, value in environment[field].items():
            _text(key, f"environment.{field}.name")
            if field == "locks":
                _sha256(value, "environment.lock.sha256")
            else:
                _text(value, "environment.package.revision")
    return docs


class _UniqueLoader(yaml.SafeLoader):
    """Read persisted catalog mappings without silently discarding duplicates."""


def _yaml_mapping(loader: _UniqueLoader, node: yaml.MappingNode) -> dict:
    """Reject duplicate keys, including YAML merge aliases, before construction."""
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if not isinstance(key, str) or key in result:
            raise ValueError(f"catalog: expected unique string key; observed {key!r}")
        result[key] = loader.construct_object(value_node, deep=True)
    return result


_UniqueLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _yaml_mapping
)


def _preparation(
    root: Path, context: dict[str, Any], describe_ancillary: AncillaryReader
) -> None:
    """Check packaged catalog closure and freshly extracted ancillary descriptors."""
    _fields(
        context,
        {
            "schema_version",
            "generated_forcing_reader",
            "pet_method",
            "forcing_elevation",
            "catalog",
            "ancillary",
        },
        "preparation_context",
        optional={"ancillary_absence_reason"},
    )
    _equal(
        "preparation schema_version", "forcing-preparation/1", context["schema_version"]
    )
    if context["pet_method"] not in {"debruin", "makkink"}:
        raise ValueError(
            f"pet_method: expected debruin or makkink; observed {context['pet_method']!r}"
        )
    reader = context["generated_forcing_reader"]
    _fields(
        reader,
        {"data_type", "driver", "metadata"},
        "generated_forcing_reader",
        optional={"data_adapter"},
    )
    _catalog_settings(reader, "generated_forcing_reader")
    _fields(context["catalog"], {"path", "sha256"}, "preparation catalog")
    _equal(
        "preparation catalog.path",
        "preparation_catalog.yml",
        context["catalog"]["path"],
    )
    catalog_path = _artifact(root, context["catalog"], "preparation catalog")
    catalog = yaml.load(catalog_path.read_text(encoding="utf-8"), Loader=_UniqueLoader)
    if type(catalog) is not dict:
        raise ValueError("preparation catalog: expected mapping")
    ancillary = context["ancillary"]
    if type(ancillary) is not list:
        raise ValueError("ancillary: expected explicit array")
    keys, ids, paths = [], {}, set()
    for entry in ancillary:
        _fields(
            entry,
            {"id", "role", "path", "sha256", "size_bytes", "descriptor"},
            "ancillary",
        )
        _text(entry["id"], "ancillary.id")
        _text(entry["role"], "ancillary.role")
        parts = entry["path"].split("/")
        if len(parts) != 3 or parts[:2] != ["ancillary", entry["id"]]:
            raise ValueError(
                f"ancillary.path: expected ancillary/<id>/<basename>; observed {entry['path']!r}"
            )
        target = _artifact(root, entry, f"ancillary {entry['id']}")
        if entry["id"] in ids or target in paths:
            raise ValueError("ancillary: expected unique ids and paths")
        ids[entry["id"]] = entry
        paths.add(target)
        keys.append((entry["role"], entry["id"]))
        if type(entry["descriptor"]) is not dict or not entry["descriptor"]:
            raise ValueError(
                "ancillary.descriptor: expected nonempty extracted descriptor"
            )
        _equal(
            f"ancillary {entry['id']}.descriptor",
            entry["descriptor"],
            describe_ancillary(target),
        )
    if keys != sorted(keys):
        raise ValueError("ancillary: expected role/id order")
    if not ancillary:
        _text(context.get("ancillary_absence_reason"), "ancillary_absence_reason")
        _equal(
            "forcing_elevation without ancillary", None, context["forcing_elevation"]
        )
    else:
        elevation = context["forcing_elevation"]
        _fields(elevation, {"catalog_key", "artifact_id"}, "forcing_elevation")
        if (
            elevation["artifact_id"] not in ids
            or elevation["catalog_key"] not in catalog
        ):
            raise ValueError(
                "forcing_elevation: expected inventoried artifact and catalog key"
            )
        _equal(
            "forcing_elevation.uri",
            ids[elevation["artifact_id"]]["path"],
            catalog[elevation["catalog_key"]]["uri"],
        )
    catalog_targets = set()
    for key, entry in catalog.items():
        _fields(
            entry,
            {"data_type", "uri", "driver"},
            f"catalog.{key}",
            optional={"metadata", "data_adapter"},
        )
        target = confined_path(root, entry["uri"])
        if target not in paths:
            raise ValueError(
                f"catalog.{key}.uri: expected inventoried ancillary; observed {entry['uri']!r}"
            )
        catalog_targets.add(target)
        _catalog_settings(entry, f"catalog.{key}")
    if catalog_targets != paths:
        raise ValueError("catalog: expected exact ancillary URI coverage")


def _catalog_settings(entry: dict[str, Any], field: str) -> None:
    """Check the existing preparation binding's executable catalog field subset.

    Current generated, ERA5, E-OBS and CHIRPS elevation readers use raster_xarray
    with chunks, lock and optional dimension preprocessing. Unknown executable
    options refuse until their preparation closure is explicitly supported.
    Descriptive metadata is retained verbatim and never treated as an I/O plan.
    """
    _equal(f"{field}.data_type", "RasterDataset", entry["data_type"])
    if "metadata" in entry and type(entry["metadata"]) is not dict:
        raise ValueError(f"{field}.metadata: expected object")
    driver = entry["driver"]
    if isinstance(driver, str):
        name, options = driver, {}
    else:
        _fields(driver, {"name"}, f"{field}.driver", optional={"options"})
        name, options = driver["name"], driver.get("options", {})
    _equal(f"{field}.driver.name", "raster_xarray", name)
    _fields(
        options,
        set(),
        f"{field}.driver.options",
        optional={"chunks", "lock", "preprocess"},
    )
    if "lock" in options and type(options["lock"]) is not bool:
        raise ValueError(f"{field}.driver.options.lock: expected boolean")
    if "preprocess" in options and options["preprocess"] not in {
        "harmonise_dims",
        "round_latlon",
    }:
        raise ValueError(
            f"{field}.driver.options.preprocess: expected supported dimension preprocessor"
        )
    if "chunks" in options:
        chunks = options["chunks"]
        if type(chunks) is not dict:
            raise ValueError(
                f"{field}.driver.options.chunks: expected dimension mapping"
            )
        for dimension, size in chunks.items():
            _text(dimension, "chunks.dimension")
            _integer(size, "chunks.size")
    if "data_adapter" in entry:
        adapter = entry["data_adapter"]
        _fields(
            adapter,
            set(),
            f"{field}.data_adapter",
            optional={"rename", "unit_mult", "unit_add"},
        )
        for operation, values in adapter.items():
            if type(values) is not dict:
                raise ValueError(
                    f"{field}.data_adapter.{operation}: expected variable mapping"
                )
            for variable, value in values.items():
                _text(variable, "data_adapter.variable")
                if operation == "rename":
                    _text(value, "data_adapter.rename")
                elif type(value) not in {int, float} or not math.isfinite(value):
                    raise ValueError(
                        f"{field}.data_adapter.{operation}: expected finite number"
                    )


def _csv_records(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Read exact textual cells without pandas header mangling or ID coercion."""
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, strict=True)
        header = next(reader, [])
        if not header or len(header) != len(set(header)):
            raise ValueError(
                f"{path.name}: expected unique nonempty header; observed {header}"
            )
        records = []
        for cells in reader:
            if len(cells) != len(header):
                raise ValueError(
                    f"{path.name}: expected {len(header)} cells; observed {len(cells)}"
                )
            records.append(dict(zip(header, cells, strict=True)))
    return header, records


def _forcing_descriptor(record: dict[str, Any]) -> None:
    """Require the version-one forcing descriptor before comparing extraction."""
    _fields(
        record,
        {
            "source_calendar",
            "timestep",
            "time_label",
            "start",
            "end",
            "spatial_representation_sha256",
            "variables",
        },
        "forcing.descriptor",
    )
    for field in ("source_calendar", "timestep", "time_label", "start", "end"):
        _text(record[field], f"forcing.descriptor.{field}")
    _sha256(record["spatial_representation_sha256"], "spatial_representation_sha256")
    if type(record["variables"]) is not list or not record["variables"]:
        raise ValueError("forcing.variables: expected nonempty array")
    names = []
    for variable in record["variables"]:
        _fields(variable, {"name", "units", "missing_value"}, "forcing.variable")
        _text(variable["name"], "variable.name")
        _text(variable["units"], "variable.units")
        names.append(variable["name"])
    if names != sorted(set(names)):
        raise ValueError("forcing.variables: expected unique canonical-name order")


def _validate(
    root: Path,
    manifest: dict[str, Any],
    describe_forcing: ForcingReader,
    describe_ancillary: AncillaryReader,
) -> dict[str, Any]:
    """Check a candidate or published manifest against retained state."""
    try:
        _fields(
            manifest,
            {
                "schema_version",
                "status",
                "collection_id",
                "collection_revision",
                "intent_path",
                "intent_sha256",
                "scenario_table",
                "scenario_type_artifacts",
                "preparation_context",
                "forcing",
            },
            "collection",
        )
        _equal("schema_version", "scenario-collection/1", manifest["schema_version"])
        _equal("status", "ready", manifest["status"])
        intent_path = confined_path(root, manifest["intent_path"])
        intent = read_canonical_json(intent_path)
        _intent(intent)
        _equal("collection_id", intent["collection_id"], manifest["collection_id"])
        _equal("collection directory", manifest["collection_id"], root.name)
        _artifact(
            root,
            {"path": manifest["intent_path"], "sha256": manifest["intent_sha256"]},
            "intent",
        )
        _equal("intent_path", "collection_intent.json", manifest["intent_path"])
        docs = _documents(root, intent)
        _equal(
            "preparation_context",
            intent["preparation_context"],
            manifest["preparation_context"],
        )
        _fields(manifest["scenario_table"], {"path", "sha256"}, "scenario_table")
        _equal(
            "scenario_table.path",
            "scenario_table.csv",
            manifest["scenario_table"]["path"],
        )
        table_path = _artifact(root, manifest["scenario_table"], "scenario_table")
        header, records = _csv_records(table_path)
        _equal(
            "scenario_table.header",
            ["run_id", "derived_from", "evaluated", "scenario_type", "rlz", "st_id"],
            header,
        )
        rows = tuple(ScenarioRow.from_record(record) for record in records)
        validate_stochastic(
            rows,
            n_realizations=intent["scenario_spec"]["n_realizations"],
            st_num=intent["scenario_spec"]["n_design_points"],
            unit_id_capacity=intent["unit_id_capacity"],
        )
        _equal(
            "scenario_semantics_sha256",
            intent["scenario_semantics_sha256"],
            scenario_semantics_sha256(rows),
        )
        artifacts = manifest["scenario_type_artifacts"]
        if type(artifacts) is not list or len(artifacts) != 1:
            raise ValueError(
                "scenario_type_artifacts: expected exactly one stochastic perturbation lookup"
            )
        lookup = artifacts[0]
        _fields(lookup, {"role", "path", "sha256"}, "scenario_type_artifact")
        _equal("scenario_type_artifact.role", "perturbation_lookup", lookup["role"])
        _equal("perturbation_lookup.path", "stress_test_lookup.csv", lookup["path"])
        lookup_path = _artifact(root, lookup, "perturbation_lookup")
        _, lookup_records = _csv_records(lookup_path)
        diffs = validate_wg2(
            pd.DataFrame(lookup_records),
            st_num=intent["scenario_spec"]["n_design_points"],
        )
        if diffs:
            raise ValueError("perturbation_lookup: " + "; ".join(diffs))
        for record in lookup_records:
            for field in ("temp_change", "precip_change", "precip_variance_change"):
                if not math.isfinite(float(record[field])):
                    raise ValueError(
                        f"perturbation_lookup.{field}: expected finite number; observed {record[field]!r}"
                    )
        forcing = manifest["forcing"]
        if type(forcing) is not list:
            raise ValueError("forcing: expected inventory array")
        _equal(
            "forcing.run_id coverage/order",
            [row.run_id for row in rows],
            [entry["run_id"] for entry in forcing],
        )
        seen = set()
        for entry in forcing:
            _fields(
                entry,
                {"run_id", "path", "sha256", "size_bytes", "descriptor"},
                "forcing entry",
            )
            _equal(
                f"forcing {entry['run_id']}.path",
                f"forcing/run_{entry['run_id']}.nc",
                entry["path"],
            )
            target = _artifact(root, entry, f"forcing {entry['run_id']}")
            if target in seen:
                raise ValueError(
                    "forcing: expected distinct artifact paths; observed alias"
                )
            seen.add(target)
        _preparation(root, docs["preparation_context"], describe_ancillary)
        for entry in forcing:
            _forcing_descriptor(entry["descriptor"])
            observed = describe_forcing(
                confined_path(root, entry["path"]),
                docs["preparation_context"]["generated_forcing_reader"],
            )
            _equal(
                f"forcing {entry['run_id']}.descriptor", entry["descriptor"], observed
            )
        _equal(
            "collection_revision",
            collection_revision(manifest),
            manifest["collection_revision"],
        )
    except (OSError, ValueError, TypeError, KeyError, csv.Error, yaml.YAMLError) as exc:
        raise ScenarioCollectionNotReady(
            f"collection {root}: expected valid retained contract; observed {exc}"
        ) from exc
    return manifest


def read_collection(
    manifest_path: Path,
    *,
    describe_forcing: ForcingReader,
    describe_ancillary: AncillaryReader,
) -> dict[str, Any]:
    """Read and validate the sole ready marker without accessing live inputs."""
    try:
        if manifest_path.name != "collection.json":
            raise ValueError("expected collection.json as the sole ready marker")
        marker = confined_path(manifest_path.parent, manifest_path.name)
        manifest = read_canonical_json(marker)
    except (OSError, ValueError, TypeError) as exc:
        raise ScenarioCollectionNotReady(
            f"collection {manifest_path.parent}: expected ready marker; observed {exc}"
        ) from exc
    return _validate(
        manifest_path.parent, manifest, describe_forcing, describe_ancillary
    )


def publish_collection(
    claim: CollectionClaim,
    manifest: dict[str, Any],
    *,
    describe_forcing: ForcingReader,
    describe_ancillary: AncillaryReader,
) -> dict[str, Any]:
    """Validate all retained payloads and atomically write collection.json last.

    Repeated publication may only return the fully validated identical ready
    record. It never updates even the ready marker's modification time.
    """
    _check_claim(claim)
    marker = claim.root / "collection.json"
    if marker.exists():
        try:
            existing = read_collection(
                marker,
                describe_forcing=describe_forcing,
                describe_ancillary=describe_ancillary,
            )
            _equal("immutable ready manifest", existing, manifest)
        except ValueError as exc:
            raise ImmutableCollectionError(f"collection {claim.root}: {exc}") from exc
        return existing
    _validate(claim.root, manifest, describe_forcing, describe_ancillary)
    raw = canonical_json_bytes(manifest)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=".collection-",
            suffix=".tmp",
            dir=claim.root,
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, marker)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return manifest


def reuse_collection(
    manifest_path: Path,
    expected_intent: dict[str, Any],
    *,
    live_sources: Mapping[str, Path],
    live_code: Mapping[str, Path],
    live_environment: dict[str, Any],
    describe_forcing: ForcingReader,
    describe_ancillary: AncillaryReader,
) -> dict[str, Any]:
    """Verify ready state and live producer inputs without modifying any bytes.

    Mapping keys are persisted source locators and repository code paths. The
    source plan supplies their current resolved files and environment revisions.
    Consumer reads deliberately have no such live dependency.
    """
    root = manifest_path.parent
    try:
        manifest = read_collection(
            manifest_path,
            describe_forcing=describe_forcing,
            describe_ancillary=describe_ancillary,
        )
        intent = read_canonical_json(root / manifest["intent_path"])
        _equal("producer intent", intent, expected_intent)
        for field, supplied in (
            ("source_inventory", live_sources),
            ("provider_code", live_code),
        ):
            entries = read_canonical_json(confined_path(root, intent[field]["path"]))
            _equal(
                f"live {field}.keys",
                sorted({entry["path"] for entry in entries}),
                sorted(supplied),
            )
            for entry in entries:
                path = supplied[entry["path"]]
                _equal(
                    f"live {field} {entry['path']}.sha256",
                    entry["sha256"],
                    file_sha256(path),
                )
                if "size_bytes" in entry:
                    _equal(
                        f"live source {entry['path']}.size_bytes",
                        entry["size_bytes"],
                        path.stat().st_size,
                    )
        stored_environment = read_canonical_json(
            confined_path(root, intent["environment"]["path"])
        )
        _equal("live environment", stored_environment, live_environment)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise ImmutableCollectionError(
            f"collection {root}: producer reuse refused; {exc}"
        ) from exc
    return manifest


def collection_size(root: Path) -> tuple[int, int]:
    """Report every retained file and byte without a cap or automatic deletion."""
    count = total = 0
    for path in root.rglob("*"):
        confined_path(root, path.relative_to(root).as_posix())
        if path.is_file():
            count += 1
            total += path.stat().st_size
    return count, total


def _initialization_path(project, plan, invocation_id):
    if (
        not isinstance(invocation_id, str)
        or re.fullmatch(r"[0-9a-f]{32}", invocation_id) is None
    ):
        raise ImmutableCollectionError(
            "initializer requires the current invocation UUID"
        )
    _sha256(plan["generation_request_id"], "generation_request_id")
    expected = content_sha256(
        {key: value for key, value in plan.items() if key != "plan_sha256"}
    )
    if (
        expected != plan["plan_sha256"]
        or content_sha256(plan["request"]) != plan["generation_request_id"]
    ):
        raise ImmutableCollectionError("initialization source plan digest differs")
    relative = f"scenario_plans/{plan['generation_request_id']}/initializations/{invocation_id}.json"
    path = confined_path(project, relative)
    if path != project / relative:
        raise ImmutableCollectionError("initialization receipt path is aliased")
    return path


def _job_collection_claim(project_dir, plan, invocation_id):
    """Authorize only jobs of the current explicitly supplied initialization."""
    project = Path(project_dir).resolve()
    path = _initialization_path(project, plan, invocation_id)
    expected = {
        "invocation_id": invocation_id,
        "collection_id": plan["collection_id"],
        "intent_sha256": plan["intent_sha256"],
        "plan_sha256": plan["plan_sha256"],
    }
    try:
        _equal("initialization receipt", expected, read_canonical_json(path))
        _sha256(plan["collection_id"], "collection_id")
        root = confined_path(project, f"scenario_collections/{plan['collection_id']}")
        if root != project / "scenario_collections" / plan["collection_id"]:
            raise ValueError("collection writer path is aliased")
        _equal(
            "initialized intent",
            plan["intent"],
            read_canonical_json(confined_path(root, "collection_intent.json")),
        )
        _equal(
            "initialized intent digest",
            plan["intent_sha256"],
            file_sha256(confined_path(root, "collection_intent.json")),
        )
        return CollectionClaim(root, plan["intent_sha256"])
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise ImmutableCollectionError(
            f"current invocation has no valid collection initialization: {exc}"
        ) from exc


def initialize_collection_jobs(project_dir, plan, invocation_id, payloads):
    """Exclusively initialize the collection, then publish one invocation receipt.

    Receipts are scheduling state outside scientific identity. They authorize no
    later invocation, retry recovery, lease or ownership transfer. The parent
    launcher supplies a fresh ID and propagates that same ID to its child jobs.
    """
    from blueearth_cst.experiment.content_identity import atomic_record

    project = Path(project_dir).resolve()
    receipt = _initialization_path(project, plan, invocation_id)
    if receipt.exists():
        claim = _job_collection_claim(project, plan, invocation_id)
        if (claim.root / "collection.json").exists():
            raise ImmutableCollectionError(
                "ready reuse does not confer writer authorization"
            )
        return claim
    claim = claim_collection(project, plan["intent"])
    for name, payload in payloads.items():
        write_collection_payload(claim, name, payload)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    atomic_record(
        receipt,
        {
            "invocation_id": invocation_id,
            "collection_id": plan["collection_id"],
            "intent_sha256": plan["intent_sha256"],
            "plan_sha256": plan["plan_sha256"],
        },
    )
    return claim


def collection_references(project_dir: Path, selected_id: str) -> list[str]:
    """List every retained simulation reference, refusing unreadable records."""
    _sha256(selected_id, "collection_id")
    project = Path(project_dir).resolve()
    references = []
    for path in sorted((project / "experiments").glob("*/config/simulation.json")):
        if not path.resolve().is_relative_to(project):
            raise ImmutableCollectionError(f"simulation record escapes project: {path}")
        try:
            record = read_canonical_json(path)
            referenced = record["collection"]["collection_id"]
            _sha256(referenced, "simulation.collection_id")
        except (OSError, KeyError, TypeError, ValueError) as exc:
            raise ImmutableCollectionError(
                f"cannot establish references from {path}: {exc}"
            ) from exc
        if referenced == selected_id:
            references.append(path.relative_to(project).as_posix())
    return references


def list_collections(project_dir: Path) -> list[dict[str, Any]]:
    """Report all collection directories, retained bytes and simulation references.

    A marker's presence is reported without claiming validated readiness. This is
    the explicit inspection path; automatic collection selection never scans it.
    """
    project = Path(project_dir).resolve()
    store = project / "scenario_collections"
    if not store.exists():
        return []
    records = []
    for path in sorted(store.iterdir()):
        _sha256(path.name, "collection directory")
        if path.is_symlink() or not path.resolve().is_relative_to(project):
            raise ImmutableCollectionError(f"collection directory is an alias: {path}")
        if not path.is_dir():
            raise ImmutableCollectionError(f"unexpected collection store file: {path}")
        count, size = collection_size(path)
        records.append(
            {
                "collection_id": path.name,
                "path": path.as_posix(),
                "marker_present": (path / "collection.json").exists(),
                "file_count": count,
                "size_bytes": size,
                "simulation_references": collection_references(project, path.name),
            }
        )
    return records


def delete_collection(
    project_dir: Path, selected_id: str, *, force: bool = False
) -> dict[str, Any]:
    """Explicitly delete one named collection; retained references require force.

    Call only from an explicit deletion action. Normal generation, simulation
    and retention summaries never invoke this function. Return byte accounting.
    """
    _sha256(selected_id, "collection_id")
    if type(force) is not bool:
        raise TypeError("force must be an explicit boolean")
    project = Path(project_dir).resolve(strict=True)
    store = project / "scenario_collections"
    target = store / selected_id
    if store.is_symlink() or target.is_symlink() or target.resolve() != target:
        raise ImmutableCollectionError(
            f"refuse deletion through a collection alias: {target}"
        )
    if not target.resolve().is_relative_to(project) or target.parent != store:
        raise ImmutableCollectionError(f"collection deletion escapes project: {target}")
    references = collection_references(project, selected_id)
    if references and not force:
        raise ImmutableCollectionError(
            f"collection {selected_id} is referenced by {references}; explicit force required"
        )
    count, size = collection_size(target)
    shutil.rmtree(target)
    return {
        "collection_id": selected_id,
        "file_count": count,
        "size_bytes": size,
        "simulation_references": references,
    }
