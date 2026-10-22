"""Export a WF2 product as a portable bundle, or import one into another project.

Export writes one ZIP with the product, its exact configuration snapshots, the
basin polygon and a checksummed manifest. Import validates the whole bundle and
the destination before publishing the product atomically. Imported results are
for reading and interpretation; the runner does not adopt them as its own run.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from blueearth_cst.shared.result_bundle import BundleError, export_bundle  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    export = commands.add_parser("export", help="Write a WF2 result bundle.")
    export.add_argument("--project-dir", type=Path, required=True)
    export.add_argument("--output", type=Path, required=True, help="New .zip path.")
    export.add_argument(
        "--ensemble",
        help="Product directory under data/climate/projections/ "
        "(default: the captured WF2 configuration's ensemble).",
    )
    args = parser.parse_args(argv)
    try:
        report = export_bundle(args.project_dir, args.output, ensemble=args.ensemble)
    except BundleError as error:
        print(f"Refused: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
