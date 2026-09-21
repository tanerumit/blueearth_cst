"""Exact scenario-request selection and source freshness without collection discovery."""

import os
import tempfile
from pathlib import Path

from blueearth_cst.experiment.content_identity import (
    canonical_json_bytes,
    collection_id,
    content_sha256,
    identity_segment,
    read_canonical_json,
)
from blueearth_cst.experiment.scenario_collection import (
    ScenarioCollectionNotReady,
    read_collection,
    reuse_collection,
)
from blueearth_cst.shared.provenance import file_sha256
from blueearth_cst.shared.snake_utils import log_row, plural


class GeneratedCollectionUnavailable(ValueError):
    """The exact project request has no completed plan or ready collection."""


class GeneratedCollectionStale(ValueError):
    """The project request, live inputs, or selected immutable state changed."""


def scenario_request(project_dir, request, intent, source_inventory, documents=None):
    """Build rebuildable scheduling state after source preparation has completed."""
    if collection_id(intent) != intent["collection_id"]:
        raise ValueError("collection intent identity mismatch")
    if content_sha256(source_inventory) != intent["source_inventory"]["sha256"]:
        raise ValueError("source inventory identity mismatch")
    request_id = content_sha256(request)
    root = Path(project_dir).resolve()
    manifest_path = (
        root
        / "scenarios"
        / "collections"
        / identity_segment(intent["collection_id"], "collection_id")
        / "collection.json"
    )
    plan = {
        "schema_version": "scenario-request/1",
        "generation_request_id": request_id,
        "request": request,
        "source_inventory": source_inventory,
        "source_inventory_sha256": content_sha256(source_inventory),
        "intent": intent,
        "intent_sha256": content_sha256(intent),
        "collection_id": intent["collection_id"],
        "manifest_path": manifest_path.as_posix(),
    }
    if documents is not None:
        for name, document in documents.items():
            if content_sha256(document) != intent[name]["sha256"]:
                raise ValueError(f"{name} document identity mismatch")
        plan["documents"] = documents
    plan["request_sha256"] = content_sha256(plan)
    return plan


def write_scenario_request(project_dir, plan):
    """Atomically replace planning state; never claim or write a collection."""
    root = Path(project_dir).resolve()
    request_id = content_sha256(plan["request"])
    expected = scenario_request(
        root,
        plan["request"],
        plan["intent"],
        plan["source_inventory"],
        plan.get("documents"),
    )
    if canonical_json_bytes(plan) != canonical_json_bytes(expected):
        raise ValueError("scenario request differs from its canonical inputs")
    target = (
        root
        / "scenarios"
        / "requests"
        / identity_segment(request_id, "generation_request_id")
        / "request.json"
    )
    if target.resolve() != target:
        raise ValueError("scenario request uses an aliased path")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(canonical_json_bytes(plan))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    spec = plan["intent"]["scenario_spec"]
    log_row(
        f"{target.parent.name}: "
        f"{plural(spec['n_realizations'], 'realization')} x {plural(spec['n_design_points'], 'design point')} "
        f"from {plural(len(plan['source_inventory']), 'source file')}",
        module="request",
    )
    return target


def verify_scenario_request(
    project_dir, request, *, live_sources, expected_intent, generation_command
):
    """Preflight the exact request on every invocation, including no-job reuse.

    The producer supplies the newly recomputed intent and complete resolved
    source mapping. A changed source refuses even if timestamps stayed unchanged.
    No missing source is treated as permission to use a different collection.
    """
    root = Path(project_dir).resolve()
    target = (
        root
        / "scenarios"
        / "requests"
        / identity_segment(content_sha256(request), "generation_request_id")
        / "request.json"
    )
    if not target.exists():
        raise GeneratedCollectionUnavailable(
            f"missing {target}; run {generation_command}"
        )
    try:
        if target.resolve() != target:
            raise ValueError("scenario request uses an aliased path")
        plan = read_canonical_json(target)
        expected = scenario_request(
            root,
            request,
            expected_intent,
            plan["source_inventory"],
            plan.get("documents"),
        )
        if canonical_json_bytes(plan) != canonical_json_bytes(expected):
            raise ValueError(
                f"request digest expected={expected['request_sha256']} "
                f"observed={plan.get('request_sha256')}"
            )
        inventory = plan["source_inventory"]
        if set(live_sources) != {entry["path"] for entry in inventory}:
            raise ValueError("live source paths differ from planned inventory")
        for entry in inventory:
            source = Path(live_sources[entry["path"]])
            observed = file_sha256(source)
            if (
                observed != entry["sha256"]
                or source.stat().st_size != entry["size_bytes"]
            ):
                raise ValueError(
                    f"source {source}: expected={entry['sha256']} observed={observed}"
                )
        return plan
    except (KeyError, TypeError, ValueError, OSError) as exc:
        raise GeneratedCollectionStale(
            f"{target}: {exc}; run {generation_command}"
        ) from exc


