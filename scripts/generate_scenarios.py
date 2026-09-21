"""Owned two-phase WF3 launcher: prepare sources, freeze a plan, then generate."""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from blueearth_cst.experiment.generation_plan import (
    build_candidate_intent,
    generation_configuration,
    publish_plan_pointer,
    select_generation_plan,
)
from blueearth_cst.experiment.generation_publication import initialize_generation
from blueearth_cst.shared import invocation_history
from blueearth_cst.shared.config_composition import compose_config
from blueearth_cst.shared.windows_job import run_project_child
from blueearth_cst.shared.workflow_config_snapshot import archive_lock

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECTION = ("project", "basin", "climate", "workflows.generate_scenarios")


def _command(config_path: Path, cores: int, extra: list[str]) -> list[str]:
    return [
        "snakemake",
        "all",
        "-c",
        str(cores),
        "-s",
        "generate_scenarios.smk",
        "--configfile",
        str(config_path),
        *extra,
    ]


def run_owned(
    config_path: Path,
    project_root: Path,
    cores: int,
    extra: list[str],
    *,
    invocation_id: str,
    history_pair: tuple[Path, dict[str, Any]] | None = None,
) -> int:
    """Run while the caller holds project-execution ownership."""
    if cores < 1:
        raise ValueError("cores must be positive")
    config_path = Path(config_path).resolve(strict=True)
    project_root = Path(project_root).resolve()
    dry_run = "--dry-run" in extra or "-n" in extra
    command = _command(config_path, cores, extra)
    base_env = {
        **os.environ,
        "CST_GENERATION_OWNED": invocation_id,
        "CST_GENERATION_INVOCATION_ID": invocation_id,
    }
    source_code = run_project_child(
        command,
        cwd=REPO_ROOT,
        env={**base_env, "CST_GENERATION_PHASE": "source"},
        writing=not dry_run,
    )
    if source_code or dry_run:
        return source_code
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config, _ = compose_config(
        raw,
        config_path,
        entry="generate_scenarios",
        declared_sections=PROJECTION,
    )
    if config["workflows"]["generate_scenarios"].get("enabled") is False:
        raise ValueError("WF3 is disabled in this project configuration")
    if Path(config["project"]["project_dir"]).resolve() != project_root:
        raise ValueError("WF3 config project root differs from owned root")
    settings = generation_configuration(config, REPO_ROOT)
    candidate = build_candidate_intent(settings)
    plan = select_generation_plan(settings, candidate)
    plan_path, plan_sha256 = publish_plan_pointer(settings, plan)
    lookup_path = (
        Path(settings["request_path"]).parent
        / "generation/config/stress_test_lookup.csv"
    )
    receipt_path = initialize_generation(
        project_root,
        plan_path,
        plan_sha256,
        config_path=config_path,
        loaded_config=config,
        invocation_id=invocation_id,
        lookup_path=lookup_path,
        command=command,
    )
    if history_pair is not None:
        history_path, history = history_pair
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        history["configuration"].update(
            source_config_sha256=hashlib.sha256(config_path.read_bytes()).hexdigest(),
            run_record=receipt["creator_archive"],
            archive_state="creator",
        )
        history["plan"] = {
            "generation_request_id": plan["generation_request_id"],
            "plan_sha256": plan_sha256,
            "decision": plan["decision"],
            "collection_id": plan["collection_id"],
        }
        invocation_history.update(history_path, history)
    generation_env = {
        **base_env,
        "CST_GENERATION_PHASE": "generation",
        "CST_GENERATION_PLAN_PATH": str(plan_path),
        "CST_GENERATION_PLAN_SHA256": plan_sha256,
        "CST_GENERATION_RECEIPT_PATH": str(receipt_path),
    }
    return run_project_child(command, cwd=REPO_ROOT, env=generation_env)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a pinned scenario collection"
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--cores", type=int, default=3)
    parser.add_argument("extra", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    extra = args.extra[1:] if args.extra[:1] == ["--"] else args.extra
    project_root = args.project_dir.resolve()
    history_path, history = invocation_history.start(
        project_root,
        workflow="generate_scenarios",
        entry_point="scripts/generate_scenarios.py",
        command=[
            "generate_scenarios",
            "--config",
            str(args.config),
            "--project-dir",
            str(args.project_dir),
            "--cores",
            str(args.cores),
            *extra,
        ],
        targets=["all"],
        mode="dry_run" if "--dry-run" in extra or "-n" in extra else "execute",
        contract_mode="new_schema",
    )
    try:
        with archive_lock(project_root, "project-execution"):
            result = run_owned(
                args.config,
                project_root,
                args.cores,
                extra,
                invocation_id=history["invocation_id"],
                history_pair=(history_path, history),
            )
        invocation_history.finish(history_path, history, exit_code=result)
        return result
    except BaseException as error:
        invocation_history.finish(history_path, history, exit_code=None, error=error)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
