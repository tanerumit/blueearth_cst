"""Resolve authored Qcrit rules from WF1's historical model output only."""

from __future__ import annotations

import tomllib
from pathlib import Path

from blueearth_cst.experiment.wflow_response_reader import (
    NativeRunArtifacts,
    ResponseRequest,
    open_responses,
)
from blueearth_cst.indicators.sets.crop_water.calculations import prepare_baseline_qcrit
from blueearth_cst.shared.provenance import file_sha256


def resolve_thresholds(parameters: dict, set_path: Path) -> dict:
    """Replace a baseline_quantile rule with sealed per-location thresholds.

    Paths resolve against the authored set file. Only the owned WF1 historical
    output layout is accepted; observations and retained scenario responses
    cannot be selected through this interface. Input digests enter calculation
    parameters and therefore the indicator identity, including on reuse.
    """
    thresholds = parameters.get("thresholds")
    if not isinstance(thresholds, dict) or "baseline_quantile" not in thresholds:
        return parameters
    if set(thresholds) != {"baseline_quantile"}:
        raise ValueError("baseline_quantile cannot be mixed with explicit thresholds")
    rule = thresholds["baseline_quantile"]
    required = {"model_root", "source_id", "years"}
    optional = {"quantile", "convention", "reference_period", "quantile_method"}
    if (
        not isinstance(rule, dict)
        or not required <= set(rule)
        or set(rule) - required - optional
    ):
        raise ValueError(
            "baseline_quantile needs model_root, source_id, years and optional quantile settings"
        )
    if not isinstance(rule["model_root"], str) or not rule["model_root"]:
        raise ValueError("baseline_quantile.model_root must be a path string")
    if not isinstance(rule["source_id"], str) or not rule["source_id"]:
        raise ValueError(
            "baseline_quantile.source_id must identify historical model discharge"
        )
    if not isinstance(rule["years"], list):
        raise ValueError("baseline_quantile.years must be an explicit list of years")
    model = (set_path.parent / rule["model_root"]).resolve()
    csv_path = model / "run_default/output.csv"
    toml_path = model / "wflow_sbm.toml"
    before = [file_sha256(path) for path in (csv_path, toml_path)]
    with toml_path.open("rb") as stream:
        config = tomllib.load(stream)
    forcing = config.get("input", {}).get("path_forcing", "")
    if not isinstance(forcing, str) or Path(forcing).name != "inmaps_historical.nc":
        raise ValueError(
            "baseline_quantile requires WF1 historical model forcing inmaps_historical.nc"
        )
    # Hash the exact native input bytes; recheck after reading to refuse concurrent
    # WF1 writes rather than assign an identity to a mixed snapshot.
    identity = f"{rule['source_id']};csv-sha256={before[0]};toml-sha256={before[1]}"
    responses = open_responses(
        identity, NativeRunArtifacts(csv_path, toml_path), ResponseRequest(("q",))
    )
    options = {key: rule[key] for key in optional if key in rule}
    prepared = prepare_baseline_qcrit(
        responses, source_id=identity, years=rule["years"], **options
    )
    after = [file_sha256(path) for path in (csv_path, toml_path)]
    if before != after:
        raise ValueError("Qcrit historical model inputs changed during preparation")
    return {**parameters, "thresholds": prepared}