def resolve_project_collection(
    project_dir,
    request,
    *,
    live_sources,
    live_code,
    live_environment,
    expected_intent,
    generation_command,
    describe_forcing,
    describe_ancillary,
):
    """Resolve only a verified project's exact plan, with no scan or fallback."""
    plan = verify_scenario_request(
        project_dir,
        request,
        live_sources=live_sources,
        expected_intent=expected_intent,
        generation_command=generation_command,
    )
    path = Path(plan["manifest_path"])
    if path.parent.resolve() != path.parent:
        raise GeneratedCollectionStale(
            f"collection store uses an aliased path: {path}; run {generation_command}"
        )
    if not path.exists():
        raise GeneratedCollectionUnavailable(
            f"missing {path}; run {generation_command}"
        )
    try:
        manifest = reuse_collection(
            path,
            expected_intent,
            live_sources=live_sources,
            live_code=live_code,
            live_environment=live_environment,
            describe_forcing=describe_forcing,
            describe_ancillary=describe_ancillary,
        )
    except (ScenarioCollectionNotReady, ValueError, OSError) as exc:
        raise GeneratedCollectionStale(
            f"{path}: {exc}; run {generation_command}"
        ) from exc
    return _selection("project-generation", path, manifest), manifest


def resolve_explicit_collection(selector, *, describe_forcing, describe_ancillary):
    """Advanced reuse takes only a manifest path and requires no original sources."""
    if type(selector) is not dict or set(selector) != {"manifest_path"}:
        raise ValueError("scenario_collection accepts only manifest_path")
    path = Path(selector["manifest_path"])
    manifest = read_collection(
        path, describe_forcing=describe_forcing, describe_ancillary=describe_ancillary
    )
    return _selection("explicit-manifest", path, manifest), manifest


def _selection(mode, path, manifest):
    return {
        "resolution_mode": mode,
        "manifest_path": path.resolve().as_posix(),
        "collection_id": manifest["collection_id"],
        "collection_revision": manifest["collection_revision"],
    }


def discover_collections_v2(project_dir: Path) -> list[dict]:
    """List only checked v2 engine markers; ignore bare scenario data roots."""
    from blueearth_cst.experiment.scenario_collection_v2 import read_collection_v2

    engine = Path(project_dir).resolve() / "scenarios" / "_engine" / "collections"
    if not engine.exists():
        return []
    collections = []
    for directory in sorted(engine.iterdir()):
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError(f"aliased collection engine directory: {directory}")
        marker = directory / "collection.json"
        if marker.exists():
            collections.append(read_collection_v2(marker))
    return collections


def resolve_explicit_collection_v2(selector: dict) -> tuple[dict, dict]:
    """Resolve an advanced v2 manifest selector without predecessor readers."""
    from blueearth_cst.experiment.scenario_collection_v2 import read_collection_v2

    if type(selector) is not dict or set(selector) != {"manifest_path"}:
        raise ValueError("scenario_collection accepts only manifest_path")
    marker_path = Path(selector["manifest_path"])
    marker = read_collection_v2(marker_path)
    return (
        {
            "resolution_mode": "explicit-manifest",
            "manifest_path": marker_path.resolve().as_posix(),
            "collection_id": marker["collection_id"],
            "collection_revision": marker["collection_revision"],
        },
        marker,
    )
