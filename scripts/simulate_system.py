"""Run the configured simulation operation through one validated Snakemake invocation."""

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from blueearth_cst.experiment.simulation_runner import (
    simulation_command,
    simulation_settings,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
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
    try:
        command, environment = simulation_command(
            args.config, args.target, args.cores, extra
        )
    except (OSError, KeyError, TypeError, ValueError) as exc:
        parser.error(str(exc))
    print("simulate_system: " + " ".join(args.target), flush=True)
    from blueearth_cst.experiment.content_identity import atomic_record

    project, settings = simulation_settings(args.config)
    invocation = environment["CST_SIMULATION_INVOCATION_ID"]
    record_path = (
        Path(project["project"]["project_dir"]).resolve()
        / "config/runs/invocations"
        / f"simulation-{invocation}.json"
    )
    record = {
        "schema_version": "simulation-invocation/1",
        "operation": settings["operation"],
        "targets": args.target,
        "config_path": str(Path(args.config).resolve()),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "running",
        "exit_code": None,
    }
    record_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_record(record_path, record)
    try:
        result = subprocess.run(
            command,
            env=environment,
            cwd=Path(__file__).resolve().parents[1],
            check=False,
        )
        record.update(
            status="succeeded" if result.returncode == 0 else "failed",
            exit_code=result.returncode,
        )
        return result.returncode
    except BaseException as exc:
        record.update(status="failed", error_type=type(exc).__name__)
        raise
    finally:
        record["ended_at_utc"] = datetime.now(timezone.utc).isoformat()
        atomic_record(record_path, record, replace=True)


if __name__ == "__main__":
    raise SystemExit(main())
