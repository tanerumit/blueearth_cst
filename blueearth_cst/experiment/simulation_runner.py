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


def validate_targets(config_path, targets):
    """Refuse operation bypass before Snakemake can build any DAG."""
    _, settings = simulation_settings(config_path)
    operation = settings["operation"]
    supported = "simulate-and-metrics + all; metrics-only + metrics or one selected metric-set file"
    if len(targets) != 1:
        raise ValueError(f"UnsupportedOperationTarget: {supported}")
    target = targets[0]
    if operation == "simulate-and-metrics":
        allowed = target == "all"
    else:
        from blueearth_cst.experiment.metric_plan import (
            build_metric_plan,
            current_metric_request,
            metrics_only_configuration,
        )

        if target in {"all", "responses", "scenarios"} or (
            target != "metrics" and "metric_sets" not in Path(target).parts
        ):
            raise ValueError(f"UnsupportedOperationTarget: {supported}")
        root, tokens, anchor = metrics_only_configuration(config_path)
        plan = build_metric_plan(root, current_metric_request(root, tokens, anchor))
        allowed = (
            target == "metrics"
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
        *targets,
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
        resolve_explicit_collection,
        resolve_project_collection,
    )
    from blueearth_cst.experiment.forcing_descriptor import (
        collection_forcing_descriptor,
    )
    from blueearth_cst.experiment.legacy_generation_plan import (
        generation_configuration,
        resolve_generation_plan,
    )
    from blueearth_cst.experiment.wf4_ancillary_descriptor import describe_ancillary
    from blueearth_cst.shared.config_composition import compose_config

    project, settings = simulation_settings(config_path)
    descriptors = dict(
        describe_forcing=collection_forcing_descriptor,
        describe_ancillary=describe_ancillary,
    )
    if "scenario_collection" in settings:
        return resolve_explicit_collection(
            settings["scenario_collection"], **descriptors
        )
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
    command = (
        f'snakemake all -s generate_scenarios.smk --configfile "{config_path}" -c 3'
    )
    if not Path(generation["request_path"]).is_file():
        raise GeneratedCollectionUnavailable(
            f"missing {generation['request_path']}; run {command}"
        )
    try:
        plan, _, _ = resolve_generation_plan(generation)
    except OSError as exc:
        from blueearth_cst.experiment.collection_resolution import (
            GeneratedCollectionStale,
        )

        raise GeneratedCollectionStale(
            f"{generation['request_path']}: {exc}; run {command}"
        ) from exc
    return resolve_project_collection(
        generation["project_dir"],
        generation["request"],
        live_sources={
            item["path"]: Path(item["path"]) for item in plan["source_inventory"]
        },
        live_code={
            item["path"]: Path(repository) / item["path"] for item in generation["code"]
        },
        live_environment=plan["documents"]["environment"],
        expected_intent=plan["intent"],
        generation_command=command,
        **descriptors,
    )
