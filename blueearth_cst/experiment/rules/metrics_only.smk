# This module declares no generation, model, preparation, or simulation producers.
from blueearth_cst.experiment.metric_plan import metrics_only_configuration

_metric_root, METRIC_TOKENS, METRIC_ANCHOR = metrics_only_configuration(config_path)
exp_dir = _metric_root.as_posix()
results_dir = f"{exp_dir}/results"

def _frozen_simulation(wc):
    return f"{exp_dir}/config/simulation.json"

# 4.00  all
rule all:
    input:
        lambda wc: _selected_metric_outputs(wc),
