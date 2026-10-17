"""Named indicator sets through the real runner and metric checkpoint.

Indicators-only over a retained v2 simulation: several sets plan in one
invocation, identical numerical requests share one immutable set, and an
authored alias publishes the registered calculation under its own metric key.
"""

import csv
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from blueearth_cst.experiment.content_identity import read_canonical_json
from tests._v2_experiment import build_v2_experiment

pytestmark = pytest.mark.workflow_contract

REPO = Path(__file__).resolve().parents[1]

ALIAS = """\
schema_version: 1
id: depth_alias
title: Recharge depth alias
description: Authored alias of the registered recharge depth.
selection:
  indicators:
    - id: recharge_depth
      title: Recharge depth
      description: Same calculation as gwr_annual_total.
      references: [Example citation]
      calculation:
        method: annual_summary/1
        parameters: {variable: gwr, statistic: sum}
"""

SAME_AS_DEFAULT = """\
schema_version: 1
id: same_numbers
title: Same numbers as default
description: Selects the default's single gwr definition explicitly.
selection:
  indicators:
    - definition: gwr_annual_total
"""


def _named(experiment, settings):
    workflow = experiment.config.parent / "simulate_system.yml"
    (experiment.config.parent / "sets").mkdir(exist_ok=True)
    (experiment.config.parent / "sets/depth_alias.yml").write_text(
        ALIAS, encoding="utf-8"
    )
    (experiment.config.parent / "sets/same_numbers.yml").write_text(
        SAME_AS_DEFAULT, encoding="utf-8"
    )
    workflow.write_text(
        yaml.safe_dump({"experiment_name": experiment.root.name, **settings}),
        encoding="utf-8",
    )


def _simulate(experiment, *extra):
    environment = os.environ.copy()
    environment.pop("SNAKEMAKE_PROFILE", None)
    environment.pop("SNAKEMAKE_WORKFLOW_PROFILE", None)
    result = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts/simulate_system.py"),
            "--config",
            str(experiment.config),
            "--cores",
            "1",
            *extra,
        ],
        cwd=REPO,
        env=environment,
        capture_output=True,
        text=True,
        timeout=600,
    )
    return result.returncode, result.stdout + result.stderr


SETTINGS = {
    "operations": ["indicators"],
    "indicator_sets": ["default", "depth_alias", "same_numbers"],
    "indicator_set_definitions": {
        "depth_alias": {"config_path": "sets/depth_alias.yml"},
        "same_numbers": {"config_path": "sets/same_numbers.yml"},
    },
}


def test_named_sets_dry_run_plans_each_distinct_request(tmp_path):
    experiment = build_v2_experiment(tmp_path)
    _named(experiment, SETTINGS)
    code, output = _simulate(experiment, "--dry-run")
    assert code == 0, output
    # default (outvars absent -> retained gwr) and same_numbers are one request.
    assert re.search(r"prepare_indicator_plan\s+2", output), output
    assert not (experiment.root / "_engine/metric_requests").exists()


def test_named_sets_refuse_an_explicit_target(tmp_path):
    experiment = build_v2_experiment(tmp_path)
    _named(experiment, SETTINGS)
    code, output = _simulate(experiment, "--target", "metrics", "--dry-run")
    assert code != 0
    assert "omit --target" in output, output


@pytest.mark.skipif(
    os.name != "nt",
    reason="run_project_child refuses project writers off Windows",
)
def test_named_sets_publish_independent_immutable_sets(tmp_path):
    experiment = build_v2_experiment(tmp_path)
    root = experiment.root
    _named(experiment, SETTINGS)
    code, output = _simulate(experiment)
    assert code == 0, output
    markers = sorted((root / "_engine/metric_sets").glob("*/metrics.json"))
    assert len(markers) == 2, markers
    manifests = [read_canonical_json(marker) for marker in markers]
    assert {m["schema_version"] for m in manifests} == {"metric-set/4"}
    by_metric = {m["calculations"][0]["metric"]: m for m in manifests}
    assert set(by_metric) == {"gwr_annual_total", "recharge_depth"}
    alias = by_metric["recharge_depth"]["calculations"][0]
    assert alias["definition"] == "gwr_annual_total"

    def rows(manifest, scope):
        path = root / next(
            item["file"]["path"]
            for item in manifest["tables"]
            if item["scope"] == scope
        )
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    for scope in ("run", "group"):
        registered = rows(by_metric["gwr_annual_total"], scope)
        authored = rows(by_metric["recharge_depth"], scope)
        assert registered and len(registered) == len(authored)
        # Only the metric key differs; values and keys match exactly.
        assert [{**row, "metric": "gwr_annual_total"} for row in authored] == registered


@pytest.mark.skipif(
    os.name != "nt",
    reason="run_project_child refuses project writers off Windows",
)
def test_named_sets_export_one_readable_folder_per_set(tmp_path):
    from blueearth_cst.experiment.named_export import read_current_publication

    experiment = build_v2_experiment(tmp_path)
    root = experiment.root
    _named(experiment, SETTINGS)
    code, output = _simulate(experiment)
    assert code == 0, output
    records = {
        set_id: read_current_publication(root, set_id)
        for set_id in ("default", "depth_alias", "same_numbers")
    }
    # Identical normalized requests reuse one immutable metric set across names.
    assert (
        records["default"]["metric_set_id"] == records["same_numbers"]["metric_set_id"]
    )
    assert (
        records["default"]["metric_set_id"] != records["depth_alias"]["metric_set_id"]
    )
    for set_id in records:
        assert (root / "results/metric_sets" / set_id / "indicators.csv").is_file()
    assert "Indicator set depth_alias current" in output, output
    # A metadata-only edit refreshes the publication but not the numbers.
    alias = experiment.config.parent / "sets/depth_alias.yml"
    alias.write_text(
        alias.read_text(encoding="utf-8").replace(
            "title: Recharge depth\n", "title: Renamed\n"
        ),
        encoding="utf-8",
    )
    code, output = _simulate(experiment)
    assert code == 0, output
    refreshed = read_current_publication(root, "depth_alias")
    assert refreshed["metric_set_id"] == records["depth_alias"]["metric_set_id"]
    assert refreshed["publication_id"] != records["depth_alias"]["publication_id"]
    assert "Renamed" in (
        root / "results/metric_sets/depth_alias/indicators.csv"
    ).read_text(encoding="utf-8")
