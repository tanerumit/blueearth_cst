"""Run the configured simulation operation through one validated Snakemake invocation."""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from blueearth_cst.experiment.simulation_record import capture_simulation_sources_v2
from blueearth_cst.experiment.simulation_runner import (
    current_targets,
    simulation_command,
    simulation_selection,
    simulation_settings,
)
from blueearth_cst.shared import invocation_history
from blueearth_cst.shared.provenance import file_sha256
from blueearth_cst.shared.windows_job import run_project_child
from blueearth_cst.shared.workflow_config_snapshot import archive_lock


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--project-dir", type=Path)
    parser.add_argument("--target", nargs="+", default=["all"])
    parser.add_argument("--cores", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--forceall", action="store_true")
    parser.add_argument("--new-experiment", action="store_true")
    parser.add_argument("--note")
    parser.add_argument("--recover-reservation", action="store_true")
    args, extra = parser.parse_known_args(argv)
    if extra[:1] == ["--"]:
        extra = extra[1:]
    if args.dry_run:
        extra.append("--dry-run")
    if args.forceall:
        extra.append("--forceall")
    preview = args.dry_run or any(
        flag in extra for flag in ("-n", "--dry-run", "--unlock")
    )
    if args.cores < 1:
        parser.error("--cores must be positive")
    if args.project_dir is None:
        # Config-only syntax has reduced startup-failure coverage: its root is
        # unavailable until the configuration can be parsed.
        try:
            project, _ = simulation_settings(args.config)
        except (OSError, KeyError, TypeError, ValueError) as exc:
            parser.error(str(exc))
        root = Path(project["project"]["project_dir"]).resolve()
    else:
        root = args.project_dir.resolve()
    record_path, record = invocation_history.start(
        root,
        workflow="simulate_system",
        entry_point="scripts/simulate_system.py",
        command=[
            "simulate_system",
            "--config",
            args.config,
            "--target",
            *args.target,
            *extra,
        ],
        targets=list(args.target),
        mode="dry_run" if preview else "execute",
        contract_mode="new_schema",
        invocation_id=os.environ.get(invocation_history.INVOCATION_ENV),
        parent_invocation_id=os.environ.get(invocation_history.PARENT_ENV),
    )
    try:
        project, settings, selection = simulation_selection(args.config)
        if Path(project["project"]["project_dir"]).resolve() != root:
            raise ValueError("--project-dir differs from composed project root")
        record["operation"] = settings["operation"]
        record["indicator_sets"] = [item.set_id for item in selection.sets]
        command, environment = simulation_command(
            args.config,
            args.target,
            args.cores,
            extra,
            snapshot_path=record_path.with_suffix(".indicator-selection"),
        )
        record["configuration"]["source_config_sha256"] = file_sha256(Path(args.config))
        with archive_lock(root, "project-execution"):
            from blueearth_cst.experiment.reservation_context import admit_context_owned

            context = admit_context_owned(
                Path(args.config),
                Path(__file__).resolve().parents[1],
                root,
                record["invocation_id"],
                new_experiment=args.new_experiment,
                note=args.note,
                recover=args.recover_reservation,
                preview=preview,
            )
            if not preview:
                from blueearth_cst.experiment.simulation_runner import (
                    validate_retained_metric_sets,
                )

                validate_retained_metric_sets(
                    root / "experiments" / context.name, command
                )
            if not preview and settings["operation"] == "simulate-and-metrics":
                context.bind_selection()
                capture = capture_simulation_sources_v2(
                    args.config, root, record["invocation_id"]
                )
                environment["CST_SIMULATION_CAPTURE"] = str(capture)
                record["configuration"]["archive_state"] = "pending"
            else:
                record["configuration"]["archive_state"] = "not_applicable"
            environment.update(context.environment())
            environment["CST_SIMULATION_INVOCATION_ID"] = record["invocation_id"]
            invocation_history.update(record_path, record)
            print("WF4 targets: " + " ".join(args.target), flush=True)
            result = run_project_child(
                command,
                env=environment,
                cwd=Path(__file__).resolve().parents[1],
                writing=not preview,
            )
            if (
                result == 0
                and not preview
                and selection.indicators
                and current_targets(args.target) != ["simulations_only"]
            ):
                from blueearth_cst.experiment.metric_export import (
                    export_selected_metrics,
                )

                # Snakemake skips onsuccess when an explicit file target is current.
                # Refresh here, still under project execution ownership, for all reuse.
                export_selected_metrics(
                    root / "experiments" / context.name, project, settings, selection
                )
                from blueearth_cst.shared.run_log_core import log_row

                log_row(
                    f"Selected metric tables exported → {root / 'experiments' / context.name / 'results/metric_sets'}",
                    module="metrics",
                )
        invocation_history.finish(record_path, record, exit_code=result)
        return result
    except ValueError as exc:
        invocation_history.finish(record_path, record, exit_code=None, error=exc)
        parser.error(str(exc))
    except BaseException as exc:
        invocation_history.finish(record_path, record, exit_code=None, error=exc)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
