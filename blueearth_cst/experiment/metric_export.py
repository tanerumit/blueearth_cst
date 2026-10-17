"""Publish each selected named indicator set after a WF4 invocation.

Sets commit independently: a set whose immutable metric set is complete is
published even when another set failed, and a failed set keeps its prior
publication. This is per-set completion, not an all-set transaction.
"""

from pathlib import Path

from blueearth_cst.experiment import indicator_sets
from blueearth_cst.experiment.metric_plan import (
    current_metric_request,
    metric_anchor,
    verify_metric_plan,
)
from blueearth_cst.experiment.named_export import (
    NamedExportError,
    legacy_flat_export,
    publish_named_set,
    read_current_publication,
)
from blueearth_cst.experiment.simulation_record import read_simulation_intent_v2
from blueearth_cst.shared.snake_utils import resolve_water_year_start


def publish_selected_sets(
    root: Path, project: dict, settings: dict, selection
) -> list[dict]:
    """Publish every selected set whose metric set is ready; report each outcome.

    Returns one record per set: ``status`` is ``current`` or ``failed``, with
    the metric-set and publication ids, the failure reason, and any prior
    publication a failed set keeps (a mixed-age export).
    """
    root = Path(root).resolve()

    def retained_variables():
        request = read_simulation_intent_v2(root)["documents"]["response_request"]
        return [item["variable"] for item in request["variables"]]

    month = resolve_water_year_start(
        (project.get("climate") or {}).get("water_year_start")
    )
    sets = indicator_sets.selected_sets(
        project,
        settings,
        selection,
        simulation_path=settings["operation"] == "simulate-and-metrics",
        retained_variables=retained_variables,
        legacy_context="export",
    )
    outcomes = []
    for item in sets:
        try:
            request = current_metric_request(
                root,
                indicator_sets.calculation_records(item.indicators),
                metric_anchor(project),
            )
            plan = verify_metric_plan(root, request)
            record = publish_named_set(
                root, item, Path(plan["targets"]["manifest"]), water_year_start=month
            )
            outcomes.append(
                {
                    "set_id": item.set_id,
                    "status": "current",
                    "metric_set_id": record["metric_set_id"],
                    "publication_id": record["publication_id"],
                }
            )
        except (OSError, KeyError, ValueError) as exc:
            try:
                prior = read_current_publication(root, item.set_id)["publication_id"]
            except (OSError, KeyError, ValueError, NamedExportError):
                prior = None
            outcomes.append(
                {
                    "set_id": item.set_id,
                    "status": "failed",
                    "reason": f"{type(exc).__name__}: {exc}",
                    "prior_publication_id": prior,
                }
            )
    return outcomes


def report_publication(root: Path, outcomes) -> bool:
    """Log one row per set and any preserved legacy flat export; True if all current."""
    from blueearth_cst.shared.run_log_core import log_row

    legacy = legacy_flat_export(root)
    if legacy:
        log_row(
            f"Legacy flat metric export preserved, not refreshed: {legacy[0]}; named sets "
            "publish under results/metric_sets/<set-id>/ (see the migration note)",
            module="metrics",
        )
    for outcome in outcomes:
        if outcome["status"] == "current":
            log_row(
                f"Indicator set {outcome['set_id']} current: metric set "
                f"{outcome['metric_set_id'][:12]}, publication {outcome['publication_id'][:12]} "
                f"→ {Path(root) / 'results/metric_sets' / outcome['set_id']}",
                module="metrics",
            )
        else:
            kept = (
                f"prior publication {outcome['prior_publication_id'][:12]} kept (mixed-age export)"
                if outcome["prior_publication_id"]
                else "no prior publication"
            )
            log_row(
                f"Indicator set {outcome['set_id']} FAILED; {kept}; {outcome['reason'].splitlines()[0]}",
                module="metrics",
            )
    return all(outcome["status"] == "current" for outcome in outcomes)
