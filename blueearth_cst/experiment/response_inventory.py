"""Complete retained native response coverage without a live model or generation."""

import os
import tomllib
from pathlib import Path

import pandas as pd

from blueearth_cst.experiment.content_identity import (
    content_sha256,
    read_canonical_json,
)
from blueearth_cst.experiment.simulation_record import (
    atomic_record,
    complete_simulation,
    read_simulation,
)
from blueearth_cst.experiment.wflow_response_reader import (
    NativeRunArtifacts,
    ResponseRequest,
    open_responses,
)
from blueearth_cst.shared.provenance import file_sha256


class MissingResponseRequirement(ValueError):
    """Retained native responses do not satisfy the frozen complete request."""


class ResponseReaderUnavailable(ValueError):
    """The native reader revision needed by retained state is not installed."""


def response_reader_revision():
    """Fingerprint the actual native reader and neutral validation implementation."""
    directory = Path(__file__).parent
    return content_sha256(
        [
            {"path": name, "sha256": file_sha256(directory / name)}
            for name in ("response_series.py", "wflow_response_reader.py")
        ]
    )


def make_response_request(run_ids, variables):
    """Freeze evaluated runs and model-declared ordered locations before execution.

    Each variable declaration supplies variable, locations, units, calendar,
    timestep, time_label, start, end and missing_value. Location order comes from
    the native simulator's output plan, never from completed CSV contents.
    """
    request = {
        "schema_version": "response-request/1",
        "reader": {"name": "wflow-csv", "revision": response_reader_revision()},
        "run_ids": list(run_ids),
        "variables": variables,
        "expected_series": [
            [run, item["variable"], location]
            for run in run_ids
            for item in variables
            for location in item["locations"]
        ],
    }
    validate_response_request(request)
    return request


def validate_response_request(request):
    """Require exact independently declared keys and complete physical metadata."""
    if (
        set(request)
        != {"schema_version", "reader", "run_ids", "variables", "expected_series"}
        or request["schema_version"] != "response-request/1"
    ):
        raise MissingResponseRequirement("invalid response-request/1 fields")
    runs = request["run_ids"]
    if (
        not runs
        or any(not isinstance(run, str) or not run.isdecimal() for run in runs)
        or runs != sorted(set(runs), key=int)
    ):
        raise MissingResponseRequirement(
            "response request requires unique numerically ordered run ids"
        )
    variables = request["variables"]
    if not variables:
        raise MissingResponseRequirement("response request has no variables")
    names = []
    for item in variables:
        if set(item) != {
            "variable",
            "locations",
            "units",
            "calendar",
            "timestep",
            "time_label",
            "start",
            "end",
            "missing_value",
        }:
            raise MissingResponseRequirement("response variable metadata is incomplete")
        names.append(item["variable"])
        locations = item["locations"]
        if (
            not locations
            or len(set(locations)) != len(locations)
            or any(not isinstance(value, str) or not value for value in locations)
        ):
            raise MissingResponseRequirement(
                "response locations must be unique ordered text"
            )
        if any(
            not isinstance(item[key], str) or not item[key]
            for key in (
                "variable",
                "units",
                "calendar",
                "timestep",
                "time_label",
                "start",
                "end",
            )
        ):
            raise MissingResponseRequirement(
                "response physical metadata must be explicit"
            )
    if len(set(names)) != len(names):
        raise MissingResponseRequirement("duplicate requested variables")
    expected = [
        [run, item["variable"], location]
        for run in runs
        for item in variables
        for location in item["locations"]
    ]
    if request["expected_series"] != expected:
        raise MissingResponseRequirement(
            "expected_series differs from frozen runs and locations"
        )


def _artifact_path(root, inventory_dir, relative):
    """Allow inventory-relative ../ paths while confining to the experiment."""
    if (
        not isinstance(relative, str)
        or "\\" in relative
        or ":" in relative
        or Path(relative).is_absolute()
    ):
        raise MissingResponseRequirement(f"invalid retained artifact path {relative!r}")
    from pathlib import PureWindowsPath

    if any(
        part not in {".", ".."}
        and (part.endswith((".", " ")) or PureWindowsPath(part).is_reserved())
        for part in relative.split("/")
    ):
        raise MissingResponseRequirement(
            f"nonportable retained artifact path {relative!r}"
        )
    path = (inventory_dir / relative).resolve()
    if not path.is_relative_to(root):
        raise MissingResponseRequirement(
            f"retained artifact escapes experiment: {relative}"
        )
    return path


def _relative(path, directory):
    return os.path.relpath(path, directory).replace("\\", "/")


