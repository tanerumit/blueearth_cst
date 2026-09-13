"""Read-only checks of current metric identity and validation annotation seams."""

import importlib.metadata
import json
import shutil

from blueearth_cst.experiment.metric_plan import metric_request

legacy = {"status": "provisional_operational", "benchmark": "not assessed"}
request = metric_request("inspection-only", ["q"], "YS-JAN", {}, legacy)
try:
    metric_request(
        "inspection-only",
        ["q"],
        "YS-JAN",
        {},
        {"status": "provisional_operational", "benchmark": "reviewed_bounded"},
    )
except ValueError as error:
    rejection = str(error)
else:
    raise AssertionError("Expected the current validation vocabulary to be closed")
try:
    lmoments_version = importlib.metadata.version("lmoments3")
except importlib.metadata.PackageNotFoundError:
    lmoments_version = None
print(
    json.dumps(
        {
            "legacy_validation_accepted": request["return_level_validation"] == legacy,
            "reviewed_benchmark_annotation_rejected": rejection,
            "shared_environment_lmoments3_version": lmoments_version,
            "pixi_on_path": shutil.which("pixi"),
            "code_inventory_paths": [row["path"] for row in request["code_inventory"]],
            "new_fits": 0,
        },
        indent=2,
    )
)
