"""Response-dependent metric identities, complete keys and immutable result sets."""

import csv
import io
import json
import os
from dataclasses import asdict
from pathlib import Path

import numpy as np

from blueearth_cst.experiment import gev_lmoments, return_level_validation
from blueearth_cst.experiment.content_identity import (
    canonical_json_bytes,
    confined_path,
    content_sha256,
    identity_segment,
    read_canonical_json,
    repository_code_inventory,
)
from blueearth_cst.experiment.metric_groups import metric_groups
from blueearth_cst.experiment.metric_registry import (
    DeclaredBundle,
    declarations,
    metric_unit_index,
    reduce_bundle,
    reduce_run,
    resolve_month_reference,
)
from blueearth_cst.experiment.response_inventory import (
    read_response_inventory,
    read_response_inventory_v2,
)
from blueearth_cst.experiment.scenario_collection import read_collection
from blueearth_cst.experiment.scenario_rows import ScenarioRow
from blueearth_cst.experiment.simulation_record import (
    atomic_record,
    read_simulation,
    read_simulation_intent_v2,
    read_simulation_v2,
)
from blueearth_cst.experiment.wflow_response_reader import (
    NativeRunArtifacts,
    ResponseRequest,
    open_responses,
)
from blueearth_cst.shared.provenance import file_sha256
from blueearth_cst.shared.snake_utils import log_row, plural


class MetricPlanStale(ValueError):
    """A scheduling plan cannot certify the requested live inputs or responses."""


class MetricsOnlyIdentityMismatch(ValueError):
    """An explicit collection assertion differs from the retained simulation."""


class ImmutableMetricSetError(ValueError):
    """A result set is partial, changed or fails its declared complete key set."""


def _plain(value):
    """Convert known dataclass tuple fields to the persisted JSON array dialect."""
    return json.loads(json.dumps(value, allow_nan=False))


def metrics_only_configuration(config_path):
    """Read only the selected experiment and metric settings.

    This projection never opens generation or model workflow files.
    """
    import yaml

    from blueearth_cst.shared.indicator_tables import indicator_tables
    from blueearth_cst.shared.snake_utils import (
        resolve_water_year_start,
        validate_experiment_name,
    )

    path = Path(config_path).resolve()
    project = yaml.safe_load(path.read_text(encoding="utf-8"))
    descriptor = project["workflows"]["simulate_system"]
    if set(descriptor) != {"enabled", "config_path"} or not isinstance(
        descriptor["enabled"], bool
    ):
        raise ValueError("metrics-only requires an enabled simulate_system config_path")
    workflow = yaml.safe_load(
        (path.parent / descriptor["config_path"]).read_text(encoding="utf-8")
    )
    project_root = Path(project["project"]["project_dir"]).resolve()
    name = validate_experiment_name(workflow["experiment_name"], project_root)
    root = project_root / "experiments" / name
    v2 = (root / "_engine/simulation.json").is_file()
    simulation = (
        read_simulation_v2(root) if v2 else read_simulation(root, require_complete=True)
    )
    intent_v2 = read_simulation_intent_v2(root) if v2 else None
    retained_collection = intent_v2["collection"] if v2 else simulation["collection"]
    if "scenario_collection" in workflow:
        if v2:
            asserted = workflow["scenario_collection"]
            retained = retained_collection
            for field in ("collection_id", "collection_revision"):
                if asserted.get(field) not in (None, retained[field]):
                    raise MetricsOnlyIdentityMismatch(
                        f"{field}: retained={retained[field]!r}; asserted={asserted[field]!r}"
                    )
        else:
            from blueearth_cst.experiment.collection_resolution import (
                resolve_explicit_collection,
            )
            from blueearth_cst.experiment.forcing_descriptor import (
                collection_forcing_descriptor,
            )
            from blueearth_cst.experiment.wf4_ancillary_descriptor import (
                describe_ancillary,
            )

            selection, _ = resolve_explicit_collection(
                workflow["scenario_collection"],
                describe_forcing=collection_forcing_descriptor,
                describe_ancillary=describe_ancillary,
            )
            retained = simulation["collection"]
            for field in ("collection_id", "collection_revision"):
                expected = retained[field]
                if selection[field] != expected:
                    raise MetricsOnlyIdentityMismatch(
                        f"{field}: retained={expected!r}; asserted={selection[field]!r}"
                    )
    tokens = workflow.get("metrics")
    if tokens is None:
        outvars = (project.get("model") or {}).get("outvars")
        if outvars is not None:
            tokens = list(indicator_tables(outvars))
        else:
            request = (
                intent_v2["documents"]["response_request"]
                if v2
                else read_canonical_json(root / "config/response_request.json")
            )
            tokens = [item["variable"] for item in request["variables"]]
    climate = project.get("climate") or {}
    anchor = f"YS-{resolve_water_year_start(climate.get('water_year_start')).upper()}"
    ignored = [
        f"simulate_system.{key}"
        for key in sorted(workflow)
        if key not in {"experiment_name", "metrics", "scenario_collection"}
    ]
    ignored += [
        f"climate.{key}" for key in sorted(climate) if key != "water_year_start"
    ]
    ignored += [
        f"model.{key}"
        for key in sorted(project.get("model") or {})
        if key != "outvars" or workflow.get("metrics") is not None
    ]
    if ignored:
        print(
            "metrics-only: ignored current settings "
            + ", ".join(ignored)
            + f"; retained simulation/model inputs come from {(root / ('_engine/simulation.json' if v2 else 'config/simulation.json')).as_posix()}"
            + f" and generation inputs from {retained_collection.get('manifest_path', retained_collection.get('manifest', {}).get('path', 'retained collection'))}",
            flush=True,
        )
    return root, list(tokens), anchor


