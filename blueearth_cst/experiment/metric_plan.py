"""Response-dependent metric identities, complete keys and immutable result sets."""

import csv
import io
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from blueearth_cst.experiment import gev_lmoments, return_level_validation
from blueearth_cst.experiment.content_identity import (
    canonical_json_bytes,
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
from blueearth_cst.experiment.response_inventory import read_response_inventory_v2
from blueearth_cst.experiment.scenario_rows import ScenarioRow
from blueearth_cst.experiment.simulation_record import (
    MetricsOnlySimulationUnavailable,
    atomic_record,
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

#: The published return-level provenance beside each v2 metric set's marker.
RETURN_LEVEL_EVIDENCE_FILENAME = "return_level_evidence.json"
RETURN_LEVEL_EVIDENCE_SCHEMA = "return-level-evidence/1"


class MetricPlanStale(ValueError):
    """A scheduling plan cannot certify the requested live inputs or responses."""


class MetricsOnlyIdentityMismatch(ValueError):
    """An explicit collection assertion differs from the retained simulation."""


class ImmutableMetricSetError(ValueError):
    """A result set is partial, changed or fails its declared complete key set."""


def _require_v2(root):
    """Refuse a pre-release v1 experiment by name rather than as a missing file.

    v1 simulation records existed only between 2026-09-11 and 2026-09-22, and
    no release wrote one, so this toolbox reads v2 alone.
    """
    if (
        not (root / "_engine/simulation.json").is_file()
        and (root / "config/simulation.json").is_file()
    ):
        raise MetricsOnlySimulationUnavailable(
            f"{root.name}: written in the pre-release v1 simulation record "
            "format, which this toolbox no longer reads; simulate it again "
            "under a new experiment name"
        )


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
    _require_v2(root)
    read_simulation_v2(root)
    intent_v2 = read_simulation_intent_v2(root)
    retained_collection = intent_v2["collection"]
    if "scenario_collection" in workflow:
        asserted = workflow["scenario_collection"]
        retained = retained_collection
        for field in ("collection_id", "collection_revision"):
            if asserted.get(field) not in (None, retained[field]):
                raise MetricsOnlyIdentityMismatch(
                    f"{field}: retained={retained[field]!r}; asserted={asserted[field]!r}"
                )
    tokens = workflow.get("metrics")
    if tokens is None:
        outvars = (project.get("model") or {}).get("outvars")
        if outvars is not None:
            tokens = list(indicator_tables(outvars))
        else:
            request = intent_v2["documents"]["response_request"]
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
            + f"; retained simulation/model inputs come from {(root / '_engine/simulation.json').as_posix()}"
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
    _require_v2(root)
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
    if (root / "_engine/simulation_intent.json").is_file():
        # The v2 freeze has committed but responses have not published
        # _engine/simulation.json yet -- the DAG-build-time evaluation this
        # feeds (checkpoint prepare_indicator_plan, rule all's target lambda)
        # runs long before that, so the request's identity comes from the
        # frozen INTENT rather than waiting on a completed simulation.
        #
        # simulation_schema_version is pinned to the "simulation/2" literal
        # (matching build_metric_plan), never the intent's
        # own "simulation-intent/1" tag -- the checkpoint wildcard is fixed
        # from this request before responses complete, and params.request is
        # re-resolved (this time via the v2-complete branch above) once the
        # job actually runs, so the two resolutions must hash identically.
        intent = read_simulation_intent_v2(root)
        request = metric_request(
            intent["simulation_id"],
            tokens,
            anchor,
            resolve_metric_environment(),
            return_level_validation.build_declaration(),
        )
        request["schema_version"] = "metric-request/2"
        request["simulation_schema_version"] = "simulation/2"
        return request
    raise MetricsOnlySimulationUnavailable(
        f"{root.name}: no frozen simulation intent; simulate the experiment first"
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
            collection["intent"],
            {"project_root": project, "record_directory": path.parent},
        )
    )
    with resolve_file_reference(
        collection["scenario_run_lookup"],
        {"project_root": project, "record_directory": path.parent},
    ).open(encoding="utf-8", newline="") as handle:
        rows = _v2_scenario_rows(csv.DictReader(handle))
    return collection, intent, rows


def _v2_scenario_rows(records):
    """Adapt v2's compact scenario lookup to the legacy metric grouping rows."""
    expected = {"run_id", "evaluate", "type", "rlz", "st_id"}
    values = list(records)
    if any(set(record) != expected for record in values):
        raise MetricPlanStale("v2 scenario lookup has unknown fields")
    roots = {}
    for record in values:
        if record["evaluate"] not in {"true", "false"}:
            raise MetricPlanStale("v2 scenario lookup evaluate flag is invalid")
        if not record["run_id"] or not record["type"] or not record["rlz"]:
            raise MetricPlanStale("v2 scenario lookup has incomplete identifiers")
        if not record["st_id"]:
            if record["rlz"] in roots:
                raise MetricPlanStale(
                    "v2 scenario lookup has duplicate realization roots"
                )
            roots[record["rlz"]] = record["run_id"]
    if not roots:
        raise MetricPlanStale("v2 scenario lookup has no realization roots")
    rows = []
    for record in values:
        if record["st_id"] and record["rlz"] not in roots:
            raise MetricPlanStale("v2 scenario lookup member lacks a realization root")
        rows.append(
            ScenarioRow(
                run_id=record["run_id"],
                derived_from=roots[record["rlz"]] if record["st_id"] else "",
                evaluated=record["evaluate"] == "true",
                scenario_type=record["type"],
                payload=(("rlz", record["rlz"]), ("st_id", record["st_id"])),
            )
        )
    return tuple(rows)


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
    _require_v2(root)
    simulation = read_simulation_v2(root)
    intent_v2 = read_simulation_intent_v2(root)
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
    live["schema_version"] = "metric-request/2"
    live["simulation_schema_version"] = "simulation/2"
    if live != request:
        raise MetricPlanStale("metric declarations or invoked code changed")
    inventory = read_response_inventory_v2(root)
    collection, intent, rows = _collection(simulation)
    source_descriptors = [item["descriptor"] for item in collection["series"]]
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
        unit_id_capacity=intent["run_group_id_capacity"],
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
        unit_id_capacity=intent["run_group_id_capacity"],
    )
    units = _v2_run_groups([asdict(item) for item in unit_rows])
    bundle_ids = {
        bundle.canonical_key: f"{len(rows) + number:0{intent['run_group_id_width']}d}"
        for number, bundle in enumerate(
            sorted(bundles, key=lambda item: (item.bundle_by, item.canonical_key)), 1
        )
    }
    frozen_request = intent_v2["documents"]["response_request"]
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
        native = _native_runs_v2(root, inventory)
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
        "response_identity_sha256": inventory["response_identity_sha256"],
        "metric_definition_sha256": definition_digest,
        "metric_environment_sha256": environment_digest,
        "groups": {key: list(value) for key, value in groups.items()},
        "run_groups": units,
        "reference": references,
        "water_year_anchor": request["water_year_anchor"],
        "return_level_validation_sha256": content_sha256(
            request["return_level_validation"]
        ),
    }
    identity = content_sha256(identity_projection)
    destination = (
        root / "results/metric_sets" / identity_segment(identity, "metric_set_id")
    )
    plan = {
        "schema_version": "metric-request/2",
        "metric_request_id": content_sha256(request),
        "request": request,
        "response_inventory_sha256": inventory["response_inventory_sha256"],
        "resolved_references": references,
        "units": units,
        "expected_result_keys": expected_keys,
        "groups": {key: list(value) for key, value in groups.items()},
        "bundle_run_group_ids": bundle_ids,
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
            ).as_posix(),
            "unit_index": (destination / "metric_run_lookup.csv").as_posix(),
            "environment": (
                root
                / "_engine/metric_sets"
                / identity_segment(identity, "metric_set_id")
                / "metric_environment.json"
            ).as_posix(),
            **{
                token: (destination / f"{token}_indicators.csv").as_posix()
                for token in request["tokens"]
            },
        },
    }
    plan["request_sha256"] = content_sha256(plan)
    return plan


