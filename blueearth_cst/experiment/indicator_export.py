"""Publish each selected named indicator set after a WF4 invocation.

Sets commit independently: a set whose immutable indicator set is complete is
published even when another set failed, and a failed set keeps its prior
publication. This is per-set completion, not an all-set transaction.
"""

from pathlib import Path

from blueearth_cst.experiment import indicator_sets
from blueearth_cst.experiment.console_reporting import (
    record_indicator_detail,
    result_counts,
)
from blueearth_cst.experiment.content_identity import read_canonical_json
from blueearth_cst.experiment.indicator_plan import (
    current_indicator_request,
    indicator_anchor,
    verify_indicator_plan,
)
from blueearth_cst.experiment.named_export import (
    NamedExportError,
    legacy_flat_export,
    publish_named_set,
    read_current_publication,
)
from blueearth_cst.experiment.simulation_record import read_simulation_intent_v2
from blueearth_cst.shared.snake_utils import plural, resolve_water_year_start


def publish_selected_sets(
    root: Path, project: dict, settings: dict, selection
) -> list[dict]:
    """Publish every selected set whose indicator set is ready; report each outcome.

    Returns one record per set: ``status`` is ``current`` or ``failed``, with
    the indicator-set and publication ids, the failure reason, and any prior
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
        simulation_path=settings["operation"] == "simulate-and-indicators",
        retained_variables=retained_variables,
        legacy_context="export",
    )
    outcomes = []
    for item in sets:
        try:
            previous = read_current_publication(root, item.set_id)["publication_id"]
        except (OSError, KeyError, ValueError, NamedExportError):
            previous = None
        try:
            request = current_indicator_request(
                root,
                indicator_sets.calculation_records(item.indicators),
                indicator_anchor(project),
            )
            plan = verify_indicator_plan(root, request)
            counts = result_counts(
                root, read_canonical_json(Path(plan["targets"]["manifest"]))
            )
            record = publish_named_set(
                root, item, Path(plan["targets"]["manifest"]), water_year_start=month
            )
            outcomes.append(
                {
                    "set_id": item.set_id,
                    "status": "current",
                    "indicator_set_id": record["indicator_set_id"],
                    "publication_id": record["publication_id"],
                    "reused": previous == record["publication_id"],
                    "available_results": counts[0],
                    "missing_results": counts[1],
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
            f"Earlier results kept at {legacy[0]}; updated results are saved separately "
            "under results/indicator_sets/<set-id>/",
            module="indicators",
        )
    for outcome in outcomes:
        if outcome["status"] == "current":
            action = (
                "results unchanged; reusing saved results"
                if outcome.get("reused")
                else "results saved"
            )
            destination = f"<experiment>/results/indicator_sets/{outcome['set_id']}/"
            log_row(
                f"{outcome['set_id']}: {action} → {destination}",
                module="indicators",
            )
            if outcome.get("missing_results"):
                log_row(
                    f"{outcome['set_id']}: {plural(outcome['missing_results'], 'result')} missing or invalid; "
                    f"{plural(outcome['available_results'], 'result')} available; check result tables and coverage evidence",
                    module="indicators",
                    level="WARNING",
                )
            record_indicator_detail(
                root,
                f"{outcome['set_id']}; indicator set {outcome['indicator_set_id']}; "
                f"publication {outcome['publication_id']}; "
                f"available results={outcome.get('available_results')}; "
                f"missing or invalid results={outcome.get('missing_results')}",
            )
        else:
            kept = (
                "previous results kept; they have not been updated"
                if outcome["prior_publication_id"]
                else "no saved results available"
            )
            log_row(
                f"{outcome['set_id']}: could not update results; {kept}; {outcome['reason'].splitlines()[0]}",
                module="indicators",
                level="ERROR",
            )
    return all(outcome["status"] == "current" for outcome in outcomes)
