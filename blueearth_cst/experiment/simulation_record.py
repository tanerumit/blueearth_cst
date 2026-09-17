"""Freeze simulation inputs independently of metric selection and completion."""

import re
from pathlib import Path

from blueearth_cst.experiment.content_identity import (
    atomic_record,
    canonical_json_bytes,
    confined_path,
    content_sha256,
    read_canonical_json,
)
from blueearth_cst.shared.provenance import file_sha256
from blueearth_cst.shared.snake_utils import log_row


class SimulationFrozenError(ValueError):
    """An experiment cannot reuse changed immutable simulation inputs."""


class MetricsOnlySimulationUnavailable(ValueError):
    """The selected experiment has no complete retained simulation."""


def live_simulation_inputs(
    experiment_root,
    *,
    project_dir,
    model_root,
    collection,
    settings,
    julia_command,
    header_path,
):
    """Resolve the current Wflow binding before any prepared/native output is written."""
    import tomllib

    from blueearth_cst.experiment.content_identity import (
        repository_code_inventory,
        stage_environment,
    )
    from blueearth_cst.experiment.forcing_window import forcing_window
    from blueearth_cst.experiment.simulator_adapter import plan_native_response_request
    from blueearth_cst.experiment.write_model_reference import build_model_reference

    root = Path(experiment_root).resolve()
    model = Path(model_root).resolve()
    repo = Path(__file__).resolve().parents[2]
    reference = build_model_reference(model, project_dir)
    with (model / reference["model_toml"]).open("rb") as handle:
        model_config = tomllib.load(handle)
    first, last = forcing_window(
        settings["simulation_window"]["start"], settings["simulation_window"]["end"]
    )
    step = model_config["time"]["timestepsecs"]
    request = plan_native_response_request(
        model / reference["model_toml"],
        [item["run_id"] for item in collection["forcing"]],
        julia_command=julia_command,
        header_path=header_path,
        # Preparation explicitly sets the standard calendar and refreshes the
        # configured forcing endpoints. The adapter adds the response offset.
        first_time=first,
        last_time=last,
        calendar="standard",
        timestep_seconds=step,
    )
    code = repository_code_inventory(
        repo,
        [
            "blueearth_cst/experiment/simulator_adapter.py",
            "blueearth_cst/experiment/downscale_climate_forcing.py",
            "blueearth_cst/experiment/run_wflow_batch.jl",
            "blueearth_cst/shared/wflow_progress.jl",
            "blueearth_cst/shared/run_logged.py",
        ],
    )
    environment = stage_environment(
        ["hydromt-wflow", "xarray", "netCDF4", "pyproj"],
        julia_manifest=repo / "Manifest.toml",
        julia_command=julia_command,
    )
    documents = {
        "settings": settings,
        "response_request": request,
        "simulator_adapter_code": code,
        "environment": environment,
    }
    selection = {
        "resolution_mode": settings["resolution_mode"],
        "manifest_path": settings["manifest_path"],
        "collection_id": collection["collection_id"],
        "collection_revision": collection["collection_revision"],
    }
    # Resolution provenance and paths are not result-affecting simulator settings.
    documents["settings"] = {
        key: value
        for key, value in settings.items()
        if key not in {"resolution_mode", "manifest_path"}
    }
    simulator = {
        "name": "wflow",
        "revision": content_sha256(
            {"julia:Wflow": environment["packages"]["julia:Wflow"]}
        ),
    }
    return simulation_document(
        root.name, selection, reference["digest"], simulator, documents
    ), documents


_DOCUMENTS = {
    "settings": "simulator_settings.json",
    "simulator_adapter_code": "simulator_adapter_code_inventory.json",
    "environment": "simulation_environment.json",
    "response_request": "response_request.json",
}


def _simulation_path(root, relative):
    path = confined_path(root, relative)
    if path != root / relative:
        raise SimulationFrozenError(f"simulation record path is aliased: {relative}")
    return path


def _check_model_reference(root, record):
    """Verify the retained model identity without opening the live model."""
    import yaml

    from blueearth_cst.shared.model_digest import (
        DIGEST_VERSION,
        model_digest_from_entries,
    )

    reference = yaml.safe_load(
        _simulation_path(root, "config/model_reference.yml").read_text(encoding="utf-8")
    )
    if reference["digest_version"] != DIGEST_VERSION:
        raise SimulationFrozenError("retained model digest version differs")
    digest = model_digest_from_entries(sorted(reference["inputs"].items()))
    if digest != reference["digest"] or digest != record["model"]["model_digest"]:
        raise SimulationFrozenError("retained model reference digest differs")


