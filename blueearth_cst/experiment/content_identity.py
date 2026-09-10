"""Canonical bytes and identity projections for R12 durable collections.

Implements collection-canon/1 and the two equations in the accepted R12 design,
section 8.2. These helpers do not establish collection readiness: persisted
schema, inventory, ordering, and physical descriptors require collection
validation before publication or consumption.
"""

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from blueearth_cst.experiment.scenario_rows import ScenarioRow


def _check_json(value: Any) -> None:
    """Refuse implicit JSON conversions that would erase input distinctions."""
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise TypeError("canonical JSON object keys must be strings")
            _check_json(item)
    elif type(value) is list:
        for item in value:
            _check_json(item)
    elif value is not None and type(value) not in (str, bool, int, float):
        raise TypeError(f"unsupported canonical JSON type: {type(value).__name__}")


def canonical_json_bytes(value: Any) -> bytes:
    """Encode plain JSON using collection-canon/1, including its final LF.

    Paths must already be normalized by the caller. Arrays retain their order;
    finite floats use Python's JSON representation (including 1.0 and -0.0).
    Non-JSON types and nonfinite numbers raise rather than being coerced.
    """
    _check_json(value)
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def content_sha256(value: Any) -> str:
    """Hash collection-canon/1 bytes, without provenance type tags."""
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON keys before a decoder can discard their values."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate canonical JSON key: {key!r}")
        result[key] = value
    return result


def read_canonical_json(path: Path) -> Any:
    """Read a persisted canonical document, refusing ambiguous or altered bytes.

    This verifies encoding, not the document's application schema or digest.
    """
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    if raw != canonical_json_bytes(value):
        raise ValueError(f"{path}: expected collection-canon/1 bytes")
    return value


def confined_path(root: Path, relative: str) -> Path:
    """Resolve a canonical POSIX artifact path inside its collection root.

    Refuse ambiguous Windows spellings as well as lexical and symlink escapes.
    File existence is checked separately by inventory validation.
    """
    if (
        not isinstance(relative, str)
        or not relative
        or any(character in relative for character in ("\\", ":", "\x00"))
        or any(segment in ("", ".", "..") for segment in relative.split("/"))
    ):
        raise ValueError(f"expected a confined relative POSIX path, got {relative!r}")
    resolved_root = root.resolve()
    target = (resolved_root / relative).resolve()
    if not target.is_relative_to(resolved_root) or target == resolved_root:
        raise ValueError(
            f"path {relative!r} resolves outside collection {resolved_root}"
        )
    return target


def _digest(value: Any, field: str) -> str:
    """Require the complete, lowercase identity rather than a display handle."""
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError(f"{field}: expected lowercase SHA-256, got {value!r}")
    return value


def scenario_semantics_sha256(rows: Sequence[ScenarioRow]) -> str:
    """Hash ordered semantic rows, stripping only run_id as required by R12."""
    return content_sha256(
        [
            {key: value for key, value in row.as_record().items() if key != "run_id"}
            for row in rows
        ]
    )


def collection_id(intent: Mapping[str, Any]) -> str:
    """Recompute the generation identity from the persisted intent projection.

    Required identity fields raise on absence; the collection validator owns
    full scenario-spec consistency and referenced-document verification.
    """
    for field, expected in (
        ("schema_version", "scenario-collection/1"),
        ("canonicalization_id", "collection-canon/1"),
    ):
        if intent[field] != expected:
            raise ValueError(f"{field}: expected {expected!r}, got {intent[field]!r}")
    capacity = intent["unit_id_capacity"]
    if type(capacity) is not int or capacity < 1:
        raise ValueError(
            f"unit_id_capacity: expected positive integer, got {capacity!r}"
        )
    provider = intent["provider"]
    if not isinstance(provider["name"], str) or not provider["name"]:
        raise ValueError("provider.name: expected nonempty string")
    projection = {
        "schema_version": intent["schema_version"],
        "scenario_spec": intent["scenario_spec"],
        "scenario_semantics_sha256": _digest(
            intent["scenario_semantics_sha256"], "scenario_semantics_sha256"
        ),
        "provider_name_and_revision": {
            "name": provider["name"],
            "revision": _digest(provider["revision"], "provider.revision"),
        },
        "unit_id_capacity": capacity,
    }
    for field in (
        "generation_config",
        "source_inventory",
        "provider_code",
        "environment",
        "preparation_context",
    ):
        projection[f"{field}_sha256"] = _digest(intent[field]["sha256"], field)
    return content_sha256(projection)


def collection_revision(manifest: Mapping[str, Any]) -> str:
    """Hash the produced-byte inventory in its declared order, excluding itself.

    No sorting or normalization repairs a malformed inventory here; readiness
    validation must reject wrong ordering, missing entries, and descriptors.
    """
    return content_sha256(
        {
            "collection_id": _digest(manifest["collection_id"], "collection_id"),
            "intent_sha256": _digest(manifest["intent_sha256"], "intent_sha256"),
            "scenario_table_sha256": _digest(
                manifest["scenario_table"]["sha256"], "scenario_table.sha256"
            ),
            "scenario_type_artifact_inventory": manifest["scenario_type_artifacts"],
            "preparation_context_sha256": _digest(
                manifest["preparation_context"]["sha256"], "preparation_context.sha256"
            ),
            "ordered_forcing_inventory_with_descriptors": manifest["forcing"],
        }
    )
