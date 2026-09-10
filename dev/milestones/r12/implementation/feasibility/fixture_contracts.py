"""Tiny synthetic identities for P0 mechanics, not production schemas or metrics."""

import hashlib
import json
from pathlib import Path
from typing import Any


def digest(value: Any) -> str:
    """Hash canonical synthetic JSON."""
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def read_json(path: str | Path) -> dict:
    """Read a synthetic JSON object."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def file_digest(path: str | Path) -> str:
    """Digest the actual input bytes."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path: str | Path, value: dict) -> None:
    """Atomically replace rebuildable planning state."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
    temporary.replace(path)


def preserve_json(path: str | Path, value: dict) -> None:
    """Keep a matching publication untouched; refuse an existing mismatch."""
    path = Path(path)
    if path.exists():
        if read_json(path) != value:
            raise ValueError(f"ImmutablePublicationMismatch: {path}")
        print(f"P0_REUSED {path}", flush=True)
    else:
        write_json(path, value)


def validate_inventory() -> dict:
    """Require the selected retained artifact and response variable."""
    inventory_path = Path("retained/inventory.json")
    if not inventory_path.is_file():
        raise ValueError("MissingResponseRequirement: retained/inventory.json")
    inventory = read_json(inventory_path)
    if "q" not in inventory["variables"]:
        raise ValueError("MissingResponseRequirement: q")
    artifact = Path(inventory["artifact"])
    if not artifact.is_file():
        raise ValueError(f"MissingResponseRequirement: {artifact}")
    if file_digest(artifact) != inventory["sha256"]:
        raise ValueError(f"StaleResponseArtifact: {artifact}")
    return inventory


def metric_plan() -> dict:
    """Resolve the final id from existing response bytes, never filenames alone."""
    inventory = validate_inventory()
    metric_id = digest({"response": inventory, "declaration": "synthetic-q-v1"})
    return {
        "request": "synthetic-q-v1",
        "id": metric_id,
        "target": f"metrics/{metric_id}/metrics.json",
        "response": inventory,
    }


def verify_metric_plan() -> None:
    """Reject a stale plan even when the DAG would otherwise have no jobs."""
    path = Path("planning/metric.json")
    if path.exists():
        plan = read_json(path)
        if plan != metric_plan():
            raise ValueError(f"StaleMetricPlan: {path}; remove the plan and rebuild")
        ready = Path(plan["target"])
        if ready.exists() and read_json(ready) != metric_publication(plan):
            raise ValueError(f"ImmutablePublicationMismatch: {ready}")


def metric_publication(plan: dict) -> dict:
    """Build the synthetic terminal payload from verified response bytes."""
    artifact = plan["response"]["artifact"]
    return {
        "id": plan["id"],
        "response_sha256": file_digest(artifact),
        "fixture_value": Path(artifact).read_text(encoding="utf-8"),
    }


def source_plan() -> dict:
    """Resolve the synthetic collection from raw and prepared source bytes."""
    sources = {
        name: file_digest(name) for name in ("raw/source.txt", "prepared/source.txt")
    }
    collection_id = digest({"sources": sources, "request": "synthetic-source-v1"})
    return {
        "request": "synthetic-source-v1",
        "id": collection_id,
        "sources": sources,
        "target": f"collections/{collection_id}/manifest.json",
    }
