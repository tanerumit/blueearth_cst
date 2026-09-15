"""Reproduce R12 GF9 comparisons without modifying either numerical run.

Use --development for exploratory outputs; it cannot produce acceptance evidence.
Final acceptance also needs reviewed final run provenance and the GF27/28/31 gates.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import sys
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xarray as xr
import yaml

REPOSITORY = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(REPOSITORY))

from blueearth_cst.experiment.forcing_descriptor import (  # noqa: E402
    collection_forcing_descriptor,
    describe_ancillary,
)
from blueearth_cst.experiment.metric_plan import read_metric_set  # noqa: E402
from blueearth_cst.experiment.metric_registry import (  # noqa: E402
    declarations,
    resolve_month_reference,
)
from blueearth_cst.experiment.response_inventory import (  # noqa: E402
    read_response_inventory,
)
from blueearth_cst.experiment.scenario_collection import read_collection  # noqa: E402
from blueearth_cst.experiment.simulation_record import read_simulation  # noqa: E402
from blueearth_cst.experiment.wflow_response_reader import (  # noqa: E402
    NativeRunArtifacts,
    ResponseRequest,
    open_responses,
)
from blueearth_cst.shared.config_composition import compose_config  # noqa: E402
from dev.scripts.check_baseline import (  # noqa: E402
    INDICATOR_ATOL_FRAC,
    INDICATOR_RTOL,
    compare_indicator_table,
    read_indicator_table,
)


def sha256(path: Path) -> str:
    """Hash bytes without loading an entire large artifact."""
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def document(path: Path) -> Any:
    """Read the recorded JSON document."""
    return json.loads(path.read_text(encoding="utf-8"))


def records(path: Path) -> list[dict[str, str]]:
    """Preserve textual IDs, including leading zeroes and empty grouping keys."""
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str) -> None:
    """Fail a gate even if Python runs with assertions disabled."""
    if not condition:
        raise ValueError(message)


def formatted(value: float) -> str:
    """Independently apply the unchanged float32/four-significant-digit format."""
    return np.format_float_positional(
        np.float32(value), precision=4, unique=False, fractional=False, trim="-"
    )


def old_integrity(old_root: Path, old_records: Path) -> dict[str, Any]:
    """Recheck every file in the accepted fresh P0 output inventory."""
    path = old_records / "prechange-completeness.json"
    inventory = document(path)
    failures = []
    for relative, expected in inventory["artifacts"].items():
        target = old_root / relative
        if not target.is_file():
            failures.append(f"missing: {relative}")
        elif (
            target.stat().st_size != expected["bytes"]
            or sha256(target) != expected["sha256"]
        ):
            failures.append(f"changed: {relative}")
    actual = {
        p.relative_to(old_root).as_posix() for p in old_root.rglob("*") if p.is_file()
    }
    failures.extend(
        f"uninventoried: {p}" for p in sorted(actual - set(inventory["artifacts"]))
    )
    require(not failures, f"P0 integrity failed: {failures}")
    provenance_path = old_records / "prechange-provenance.json"
    provenance = document(provenance_path)
    return {
        "root": str(old_root),
        "file_count": len(actual),
        "inventory_sha256": sha256(path),
        "provenance_sha256": sha256(provenance_path),
        "source_commit": provenance["source_commit"],
        "source_inventory_sha256": provenance["production_inventory_sha256"],
        "config_files_sha256": provenance["config_files_sha256"],
        "python": provenance["python"],
        "python_packages": provenance["python_packages"],
    }


def scientific_settings(
    old_root: Path, new_config: Path, collection_root: Path, experiment: Path
) -> dict[str, Any]:
    """Compare frozen scientific settings through the approved configuration split."""
    frozen_path = old_root.parent / "config/scientific-config.json"
    frozen = document(frozen_path)
    old = frozen["composed_scientific_config"]
    composed, sources = compose_config(
        yaml.safe_load(new_config.read_text()), new_config
    )
    # Workflow enablement, experiment names and storage selectors are orchestration.
    # All physical basin/climate/model settings must still match this reference.
    for section in ("basin", "climate", "model"):
        require(
            composed.get(section) == old.get(section),
            f"scientific config differs: {section}",
        )
    generation = document(collection_root / "generation_config.json")
    before = old["workflows"]["run_stress_test"]
    require(
        generation["seed"]["resolved"] == frozen["resolved_seed"],
        "resolved seed differs from P0",
    )
    require(
        generation["climate_perturbations"] == before["climate_perturbations"],
        "perturbation settings differ",
    )
    old_generator = yaml.safe_load(
        (
            old_root
            / "experiments/experiment/climate/weathergenr/config/weathergen_config.yml"
        ).read_text()
    )
    new_generator = copy.deepcopy(generation["weathergen"])
    for payload in (old_generator, new_generator):
        payload["generate_weather"].pop("out_dir", None)
        for key in ("out_dir", "file_prefix", "file_suffix"):
            payload["write_netcdf"].pop(key, None)
    require(
        old_generator == new_generator,
        "effective generator settings differ beyond declared output locators",
    )
    settings = document(experiment / "config/simulator_settings.json")
    require(
        settings["simulation_window"] == before["simulation_window"],
        "simulation window differs",
    )
    require(
        composed["workflows"]["generate_scenarios"]["n_realizations"]
        == before["n_realizations"],
        "realization count differs",
    )
    return {
        "frozen_scientific_config_sha256": sha256(frozen_path),
        "recorded_scientific_payload_sha256": frozen["sha256"],
        "new_config_sha256": sha256(new_config),
        "new_config_sources": sources,
        "new_composed_config": composed,
        "resolved_seed": generation["seed"]["resolved"],
        "effective_generator_settings_equal": True,
    }


def reference_invariance(
    native: dict[str, NativeRunArtifacts], roots: list[str]
) -> dict[str, Any]:
    """Reverse native-artifact enumeration and neutral-series order independently."""
    variants = {}
    baseline = None
    for artifact_reverse, series_reverse in (
        (False, False),
        (True, False),
        (False, True),
        (True, True),
    ):
        order = list(reversed(roots)) if artifact_reverse else roots
        series = tuple(
            item
            for run in order
            for item in open_responses(run, native[run], ResponseRequest(("q",)))
        )
        if series_reverse:
            series = tuple(reversed(series))
        resolved = {
            which: asdict(
                resolve_month_reference(series, expected_run_ids=order, which=which)
            )
            for which in ("wet", "dry")
        }
        if baseline is None:
            baseline = resolved
        require(resolved == baseline, "Class-C reference changed under order reversal")
        variants[
            f"artifacts_reverse={artifact_reverse};series_reverse={series_reverse}"
        ] = resolved
    return {"reference": baseline, "variants_equal": len(variants)}


def opposite_season_fixture(scratch: Path) -> dict[str, Any]:
    """Exercise actual native reading with opposite-season gauges and reversed orders."""
    folder = scratch / "opposite-season"
    folder.mkdir(parents=True, exist_ok=True)
    time = pd.date_range("2019-01-02", "2022-12-31")
    curve = np.array([1, 2, 4, 6, 8, 10, 14, 11, 8, 5, 3, 2], dtype=float)
    native = {}
    for run, multiplier in (("01", 1), ("08", 2)):
        csv_path, toml_path = (
            folder / f"opaque-{run}.csv",
            folder / f"reader-{run}.toml",
        )
        pd.DataFrame(
            {
                "time": time,
                "Q_9": multiplier * curve[time.month - 1],
                "Q_2": multiplier * (16 - curve[time.month - 1]),
            }
        ).to_csv(csv_path, index=False)
        toml_path.write_text(
            '[time]\ncalendar="standard"\ntimestepsecs=86400\nstarttime="2019-01-01T00:00:00"\nendtime="2022-12-31T00:00:00"\n[[output.csv.column]]\nheader="Q"\nparameter="river_water__volume_flow_rate"\n',
            encoding="utf-8",
        )
        native[run] = NativeRunArtifacts(csv_path, toml_path)
    report = reference_invariance(native, ["01", "08"])
    ref = report["reference"]
    require(
        (ref["wet"]["reference_location_id"], ref["wet"]["month"], ref["dry"]["month"])
        == ("9", 7, 1),
        "opposite-season fixture does not select native-first gauge",
    )
    series = tuple(
        item
        for run in native
        for item in open_responses(run, native[run], ResponseRequest(("q",)))
    )
    swapped = tuple(
        replace(item, location_ordinal=1 - item.location_ordinal) for item in series
    )
    wrong = resolve_month_reference(swapped, expected_run_ids=["01", "08"], which="wet")
    require(
        (wrong.reference_location_id, wrong.month) == ("2", 1),
        "fixture does not discriminate wrong-gauge selection",
    )
    report["wrong_gauge_control"] = {
        "reference_location_id": wrong.reference_location_id,
        "wet_month": wrong.month,
    }
    report["opposite_peaks"] = {"9": 7, "2": 1}
    report["retained_ordinals"] = {"9": 0, "2": 1}
    report["leap_day_present"] = bool(pd.Timestamp("2020-02-29") in time)
    return report


def compare(args: argparse.Namespace) -> dict[str, Any]:
    """Check a complete successor against immutable P0 and report every crosswalk."""
    old_root, experiment = args.old_root.resolve(), args.new_experiment.resolve()
    scratch = args.scratch.resolve()
    for output in (scratch, args.report.resolve()):
        require(
            not output.is_relative_to(old_root)
            and not output.is_relative_to(experiment),
            "comparison outputs must be outside both numerical runs",
        )
    scratch.mkdir(parents=True, exist_ok=True)
    old_report = old_integrity(old_root, args.old_records.resolve())
    old_experiment = old_root / "experiments/experiment"
    simulation = document(experiment / "config/simulation.json")
    inventory = document(experiment / "responses/response_inventory.json")
    marker = args.metric_manifest.resolve()
    manifest = document(marker)
    collection_root = Path(simulation["collection"]["manifest_path"]).parent
    collection = read_collection(
        collection_root / "collection.json",
        describe_forcing=collection_forcing_descriptor,
        describe_ancillary=describe_ancillary,
    )
    if not args.development:
        read_simulation(experiment, require_complete=True)
        read_response_inventory(experiment)
        read_metric_set(experiment, marker)
    rows = records(collection_root / "scenario_table.csv")
    require(
        all(row["evaluated"] == "true" for row in rows),
        "P0 comparator requires the same evaluated member set",
    )
    members = {(row["rlz"], row["st_id"] or "0"): row["run_id"] for row in rows}
    require(len(members) == len(rows), "duplicate scenario payload mapping")
    roots = [row["run_id"] for row in rows if not row["derived_from"]]
    by_run = {row["run_id"]: row for row in rows}
    forcing = {item["run_id"]: item for item in collection["forcing"]}
    native, native_report, forcing_report = {}, [], []
    artifact_by_run = {item["run_id"]: item for item in inventory["artifacts"]}
    for row in rows:
        run = row["run_id"]
        old_member = f"rlz_{row['rlz']}_st_{row['st_id'] or '0'}"
        original = old_experiment / "climate/weathergenr/output" / f"{old_member}.nc"
        current = collection_root / forcing[run]["path"]
        with xr.open_dataset(original) as before, xr.open_dataset(current) as after:
            xr.testing.assert_identical(before, after)
            forcing_report.append(
                {
                    "run_id": run,
                    "old_member": old_member,
                    "values_grid_time_attributes_exact": True,
                    "bytes_exact": sha256(original) == sha256(current),
                    "calendar": str(after.time.dt.calendar),
                    "start": str(after.time.values[0]),
                    "end": str(after.time.values[-1]),
                    "steps": len(after.time),
                }
            )
        original = old_experiment / "hydrology/wflow/output" / f"{old_member}.csv"
        current = (experiment / "responses" / artifact_by_run[run]["path"]).resolve()
        before, after = pd.read_csv(original), pd.read_csv(current)
        pd.testing.assert_frame_equal(before, after, check_exact=True)
        selector = next(
            item["native_selector"]
            for item in inventory["series"]
            if item["run_id"] == run
        )
        toml_path = (experiment / "responses" / selector["toml_path"]).resolve()
        native[run] = NativeRunArtifacts(current, toml_path)
        native_report.append(
            {
                "run_id": run,
                "old_member": old_member,
                "values_time_exact": True,
                "bytes_exact": sha256(original) == sha256(current),
                "sha256": sha256(current),
                "rows": len(after),
                "columns": list(after.columns),
                "start": str(after.time.iloc[0]),
                "end": str(after.time.iloc[-1]),
            }
        )
    settings = scientific_settings(
        old_root, args.new_config.resolve(), collection_root, experiment
    )
    old_model = yaml.safe_load(
        (old_experiment / "config/model_reference.yml").read_text()
    )
    require(
        simulation["model"]["model_digest"] == old_model["digest"],
        "model digest differs from fresh P0",
    )
    unit_rows = records(marker.parent / "unit_index.csv")
    require(
        len({(r["unit_id"], r["member_run_id"]) for r in unit_rows}) == len(unit_rows),
        "duplicate unit-index join",
    )
    run_units = {
        r["member_run_id"]: r["unit_id"] for r in unit_rows if r["grain"] == "run"
    }
    require(
        run_units == {run: run for run in by_run},
        "run units lack exact self membership",
    )
    bundles = {}
    for row in unit_rows:
        if row["grain"] == "bundle":
            bundles.setdefault(row["unit_id"], []).append(row["member_run_id"])
    groups = {}
    for row in rows:
        groups.setdefault(row["st_id"] or "0", []).append(row["run_id"])
    group_units = {}
    for group, runs in groups.items():
        matches = [
            unit for unit, values in bundles.items() if values == sorted(runs, key=int)
        ]
        require(len(matches) == 1, f"no unique pooled bundle crosswalk: {group}")
        group_units[group] = matches[0]
    declarations_by_name = {item["name"]: item for item in manifest["declarations"]}
    registry = {
        item.name: item
        for item in declarations([t["token"] for t in manifest["indicator_tables"]])
    }
    new_rows = [
        row
        for table in manifest["indicator_tables"]
        for row in records(marker.parent / table["path"])
    ]
    new_keys = {(r["metric"], r["location"], r["unit_id"]): r for r in new_rows}
    require(len(new_keys) == len(new_rows), "duplicate new metric key")
    require(
        set(new_keys) == set(map(tuple, manifest["expected_result_keys"])),
        "published expected keys differ",
    )
    old_tables = [
        read_indicator_table(
            str(old_experiment / "results" / f"{t['token']}_indicators.csv")
        )
        for t in manifest["indicator_tables"]
    ]
    old = pd.concat(old_tables, ignore_index=True)
    require(
        not old.drop(columns="value").duplicated().any(), "duplicate old metric key"
    )
    used, projected, mapping = set(), [], []
    raw_c_checks = []
    anchor = manifest["metric_definition"]["water_year_anchor"]
    for row in old.to_dict("records"):
        key = (row["metric"], row["location"])
        declaration = declarations_by_name[row["metric"]]
        if row["rlz_id"] != "0":
            require(
                declaration["grain"] == "run" and declaration["reference"] is None,
                "old run row changed class",
            )
            units = [run_units[members[(row["rlz_id"], row["st_id"])]]]
            kind = "A"
        elif declaration["grain"] == "bundle":
            units = [group_units[row["st_id"]]]
            kind = "B"
        else:
            require(
                declaration["reference"] is not None,
                "unexplained pooled-to-run migration",
            )
            units = [run_units[run] for run in groups[row["st_id"]]]
            kind = "C"
        keys = [(*key, unit) for unit in units]
        require(all(k in new_keys for k in keys), f"lost new row: {keys}")
        require(not used.intersection(keys), f"duplicate crosswalk consumption: {keys}")
        used.update(keys)
        value = float(np.mean([float(new_keys[k]["value"]) for k in keys]))
        projected.append({**row, "value": value})
        mapping.append(
            {
                "class": kind,
                "old": [row[k] for k in ("metric", "location", "st_id", "rlz_id")],
                "new": [list(k) for k in keys],
                "old_value": row["value"],
                "new_projection": value,
                "absolute_difference": abs(value - row["value"]),
            }
        )
        if kind == "C":
            definition = registry[row["metric"]]
            which = "wet" if definition.statistic == "wetmonth_mean" else "dry"
            month = manifest["resolved_references"][which]["month"]
            raw_values = []
            for run, new_key in zip(groups[row["st_id"]], keys):
                frame = pd.read_csv(native[run].csv_path, index_col=0, parse_dates=True)
                raw = (
                    frame.loc[frame.index.month == month, "Q_" + row["location"]]
                    .resample(anchor)
                    .mean()
                    .mean()
                )
                require(
                    formatted(raw) == new_keys[new_key]["value"],
                    f"Class-C independent run calculation differs: {new_key}",
                )
                raw_values.append(raw)
            require(
                float(formatted(float(np.mean(raw_values)))) == row["value"],
                f"Class-C raw mean relation fails: {key}",
            )
            raw_c_checks.append(
                {
                    "metric": row["metric"],
                    "location": row["location"],
                    "st_id": row["st_id"],
                    "raw_mean_at_publication_precision_exact": True,
                }
            )
    require(
        used == set(new_keys), f"unaccounted new rows: {sorted(set(new_keys) - used)}"
    )
    current = pd.DataFrame(projected, columns=old.columns)
    # GF-9 assigns the predecessor table tolerance to Classes A/B. Class C
    # changes publication grain: mean(round(each run)) need not equal
    # round(mean(raw runs)). Above, independently calculated raw values must
    # reproduce every published run value and the old pooled value exactly at
    # the unchanged publication precision. Keep rounded-mean deltas in mapping.
    ab_rows = [index for index, item in enumerate(mapping) if item["class"] != "C"]
    old_ab = old.iloc[ab_rows].reset_index(drop=True)
    current_ab = current.iloc[ab_rows].reset_index(drop=True)
    comparison = compare_indicator_table(old_ab, current_ab)
    require(
        comparison["ok"], f"GF9 established indicator tolerance failure: {comparison}"
    )
    # Deliberate wrong-answer controls prove the numeric and row checks discriminate.
    changed = current_ab.copy(deep=True)
    changed.loc[0, "value"] += max(1.0, abs(float(changed.loc[0, "value"])))
    require(
        not compare_indicator_table(old_ab, changed)["ok"],
        "numeric comparator did not discriminate",
    )
    require(
        not compare_indicator_table(old_ab, current_ab.iloc[:-1])["ok"],
        "lost-row comparator did not discriminate",
    )
    require(
        not compare_indicator_table(
            old_ab, pd.concat([current_ab, current_ab.iloc[:1]], ignore_index=True)
        )["ok"],
        "duplicate-row comparator did not discriminate",
    )
    reversal = reference_invariance(native, roots)
    require(
        json.loads(json.dumps(reversal["reference"]))
        == manifest["resolved_references"],
        "persisted reference differs from independent reversal check",
    )
    class_report = {}
    for kind in ("A", "B", "C"):
        subset = [item for item in mapping if item["class"] == kind]
        class_report[kind] = {
            "old_rows": len(subset),
            "new_rows": sum(len(item["new"]) for item in subset),
            "max_absolute_difference": max(
                item["absolute_difference"] for item in subset
            ),
        }
    return {
        "status": "DEVELOPMENT_ONLY"
        if args.development
        else "COMPARISON_PASSED_PENDING_SIGNED_REVIEW",
        "comparator_sha256": sha256(Path(__file__)),
        "old": old_report,
        "settings": settings,
        "new": {
            "experiment": str(experiment),
            "simulation": simulation,
            "collection_id": collection["collection_id"],
            "collection_revision": collection["collection_revision"],
            "metric_set_id": manifest["metric_set_id"],
            "response_inventory_sha256": inventory["response_inventory_sha256"],
            "metric_manifest_sha256": sha256(marker),
            "source_inventory": document(collection_root / "source_inventory.json"),
            "generation_code": document(
                collection_root / "provider_code_inventory.json"
            ),
            "generation_environment": document(
                collection_root / "generation_environment.json"
            ),
            "simulation_environment": document(
                experiment / "config/simulation_environment.json"
            ),
            "metric_environment": document(
                marker.parent / manifest["metric_environment"]["path"]
            ),
        },
        "forcing": forcing_report,
        "native": native_report,
        "run_crosswalk": [
            {"old_rlz": pair[0], "old_st_id": pair[1], "run_id": run}
            for pair, run in sorted(
                members.items(), key=lambda item: (int(item[0][0]), int(item[0][1]))
            )
        ],
        "pooled_crosswalk": [
            {
                "old_rlz_id": "0",
                "old_st_id": group,
                "bundle_unit_id": unit,
                "members": bundles[unit],
            }
            for group, unit in sorted(
                group_units.items(), key=lambda item: int(item[0])
            )
        ],
        "metrics": {
            "old_rows": len(old),
            "new_rows": len(new_rows),
            "unmatched_old": [],
            "unmatched_new": [],
            "duplicate_joins": 0,
            "class_summary": class_report,
            "tolerance": {
                "classes": ["A", "B"],
                "INDICATOR_RTOL": INDICATOR_RTOL,
                "INDICATOR_ATOL_FRAC": INDICATOR_ATOL_FRAC,
                "grouping": ["metric", "location"],
                "logic": "reject absolute exceedance OR applicable relative exceedance; not additive np.isclose",
            },
            "comparison": comparison,
            "crosswalk": mapping,
            "independent_class_c_mean": raw_c_checks,
        },
        "actual_reference_reversal": reversal,
        "opposite_season_fixture": opposite_season_fixture(scratch),
        "discrimination": {
            "numeric_perturbation_rejected": True,
            "lost_row_rejected": True,
            "duplicate_row_rejected": True,
        },
        "temporal_preparation": inventory["temporal_preparation"],
        "return_level_validation": manifest["return_level_validation"],
        "return_level_evidence": manifest["return_level_evidence"],
        "additional_gates": "GF27 capacity/seed forcing executions, bounded GF28, GF31 and final run provenance require separate signed assessment; no GF15 adequacy approval",
    }


def main() -> None:
    """Run the comparator and emit a report only after every assertion passes."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in (
        "old-root",
        "old-records",
        "new-experiment",
        "new-config",
        "metric-manifest",
        "scratch",
        "report",
    ):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--development", action="store_true")
    args = parser.parse_args()
    result = compare(args)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "old_files": result["old"]["file_count"],
                "classes": result["metrics"]["class_summary"],
                "indicator_comparison": result["metrics"]["comparison"],
                "report": str(args.report),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
