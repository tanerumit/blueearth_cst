"""Read saved artifact contracts without importing current indicator registries."""

import csv
from pathlib import Path

import numpy as np

from blueearth_cst.experiment.content_identity import (
    content_sha256,
    identity_segment,
    read_canonical_json,
)
from blueearth_cst.experiment.legacy_indicator_names import indicator_names
from blueearth_cst.shared.provenance import file_sha256

RETURN_LEVEL_EVIDENCE_FILENAME = "return_level_evidence.json"
COVERAGE_EVIDENCE_FILENAME = "coverage_evidence.json"


class ImmutableIndicatorSetError(ValueError):
    """A result set is incomplete or inconsistent with its saved contract."""


def _validate_tables(tables, expected_keys, declarations_by_name, units):
    grains = {}
    key = "run_group_id"
    for row in units:
        previous = grains.setdefault(row[key], row["grain"])
        if previous != row["grain"]:
            raise ImmutableIndicatorSetError("indicator unit has more than one grain")
    actual = []
    for token, rows in tables.items():
        for row in rows:
            expected_fields = {"indicator", "location", key, "value"}
            if set(row) != expected_fields:
                raise ImmutableIndicatorSetError(
                    "indicator table fields are not the declared indicator schema"
                )
            declaration = declarations_by_name.get(row["indicator"])
            if (
                declaration is None
                or declaration["required_responses"]["variable"] != token
            ):
                raise ImmutableIndicatorSetError(
                    "indicator row has undeclared indicator or wrong table token"
                )
            grain = grains.get(row[key])
            if grain is None or (
                declaration["grain"] == "bundle" and grain != "bundle"
            ):
                raise ImmutableIndicatorSetError("indicator and unit grain differ")
            value = float(row["value"]) if row["value"] != "" else float("nan")
            if np.isinf(value) or (
                declaration["grain"] == "bundle" and not np.isfinite(value)
            ):
                raise ImmutableIndicatorSetError(
                    "indicator value violates declared validity"
                )
            actual.append((row["indicator"], row["location"], row[key]))
    if len(actual) != len(set(actual)) or sorted(actual) != [
        tuple(key) for key in expected_keys
    ]:
        raise ImmutableIndicatorSetError(
            "indicator keys differ from exact expected result keys"
        )


def read_indicator_set(experiment_root, manifest_path, *, integrity_only=False):
    """Read only the selected immutable set, with named malformed-state refusals."""
    try:
        marker = Path(manifest_path)
        if not marker.is_file():
            raise ImmutableIndicatorSetError(
                f"indicator set {manifest_path}: missing completion receipt indicators.json"
            )
        if (
            marker.parent.parent.name in ("indicator_sets", "metric_sets")
            and marker.parent.parent.parent.name == "_engine"
        ):
            expected_marker = (
                "metrics.json"
                if marker.parent.parent.name == "metric_sets"
                else "indicators.json"
            )
            if marker.name != expected_marker:
                raise ImmutableIndicatorSetError(
                    f"indicator set {manifest_path}: the engine marker is named "
                    "indicators.json; another file in the set is not a marker"
                )
            return _read_indicator_set_v2(
                experiment_root, marker, integrity_only=integrity_only
            )
        raise ImmutableIndicatorSetError(
            f"indicator set {manifest_path}: not an engine marker under "
            "_engine/indicator_sets/; the pre-release v1 indicator-set layout is not read"
        )
    except ImmutableIndicatorSetError:
        raise
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise ImmutableIndicatorSetError(
            f"indicator set {manifest_path}: {exc}"
        ) from exc


