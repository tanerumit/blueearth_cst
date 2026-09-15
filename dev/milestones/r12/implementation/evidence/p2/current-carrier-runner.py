"""P2 validation harness: enforce operations before launching current WF3 once.

This is retained implementation evidence, not the P3 production runner.
"""

import argparse
import os
import subprocess
import sys
import uuid
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument(
        "--operation",
        choices=("simulate-and-metrics", "metrics-only"),
        default="simulate-and-metrics",
    )
    parser.add_argument("--target", nargs="+", default=["all"])
    parser.add_argument("--cores", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--forceall", action="store_true")
    args = parser.parse_args(argv)
    repo = Path(__file__).resolve().parents[6]
    sys.path.insert(0, str(repo))
    supported = "simulate-and-metrics + all; metrics-only + metrics or one selected metric-set file"
    if len(args.target) != 1:
        parser.error(f"UnsupportedOperationTarget: {supported}")
    target = args.target[0]
    if args.operation == "simulate-and-metrics":
        allowed = target == "all"
    else:
        if target in {"all", "responses", "scenarios"} or (
            target != "metrics" and "metric_sets" not in target
        ):
            parser.error(f"UnsupportedOperationTarget: {supported}")
        from blueearth_cst.experiment.metric_plan import (
            build_metric_plan,
            current_metric_request,
            metrics_only_configuration,
        )

        try:
            root, tokens, anchor = metrics_only_configuration(args.config)
            plan = build_metric_plan(root, current_metric_request(root, tokens, anchor))
            allowed = (
                target == "metrics"
                or Path(target).resolve().as_posix() in plan["targets"].values()
            )
        except (OSError, KeyError, TypeError, ValueError) as error:
            parser.error(str(error))
    if not allowed:
        parser.error(f"UnsupportedOperationTarget: {supported}")
    environment = {
        **os.environ,
        "CST_WF3_OPERATION": args.operation,
        "CST_WF3_INVOCATION_ID": uuid.uuid4().hex,
    }
    command = [
        sys.executable,
        "-m",
        "snakemake",
        target,
        "-s",
        str(repo / "run_stress_test.smk"),
        "--configfile",
        str(Path(args.config).resolve()),
        "--cores",
        str(args.cores),
    ]
    if args.dry_run:
        command.append("--dry-run")
    if args.forceall:
        command.append("--forceall")
    print("P2_LAUNCH_SNAKEMAKE", flush=True)
    return subprocess.run(command, env=environment, cwd=repo, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