#: Metric-stage dependency roots. lmoments3 joins them because the return-level
#: estimator is now part of what this stage's identity must describe (D5).
METRIC_ENVIRONMENT_ROOTS = (
    "numpy",
    "pandas",
    "scipy",
    "xarray",
    "xclim",
    "netCDF4",
    "pyproj",
    "PyYAML",
    "lmoments3",
)


def resolve_metric_environment():
    """Observe the LIVE metric-stage environment, including D7 source hashes.

    Always a fresh observation. It is never derived from a retained request, a
    cached planning descriptor or lock-file intent, because the whole point is
    to notice that the executing environment has drifted from the planned one.
    """
    from blueearth_cst.experiment.content_identity import stage_environment

    environment = stage_environment(list(METRIC_ENVIRONMENT_ROOTS))
    return {
        **environment,
        "return_level_estimator": {
            "estimator_id": gev_lmoments.ESTIMATOR_ID,
            "package": "lmoments3",
            "version": gev_lmoments.DEPENDENCY_VERSION,
            "source_sha256": dict(sorted(gev_lmoments.observed_source().items())),
        },
    }


def current_metric_request(experiment_root, tokens, anchor):
    """Resolve stage-three identity without any live source/model or Julia access."""
    root = Path(experiment_root).resolve()
    if (root / "_engine/simulation.json").is_file():
        record = read_simulation_v2(root)
        request = metric_request(
            record["simulation_id"],
            tokens,
            anchor,
            resolve_metric_environment(),
            return_level_validation.build_declaration(),
        )
        request["schema_version"] = "metric-request/2"
        request["simulation_schema_version"] = record["schema_version"]
        return request
    record = read_simulation(root)
    return metric_request(
        record["simulation_id"],
        tokens,
        anchor,
        resolve_metric_environment(),
        return_level_validation.build_declaration(),
    )


def metric_request(simulation_id, tokens, anchor, environment, validation):
    """Compute a scheduling request before response values or reference months exist."""
    registry = declarations(tokens)
    # A NEW request must carry the D4 declaration. Legacy acceptance is a read
    # compatibility guarantee (D6), never a write escape hatch, so the retained
    # pre-C record is refused here rather than silently re-emitted.
    if return_level_validation.is_legacy(validation):
        raise ValueError(
            "the legacy unassessed return-level record cannot be written into a "
            "new metric request; it is readable, not writable"
        )
    return_level_validation.verify_declaration(
        validation, return_level_validation.load_report_bytes()
    )
    directory = Path(__file__).parent
    repo = directory.parents[1]
    code = repository_code_inventory(repo, ["blueearth_cst/experiment/metric_plan.py"])
    return {
        "schema_version": "metric-request/1",
        "simulation_id": simulation_id,
        "tokens": list(tokens),
        "declarations": [_plain(asdict(item)) for item in registry],
        "grouping": "stochastic/st_id including empty unperturbed key",
        "reference": "unperturbed evaluated runs; first native q location; monthly sum; first month on ties",
        "water_year_anchor": anchor,
        "code_inventory": code,
        "metric_environment": environment,
        "return_level_validation": validation,
    }


def _collection(simulation):
    from blueearth_cst.experiment.forcing_descriptor import (
        collection_forcing_descriptor,
    )
    from blueearth_cst.experiment.wf4_ancillary_descriptor import describe_ancillary

    if simulation["schema_version"] == "simulation/2":
        from blueearth_cst.experiment.scenario_collection_v2 import read_collection_v2
        from blueearth_cst.shared.workflow_config_snapshot import resolve_file_reference

        root = Path(simulation["_root"])
        project = root.parent.parent
        path = resolve_file_reference(
            simulation["collection"]["manifest"], {"project_root": project}
        )
        collection = read_collection_v2(path)
        intent = read_canonical_json(
            resolve_file_reference(
                collection["intent"], {"record_directory": path.parent}
            )
        )
        with resolve_file_reference(
            collection["scenario_run_lookup"],
            {"project_root": project, "record_directory": path.parent},
        ).open(encoding="utf-8", newline="") as handle:
            rows = tuple(
                ScenarioRow.from_record(row)
                for row in __import__("csv").DictReader(handle)
            )
        return collection, intent, rows
    path = Path(simulation["collection"]["manifest_path"])
    collection = read_collection(
        path,
        describe_forcing=collection_forcing_descriptor,
        describe_ancillary=describe_ancillary,
    )
    if any(
        collection[key] != simulation["collection"][key]
        for key in ("collection_id", "collection_revision")
    ):
        raise MetricPlanStale("retained collection differs from frozen simulation")
    root = path.parent.resolve()
    with confined_path(root, collection["scenario_table"]["path"]).open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = tuple(ScenarioRow.from_record(row) for row in csv.DictReader(handle))
    intent = read_canonical_json(root / collection["intent_path"])
    return collection, intent, rows


def _native_runs(root, inventory):
    from blueearth_cst.experiment.response_inventory import _artifact_path

    result = {}
    for index, artifact in enumerate(inventory["artifacts"]):
        item = next(item for item in inventory["series"] if item["artifact"] == index)
        selector = item["native_selector"]
        result[artifact["run_id"]] = NativeRunArtifacts(
            _artifact_path(root, root / "responses", artifact["path"]),
            _artifact_path(root, root / "responses", selector["toml_path"]),
            _artifact_path(root, root / "responses", selector["temporal_path"]),
        )
    return result