def _validate_temporal(temporal, config):
    required = {
        "source_calendar",
        "prepared_forcing_calendar",
        "response_calendar",
        "operations",
        "prepared_start",
        "prepared_end",
        "response_start",
        "response_end",
        "time_label",
    }
    if set(temporal) != required:
        raise MissingResponseRequirement("temporal preparation evidence is incomplete")
    suffix = ["clip_to_configured_window", "refresh_toml_endpoints"]
    expected_operations = [suffix]
    if temporal["source_calendar"] == "noleap":
        expected_operations = [
            [conversion, *suffix]
            for conversion in ("cftime_to_datetime64", "hydromt_reader_to_datetime64")
        ]
    if (
        temporal["operations"] not in expected_operations
        or temporal["prepared_forcing_calendar"] != "proleptic_gregorian"
    ):
        raise MissingResponseRequirement("unsupported temporal preparation chain")
    clock = config["time"]
    if (
        pd.Timestamp(temporal["prepared_start"]) != pd.Timestamp(clock["starttime"])
        or pd.Timestamp(temporal["prepared_end"]) != pd.Timestamp(clock["endtime"])
        or temporal["response_calendar"] != clock["calendar"]
        or pd.Timestamp(temporal["response_start"])
        != pd.Timestamp(clock["starttime"])
        + pd.Timedelta(seconds=clock["timestepsecs"])
        or pd.Timestamp(temporal["response_end"]) != pd.Timestamp(clock["endtime"])
        or temporal["time_label"] != "interval_end"
    ):
        raise MissingResponseRequirement(
            "temporal preparation differs from native simulation clock"
        )


def build_response_inventory(experiment_root, native_runs, temporal_preparation):
    """Reopen every requested native series and derive a complete inventory.

    TOML reader dependencies are hashed inside adapter-private selectors. Native
    CSV artifacts are retained without normalized copies. All expected locations,
    ordering and metadata must match the prior immutable response request.
    """
    root = Path(experiment_root).resolve()
    directory = root / "responses"
    simulation = read_simulation(root)
    request = read_canonical_json(root / "config/response_request.json")
    validate_response_request(request)
    if request["reader"] != {
        "name": "wflow-csv",
        "revision": response_reader_revision(),
    }:
        raise ResponseReaderUnavailable(f"reader unavailable: {request['reader']}")
    if set(native_runs) != set(request["run_ids"]):
        raise MissingResponseRequirement(
            "native runs differ from frozen response request"
        )
    artifacts, series = [], []
    for run in request["run_ids"]:
        native = native_runs[run]
        if native.temporal_path is None:
            raise MissingResponseRequirement(
                f"run {run}: missing retained temporal preparation evidence"
            )
        for path in (native.csv_path, native.toml_path, native.temporal_path):
            if not Path(path).resolve().is_relative_to(root):
                raise MissingResponseRequirement(
                    f"native artifact escapes experiment: {path}"
                )
        csv_path, toml_path = Path(native.csv_path), Path(native.toml_path)
        temporal = read_canonical_json(Path(native.temporal_path))
        if temporal != temporal_preparation:
            raise MissingResponseRequirement(
                f"run {run}: inconsistent temporal preparation evidence"
            )
        with toml_path.open("rb") as handle:
            _validate_temporal(temporal, tomllib.load(handle))
        index = len(artifacts)
        artifacts.append(
            {
                "run_id": run,
                "path": _relative(csv_path, directory),
                "sha256": file_sha256(csv_path),
                "size_bytes": csv_path.stat().st_size,
            }
        )
        values = open_responses(
            run,
            native,
            ResponseRequest(tuple(item["variable"] for item in request["variables"])),
        )
        actual_keys = {item.key for item in values}
        expected_keys = {
            tuple(key) for key in request["expected_series"] if key[0] == run
        }
        if actual_keys != expected_keys:
            raise MissingResponseRequirement(
                f"run {run}: response keys missing={sorted(expected_keys - actual_keys)} extra={sorted(actual_keys - expected_keys)}"
            )
        metadata = {item["variable"]: item for item in request["variables"]}
        for item in values:
            declared = metadata[item.variable]
            seconds = item.timestep.total_seconds()
            observed = {
                "units": item.units,
                "calendar": item.calendar,
                "timestep": "P1D" if seconds == 86400 else f"PT{seconds:g}S",
                "time_label": item.time_label,
                "start": str(item.time[0]),
                "end": str(item.time[-1]),
                "missing_value": "NaN",
            }
            for key, value in observed.items():
                if declared[key] != value:
                    raise MissingResponseRequirement(
                        f"{item.key}: {key} expected={declared[key]} observed={value}"
                    )
            if declared["locations"][item.location_ordinal] != item.location_id:
                raise MissingResponseRequirement(
                    f"{item.key}: native location order differs from request"
                )
            from blueearth_cst.experiment.wflow_response_reader import NATIVE_VARIABLES

            selector = {
                "column": f"{NATIVE_VARIABLES[item.variable][0]}_{item.location_id}",
                "toml_path": _relative(toml_path, directory),
                "toml_sha256": file_sha256(toml_path),
                "temporal_path": _relative(native.temporal_path, directory),
                "temporal_sha256": file_sha256(native.temporal_path),
            }
            series.append(
                {
                    "run_id": run,
                    "variable": item.variable,
                    "location_id": item.location_id,
                    "location_ordinal": item.location_ordinal,
                    "artifact": index,
                    "native_selector": selector,
                    **observed,
                }
            )
    series.sort(
        key=lambda item: (
            int(item["run_id"]),
            item["variable"],
            item["location_ordinal"],
            item["location_id"],
        )
    )
    inventory = {
        "schema_version": "response-inventory/1",
        "simulation_id": simulation["simulation_id"],
        "collection_id": simulation["collection"]["collection_id"],
        "collection_revision": simulation["collection"]["collection_revision"],
        "model_digest": simulation["model"]["model_digest"],
        "simulator": simulation["simulator"],
        "settings_sha256": simulation["settings"]["sha256"],
        "response_request": {
            "path": "../config/response_request.json",
            "sha256": simulation["response_request"]["sha256"],
        },
        "temporal_preparation": temporal_preparation,
        "artifacts": artifacts,
        "series": series,
    }
    inventory["response_inventory_sha256"] = content_sha256(inventory)
    return inventory


