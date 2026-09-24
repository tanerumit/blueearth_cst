"""Shared operation/target contract for the two public simulation runners."""

import os
import sys
import uuid
from pathlib import Path

import yaml


def simulation_settings(config_path):
    """Read the simulation file without opening generation or model files."""
    path = Path(config_path).resolve()
    project = yaml.safe_load(path.read_text(encoding="utf-8"))
    workflows = project.get("workflows", {})
    if "run_stress_test" in workflows:
        raise ValueError(
            "run_stress_test is retired; migrate to generate_scenarios and "
            "simulate_system with scripts/migrate_project_config.py"
        )
    stanza = workflows.get("simulate_system", {})
    if set(stanza) != {"enabled", "config_path"} or not isinstance(
        stanza["enabled"], bool
    ):
        raise ValueError("simulate_system requires a closed enabled/config_path stanza")
    settings = yaml.safe_load(
        (path.parent / stanza["config_path"]).read_text(encoding="utf-8")
    )
    if settings.get("operation") not in {"simulate-and-metrics", "metrics-only"}:
        raise ValueError(
            "simulate_system.operation must be simulate-and-metrics or metrics-only"
        )
    return project, settings


#: Target names retired 2026-09-24, accepted for one release and rewritten to
#: the current rule name before Snakemake sees them.
LEGACY_TARGETS = {
    "responses": "simulations_only",
    "metrics": "simulations_and_indicators",
}


def current_targets(targets):
    """``targets`` with any retired target name replaced by its current one."""
    return [LEGACY_TARGETS.get(target, target) for target in targets]


def validate_targets(config_path, targets):
    """Refuse operation bypass before Snakemake can build any DAG."""
    _, settings = simulation_settings(config_path)
    operation = settings["operation"]
    supported = (
        "simulate-and-metrics + all/simulations_only; "
        "metrics-only + simulations_and_indicators or one selected metric output"
    )
    if len(targets) != 1:
        raise ValueError(f"UnsupportedOperationTarget: {supported}")
    target = current_targets(targets)[0]
    if operation == "simulate-and-metrics":
        allowed = target in {"all", "simulations_only"}
    else:
        from blueearth_cst.experiment.metric_plan import (
            build_metric_plan,
            current_metric_request,
            metrics_only_configuration,
        )

        root, tokens, anchor = metrics_only_configuration(config_path)
        plan = build_metric_plan(root, current_metric_request(root, tokens, anchor))
        allowed = (
            target == "simulations_and_indicators"
            or Path(target).resolve().as_posix() in plan["targets"].values()
        )
    if not allowed:
        raise ValueError(f"UnsupportedOperationTarget: {supported}")
    return operation


def simulation_command(config_path, targets, cores, extra=()):
    """Build one checked invocation; callers control lifecycle reporting."""
    operation = validate_targets(config_path, targets)
    # Target selection and config belong to this runner. Passthrough is limited
    # to execution controls so a second target cannot bypass the check above.
    switches = {
        "--dry-run",
        "-n",
        "--forceall",
        "-F",
        "--printshellcmds",
        "-p",
        "--keep-going",
        "--rerun-incomplete",
        "--notemp",
        "--unlock",
    }
    value_switches = {
        "--resources",
        "--set-resources",
        "--set-threads",
        "--forcerun",
        "--rerun-triggers",
    }
    index = 0
    while index < len(extra):
        option = extra[index]
        index += 1
        if option in switches:
            continue
        if option not in value_switches:
            raise ValueError(
                "unsupported simulation execution option; target/config overrides are refused"
            )
        start = index
        while index < len(extra) and not extra[index].startswith("-"):
            index += 1
        if index == start:
            raise ValueError(f"{option} requires a value")
    repo = Path(__file__).resolve().parents[2]
    command = [
        sys.executable,
        "-m",
        "snakemake",
        *current_targets(targets),
        "-s",
        str(repo / "simulate_system.smk"),
        "--configfile",
        str(Path(config_path).resolve()),
        "-c",
        str(cores),
        *extra,
    ]
    environment = {
        **os.environ,
        "CST_SIMULATION_OPERATION": operation,
        "CST_SIMULATION_INVOCATION_ID": uuid.uuid4().hex,
    }
    return command, environment


