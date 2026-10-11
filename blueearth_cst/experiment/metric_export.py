"""Stable CSV copies of the last successfully selected immutable metric set."""

import os
import re
import shutil
import uuid
from pathlib import Path

from blueearth_cst.experiment.content_identity import atomic_record, read_canonical_json
from blueearth_cst.experiment.metric_plan import (
    current_metric_request,
    read_metric_set,
    verify_metric_plan,
)
from blueearth_cst.experiment.simulation_record import read_simulation_intent_v2
from blueearth_cst.shared.indicator_tables import indicator_tables
from blueearth_cst.shared.snake_utils import (
    DEFAULT_WFLOW_OUTVARS,
    resolve_water_year_start,
)


def export_selected_metrics(root: Path, project: dict, settings: dict) -> None:
    """Resolve the successful runner's selection, including a no-op file target."""
    tokens = settings.get("metrics")
    if tokens is None:
        outvars = (project.get("model") or {}).get("outvars")
        if outvars is not None or settings["operation"] == "simulate-and-metrics":
            tokens = list(
                indicator_tables(DEFAULT_WFLOW_OUTVARS if outvars is None else outvars)
            )
        else:
            request = read_simulation_intent_v2(root)["documents"]["response_request"]
            tokens = [item["variable"] for item in request["variables"]]
    month = resolve_water_year_start(
        (project.get("climate") or {}).get("water_year_start")
    )
    request = current_metric_request(root, tokens, f"YS-{month.upper()}")
    plan = verify_metric_plan(root, request)
    export_metric_set(root, Path(plan["targets"]["manifest"]))


def export_metric_set(experiment_root: Path, manifest_path: Path) -> None:
    """Refresh the flat export while the caller holds project execution ownership.

    Validate and stage before replacing files, then publish tracking metadata last.
    Roll back ordinary I/O failures. Readers must wait for workflow completion:
    replacing several CSVs is not a single atomic filesystem operation.
    """
    root = Path(experiment_root).resolve()
    manifest = read_metric_set(root, manifest_path)
    destination = root / "results/metric_sets"
    tracking = root / "_engine/metric_sets/current.json"
    references = [
        manifest["group_members"],
        manifest["group_metadata"],
        *(table["file"] for table in manifest["tables"]),
    ]
    files = {Path(item["path"]).name: item["sha256"] for item in references}
    previous = {}
    if tracking.exists():
        record = read_canonical_json(tracking)
        if record.get("schema_version") != "metric-export/1":
            raise ValueError(f"unsupported metric export record: {tracking}")
        previous = record["files"]
        if not isinstance(previous, dict):
            raise ValueError(f"invalid metric export file inventory: {tracking}")
    names = set(previous) | set(files)
    for name in names:
        if not isinstance(name, str) or not re.fullmatch(
            r"(?:group_members|group_metadata|[a-z][a-z0-9_]*_(?:run|group)_indicators)\.csv",
            name,
        ):
            raise ValueError(f"invalid metric export filename: {name!r}")
    for path in (destination, tracking, *(destination / name for name in names)):
        if path.is_symlink() or path.resolve() != path:
            raise ValueError(f"metric export path is aliased: {path}")
    for name in names:
        path = destination / name
        if path.exists() and (name not in previous or not path.is_file()):
            raise ValueError(f"metric export would overwrite an unowned path: {path}")

    record = {
        "schema_version": "metric-export/1",
        "metric_set_id": manifest["metric_set_id"],
        "manifest": f"{manifest['engine_root']}/metrics.json",
        "files": files,
    }
    staging = tracking.parent / f".export-{uuid.uuid4().hex}"
    staging.mkdir()
    changed = []
    rollback_failed = False
    try:
        # Stage both the new set and rollback copies before changing the export.
        for item in references:
            shutil.copyfile(root / item["path"], staging / Path(item["path"]).name)
        for name in names:
            path = destination / name
            if path.exists():
                shutil.copyfile(path, staging / f"{name}.previous")
        try:
            for name in sorted(names):
                path = destination / name
                if name in files:
                    os.replace(staging / name, path)
                else:
                    path.unlink(missing_ok=True)
                changed.append(name)
            atomic_record(tracking, record, replace=True)
        except OSError:
            try:
                for name in reversed(changed):
                    backup = staging / f"{name}.previous"
                    path = destination / name
                    if backup.exists():
                        os.replace(backup, path)
                    else:
                        path.unlink(missing_ok=True)
            except OSError as exc:
                rollback_failed = True
                raise OSError(
                    f"metric export rollback failed; backups: {staging}"
                ) from exc
            raise
    finally:
        if not rollback_failed:
            for path in staging.iterdir():
                path.unlink()
            staging.rmdir()