def _native_runs_v2(root, inventory):
    from blueearth_cst.shared.workflow_config_snapshot import resolve_file_reference

    result = {}
    for artifact in inventory["artifacts"]:
        run = artifact["run_id"]
        series = next(item for item in inventory["series"] if item["run_id"] == run)
        result[run] = NativeRunArtifacts(
            resolve_file_reference(artifact["file"], {"experiment_root": root}),
            resolve_file_reference(
                series["native_selector"]["toml"], {"experiment_root": root}
            ),
            None,
        )
    return result


def build_metric_plan(experiment_root, request):
    """Resolve units, references and final identity from complete retained responses."""
    root = Path(experiment_root).resolve()
    v2 = (root / "_engine/simulation.json").is_file()
    simulation = (
        read_simulation_v2(root) if v2 else read_simulation(root, require_complete=True)
    )
    intent_v2 = read_simulation_intent_v2(root) if v2 else None
    if v2:
        simulation = {
            **simulation,
            "_root": root,
            "collection": intent_v2["collection"],
        }
    if request["simulation_id"] != simulation["simulation_id"]:
        raise MetricPlanStale("metric request selects a different simulation")
    live = metric_request(
        simulation["simulation_id"],
        request["tokens"],
        request["water_year_anchor"],
        request["metric_environment"],
        request["return_level_validation"],
    )
    if v2:
        live["schema_version"] = "metric-request/2"
        live["simulation_schema_version"] = "simulation/2"
    if live != request:
        raise MetricPlanStale("metric declarations or invoked code changed")
    inventory = (
        read_response_inventory_v2(root) if v2 else read_response_inventory(root)
    )
    collection, intent, rows = _collection(simulation)
    source_descriptors = (
        [item["descriptor"] for item in collection["series"]]
        if v2
        else [item["descriptor"] for item in collection["forcing"]]
    )
    if any(
        item["source_calendar"] != inventory["temporal_preparation"]["source_calendar"]
        for item in source_descriptors
    ):
        raise MetricPlanStale(
            "response source calendar differs from retained collection"
        )
    specification = intent["scenario_spec"]
    groups, reference_runs, _ = metric_groups(
        rows,
        n_realizations=specification["n_realizations"],
        st_num=specification["n_design_points"],
        unit_id_capacity=intent.get(
            "run_group_id_capacity", intent.get("unit_id_capacity")
        ),
    )
    registry = declarations(request["tokens"])
    bundles = (
        tuple(DeclaredBundle("st_id", key, members) for key, members in groups.items())
        if any(item.grain == "bundle" for item in registry)
        else ()
    )
    unit_rows = metric_unit_index(
        [row.run_id for row in rows],
        [row.run_id for row in rows if row.evaluated],
        bundles,
        unit_id_capacity=intent.get(
            "run_group_id_capacity", intent.get("unit_id_capacity")
        ),
    )
    units = [asdict(item) for item in unit_rows]
    bundle_ids = {
        bundle.canonical_key: f"{len(rows) + number:0{intent.get('run_group_id_width', intent.get('unit_id_width'))}d}"
        for number, bundle in enumerate(
            sorted(bundles, key=lambda item: (item.bundle_by, item.canonical_key)), 1
        )
    }
    frozen_request = (
        intent_v2["documents"]["response_request"]
        if v2
        else read_canonical_json(root / "config/response_request.json")
    )
    locations = {
        item["variable"]: item["locations"] for item in frozen_request["variables"]
    }
    required = {item.required_responses.variable for item in registry}
    if not required <= set(locations):
        raise MetricPlanStale(
            f"missing retained response requirements: {sorted(required - set(locations))}; a new simulation is required"
        )
    references = {}
    if any(item.reference for item in registry):
        native = _native_runs(root, inventory)
        series = tuple(
            item
            for run in reference_runs
            for item in open_responses(run, native[run], ResponseRequest(("q",)))
        )
        references = {
            which: _plain(
                asdict(
                    resolve_month_reference(
                        series, expected_run_ids=reference_runs, which=which
                    )
                )
            )
            for which in ("wet", "dry")
        }
    expected_keys = []
    for metric in registry:
        ids = (
            [row.run_id for row in rows if row.evaluated]
            if metric.grain == "run"
            else list(bundle_ids.values())
        )
        expected_keys.extend(
            [metric.name, location, unit]
            for unit in ids
            for location in locations[metric.required_responses.variable]
        )
    expected_keys.sort()
    definition = {
        "declarations": request["declarations"],
        "grouping": request["grouping"],
        "reference": request["reference"],
        "resolved_references": references,
        "water_year_anchor": request["water_year_anchor"],
        "code_inventory": request["code_inventory"],
        "return_level_validation": request["return_level_validation"],
    }
    definition_digest, environment_digest = (
        content_sha256(definition),
        content_sha256(request["metric_environment"]),
    )
    identity_projection = {
        "simulation_id": simulation["simulation_id"],
        (
            "response_identity_sha256" if v2 else "response_inventory_sha256"
        ): inventory.get(
            "response_identity_sha256", inventory["response_inventory_sha256"]
        ),
        "metric_definition_sha256": definition_digest,
        "metric_environment_sha256": environment_digest,
    }
    if v2:
        identity_projection.update(
            {
                "groups": {key: list(value) for key, value in groups.items()},
                "run_groups": units,
                "reference": references,
                "water_year_anchor": request["water_year_anchor"],
                "return_level_validation_sha256": content_sha256(
                    request["return_level_validation"]
                ),
            }
        )
    identity = content_sha256(identity_projection)
    destination = (
        root / "results/metric_sets" / identity_segment(identity, "metric_set_id")
    )
    if v2:
        units = [
            {
                **item,
                "run_group_id": item.pop("unit_id"),
                "run_id": item.pop("member_run_id"),
            }
            for item in units
        ]
        expected_keys = [
            [metric, location, group_id] for metric, location, group_id in expected_keys
        ]
    plan = {
        "schema_version": "metric-request/2" if v2 else "metric-request/1",
        "metric_request_id": content_sha256(request),
        "request": request,
        "response_inventory_sha256": inventory["response_inventory_sha256"],
        "resolved_references": references,
        "units": units,
        "expected_result_keys": expected_keys,
        "groups": {key: list(value) for key, value in groups.items()},
        "bundle_run_group_ids" if v2 else "bundle_unit_ids": bundle_ids,
        "metric_definition": definition,
        "metric_definition_sha256": definition_digest,
        "metric_environment_sha256": environment_digest,
        "identity_projection": identity_projection,
        "metric_set_id": identity,
        "targets": {
            "manifest": (
                root
                / "_engine/metric_sets"
                / identity_segment(identity, "metric_set_id")
                / "metrics.json"
                if v2
                else destination / "metrics.json"
            ).as_posix(),
            "unit_index": (
                destination / "metric_run_lookup.csv"
                if v2
                else destination / "unit_index.csv"
            ).as_posix(),
            "environment": (
                root
                / "_engine/metric_sets"
                / identity_segment(identity, "metric_set_id")
                / "metric_environment.json"
                if v2
                else destination / "metric_environment.json"
            ).as_posix(),
            **{
                token: (destination / f"{token}_indicators.csv").as_posix()
                for token in request["tokens"]
            },
        },
    }
    plan["request_sha256"] = content_sha256(plan)
    return plan


