# scripts/

What a user runs to execute the pipeline. Snakemake-executed modules live in `blueearth_cst/`;
repository inspection and maintenance tools live in `dev/scripts/` and are never part of a run.

## Runners

| Script | What it does |
|---|---|
| [`run_workflows.py`](run_workflows.py) | Run every enabled workflow in fixed order; the contract is its module docstring. |
| [`run_workflow.py`](run_workflow.py) | Run one of the five workflows through its owned runner. |
| [`generate_scenarios.py`](generate_scenarios.py) | Owned two-phase WF3 launcher: prepare sources, freeze a plan, then generate. |
| [`simulate_system.py`](simulate_system.py) | WF4 runner: validates the operation and targets, then starts one Snakemake call. |
| [`run_snake_docker.sh`](run_snake_docker.sh) | `run_workflows.py` inside the `cst-workflow` Docker image, Linux baseline config. |

## Case setup

| Script | What it does |
|---|---|
| [`create_case.py`](create_case.py) | Create an external case from the example-basin template. |
| [`suggest_experiment_name.py`](suggest_experiment_name.py) | Pin a deliberate `experiment_name` into a config; never overwrites. |
| [`calibrate_batching.py`](calibrate_batching.py) | Time WF4 batch settings on your basin and machine. |
| [`plot_workflow_dag.py`](plot_workflow_dag.py) | Render a workflow's DAG under the project's own `logs/dag/`. |
