# This module declares no generation, model, preparation, or simulation producers.
from blueearth_cst.experiment.metric_plan import metrics_only_configuration
from blueearth_cst.shared.snake_utils import declare_path_tokens, declare_project_root
from blueearth_cst.shared.console_style import RuleRegistry, target_banner

_metric_root, METRIC_TOKENS, METRIC_ANCHOR = metrics_only_configuration(config_path)
exp_dir = _metric_root.as_posix()
results_dir = f"{exp_dir}/results"
engine_dir = f"{exp_dir}/_engine"
# The console block at the bottom of `simulate_system.smk` is shared by both
# branches, so these four names must exist here as well as in
# `simulate_and_metrics.smk`. Derived from the experiment root rather than
# re-read from the config: `metrics_only_configuration` is deliberately a
# projection that never opens the generation or model workflow files, and
# widening it to hand back a project root would give it a second job.
experiment = _metric_root.name
project_dir = _metric_root.parent.parent.as_posix()
LOG_PARTS_DIR = f"{project_dir}/logs/_parts/simulate_system/{experiment}"
# None, not a filename: this branch declares no `gather_logs`/`gather_benchmarks`
# rule, so neither artifact is written by a metrics-only run. `run_summary`
# ignores both arguments today -- the success block is one line and the failure
# block names only the parts directory -- and naming files that the run cannot
# produce would be a lie waiting for the day it starts printing them again.
WORKFLOW_LOG_NAME = None
BENCHMARKS_NAME = None
# Registry for the banner-only 4.07 and 4.08 rules in simulate_system.smk.
RULES = RuleRegistry(LOG_PARTS_DIR, f"{project_dir}/benchmarks/_parts/simulate_system/{experiment}")

declare_path_tokens(experiment=exp_dir)
declare_project_root(project_dir)

def _frozen_simulation(wc):
    return f"{exp_dir}/_engine/simulation.json"

# all
rule all:
    # Prose rather than a path: the metric outputs are a checkpoint-dependent
    # lambda with nothing to list at parse time, and this branch produces
    # nothing else.
    message: target_banner("all", ["selected immutable metric set"], project_dir)
    input:
        lambda wc: _selected_metric_outputs(wc),