def _v2_run_groups(units):
    """Rename legacy in-memory unit rows for v2 metric-set persistence."""
    expected = {"unit_id", "grain", "member_run_id"}
    if any(set(item) != expected for item in units):
        raise MetricPlanStale("metric unit rows have unknown fields")
    return [
        {
            "run_group_id": item["unit_id"],
            "grain": item["grain"],
            "run_id": item["member_run_id"],
        }
        for item in units
    ]


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
    inventory = read_response_inventory_v2(root)
    native = _native_runs_v2(root, inventory)
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
                batches = [(plan["bundle_run_group_ids"][group], values)]
                evidence.append(
                    {
                        "metric": metric.name,
                        "run_group_id": batches[0][0],
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
                            "run_group_id": unit,
                            "value": _format_value(np.float32(value)),
                        }
                    )
    actual = [
        (row["metric"], row["location"], row["run_group_id"])
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
    key = "run_group_id"
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
    if plan["schema_version"] != "metric-request/2":
        raise MetricPlanStale(f"unsupported metric plan {plan['schema_version']!r}")
    return _publish_metric_set_v2(experiment_root, plan)


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
    tables, evidence = reduce_metric_plan(root, plan)
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
    # Each return level's provenance: usable block counts per member against
    # the required minimum, the fitted parameters, fit and shape coverage, and
    # the extraction / missingness / partial-block policies applied. Without it
    # a published return level is a bare number that cannot be audited.
    evidence_payload = canonical_json_bytes(
        {"schema_version": RETURN_LEVEL_EVIDENCE_SCHEMA, "bundles": _plain(evidence)}
    )
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
    (engine / RETURN_LEVEL_EVIDENCE_FILENAME).write_bytes(evidence_payload)
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
            f"results/metric_sets/{short}/metric_run_lookup.csv", lookup
        ),
        "tables": [
            {
                "token": token,
                "file": ref(
                    f"results/metric_sets/{short}/{token}_indicators.csv",
                    payloads[f"{token}_indicators.csv"],
                ),
            }
            for token in sorted(tables)
        ],
        "return_level_benchmark": ref(return_level_validation.REPORT_FILENAME, report),
        "return_level_evidence": ref(RETURN_LEVEL_EVIDENCE_FILENAME, evidence_payload),
        "result_root": f"results/metric_sets/{short}",
        "engine_root": f"_engine/metric_sets/{short}",
    }
    manifest["metrics_manifest_sha256"] = content_sha256(manifest)
    atomic_record(marker, manifest)
    return read_metric_set(root, marker)