def _metric_request_path(root: Path, identity: str) -> Path:
    """The engine's file for one metric request.

    A lone file per identity, so it gets a FILENAME rather than a directory
    holding one entry (t2609152104 change 3). It lives in the scope's `_engine/`
    bin because nothing here is for a reader: it exists so a run can be refused
    when its inputs moved.
    """
    return (
        root
        / "_engine"
        / "metric_requests"
        / f"{identity_segment(identity, 'metric_request_id')}.json"
    )


def write_metric_plan(experiment_root, request):
    """Publish rebuildable checkpoint state after complete native validation."""
    root = Path(experiment_root).resolve()
    plan = build_metric_plan(root, request)
    path = _metric_request_path(root, plan["metric_request_id"])
    if path.resolve() != path:
        raise MetricPlanStale("metric planning path is aliased")
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_record(path, plan, replace=True)
    log_row(
        f"{identity_segment(plan['metric_set_id'], 'metric_set_id')}: "
        f"{plural(len(plan['request']['declarations']), 'declaration')} over "
        f"{plural(len(plan['expected_result_keys']), 'result key')}",
        module="metrics",
    )
    return plan


def verify_metric_plan(experiment_root, request):
    """Validate existing plans even when timestamps would schedule no job."""
    root = Path(experiment_root).resolve()
    path = _metric_request_path(root, content_sha256(request))
    stored = read_canonical_json(path)
    expected = build_metric_plan(root, request)
    if stored != expected:
        raise MetricPlanStale(
            f"metric request expected={expected['request_sha256']} "
            f"observed={stored.get('request_sha256')}"
        )
    return stored