def read_response_inventory(experiment_root):
    """Recompute retained native bytes, selectors and coverage before any reuse."""
    root = Path(experiment_root).resolve()
    directory = root / "responses"
    path = directory / "response_inventory.json"
    try:
        stored = read_canonical_json(
            _artifact_path(root, directory, "response_inventory.json")
        )
        digest = content_sha256(
            {
                key: value
                for key, value in stored.items()
                if key != "response_inventory_sha256"
            }
        )
        if stored["response_inventory_sha256"] != digest:
            raise MissingResponseRequirement(
                "response inventory digest mismatch before native opening"
            )
        native_runs = {}
        for index, artifact in enumerate(stored["artifacts"]):
            matching = [item for item in stored["series"] if item["artifact"] == index]
            if not matching:
                raise MissingResponseRequirement(
                    "native artifact has no declared series"
                )
            tomls = {item["native_selector"]["toml_path"] for item in matching}
            temporals = {item["native_selector"]["temporal_path"] for item in matching}
            if (
                len(tomls) != 1
                or len(temporals) != 1
                or artifact["run_id"] in native_runs
            ):
                raise MissingResponseRequirement(
                    "ambiguous native artifact association"
                )
            native_runs[artifact["run_id"]] = NativeRunArtifacts(
                _artifact_path(root, directory, artifact["path"]),
                _artifact_path(root, directory, next(iter(tomls))),
                _artifact_path(root, directory, next(iter(temporals))),
            )
        observed = build_response_inventory(
            root, native_runs, stored["temporal_preparation"]
        )
        if stored != observed:
            raise MissingResponseRequirement(
                f"response inventory drift expected={stored.get('response_inventory_sha256')} observed={observed['response_inventory_sha256']}"
            )
        simulation = read_simulation(root)
        if simulation["response_inventory_sha256"] not in {
            None,
            observed["response_inventory_sha256"],
        }:
            raise MissingResponseRequirement(
                "response inventory differs from simulation completion"
            )
        return observed
    except (OSError, KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, ResponseReaderUnavailable):
            raise
        raise MissingResponseRequirement(f"retained responses {path}: {exc}") from exc


def publish_response_inventory(experiment_root, native_runs, temporal_preparation):
    """Publish complete native coverage last, then fill simulation completion."""
    root = Path(experiment_root).resolve()
    path = root / "responses/response_inventory.json"
    if path.resolve() != path:
        raise MissingResponseRequirement("response publication path is aliased")
    inventory = build_response_inventory(root, native_runs, temporal_preparation)
    if path.exists():
        if read_response_inventory(root) != inventory:
            raise MissingResponseRequirement(
                "immutable response inventory already differs"
            )
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_record(path, inventory)
    complete_simulation(root, inventory["response_inventory_sha256"])
    return inventory