def read_metric_set(experiment_root, manifest_path):
    """Read only the selected immutable set, with named malformed-state refusals."""
    try:
        marker = Path(manifest_path)
        if (
            marker.parent.parent.name == "metric_sets"
            and marker.parent.parent.parent.name == "_engine"
        ):
            if marker.name != "metrics.json":
                raise ImmutableMetricSetError(
                    f"metric set {manifest_path}: the engine marker is named "
                    "metrics.json; another file in the set is not a marker"
                )
            return _read_metric_set_v2(experiment_root, marker)
        raise ImmutableMetricSetError(
            f"metric set {manifest_path}: not an engine marker under "
            "_engine/metric_sets/; the pre-release v1 metric-set layout is not read"
        )
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
    artifacts = [manifest["environment"], manifest["return_level_benchmark"]]
    # Sets published before 2026-10-04 carry no evidence and stay readable;
    # one that names it must name the canonical file and match its bytes.
    if "return_level_evidence" in manifest:
        if manifest["return_level_evidence"]["path"] != RETURN_LEVEL_EVIDENCE_FILENAME:
            raise ImmutableMetricSetError("return-level evidence reference differs")
        artifacts.append(manifest["return_level_evidence"])
    for item in artifacts:
        if file_sha256(engine / item["path"]) != item["sha256"]:
            raise ImmutableMetricSetError(f"metric artifact differs: {item['path']}")
    lookup = result / "metric_run_lookup.csv"
    if manifest["metric_run_lookup"]["path"] != (
        f"results/metric_sets/{short}/metric_run_lookup.csv"
    ):
        raise ImmutableMetricSetError("metric lookup reference differs")
    if file_sha256(lookup) != manifest["metric_run_lookup"]["sha256"]:
        raise ImmutableMetricSetError("metric lookup differs")
    with lookup.open(newline="", encoding="utf-8") as handle:
        if csv.DictReader(handle).fieldnames != ["run_group_id", "grain", "run_id"]:
            raise ImmutableMetricSetError("metric lookup schema differs")
    for item in manifest["tables"]:
        if item["file"]["path"] != (
            f"results/metric_sets/{short}/{item['token']}_indicators.csv"
        ):
            raise ImmutableMetricSetError("metric table reference differs")
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