def _csv_bytes(fields, rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def check_live_metric_environment(plan):
    """Compare the live metric-stage environment with the retained one (D5).

    Rebuilding a plan from its own retained descriptor cannot detect drift --
    it would compare the descriptor with itself -- so the environment is
    observed afresh here and both the canonical bytes and their digest must
    agree. A mismatch aborts before any fitting and leaves no ready marker.
    """
    retained = plan["request"]["metric_environment"]
    observed = resolve_metric_environment()
    if canonical_json_bytes(observed) != canonical_json_bytes(retained):
        raise MetricPlanStale(
            "the live metric-stage environment differs from the retained "
            f"descriptor: observed {content_sha256(observed)}, "
            f"retained {content_sha256(retained)}"
        )


def reduce_metric_plan(experiment_root, plan):
    """Reduce the selected complete contract, keeping Class-C values at run grain."""
    from blueearth_cst.experiment.export_wflow_results import _format_value
    from blueearth_cst.experiment.metric_registry import MonthReference

    root = Path(experiment_root).resolve()
    if build_metric_plan(root, plan["request"]) != plan:
        raise MetricPlanStale("metric plan changed before reduction")
    check_live_metric_environment(plan)
    v2 = plan["schema_version"] == "metric-request/2"
    inventory = (
        read_response_inventory_v2(root) if v2 else read_response_inventory(root)
    )
    native = _native_runs_v2(root, inventory) if v2 else _native_runs(root, inventory)
    registry = declarations(plan["request"]["tokens"])
    references = {
        key: MonthReference(
            **{
                **value,
                "run_ids": tuple(value["run_ids"]),
                "counts": tuple(tuple(row) for row in value["counts"]),
            }
        )
        for key, value in plan["resolved_references"].items()
    }
    output = {token: [] for token in plan["request"]["tokens"]}
    evidence = []
    anchor = plan["request"]["water_year_anchor"]
    for group, members in plan["groups"].items():
        series = tuple(
            item
            for run in members
            for item in open_responses(run, native[run], ResponseRequest(tuple(output)))
        )
        for metric in registry:
            token = metric.required_responses.variable
            variable = [item for item in series if item.variable == token]
            if metric.grain == "bundle":
                values, report = reduce_bundle(
                    metric,
                    variable,
                    expected_run_ids=members,
                    anchor=anchor,
                    validation=plan["request"]["return_level_validation"],
                )
                bundle_ids = plan.get(
                    "bundle_run_group_ids", plan.get("bundle_unit_ids")
                )
                batches = [(bundle_ids[group], values)]
                evidence.append(
                    {
                        "metric": metric.name,
                        "run_group_id" if v2 else "unit_id": batches[0][0],
                        "locations": [_plain(asdict(item)) for item in report],
                    }
                )
            else:
                reference = (
                    references["wet" if metric.statistic == "wetmonth_mean" else "dry"]
                    if metric.reference
                    else None
                )
                batches = [
                    (
                        run,
                        reduce_run(
                            metric,
                            [item for item in variable if item.run_id == run],
                            anchor=anchor,
                            reference=reference,
                        ),
                    )
                    for run in members
                ]
            for unit, values in batches:
                for location, value in values.items():
                    output[token].append(
                        {
                            "metric": metric.name,
                            "location": str(location),
                            "run_group_id" if v2 else "unit_id": unit,
                            "value": _format_value(np.float32(value)),
                        }
                    )
    actual = [
        (row["metric"], row["location"], row["run_group_id"] if v2 else row["unit_id"])
        for rows in output.values()
        for row in rows
    ]
    if len(actual) != len(set(actual)) or sorted(actual) != [
        tuple(key) for key in plan["expected_result_keys"]
    ]:
        raise ImmutableMetricSetError(
            "reduced result keys differ from independent expected set"
        )
    return output, evidence


def _validate_tables(tables, expected_keys, declarations_by_name, units):
    grains = {}
    key = "run_group_id" if units and "run_group_id" in units[0] else "unit_id"
    for row in units:
        previous = grains.setdefault(row[key], row["grain"])
        if previous != row["grain"]:
            raise ImmutableMetricSetError("metric unit has more than one grain")
    actual = []
    for token, rows in tables.items():
        for row in rows:
            expected_fields = {"metric", "location", key, "value"}
            if set(row) != expected_fields:
                raise ImmutableMetricSetError(
                    "indicator table fields are not the declared metric schema"
                )
            declaration = declarations_by_name.get(row["metric"])
            if (
                declaration is None
                or declaration["required_responses"]["variable"] != token
            ):
                raise ImmutableMetricSetError(
                    "indicator row has undeclared metric or wrong table token"
                )
            if grains.get(row[key]) != declaration["grain"]:
                raise ImmutableMetricSetError("indicator metric and unit grain differ")
            value = float(row["value"]) if row["value"] != "" else float("nan")
            if np.isinf(value) or (
                declaration["grain"] == "bundle" and not np.isfinite(value)
            ):
                raise ImmutableMetricSetError(
                    "indicator value violates declared validity"
                )
            actual.append((row["metric"], row["location"], row[key]))
    if len(actual) != len(set(actual)) or sorted(actual) != [
        tuple(key) for key in expected_keys
    ]:
        raise ImmutableMetricSetError(
            "indicator keys differ from exact expected result keys"
        )


def publish_metric_set(experiment_root, plan):
    """Publish a whole declared set, preserving all bytes on exact ready reuse."""
    if plan["schema_version"] == "metric-request/2":
        return _publish_metric_set_v2(experiment_root, plan)
    root = Path(experiment_root).resolve()
    destination = (
        root
        / "results/metric_sets"
        / identity_segment(plan["metric_set_id"], "metric_set_id")
    )
    marker = destination / "metrics.json"
    if destination.resolve() != destination:
        raise ImmutableMetricSetError("metric-set directory is aliased")
    if build_metric_plan(root, plan["request"]) != plan:
        raise MetricPlanStale("metric inputs changed before publication")
    if marker.exists():
        log_row(
            f"Reusing the published metric set {destination.name}",
            module="metrics",
        )
        return read_metric_set(root, marker)

    check_live_metric_environment(plan)
    if destination.exists() and any(destination.iterdir()):
        raise ImmutableMetricSetError(
            f"partial metric set cannot be overwritten: {destination}"
        )
    tables, evidence = reduce_metric_plan(root, plan)
    declarations_by_name = {
        item["name"]: item for item in plan["request"]["declarations"]
    }
    _validate_tables(
        tables, plan["expected_result_keys"], declarations_by_name, plan["units"]
    )
    payloads = {
        f"{token}_indicators.csv": _csv_bytes(
            ["metric", "location", "unit_id", "value"],
            sorted(
                rows,
                key=lambda row: (row["metric"], row["location"], int(row["unit_id"])),
            ),
        )
        for token, rows in tables.items()
    }
    payloads["unit_index.csv"] = _csv_bytes(
        ["unit_id", "grain", "member_run_id"], plan["units"]
    )
    payloads["metric_environment.json"] = canonical_json_bytes(
        plan["request"]["metric_environment"]
    )
    # The exact checked report bytes travel with the set, so a reader never
    # needs the installed asset -- or the estimator dependency -- to validate it.
    report_bytes = return_level_validation.load_report_bytes()
    return_level_validation.verify_declaration(
        plan["request"]["return_level_validation"], report_bytes
    )
    payloads[return_level_validation.REPORT_FILENAME] = report_bytes
    import hashlib

    def reference(name):
        return {"path": name, "sha256": hashlib.sha256(payloads[name]).hexdigest()}

    simulation = read_simulation(root, require_complete=True)
    manifest = {
        "schema_version": "metric-set/1",
        "status": "ready",
        "metric_set_id": plan["metric_set_id"],
        "simulation_id": simulation["simulation_id"],
        "collection_id": simulation["collection"]["collection_id"],
        "collection_revision": simulation["collection"]["collection_revision"],
        "response_inventory": {
            "path": "../../../_engine/response_inventory.json",
            "sha256": plan["response_inventory_sha256"],
        },
        "response_request": {
            "path": "../../../config/response_request.json",
            "sha256": file_sha256(root / "config/response_request.json"),
        },
        "bundle_membership_sha256": content_sha256(plan["groups"]),
        "declarations": plan["request"]["declarations"],
        "metric_definition": plan["metric_definition"],
        "metric_definition_sha256": plan["metric_definition_sha256"],
        "metric_environment": reference("metric_environment.json"),
        "unit_index": reference("unit_index.csv"),
        "expected_result_keys": plan["expected_result_keys"],
        "groups": plan["groups"],
        "resolved_references": plan["resolved_references"],
        "return_level_validation": plan["request"]["return_level_validation"],
        "return_level_benchmark": reference(return_level_validation.REPORT_FILENAME),
        "return_level_evidence": evidence,
        "indicator_tables": [
            {
                "token": token,
                **reference(f"{token}_indicators.csv"),
                "row_count": len(tables[token]),
            }
            for token in sorted(tables)
        ],
    }
    manifest["metrics_manifest_sha256"] = content_sha256(manifest)
    destination.mkdir(parents=True, exist_ok=True)
    for name, payload in payloads.items():
        with (destination / name).open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    # Re-observe immediately before the sole ready marker: a late drift must
    # leave an unready partial destination, never a silently relabelled result.
    check_live_metric_environment(plan)
    atomic_record(marker, manifest)
    log_row(
        f"Published {destination.name}: "
        + ", ".join(
            f"{item['token']} ({item['row_count']} rows)"
            for item in manifest["indicator_tables"]
        ),
        module="metrics",
    )
    return read_metric_set(root, marker)


def _publish_metric_set_v2(experiment_root, plan):
    """Publish the v2 engine marker and paired user-facing result directory."""
    root = Path(experiment_root).resolve()
    short = identity_segment(plan["metric_set_id"], "metric_set_id")
    engine = root / "_engine/metric_sets" / short
    result = root / "results/metric_sets" / short
    marker = engine / "metrics.json"
    if engine.resolve() != engine or result.resolve() != result:
        raise ImmutableMetricSetError("metric-set directory is aliased")
    if marker.exists():
        return read_metric_set(root, marker)
    check_live_metric_environment(plan)
    if any(path.exists() and any(path.iterdir()) for path in (engine, result)):
        raise ImmutableMetricSetError("partial metric set cannot be overwritten")
    tables, _evidence = reduce_metric_plan(root, plan)
    declarations_by_name = {
        item["name"]: item for item in plan["request"]["declarations"]
    }
    _validate_tables(
        tables, plan["expected_result_keys"], declarations_by_name, plan["units"]
    )
    payloads = {
        f"{token}_indicators.csv": _csv_bytes(
            ["metric", "location", "run_group_id", "value"],
            sorted(
                rows,
                key=lambda row: (
                    row["metric"],
                    row["location"],
                    int(row["run_group_id"]),
                ),
            ),
        )
        for token, rows in tables.items()
    }
    lookup = _csv_bytes(["run_group_id", "grain", "run_id"], plan["units"])
    environment = canonical_json_bytes(plan["request"]["metric_environment"])
    report = return_level_validation.load_report_bytes()
    return_level_validation.verify_declaration(
        plan["request"]["return_level_validation"], report
    )
    import hashlib

    def ref(path, payload):
        return {"path": path, "sha256": hashlib.sha256(payload).hexdigest()}

    result.mkdir(parents=True, exist_ok=True)
    engine.mkdir(parents=True, exist_ok=True)
    for name, payload in payloads.items():
        (result / name).write_bytes(payload)
    (result / "metric_run_lookup.csv").write_bytes(lookup)
    (engine / "metric_environment.json").write_bytes(environment)
    (engine / return_level_validation.REPORT_FILENAME).write_bytes(report)
    simulation = read_simulation_v2(root)
    manifest = {
        "schema_version": "metric-set/2",
        "canonicalization_id": "collection-canon/1",
        "status": "ready",
        "metric_set_id": plan["metric_set_id"],
        "simulation_id": simulation["simulation_id"],
        "identity_projection": plan["identity_projection"],
        "response_inventory": {
            "path": "../../response_inventory.json",
            "sha256": plan["response_inventory_sha256"],
        },
        "environment": ref("metric_environment.json", environment),
        "environment_sha256": content_sha256(plan["request"]["metric_environment"]),
        "groups": plan["groups"],
        "run_groups": plan["units"],
        "metric_run_lookup": ref(
            f"../../results/metric_sets/{short}/metric_run_lookup.csv", lookup
        ),
        "tables": [
            {
                "token": token,
                "file": ref(
                    f"../../results/metric_sets/{short}/{token}_indicators.csv",
                    payloads[f"{token}_indicators.csv"],
                ),
            }
            for token in sorted(tables)
        ],
        "return_level_benchmark": ref(return_level_validation.REPORT_FILENAME, report),
        "result_root": f"results/metric_sets/{short}",
        "engine_root": f"_engine/metric_sets/{short}",
    }
    manifest["metrics_manifest_sha256"] = content_sha256(manifest)
    atomic_record(marker, manifest)
    return read_metric_set(root, marker)


def _validated_benchmark(destination, manifest, validation):
    """Dispatch on the retained validation record; never rewrite an old one.

    An exact legacy record uses the existing checks and carries no report. A
    `return-level-validation/1` record requires its copied report and is checked
    against THOSE bytes, so a historical set stays readable when the installed
    asset is a different version or absent. Any other shape is refused rather
    than defaulted.
    """
    if return_level_validation.is_legacy(validation):
        if "return_level_benchmark" in manifest:
            raise ImmutableMetricSetError(
                "a legacy unassessed metric set must not carry a benchmark report"
            )
        return None
    if (
        not isinstance(validation, dict)
        or validation.get("schema_version") != return_level_validation.SCHEMA_VERSION
    ):
        raise ImmutableMetricSetError(
            f"unknown return-level validation record "
            f"{validation.get('schema_version') if isinstance(validation, dict) else validation!r}"
        )
    reference = manifest.get("return_level_benchmark")
    if not isinstance(reference, dict) or set(reference) != {"path", "sha256"}:
        raise ImmutableMetricSetError("metric set is missing its benchmark reference")
    if reference["path"] != return_level_validation.REPORT_FILENAME:
        raise ImmutableMetricSetError(
            f"unexpected benchmark report path {reference['path']!r}"
        )
    path = confined_path(destination, reference["path"])
    if not path.is_file():
        raise ImmutableMetricSetError("retained benchmark report is missing")
    try:
        return_level_validation.verify_declaration(validation, path.read_bytes())
    except return_level_validation.ReturnLevelValidationError as error:
        raise ImmutableMetricSetError(
            f"retained return-level validation is not supported by its report: {error}"
        ) from error
    return reference


def _read_metric_set(experiment_root, manifest_path):
    """Validate retained results and identity without consulting the live metric registry."""
    root, marker = Path(experiment_root).resolve(), Path(manifest_path)
    if marker.name != "metrics.json":
        raise ImmutableMetricSetError("expected metrics.json as the sole ready marker")
    destination = marker.parent.resolve()
    if not destination.is_relative_to(root / "results/metric_sets"):
        raise ImmutableMetricSetError("metric set is outside the selected experiment")
    marker = confined_path(destination, marker.name)
    manifest = read_canonical_json(marker)
    if manifest["schema_version"] != "metric-set/1" or manifest["status"] != "ready":
        raise ImmutableMetricSetError("metric set is not ready")
    digest = content_sha256(
        {
            key: value
            for key, value in manifest.items()
            if key != "metrics_manifest_sha256"
        }
    )
    if digest != manifest["metrics_manifest_sha256"]:
        raise ImmutableMetricSetError("metric manifest digest differs")
    definition = manifest["metric_definition"]
    if manifest["response_request"] != {
        "path": "../../../config/response_request.json",
        "sha256": file_sha256(root / "config/response_request.json"),
    }:
        raise ImmutableMetricSetError("retained response request differs")
    if manifest["bundle_membership_sha256"] != content_sha256(manifest["groups"]):
        raise ImmutableMetricSetError("bundle membership digest differs")
    if (
        content_sha256(definition) != manifest["metric_definition_sha256"]
        or definition["declarations"] != manifest["declarations"]
    ):
        raise ImmutableMetricSetError("metric definition digest or declarations differ")
    if (
        definition["resolved_references"] != manifest["resolved_references"]
        or definition["return_level_validation"] != manifest["return_level_validation"]
    ):
        raise ImmutableMetricSetError("metric provenance differs from its definition")
    if (
        manifest["response_inventory"]["path"]
        != "../../../_engine/response_inventory.json"
    ):
        raise ImmutableMetricSetError("unexpected retained response inventory path")
    if (
        manifest["unit_index"]["path"] != "unit_index.csv"
        or manifest["metric_environment"]["path"] != "metric_environment.json"
    ):
        raise ImmutableMetricSetError("unexpected metric input paths")
    retained_validation = manifest["return_level_validation"]
    benchmark = _validated_benchmark(destination, manifest, retained_validation)
    for item in [
        manifest["unit_index"],
        manifest["metric_environment"],
        *([benchmark] if benchmark else []),
        *manifest["indicator_tables"],
    ]:
        if file_sha256(confined_path(destination, item["path"])) != item["sha256"]:
            raise ImmutableMetricSetError(f"metric artifact differs: {item['path']}")
    environment = read_canonical_json(
        confined_path(destination, manifest["metric_environment"]["path"])
    )
    identity = content_sha256(
        {
            "simulation_id": manifest["simulation_id"],
            "response_inventory_sha256": manifest["response_inventory"]["sha256"],
            "metric_definition_sha256": manifest["metric_definition_sha256"],
            "metric_environment_sha256": content_sha256(environment),
        }
    )
    if identity != manifest["metric_set_id"] or destination.name != identity_segment(
        identity, "metric_set_id"
    ):
        raise ImmutableMetricSetError(
            "metric-set identity differs from retained inputs"
        )
    simulation = read_simulation(root, require_complete=True)
    inventory = read_response_inventory(root)
    if (
        manifest["simulation_id"] != simulation["simulation_id"]
        or manifest["response_inventory"]["sha256"]
        != inventory["response_inventory_sha256"]
    ):
        raise ImmutableMetricSetError(
            "metric set differs from retained simulation responses"
        )
    if any(
        manifest[key] != simulation["collection"][key]
        for key in ("collection_id", "collection_revision")
    ):
        raise ImmutableMetricSetError(
            "metric collection differs from retained simulation"
        )
    collection, intent, rows = _collection(simulation)
    if any(
        item["descriptor"]["source_calendar"]
        != inventory["temporal_preparation"]["source_calendar"]
        for item in collection["forcing"]
    ):
        raise ImmutableMetricSetError(
            "response source calendar differs from retained collection"
        )
    specification = intent["scenario_spec"]
    groups, _, _ = metric_groups(
        rows,
        n_realizations=specification["n_realizations"],
        st_num=specification["n_design_points"],
        unit_id_capacity=intent["unit_id_capacity"],
    )
    has_bundles = any(item["grain"] == "bundle" for item in manifest["declarations"])
    bundles = (
        [DeclaredBundle("st_id", key, members) for key, members in groups.items()]
        if has_bundles
        else []
    )
    expected_units = [
        asdict(item)
        for item in metric_unit_index(
            [row.run_id for row in rows],
            [row.run_id for row in rows if row.evaluated],
            bundles,
            unit_id_capacity=intent["unit_id_capacity"],
        )
    ]
    with confined_path(destination, manifest["unit_index"]["path"]).open(
        encoding="utf-8", newline=""
    ) as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["unit_id", "grain", "member_run_id"]:
            raise ImmutableMetricSetError("unit index schema differs")
        units = list(reader)
    if units != expected_units:
        raise ImmutableMetricSetError("unit index differs from collection membership")
    if manifest["groups"] != {key: list(value) for key, value in groups.items()}:
        raise ImmutableMetricSetError(
            "metric grouping differs from collection membership"
        )
    frozen_request = read_canonical_json(root / "config/response_request.json")
    locations = {
        item["variable"]: item["locations"] for item in frozen_request["variables"]
    }
    expected_keys = sorted(
        [metric["name"], location, unit]
        for metric in manifest["declarations"]
        for unit in sorted(
            {item["unit_id"] for item in units if item["grain"] == metric["grain"]}
        )
        for location in locations[metric["required_responses"]["variable"]]
    )
    if expected_keys != manifest["expected_result_keys"]:
        raise ImmutableMetricSetError(
            "stored expected keys differ from independent request and unit contract"
        )
    expected_tokens = {
        item["required_responses"]["variable"] for item in manifest["declarations"]
    }
    recorded_tokens = [item["token"] for item in manifest["indicator_tables"]]
    if (
        len(recorded_tokens) != len(expected_tokens)
        or set(recorded_tokens) != expected_tokens
        or any(
            item["path"] != f"{item['token']}_indicators.csv"
            for item in manifest["indicator_tables"]
        )
    ):
        raise ImmutableMetricSetError(
            "indicator table inventory differs from declared tokens and paths"
        )
    tables = {}
    for item in manifest["indicator_tables"]:
        if item["token"] in tables:
            raise ImmutableMetricSetError("duplicate indicator table token")
        with confined_path(destination, item["path"]).open(
            encoding="utf-8", newline=""
        ) as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != ["metric", "location", "unit_id", "value"]:
                raise ImmutableMetricSetError("indicator table schema differs")
            tables[item["token"]] = list(reader)
        if len(tables[item["token"]]) != item["row_count"]:
            raise ImmutableMetricSetError("indicator table row count differs")
    _validate_tables(
        tables,
        expected_keys,
        {item["name"]: item for item in manifest["declarations"]},
        units,
    )
    return manifest


def read_metric_set(experiment_root, manifest_path):
    """Read only the selected immutable set, with named malformed-state refusals."""
    try:
        marker = Path(manifest_path)
        if (
            marker.parent.parent.name == "metric_sets"
            and marker.parent.parent.parent.name == "_engine"
        ):
            return _read_metric_set_v2(experiment_root, marker)
        return _read_metric_set(experiment_root, manifest_path)
    except ImmutableMetricSetError:
        raise
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise ImmutableMetricSetError(f"metric set {manifest_path}: {exc}") from exc


def _read_metric_set_v2(experiment_root, marker):
    root = Path(experiment_root).resolve()
    manifest = read_canonical_json(marker)
    if (
        manifest.get("schema_version") != "metric-set/2"
        or manifest.get("status") != "ready"
    ):
        raise ImmutableMetricSetError("metric set is not ready")
    if content_sha256(
        {k: v for k, v in manifest.items() if k != "metrics_manifest_sha256"}
    ) != manifest.get("metrics_manifest_sha256"):
        raise ImmutableMetricSetError("metric manifest digest differs")
    if content_sha256(manifest["identity_projection"]) != manifest["metric_set_id"]:
        raise ImmutableMetricSetError("metric-set identity projection differs")
    short = identity_segment(manifest["metric_set_id"], "metric_set_id")
    if (
        marker.parent.name != short
        or manifest["engine_root"] != f"_engine/metric_sets/{short}"
    ):
        raise ImmutableMetricSetError("metric-set engine identity differs")
    if manifest["result_root"] != f"results/metric_sets/{short}":
        raise ImmutableMetricSetError("metric-set result identity differs")
    engine = root / manifest["engine_root"]
    result = root / manifest["result_root"]
    if manifest["response_inventory"]["path"] != "../../response_inventory.json":
        raise ImmutableMetricSetError("metric inventory reference differs")
    for item in [manifest["environment"], manifest["return_level_benchmark"]]:
        if file_sha256(engine / item["path"]) != item["sha256"]:
            raise ImmutableMetricSetError(f"metric artifact differs: {item['path']}")
    lookup = result / "metric_run_lookup.csv"
    if file_sha256(lookup) != manifest["metric_run_lookup"]["sha256"]:
        raise ImmutableMetricSetError("metric lookup differs")
    with lookup.open(newline="", encoding="utf-8") as handle:
        if csv.DictReader(handle).fieldnames != ["run_group_id", "grain", "run_id"]:
            raise ImmutableMetricSetError("metric lookup schema differs")
    for item in manifest["tables"]:
        path = result / Path(item["file"]["path"]).name
        if file_sha256(path) != item["file"]["sha256"]:
            raise ImmutableMetricSetError("metric table differs")
        with path.open(newline="", encoding="utf-8") as handle:
            if csv.DictReader(handle).fieldnames != [
                "metric",
                "location",
                "run_group_id",
                "value",
            ]:
                raise ImmutableMetricSetError("metric table schema differs")
    read_simulation_v2(root)
    inventory = read_response_inventory_v2(root)
    if (
        manifest["response_inventory"]["sha256"]
        != inventory["response_inventory_sha256"]
    ):
        raise ImmutableMetricSetError("metric set differs from retained responses")
    return manifest