def resolve_selected_collection(config_path, repository):
    """Consume an exact ready collection; never invoke its producers."""
    from blueearth_cst.experiment.collection_resolution import (
        GeneratedCollectionUnavailable,
        resolve_explicit_collection_v2,
    )
    from blueearth_cst.experiment.content_identity import (
        content_sha256,
        read_canonical_json,
    )
    from blueearth_cst.experiment.generation_plan import (
        generation_configuration,
        read_pinned_plan,
    )
    from blueearth_cst.experiment.scenario_collection_v2 import read_collection_v2
    from blueearth_cst.shared.config_composition import compose_config

    project, settings = simulation_settings(config_path)
    if "scenario_collection" in settings:
        selection, marker = resolve_explicit_collection_v2(
            settings["scenario_collection"]
        )
        verify_selected_collection_source(project, selection, marker)
        return selection, marker
    composed, _ = compose_config(
        project,
        config_path,
        entry="generate_scenarios",
        declared_sections=(
            "project",
            "basin",
            "climate",
            "workflows.generate_scenarios",
        ),
    )
    generation = generation_configuration(composed, repository)
    command = f'python scripts/run_workflows.py --config "{config_path}" --project-dir "{generation["project_dir"]}"'
    pointer_path = Path(generation["request_path"])
    if not pointer_path.is_file():
        raise GeneratedCollectionUnavailable(
            f"missing {generation['request_path']}; run {command}"
        )
    try:
        pointer = read_canonical_json(pointer_path)
        if (
            set(pointer)
            != {
                "schema_version",
                "generation_request_id",
                "plan_path",
                "path_base",
                "plan_sha256",
            }
            or pointer["schema_version"] != "scenario-request/2"
            or pointer["path_base"] != "request_directory"
        ):
            raise ValueError("unsupported scenario request pointer")
        if Path(pointer["plan_path"]).name != pointer["plan_path"]:
            raise ValueError("scenario plan escapes request directory")
        plan = read_pinned_plan(
            pointer_path.parent / pointer["plan_path"],
            pointer["plan_sha256"],
            Path(generation["project_dir"]),
        )
        if pointer["generation_request_id"] != plan["generation_request_id"] or pointer[
            "generation_request_id"
        ] != content_sha256(generation["request"]):
            raise ValueError("project request pointer differs from pinned plan")
        marker_path = (
            Path(generation["project_dir"])
            / plan["outputs"]["record_root"]
            / "collection.json"
        )
        marker = read_collection_v2(marker_path)
        if marker["collection_id"] != plan["collection_id"]:
            raise ValueError("pinned collection identity differs")
        if (
            plan["decision"] == "reuse_ready"
            and marker["collection_revision"] != plan["collection_revision"]
        ):
            raise ValueError("pinned collection revision differs")
    except (OSError, KeyError, TypeError, ValueError) as exc:
        from blueearth_cst.experiment.collection_resolution import (
            GeneratedCollectionStale,
        )

        raise GeneratedCollectionStale(f"{pointer_path}: {exc}; run {command}") from exc
    selection = {
        "resolution_mode": "project-generation",
        "manifest_path": marker_path.resolve().as_posix(),
        "collection_id": marker["collection_id"],
        "collection_revision": marker["collection_revision"],
    }
    verify_selected_collection_source(project, selection, marker)
    return selection, marker


def verify_selected_collection_source(project, selection, marker):
    """Bind WF4 elevation/PET choice to the collection creator's climate source."""
    from blueearth_cst.shared.workflow_config_snapshot import (
        resolve_file_reference,
        validate_archive,
    )

    path = Path(selection["manifest_path"]).resolve(strict=True)
    record_dir = path.parent
    project_root = record_dir.parents[3]
    configured_root = Path(project["project"]["project_dir"]).resolve()
    if project_root != configured_root:
        raise ValueError("selected collection is outside the WF4 project root")
    archive_path = resolve_file_reference(
        marker["archive"],
        {"project_root": project_root, "record_directory": record_dir},
    )
    archive = validate_archive(archive_path.parent)
    if archive["owner"] != {
        "kind": "scenario_collection",
        "id": marker["collection_id"],
    }:
        raise ValueError("collection creator archive owner differs")
    selected = archive["loaded_config"]["climate"]["selected"]
    if selected != project["climate"]["selected"]:
        raise ValueError(
            f"WF4 climate source {project['climate']['selected']!r} differs from "
            f"collection creator source {selected!r}"
        )
    return selected
