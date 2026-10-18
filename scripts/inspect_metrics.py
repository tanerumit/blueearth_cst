"""Inspect immutable WF4 metrics, optionally requiring a fresh numerical recheck."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from blueearth_cst.experiment.metric_inspection import inspect_metric_set


def main(argv=None):
    """Return nonzero for corruption or an unavailable requested numerical check."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument(
        "--list", action="store_true", help="discover saved metric sets on demand"
    )
    parser.add_argument("--recheck", action="store_true")
    parser.add_argument("--traceback", action="store_true")
    args = parser.parse_args(argv)
    if args.list:
        for path in sorted(
            (args.experiment / "_engine/metric_sets").glob("*/metrics.json")
        ):
            print(path)
        return 0
    if args.manifest is None:
        parser.error("--manifest is required unless --list is used")
    try:
        report = inspect_metric_set(
            args.experiment,
            args.manifest,
            recheck=args.recheck,
            traceback=args.traceback,
        )
    except (OSError, KeyError, ValueError) as exc:
        if args.traceback:
            raise
        print(f"Metric inspection failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, allow_nan=False))
    return int(args.recheck and report["numerical"]["status"] != "passed")


if __name__ == "__main__":
    raise SystemExit(main())
