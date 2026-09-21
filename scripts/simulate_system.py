"""Run the configured simulation operation through one validated Snakemake invocation."""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from blueearth_cst.experiment.simulation_runner import (
    simulation_command,
    simulation_settings,
)
from blueearth_cst.shared import invocation_history
from blueearth_cst.shared.provenance import file_sha256
from blueearth_cst.shared.windows_job import run_project_child
from blueearth_cst.shared.workflow_config_snapshot import archive_lock


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--project-dir", type=Path)
    parser.add_argument("--target", nargs="+", default=["all"])
    parser.add_argument("--cores", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--forceall", action="store_true")
    args, extra = parser.parse_known_args(argv)
    if extra[:1] == ["--"]:
        extra = extra[1:]
    if args.dry_run:
        extra.append("--dry-run")
    if args.forceall:
        extra.append("--forceall")
    if args.cores < 1:
        parser.error("--cores must be positive")
    if args.project_dir is None:
        # Config-only syntax has reduced startup-failure coverage: its root is
        # unavailable until the configuration can be parsed.
        try:
            project, _ = simulation_settings(args.config)
        except (OSError, KeyError, TypeError, ValueError) as exc:
            parser.error(str(exc))
        root = Path(project["project"]["project_dir"]).resolve()
    else:
        root = args.project_dir.resolve()
    record_path, record = invocation_history.start(
        root,
        workflow="simulate_system",
        entry_point="scripts/simulate_system.py",
        command=[
            "simulate_system",
            "--config",
            args.config,
            "--target",
            *args.target,
            *extra,
        ],
        targets=list(args.target),
        mode="dry_run" if args.dry_run else "execute",
        contract_mode="legacy_wf4_interim",
        invocation_id=os.environ.get(invocation_history.INVOCATION_ENV),
        parent_invocation_id=os.environ.get(invocation_history.PARENT_ENV),
    )
    try:
        project, settings = simulation_settings(args.config)
        if Path(project["project"]["project_dir"]).resolve() != root:
            raise ValueError("--project-dir differs from composed project root")
        command, environment = simulation_command(
            args.config, args.target, args.cores, extra
        )
        record["configuration"]["source_config_sha256"] = file_sha256(Path(args.config))
        record["configuration"]["archive_state"] = "historical_unavailable"
        environment["CST_SIMULATION_INVOCATION_ID"] = record["invocation_id"]
        invocation_history.update(record_path, record)
        print("simulate_system: " + " ".join(args.target), flush=True)
        with archive_lock(root, "project-execution"):
            result = run_project_child(
                command,
                env=environment,
                cwd=Path(__file__).resolve().parents[1],
                writing=not args.dry_run,
            )
        invocation_history.finish(record_path, record, exit_code=result)
        return result
    except BaseException as exc:
        invocation_history.finish(record_path, record, exit_code=None, error=exc)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
