# WF4: supported through scripts/simulate_system.py or scripts/run_workflows.py.
import os
import sys
import time
from pathlib import Path
REPOSITORY = Path(workflow.basedir)
sys.path.insert(0, str(REPOSITORY))
from blueearth_cst.experiment.content_identity import content_sha256, read_canonical_json
from blueearth_cst.experiment.simulation_runner import simulation_settings
from blueearth_cst.shared.snake_utils import declare_warning_tally, patch_psutil_windows_benchmark, warning_count
from blueearth_cst.shared.console_style import install_console_style, open_run_header, run_summary, target_banner
from blueearth_cst.shared.provenance import SHORT_DIGEST_CHARS, short_digest
patch_psutil_windows_benchmark()
config_path = workflow.configfiles[0]
_, _settings = simulation_settings(config_path)
OPERATION = _settings["operation"]
if os.environ.get("CST_SIMULATION_OPERATION") != OPERATION or not os.environ.get("CST_SIMULATION_INVOCATION_ID"):
    raise ValueError("Use python scripts/simulate_system.py --config <project> --target all (or --target simulations_and_indicators for metrics-only); bare simulate_system.smk is unsupported")
if OPERATION == "metrics-only":
    include: "blueearth_cst/experiment/rules/metrics_only.smk"
else:
    include: "blueearth_cst/experiment/rules/simulate_and_metrics.smk"

# RULES comes from whichever module was included above.
PREPARE_INDICATOR_PLAN = RULES.banner_only("4.07", "prepare_indicator_plan")
DERIVE_SYSTEM_INDICATORS = RULES.banner_only("4.08", "derive_system_indicators", summary="reduce the retained responses to the immutable metric set")


def _current_metric_request(wc=None):
    from blueearth_cst.experiment.metric_plan import current_metric_request

    _frozen_simulation(wc)
    return current_metric_request(exp_dir, METRIC_TOKENS, METRIC_ANCHOR)


# 4.07  prepare_indicator_plan
checkpoint prepare_indicator_plan:
    message: PREPARE_INDICATOR_PLAN.banner(context="metric_request {wildcards.metric_request_id}")
    input:
        simulation=_frozen_simulation,
        responses=f"{engine_dir}/response_inventory.json",
    output:
        f"{engine_dir}/metric_requests/{{metric_request_id}}.json",
    wildcard_constraints:
        metric_request_id=rf"[a-f0-9]{{{SHORT_DIGEST_CHARS}}}",
    params:
        request=_current_metric_request,
    run:
        from blueearth_cst.experiment.metric_plan import write_metric_plan
        if wildcards.metric_request_id != short_digest(content_sha256(params.request)):
            raise ValueError("metric request differs from its exact checkpoint")
        write_metric_plan(exp_dir, params.request)


def _selected_metric_outputs(wc):
    request = _current_metric_request(wc)
    path = checkpoints.prepare_indicator_plan.get(metric_request_id=short_digest(content_sha256(request))).output[0]
    from blueearth_cst.experiment.metric_plan import read_metric_set, verify_metric_plan
    plan = verify_metric_plan(exp_dir, request)
    if Path(plan["targets"]["manifest"]).exists():
        read_metric_set(exp_dir, Path(plan["targets"]["manifest"]))
    return list(plan["targets"].values())


def _metric_set_plan(wc):
    request = _current_metric_request(wc)
    path = checkpoints.prepare_indicator_plan.get(metric_request_id=short_digest(content_sha256(request))).output[0]
    plan = read_canonical_json(Path(path))
    if wc.metric_set_id != short_digest(plan["metric_set_id"]):
        raise ValueError("metric set differs from its exact selected plan")
    return path


# 4.08  derive_system_indicators
rule derive_system_indicators:
    message: DERIVE_SYSTEM_INDICATORS.banner(context="metric_set {wildcards.metric_set_id}")
    input:
        plan=_metric_set_plan,
    output:
        manifest=update(f"{engine_dir}/metric_sets/{{metric_set_id}}/metrics.json"),
        units=update(f"{results_dir}/metric_sets/{{metric_set_id}}/metric_run_lookup.csv"),
        environment=update(f"{engine_dir}/metric_sets/{{metric_set_id}}/metric_environment.json"),
        # derive_system_indicators copies the checked benchmark report into the set so
        # a reader never needs the installed asset. Declared here because an
        # undeclared file is one Snakemake neither tracks nor cleans: a
        # --forcerun or partial clean would leave a manifest whose
        # return_level_benchmark.sha256 binds a file that is gone.
        benchmark=update(f"{engine_dir}/metric_sets/{{metric_set_id}}/return_level_benchmark.json"),
        tables=[update(f"{results_dir}/metric_sets/{{metric_set_id}}/{token}_indicators.csv") for token in METRIC_TOKENS],
    wildcard_constraints:
        metric_set_id=rf"[a-f0-9]{{{SHORT_DIGEST_CHARS}}}",
    run:
        from blueearth_cst.experiment.metric_plan import publish_metric_set
        publish_metric_set(exp_dir, read_canonical_json(Path(input.plan)))


