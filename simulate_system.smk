# WF4: supported through scripts/simulate_system.py or scripts/run_workflows.py.
import os
import sys
from pathlib import Path
REPOSITORY = Path(workflow.basedir)
sys.path.insert(0, str(REPOSITORY))
from blueearth_cst.experiment.content_identity import content_sha256, read_canonical_json
from blueearth_cst.experiment.simulation_runner import simulation_settings
from blueearth_cst.shared.snake_utils import patch_psutil_windows_benchmark
from blueearth_cst.shared.provenance import SHORT_DIGEST_CHARS, short_digest
patch_psutil_windows_benchmark()
config_path = workflow.configfiles[0]
_, _settings = simulation_settings(config_path)
OPERATION = _settings["operation"]
if os.environ.get("CST_SIMULATION_OPERATION") != OPERATION or not os.environ.get("CST_SIMULATION_INVOCATION_ID"):
    raise ValueError("Use python scripts/simulate_system.py --config <project> --target all (or --target metrics for metrics-only); bare simulate_system.smk is unsupported")
if OPERATION == "metrics-only":
    include: "blueearth_cst/experiment/rules/metrics_only.smk"
else:
    include: "blueearth_cst/experiment/rules/simulate_and_metrics.smk"

def _current_metric_request(wc=None):
    from blueearth_cst.experiment.metric_plan import current_metric_request

    _frozen_simulation(wc)
    return current_metric_request(exp_dir, METRIC_TOKENS, METRIC_ANCHOR)


# 4.08  prepare_metric_plan
checkpoint prepare_metric_plan:
    input:
        simulation=_frozen_simulation,
        responses=f"{exp_dir}/responses/response_inventory.json",
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
    path = checkpoints.prepare_metric_plan.get(metric_request_id=short_digest(content_sha256(request))).output[0]
    from blueearth_cst.experiment.metric_plan import read_metric_set, verify_metric_plan
    plan = verify_metric_plan(exp_dir, request)
    if Path(plan["targets"]["manifest"]).exists():
        read_metric_set(exp_dir, Path(plan["targets"]["manifest"]))
    return list(plan["targets"].values())


def _metric_set_plan(wc):
    request = _current_metric_request(wc)
    path = checkpoints.prepare_metric_plan.get(metric_request_id=short_digest(content_sha256(request))).output[0]
    plan = read_canonical_json(Path(path))
    if wc.metric_set_id != short_digest(plan["metric_set_id"]):
        raise ValueError("metric set differs from its exact selected plan")
    return path


# 4.09  publish_metric_set
rule publish_metric_set:
    input:
        plan=_metric_set_plan,
    output:
        manifest=update(f"{results_dir}/metric_sets/{{metric_set_id}}/metrics.json"),
        units=update(f"{results_dir}/metric_sets/{{metric_set_id}}/unit_index.csv"),
        environment=update(f"{results_dir}/metric_sets/{{metric_set_id}}/metric_environment.json"),
        # publish_metric_set copies the checked benchmark report into the set so
        # a reader never needs the installed asset. Declared here because an
        # undeclared file is one Snakemake neither tracks nor cleans: a
        # --forcerun or partial clean would leave a manifest whose
        # return_level_benchmark.sha256 binds a file that is gone.
        benchmark=update(f"{results_dir}/metric_sets/{{metric_set_id}}/return_level_benchmark.json"),
        tables=[update(f"{results_dir}/metric_sets/{{metric_set_id}}/{token}_indicators.csv") for token in METRIC_TOKENS],
    wildcard_constraints:
        metric_set_id=rf"[a-f0-9]{{{SHORT_DIGEST_CHARS}}}",
    run:
        from blueearth_cst.experiment.metric_plan import publish_metric_set
        publish_metric_set(exp_dir, read_canonical_json(Path(input.plan)))


# 4.10  metrics
rule metrics:
    input:
        _selected_metric_outputs,