def simulation_id(record):
    """Apply the accepted §8.3 projection, excluding names and completion facts."""
    return content_sha256(
        {
            "collection_id": record["collection"]["collection_id"],
            "collection_revision": record["collection"]["collection_revision"],
            "model_digest": record["model"]["model_digest"],
            "simulator_name_and_revision": record["simulator"],
            "simulator_adapter_code_sha256": record["simulator_adapter_code"]["sha256"],
            "settings_sha256": record["settings"]["sha256"],
            "simulation_response_request_sha256": record["response_request"]["sha256"],
            "environment_sha256": record["environment"]["sha256"],
        }
    )


def simulation_document(
    experiment_name, collection, model_digest, simulator, documents
):
    """Build the frozen record from already resolved result-affecting inputs."""
    if set(documents) != set(_DOCUMENTS):
        raise ValueError(f"simulation documents require {sorted(_DOCUMENTS)}")
    if set(collection) != {
        "resolution_mode",
        "manifest_path",
        "collection_id",
        "collection_revision",
    }:
        raise ValueError("simulation collection selection is incomplete")
    if collection["resolution_mode"] not in {"project-generation", "explicit-manifest"}:
        raise ValueError("invalid collection resolution mode")
    if set(simulator) != {"name", "revision"} or not all(simulator.values()):
        raise ValueError("simulator requires a name and immutable revision")
    for value in (
        model_digest,
        collection["collection_id"],
        collection["collection_revision"],
        simulator["revision"],
    ):
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise ValueError(
                "simulation identity inputs require lowercase SHA-256 digests"
            )
    record = {
        "schema_version": "simulation/1",
        "experiment_name": experiment_name,
        "collection": collection,
        "model": {
            "model_digest": model_digest,
            "reference_path": "config/model_reference.yml",
        },
        "simulator": simulator,
        **{
            key: {"path": name, "sha256": content_sha256(documents[key])}
            for key, name in _DOCUMENTS.items()
        },
        "response_inventory_sha256": None,
    }
    record["simulation_id"] = simulation_id(record)
    return record


def read_simulation(experiment_root, *, require_complete=False):
    """Recompute identity entirely from retained documents, without a live model."""
    root = Path(experiment_root).resolve()
    try:
        path = _simulation_path(root, "config/simulation.json")
        record = read_canonical_json(path)
        expected_fields = {
            "schema_version",
            "simulation_id",
            "experiment_name",
            "collection",
            "model",
            "simulator",
            "response_inventory_sha256",
            *_DOCUMENTS,
        }
        if set(record) != expected_fields or record["schema_version"] != "simulation/1":
            raise ValueError("invalid simulation/1 record fields")
        if record["experiment_name"] != root.name:
            raise ValueError("experiment name does not match selected namespace")
        _check_model_reference(root, record)
        documents = {}
        for key, name in _DOCUMENTS.items():
            reference = record[key]
            if set(reference) != {"path", "sha256"} or reference["path"] != name:
                raise ValueError(f"invalid {key} reference")
            artifact = _simulation_path(root, f"config/{name}")
            documents[key] = read_canonical_json(artifact)
            observed = file_sha256(artifact)
            if observed != reference["sha256"]:
                raise ValueError(
                    f"{key}: expected={reference['sha256']} observed={observed}"
                )
        expected = simulation_document(
            root.name,
            record["collection"],
            record["model"]["model_digest"],
            record["simulator"],
            documents,
        )
        expected["response_inventory_sha256"] = record["response_inventory_sha256"]
        if canonical_json_bytes(record) != canonical_json_bytes(expected):
            raise ValueError(
                f"simulation identity expected={expected['simulation_id']} observed={record['simulation_id']}"
            )
        if require_complete and record["response_inventory_sha256"] is None:
            raise MetricsOnlySimulationUnavailable(
                f"simulation {path} has no response completion"
            )
        return record
    except MetricsOnlySimulationUnavailable:
        raise
    except (OSError, KeyError, TypeError, ValueError) as exc:
        error = (
            MetricsOnlySimulationUnavailable
            if require_complete
            else SimulationFrozenError
        )
        raise error(f"simulation {root}: {exc}") from exc