# simulations_and_indicators -- target (unnumbered)
rule simulations_and_indicators:
    # A `target_banner` with NO target list, unlike `simulations_only` and
    # every `rule all`. `_selected_metric_outputs` is a checkpoint-dependent input function, so
    # its targets do not exist at parse time and re-calling it from `params`
    # to list them would evaluate that resolution twice, at two different
    # moments, for a cosmetic gain. The metric sets are named by 4.08's own
    # `Published <id>` row instead.
    message: target_banner("simulations_and_indicators", [])
    input:
        _selected_metric_outputs,


# --------------------------------------------------------------------------
# Console: the run's own opening and closing block, and the Snakemake restyle.
#
# Defined HERE, once, rather than in either included module: `simulate_system.smk`
# includes exactly one of `simulate_and_metrics.smk` and `metrics_only.smk`, so a
# copy in each would be two definitions of the same three handlers to keep in
# step. Both modules therefore define `project_dir`, `experiment`,
# `LOG_PARTS_DIR`, `WORKFLOW_LOG_NAME` and `BENCHMARKS_NAME` -- see the note in
# `metrics_only.smk`, which has no log or benchmark table to name.
#
# Restored 2026-09-16. The R12 split (868c4b7c) carried the rule bodies out of
# `run_stress_test.smk` but not the file scaffolding, so WF4 ran with no
# `_ConsoleHandler` at all.
# --------------------------------------------------------------------------

# Wall clock for the end-of-run summary. Taken at PARSE, not in `onstart`:
# Snakemake exposes no run duration to these handlers, and parse-to-finish is
# the interval a person actually waited. On WF4 that matters more than
# elsewhere, since the parse-time `_live_simulation_inputs()` above shells out
# to Julia for the simulator headers.
_RUN_STARTED = time.monotonic()

# One tally per run, opened at parse time and published to every job process
# through the environment: a rule prints its warnings from a process of its
# own, and the verdict below is written by this one. See
# `snake_utils.declare_warning_tally`.
declare_warning_tally(project_dir, WORKFLOW_LOG_NAME)


def _summary(failed):
    """Print the end-of-run block to STDERR, beside Snakemake's own output.

    stderr because that is where Snakemake writes its console, so a redirect
    that captures one captures both. Never raises: a summary that broke a
    successful run would be the worst possible trade for a convenience.
    """
    try:
        # One write, blank line before it -- see the note on `_header`.
        sys.stderr.write(
            "\n"
            + run_summary(
                "wf4 simulate_system",
                project_dir,
                WORKFLOW_LOG_NAME,
                BENCHMARKS_NAME,
                elapsed_seconds=time.monotonic() - _RUN_STARTED,
                failed=failed,
                log_parts_dir=LOG_PARTS_DIR,
                warnings=warning_count(),
            )
            + "\n"
        )
    except Exception as exc:  # noqa: BLE001 -- never break a run over a banner
        # Nested, because sys.stderr may be exactly what failed above. An
        # OSError escaping here surfaces as an error in this Snakefile and
        # masks the rule that actually failed (observed 2026-08-17, wf0).
        try:
            print(f"(run summary unavailable: {exc})", file=sys.stderr)
        except Exception:  # noqa: BLE001
            pass


def _header():
    """Print the start-of-run block to STDERR, mirroring `_summary`.

    Takes no arguments on purpose. Every name it reports is read INSIDE the
    guard, so a value that turns out not to resolve in the `onstart` namespace
    costs a line of console rather than the run -- which matters here, where
    `experiment` comes from whichever of the two modules was included.
    """
    try:
        # One write, carrying its own blank line on both sides: the block is the
        # first thing this toolbox puts on the console and it must not open
        # flush against Snakemake's preamble nor close flush against its
        # `Job stats:`. `open_run_header` owns that spacing.
        open_run_header("wf4 simulate_system", project_dir, config_path,
                        experiment=experiment, operation=OPERATION)
    except Exception as exc:  # noqa: BLE001 -- never break a run over a banner
        # Nested, for the reason given on `_summary` -- and it matters more
        # here: this runs from `onstart`, so a raise aborts the run before any
        # rule executes at all.
        try:
            print(f"(run header unavailable: {exc})", file=sys.stderr)
        except Exception:  # noqa: BLE001
            pass


onstart:
    # Restyle Snakemake's own console output into this toolbox's grammar (one
    # line per job start and end). Here and not at parse time: the logging
    # stack does not exist yet then. Fail-open; see install_console_style.
    install_console_style()
    _header()


onsuccess:
    _summary(failed=False)


onerror:
    _summary(failed=True)