def _read_indicator_set_v2(experiment_root, marker, *, integrity_only=False):
    root = Path(experiment_root).resolve()
    manifest = read_canonical_json(marker)
    legacy = marker.parent.parent.name == "metric_sets"
    prefix = "metric" if legacy else "indicator"
    if (
        manifest.get("schema_version")
        not in tuple(f"{prefix}-set/{v}" for v in (3, 4, 5))
        or manifest.get("status") != "ready"
    ):
        raise ImmutableIndicatorSetError("unsupported or unready indicator set")
    digest_key = f"{prefix}s_manifest_sha256"
    if content_sha256(
        {k: v for k, v in manifest.items() if k != digest_key}
    ) != manifest.get(digest_key):
        raise ImmutableIndicatorSetError("indicator manifest digest differs")
    if content_sha256(manifest["identity_projection"]) != manifest[f"{prefix}_set_id"]:
        raise ImmutableIndicatorSetError("indicator-set identity projection differs")
    if manifest.get("schema_version") == f"{prefix}-set/5":
        if (
            content_sha256(manifest["execution_context"][f"{prefix}_definition"])
            != (manifest["identity_projection"][f"{prefix}_definition_sha256"])
        ):
            raise ImmutableIndicatorSetError(
                "saved execution context differs from publication identity"
            )
    if legacy:
        manifest = indicator_names(manifest)
    version = manifest.get("schema_version")
    if (
        version not in ("indicator-set/3", "indicator-set/4", "indicator-set/5")
        or manifest.get("status") != "ready"
    ):
        raise ImmutableIndicatorSetError(
            "unsupported or unready indicator set; legacy mixed-ID indicator sets must be recomputed from a new simulation"
        )
    if version == "indicator-set/5":
        context = manifest["execution_context"]
        request = context["request"]
        if (
            request["declarations"] != manifest["declarations"]
            or request["calculations"] != manifest["calculations"]
            or context["indicator_definition"]["declarations"]
            != request["declarations"]
        ):
            raise ImmutableIndicatorSetError(
                "saved execution context differs from publication identity"
            )
    if (
        manifest["identity_projection"]["groups"] != manifest["groups"]
        or manifest["identity_projection"]["run_groups"] != manifest["run_groups"]
    ):
        raise ImmutableIndicatorSetError(
            "indicator-set membership differs from identity"
        )
    short = identity_segment(manifest["indicator_set_id"], "indicator_set_id")
    if (
        marker.parent.name != short
        or manifest["engine_root"] != f"_engine/{prefix}_sets/{short}"
    ):
        raise ImmutableIndicatorSetError("indicator-set engine identity differs")
    result_relative = manifest["result_root"]
    # Read-only /3 sets may occupy a legacy results/<digest>/ root; /4 never does.
    allowed_roots = [f"_engine/{prefix}_sets/{short}/data"]
    if version == "indicator-set/3":
        allowed_roots.append(f"results/{prefix}_sets/{short}")
    if result_relative not in allowed_roots:
        raise ImmutableIndicatorSetError("indicator-set result identity differs")
    if version in ("indicator-set/4", "indicator-set/5"):
        if manifest["identity_projection"].get("schema_version") != (
            "indicator-set-identity/5"
            if version == "indicator-set/5"
            else "indicator-set-identity/4"
        ):
            raise ImmutableIndicatorSetError(
                "indicator-set/4 identity projection version differs"
            )
        # Structural only: an immutable record stays readable after later code
        # changes, so it is never re-derived against the live registry here.
        if [item["indicator"] for item in manifest["calculations"]] != [
            item["name"] for item in manifest["declarations"]
        ]:
            raise ImmutableIndicatorSetError(
                "indicator-set calculations and declarations name different indicators"
            )
    engine = root / manifest["engine_root"]
    result = root / manifest["result_root"]
    if (
        marker.absolute() != engine / f"{prefix}s.json"
        or marker.resolve() != marker.absolute()
        or engine.resolve() != engine
        or result.resolve() != result
    ):
        raise ImmutableIndicatorSetError(
            "indicator-set directory is aliased or outside experiment"
        )
    if manifest["response_inventory"]["path"] != "../../response_inventory.json":
        raise ImmutableIndicatorSetError("indicator inventory reference differs")
    artifacts = [manifest["environment"], manifest["return_level_benchmark"]]
    if version == "indicator-set/5":
        if manifest["diagnostics"]["path"] != f"{prefix}_diagnostics.json":
            raise ImmutableIndicatorSetError("diagnostic artifact reference differs")
        artifacts.append(manifest["diagnostics"])
    if manifest["return_level_evidence"]["path"] != RETURN_LEVEL_EVIDENCE_FILENAME:
        raise ImmutableIndicatorSetError("return-level evidence reference differs")
    artifacts.append(manifest["return_level_evidence"])
    if version in ("indicator-set/4", "indicator-set/5"):
        if manifest["coverage_evidence"]["path"] != COVERAGE_EVIDENCE_FILENAME:
            raise ImmutableIndicatorSetError("coverage evidence reference differs")
        artifacts.append(manifest["coverage_evidence"])
    for item in artifacts:
        if file_sha256(engine / item["path"]) != item["sha256"]:
            raise ImmutableIndicatorSetError(
                f"indicator artifact differs: {item['path']}"
            )
    lookup = result / "group_members.csv"
    if manifest["group_members"]["path"] != (f"{result_relative}/group_members.csv"):
        raise ImmutableIndicatorSetError("indicator lookup reference differs")
    if file_sha256(lookup) != manifest["group_members"]["sha256"]:
        raise ImmutableIndicatorSetError("indicator lookup differs")
    with lookup.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["group_id", "run_id"]:
            raise ImmutableIndicatorSetError("indicator lookup schema differs")
        members = list(reader)
    declared_members = [
        {"group_id": row["run_group_id"], "run_id": row["run_id"]}
        for row in manifest["run_groups"]
        if row["grain"] == "bundle"
    ]
    if members != declared_members or len(
        {tuple(row.values()) for row in members}
    ) != len(members):
        raise ImmutableIndicatorSetError(
            "group membership differs or contains duplicates"
        )
    metadata = result / "group_metadata.csv"
    if (
        manifest["group_metadata"]["path"] != f"{result_relative}/group_metadata.csv"
        or file_sha256(metadata) != manifest["group_metadata"]["sha256"]
    ):
        raise ImmutableIndicatorSetError("group metadata reference or bytes differ")
    with metadata.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["group_id", "st_id", "is_reference"]:
            raise ImmutableIndicatorSetError("group metadata schema differs")
        metadata_rows = list(reader)
    expected_metadata = [
        {"group_id": group, "st_id": key, "is_reference": str(not key).lower()}
        for key, group in zip(
            sorted(manifest["groups"]), sorted({row["group_id"] for row in members})
        )
    ]
    if metadata_rows != expected_metadata:
        raise ImmutableIndicatorSetError("group metadata differs from grouping keys")
    tables = {}
    seen = set()
    for item in manifest["tables"]:
        scope = item["scope"]
        if scope not in ("run", "group") or (item["token"], scope) in seen:
            raise ImmutableIndicatorSetError(
                "duplicate or unknown indicator table scope"
            )
        seen.add((item["token"], scope))
        if item["file"]["path"] != (
            f"{result_relative}/{item['token']}_{scope}_indicators.csv"
        ):
            raise ImmutableIndicatorSetError("indicator table reference differs")
        path = result / Path(item["file"]["path"]).name
        if file_sha256(path) != item["file"]["sha256"]:
            raise ImmutableIndicatorSetError("indicator table differs")
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != [
                prefix,
                "location",
                f"{scope}_id",
                "value",
            ]:
                raise ImmutableIndicatorSetError("indicator table schema differs")
            scoped_rows = list(reader)
            if legacy:
                scoped_rows = [indicator_names(row) for row in scoped_rows]
            if any(
                not row[f"{scope}_id"].startswith(f"{scope}_") for row in scoped_rows
            ):
                raise ImmutableIndicatorSetError(
                    "indicator table ID does not match its scope"
                )
            tables.setdefault(item["token"], []).extend(
                {
                    **{k: v for k, v in row.items() if k != f"{scope}_id"},
                    "run_group_id": row[f"{scope}_id"],
                }
                for row in scoped_rows
            )
    tokens = {
        item["required_responses"]["variable"] for item in manifest["declarations"]
    }
    if seen != {(token, scope) for token in tokens for scope in ("run", "group")}:
        raise ImmutableIndicatorSetError("indicator table scopes are incomplete")
    if integrity_only:
        # Only saved declarations, membership and key structure are needed.
        # Availability of the original simulation inputs is a numerical concern.
        runs = {
            row["run_id"] for row in manifest["run_groups"] if row["grain"] == "run"
        }
        locations = {}
        by_name = {item["name"]: item for item in manifest["declarations"]}
        for indicator, location, _ in manifest["expected_result_keys"]:
            declaration = by_name[indicator]
            locations.setdefault(
                declaration["required_responses"]["variable"], set()
            ).add(location)
        inventory = {
            "series": [
                {"run_id": run, "variable": token, "location_id": location}
                for token, values in locations.items()
                for location in values
                for run in runs
            ],
            "response_inventory_sha256": manifest["response_inventory"]["sha256"],
        }
    else:
        from blueearth_cst.experiment.simulation_record import read_simulation_v2
        from blueearth_cst.shared.workflow_config_snapshot import resolve_file_reference

        # The canonical readiness check validates native bytes and selectors.
        # Follow its checked inventory reference without rebuilding them twice.
        simulation = read_simulation_v2(root)
        inventory = read_canonical_json(
            resolve_file_reference(
                simulation["response_inventory"], {"project_root": root.parent.parent}
            )
        )
    runs = {item["run_id"] for item in inventory["series"]}
    group_ids = {row["group_id"] for row in members}
    if {row["run_id"] for row in members} != runs or any(
        not row["group_id"].startswith("group_") for row in members
    ):
        raise ImmutableIndicatorSetError(
            "group membership differs from retained evaluated runs"
        )
    locations = {}
    for item in inventory["series"]:
        locations.setdefault(item["variable"], set()).add(item["location_id"])
    expected_keys = sorted(
        [declaration["name"], location, unit]
        for declaration in manifest["declarations"]
        for location in locations[declaration["required_responses"]["variable"]]
        for unit in (runs | group_ids if declaration["grain"] == "run" else group_ids)
    )
    if manifest["expected_result_keys"] != expected_keys:
        raise ImmutableIndicatorSetError(
            "indicator keys differ from declarations and retained locations"
        )
    _validate_tables(
        tables,
        expected_keys,
        {item["name"]: item for item in manifest["declarations"]},
        manifest["run_groups"],
    )
    if (
        manifest["response_inventory"]["sha256"]
        != inventory["response_inventory_sha256"]
    ):
        raise ImmutableIndicatorSetError(
            "indicator set differs from retained responses"
        )
    return manifest
