"""Compare retained Windows and newly observed Linux metric projections."""

import json
from pathlib import Path

root = Path(__file__).resolve().parents[7]
windows = json.loads(
    (
        root
        / "dev/milestones/r12/implementation/evidence/gf15-production-integration/windows-setup/stage-environment-shared.json"
    ).read_text()
)
linux = json.loads((Path(__file__).parent / "quantile-results.json").read_text())[
    "metric_environment"
]
wp = windows["packages"]
lp = linux["packages"]
shared = wp.keys() & lp.keys()
result = {
    "windows_packages": len(wp),
    "linux_packages": len(lp),
    "shared_keys": len(shared),
    "shared_equal_values": sum(wp[key] == lp[key] for key in shared),
    "shared_different_values": sum(wp[key] != lp[key] for key in shared),
    "windows_only_keys": len(wp.keys() - lp.keys()),
    "linux_only_keys": len(lp.keys() - wp.keys()),
    "windows_locks": windows["locks"],
    "linux_locks": linux["locks"],
    "windows_only_examples": sorted(wp.keys() - lp.keys())[:8],
    "linux_only_examples": sorted(lp.keys() - wp.keys())[:8],
}
print(json.dumps(result, indent=2, sort_keys=True))