def freeze_simulation(experiment_root, record, documents, config_snapshot=None):
    """Write immutable inputs before any preparation or native output is scheduled.

    Same-identity reuse verifies all retained bytes. It never rewrites completion,
    provenance or inputs. Partial document writes can only be reused byte-exactly.

    ``config_snapshot`` is the rendered ``composed_config.yml`` bytes, written
    beside the frozen documents and named by none of them. It is deliberately
    NOT one of :data:`_DOCUMENTS`: those four are hashed into ``simulation_id``,
    and ``read_simulation`` compares the record's key set against an exact
    expected set, so promoting the snapshot would both move every existing
    experiment's identity and make an older record unreadable. It is written on
    the freeze path only -- a reuse returns the retained simulation untouched,
    which is what keeps the directory immutable once it holds results.
    """
    root = Path(experiment_root).resolve()
    expected = simulation_document(
        root.name,
        record["collection"],
        record["model"]["model_digest"],
        record["simulator"],
        documents,
    )
    if canonical_json_bytes(record) != canonical_json_bytes(expected):
        raise SimulationFrozenError(
            "initial simulation differs from its resolved inputs"
        )
    _check_model_reference(root, record)
    config = _simulation_path(root, "config")
    marker = _simulation_path(root, "config/simulation.json")
    if marker.exists():
        retained = read_simulation(root)
        if retained["simulation_id"] != record["simulation_id"]:
            raise SimulationFrozenError(
                f"simulation_id expected={record['simulation_id']} retained={retained['simulation_id']}; use a new experiment name"
            )
        log_row(
            f"Reusing the frozen simulation {retained['simulation_id'][:12]}",
            module="simulation",
        )
        return retained
    if any((root / "hydrology" / "wflow" / "output").glob("*.csv")):
        raise SimulationFrozenError(
            "unrecorded native outputs exist; use a new experiment name"
        )
    # Check all conflicts before creating any new input document.
    for key, name in _DOCUMENTS.items():
        target = _simulation_path(root, f"config/{name}")
        if target.exists() and target.read_bytes() != canonical_json_bytes(
            documents[key]
        ):
            raise SimulationFrozenError(
                f"immutable simulation input already differs: {target}"
            )
    config.mkdir(parents=True, exist_ok=True)
    for key, name in _DOCUMENTS.items():
        target = _simulation_path(root, f"config/{name}")
        if not target.exists():
            atomic_record(target, documents[key])
    if config_snapshot is not None:
        from blueearth_cst.shared.workflow_config_snapshot import SNAPSHOT_NAME

        _simulation_path(root, f"config/{SNAPSHOT_NAME}").write_bytes(config_snapshot)
    atomic_record(marker, record)
    log_row(
        f"Froze simulation {record['simulation_id'][:12]}: "
        f"collection {record['collection']['collection_id'][:12]} "
        f"({record['collection']['resolution_mode']}) "
        f"against model {record['model']['model_digest'][:12]}",
        module="simulation",
    )
    return read_simulation(root)


def complete_simulation(experiment_root, response_inventory_sha256):
    """Fill the single completion fact after a matching response inventory exists."""
    root = Path(experiment_root).resolve()
    record = read_simulation(root)
    from blueearth_cst.experiment.response_inventory import read_response_inventory

    inventory = read_response_inventory(root)
    payload = {
        key: value
        for key, value in inventory.items()
        if key != "response_inventory_sha256"
    }
    if (
        inventory["simulation_id"] != record["simulation_id"]
        or inventory["response_inventory_sha256"] != response_inventory_sha256
        or content_sha256(payload) != response_inventory_sha256
    ):
        raise SimulationFrozenError(
            "response completion does not match persisted inventory"
        )
    completed = record["response_inventory_sha256"]
    if completed is not None:
        if completed != response_inventory_sha256:
            raise SimulationFrozenError(
                "a different response inventory is already complete"
            )
        return record
    record["response_inventory_sha256"] = response_inventory_sha256
    atomic_record(
        _simulation_path(root, "config/simulation.json"), record, replace=True
    )
    return record
