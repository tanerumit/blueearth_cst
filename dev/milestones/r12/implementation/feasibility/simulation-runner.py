"""P0 mandatory-runner fixture: validate targets before one Snakemake call."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from fixture_contracts import metric_plan

SUPPORTED = "simulate-and-metrics + all; metrics-only + metrics or selected metric file"


def main() -> int:
    """Validate the actual requested operation/targets, then select a fixed module."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--operation",
        choices=("simulate-and-metrics", "metrics-only"),
        default="simulate-and-metrics",
    )
    parser.add_argument("--target", nargs="+", default=["all"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--forceall", action="store_true")
    args = parser.parse_args()
    targets = args.target
    if len(targets) != 1:
        parser.error(f"UnsupportedOperationTarget: supported pairs: {SUPPORTED}")
    target = targets[0]
    if args.operation == "simulate-and-metrics":
        allowed = target == "all"
    else:
        allowed = target == "metrics"
        if not allowed and target.startswith("metrics/"):
            try:
                allowed = target == metric_plan()["target"]
            except ValueError as error:
                parser.error(str(error))
    if not allowed:
        parser.error(f"UnsupportedOperationTarget: supported pairs: {SUPPORTED}")
    command = [
        sys.executable,
        "-m",
        "snakemake",
        target,
        "--snakefile",
        str(Path(__file__).with_name("simulation-router.smk")),
        "--cores",
        "1",
        "--nocolor",
    ]
    if args.dry_run:
        command.append("--dry-run")
    if args.forceall:
        command.append("--forceall")
    command.extend(["--config", f"operation={args.operation}"])
    environment = os.environ.copy()
    environment.pop("SNAKEMAKE_PROFILE", None)
    environment.pop("SNAKEMAKE_WORKFLOW_PROFILE", None)
    print("P0_LAUNCH_SNAKEMAKE", flush=True)
    return subprocess.run(command, env=environment, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
