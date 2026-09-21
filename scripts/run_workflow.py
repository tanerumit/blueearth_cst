"""Run WF0, WF1 or WF2 with exact pre-parse configuration capture."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from blueearth_cst.shared.workflow_archive_launch import (  # noqa: E402
    WORKFLOWS,
    run_workflow,
)


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if "--" in arguments:
        boundary = arguments.index("--")
        extra = arguments[boundary + 1 :]
        arguments = arguments[:boundary]
    else:
        extra = []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", choices=WORKFLOWS)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--project-dir", required=True, type=Path)
    parser.add_argument("--cores", type=int, default=3)
    parser.add_argument("--target", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-going", action="store_true")
    args = parser.parse_args(arguments)
    return run_workflow(
        args.workflow,
        args.config,
        args.project_dir,
        cores=args.cores,
        targets=args.target or ["all"],
        dry_run=args.dry_run,
        keep_going=args.keep_going,
        extra=extra,
    )


if __name__ == "__main__":
    raise SystemExit(main())
