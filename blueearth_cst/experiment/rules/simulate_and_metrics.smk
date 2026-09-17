# WF4 stage two. Every collection artifact is an external, validated leaf.
import shlex
import subprocess
import tempfile
from datetime import datetime
from blueearth_cst.experiment.simulation_runner import simulation_settings, resolve_selected_collection
from blueearth_cst.experiment.simulation_record import live_simulation_inputs, read_simulation, SimulationFrozenError
from blueearth_cst.experiment.allocate import resolve_default_experiment_name
from blueearth_cst.experiment.batch_sizing import disk_headroom_bytes, measure_member_footprint, resolve_batch_size
from blueearth_cst.shared.indicator_tables import indicator_tables
from blueearth_cst.shared.snake_utils import ADVANCED_SETTINGS, DEFAULT_JULIA_THREADS, DEFAULT_WFLOW_OUTVARS, declare_path_tokens, declare_project_root, julia_prefix, project_slug, resolve_water_year_start, validate_experiment_name
from blueearth_cst.shared.console_style import rule_banner, target_banner

project, my_cfg = simulation_settings(config_path)
project_dir = Path(project["project"]["project_dir"]).resolve().as_posix()
experiment = my_cfg.get("experiment_name")
if experiment is None or not str(experiment).strip():
    experiment = resolve_default_experiment_name(project_dir, project_slug(project_dir, reserve=len("_YYYYMMDD")), datetime.now().strftime("%Y%m%d"))
experiment = validate_experiment_name(experiment, project_dir)
exp_dir = f"{project_dir}/experiments/{experiment}"
runs_dir = f"{exp_dir}/hydrology/wflow"
results_dir = f"{exp_dir}/results"
# Engine bookkeeping, collected per scope so a reader learns to ignore one
# directory rather than meeting machinery at three depths (t2609152104).
engine_dir = f"{exp_dir}/_engine"
basin_dir = f"{project_dir}/models/hydrology/wflow"
SELECTION, COLLECTION = resolve_selected_collection(config_path, REPOSITORY)
_intent = read_canonical_json(Path(SELECTION["manifest_path"]).parent / "collection_intent.json")
SIM_WINDOW_START = _intent["scenario_spec"]["simulation_window"]["start"]
SIM_WINDOW_END = _intent["scenario_spec"]["simulation_window"]["end"]
RUN_IDS = [item["run_id"] for item in COLLECTION["forcing"]]
LOG_PARTS_DIR = f"{project_dir}/logs/_parts/simulate_system/{experiment}"
BENCH_PARTS_DIR = f"{project_dir}/benchmarks/_parts/simulate_system/{experiment}"
WORKFLOW_LOG_NAME = f"wf4_simulate_system_{experiment}.log"
BENCHMARKS_NAME = f"wf4_benchmarks_{experiment}.md"
LOG_RULES = ["4.01_write_model_reference", "4.02_check_model_reference",
             "4.04_downscale_climate_realization", "4.05_run_wflow"]
METRIC_TOKENS = list(my_cfg.get("metrics", indicator_tables((project.get("model") or {}).get("outvars", DEFAULT_WFLOW_OUTVARS))))
METRIC_ANCHOR = f"YS-{resolve_water_year_start((project.get('climate') or {}).get('water_year_start')).upper()}"

# The run's key folders, stated ONCE -- the same block WF0/WF1/WF2 carry, and
# the one `run_stress_test.smk` had before the R12 split (868c4b7c) dropped it.
# `run_header` prints them at the top of the console, every rule log repeats
# them in its own header, and `log_row` plus the console tee rewrite every path
# below to these names. Declared longest-root-last so `experiment` -- under
# which a WF4 run writes almost everything -- wins over `project`.
#
# No `data` row unless the collection's catalog declares a local root: WF4 reads
# no global data catalog of its own, it reads the collection WF3 retained.
declare_path_tokens(
    model=basin_dir,
    scenarios=f"{project_dir}/scenarios",
    experiment=exp_dir,
)
declare_project_root(project_dir)

def _selected_collection(wc):
    return SELECTION["manifest_path"]

def _live_simulation_inputs():
    settings = {"simulation_window": {"start": SIM_WINDOW_START, "end": SIM_WINDOW_END},
                "resolution_mode": SELECTION["resolution_mode"], "manifest_path": SELECTION["manifest_path"]}
    with tempfile.TemporaryDirectory(dir=project_dir) as directory:
        return live_simulation_inputs(exp_dir, project_dir=project_dir, model_root=basin_dir,
            collection=COLLECTION, settings=settings, julia_command=shlex.split(julia_prefix(1)),
            header_path=Path(directory) / "headers.txt")

_simulation_complete = False
if Path(f"{exp_dir}/config/simulation.json").exists():
    stored = read_simulation(exp_dir)
    current, _ = _live_simulation_inputs()
    if current["simulation_id"] != stored["simulation_id"]:
        raise SimulationFrozenError("simulation inputs changed; use a new experiment name")
    if stored["response_inventory_sha256"] is not None:
        from blueearth_cst.experiment.response_inventory import read_response_inventory
        read_response_inventory(exp_dir)
        _simulation_complete = True

def _frozen_simulation(wc):
    if _simulation_complete:
        return f"{exp_dir}/config/simulation.json"
    return checkpoints.freeze_wflow_simulation.get().output.simulation

# The targets `rule all` lists, built HERE rather than inline in its `message:`:
# Snakemake's f-string preprocessor cannot parse an f-string inside a multi-line
# directive expression. See the same note in `generate_scenarios.smk`.
#
# The metric outputs are a CHECKPOINT-dependent lambda with no parse-time path,
# so they are named in prose -- as `run_stress_test.smk` named the same target.
WF4_TARGETS = ["selected immutable metric set",
               f"{project_dir}/logs/{WORKFLOW_LOG_NAME}",
               f"{project_dir}/benchmarks/{BENCHMARKS_NAME}"]

# 4.00  all
rule all:
    message: target_banner("4.00", "all", WF4_TARGETS, project_dir)
    input:
        lambda wc: _selected_metric_outputs(wc),
        f"{project_dir}/logs/{WORKFLOW_LOG_NAME}",
        f"{project_dir}/benchmarks/{BENCHMARKS_NAME}",

if not _simulation_complete:
    # 4.01  write_model_reference
    rule write_model_reference:
        message: rule_banner("4.01", "write_model_reference")
        input:
            model_ready=ancient(f"{basin_dir}/.outputs_configured"),
            model_toml=ancient(f"{basin_dir}/wflow_sbm.toml"),
        params:
            model_dir=basin_dir,
            project_dir=project_dir,
        output:
            model_reference=update(f"{exp_dir}/config/model_reference.yml"),
        log:
            f"{LOG_PARTS_DIR}/4.01_write_model_reference.log",
        script: "../write_model_reference.py"

    # 4.03  freeze_wflow_simulation
    checkpoint freeze_wflow_simulation:
        message: rule_banner("4.03", "freeze_wflow_simulation", summary="pin the simulation's inputs so the experiment cannot drift")
        input:
            collection=_selected_collection,
            model_reference=f"{exp_dir}/.model_reference_ok",
        output:
            simulation=update(f"{exp_dir}/config/simulation.json"),
            settings=update(f"{exp_dir}/config/simulator_settings.json"),
            code=update(f"{exp_dir}/config/simulator_adapter_code_inventory.json"),
            environment=update(f"{exp_dir}/config/simulation_environment.json"),
            request=update(f"{exp_dir}/config/response_request.json"),
        run:
            from blueearth_cst.experiment.simulation_record import freeze_simulation
            from blueearth_cst.shared.workflow_config_snapshot import composed_workflow_section, snapshot_bytes
            record, documents = _live_simulation_inputs()
            # Written on the freeze, inside the same call that seals the
            # experiment's inputs. Named by none of the four frozen documents,
            # so `simulation_id` -- and every metric set identified through it
            # -- stays where it was.
            freeze_simulation(exp_dir, record, documents, config_snapshot=snapshot_bytes(
                "simulate_system", config_path,
                Path(config_path).parent / project["workflows"]["simulate_system"]["config_path"],
                composed_workflow_section(project, "simulate_system", my_cfg)))

    # 4.02  check_model_reference
    rule check_model_reference:
        message: rule_banner("4.02", "check_model_reference")
        input:
            model_reference=f"{exp_dir}/config/model_reference.yml",
            model_toml=ancient(f"{basin_dir}/wflow_sbm.toml"),
        params:
            model_dir=basin_dir,
            experiment=experiment,
        output:
            ok=temp(touch(f"{exp_dir}/.model_reference_ok")),
        log:
            f"{LOG_PARTS_DIR}/4.02_check_model_reference.log",
        script: "../check_model_reference.py"

    # 4.04  downscale_climate_realization
    rule downscale_climate_realization:
        message: rule_banner("4.04", "downscale_climate_realization", "run {wildcards.run_id}", summary="downscale the perturbed climate onto the model grid")
        wildcard_constraints:
            run_id="(?:" + "|".join(RUN_IDS) + ")",
        input:
            nc=lambda wc: (Path(SELECTION["manifest_path"]).parent / "forcing" / f"run_{wc.run_id}.nc").as_posix(),
            collection=_selected_collection,
            simulation=_frozen_simulation,
            model_reference_ok=f"{exp_dir}/.model_reference_ok",
        output:
            nc=temp(f"{runs_dir}/forcing/inmaps_run_{{run_id}}.nc"),
            toml=update(f"{runs_dir}/config/run_{{run_id}}.toml"),
            catalog=temp(f"{runs_dir}/config/run_{{run_id}}.yml"),
            temporal=update(f"{runs_dir}/config/run_{{run_id}}.temporal.json"),
        params:
            model_dir=basin_dir,
            run_id=lambda wc: wc.run_id,
            validated_collection=COLLECTION,
            native_output_path=f"{runs_dir}/output/run_{{run_id}}.csv",
            native_log_path=f"{runs_dir}/output/run_{{run_id}}.log",
            sim_window_start=SIM_WINDOW_START,
            sim_window_end=SIM_WINDOW_END,
        threads: 1
        resources:
            mem_mb=2048,
        log:
            f"{LOG_PARTS_DIR}/4.04_downscale_climate_realization/run_{{run_id}}.log",
        benchmark:
            f"{BENCH_PARTS_DIR}/4.04_downscale_climate_realization/run_{{run_id}}.tsv",
        script: "../downscale_climate_forcing.py"

    compute = my_cfg.get("compute") or {}
    _cores = int(workflow.cores or 1)
    _threads = min([DEFAULT_JULIA_THREADS, *[int(value) for name, value in
        getattr(workflow.resource_settings, "overwrite_threads", {}).items() if name.startswith("run_wflow_batch_")]])
    sizing = resolve_batch_size(member_count=len(RUN_IDS), cores=max(1, _cores // max(1, min(_cores, _threads))),
        batch_size_max=compute.get("batch_size_max", 8), explicit=compute.get("batch_size"),
        footprint=measure_member_footprint(basin_dir, SIM_WINDOW_START, SIM_WINDOW_END, write_states=False),
        headroom_bytes=disk_headroom_bytes(project_dir,
            fraction=ADVANCED_SETTINGS["defaults"]["batch_disk_headroom_fraction"], headroom_gb=compute.get("disk_headroom_gb")))
    if sizing.warning:
        print(sizing.warning, flush=True)
    for batch, offset in enumerate(range(0, len(RUN_IDS), sizing.batch_size)):
        members = RUN_IDS[offset:offset + sizing.batch_size]
        # 4.05  run_wflow_batch — one bounded batch of retained runs
        rule:
            name: f"run_wflow_batch_{batch}"
            # Member COUNT rather than the span `run_stress_test.smk` printed:
            # the post-R12 batch is keyed by opaque run ids, so a span would read
            # as two digests rather than as a range. The count is the part that
            # says how long this line will sit there.
            message: rule_banner("4.05", f"run_wflow_batch_{batch}", f"{len(members)} members", summary="run Wflow for one batch")
            input:
                simulation=_frozen_simulation,
                forcing=[f"{runs_dir}/forcing/inmaps_run_{run}.nc" for run in members],
                tomls=[f"{runs_dir}/config/run_{run}.toml" for run in members],
            output:
                csvs=[update(f"{runs_dir}/output/run_{run}.csv") for run in members],
            threads: DEFAULT_JULIA_THREADS
            resources:
                mem_mb=2048,
            params:
                records=[str(batch), *[value for run in members for value in
                    (run, f"{runs_dir}/config/run_{run}.toml", f"{runs_dir}/output/run_{run}.csv")]],
                julia=lambda wc, threads: julia_prefix(threads),
            log:
                f"{LOG_PARTS_DIR}/4.05_run_wflow/batch_{batch}.log",
            benchmark:
                f"{BENCH_PARTS_DIR}/4.05_run_wflow/batch_{batch}.tsv",
            run:
                record = read_simulation(exp_dir)
                if record["response_inventory_sha256"] is not None or any(Path(p).exists() for p in output.csvs):
                    raise SimulationFrozenError("native responses already exist; use a new experiment name")
                subprocess.run([sys.executable, "-u", str(REPOSITORY / "blueearth_cst/shared/run_logged.py"),
                    str(log[0]), "--", *shlex.split(params.julia),
                    str(REPOSITORY / "blueearth_cst/experiment/run_wflow_batch.jl"), *params.records], check=True)

    # 4.06  publish_native_responses
    rule publish_native_responses:
        message: rule_banner("4.06", "publish_native_responses", summary="inventory the retained native runs")
        input:
            simulation=_frozen_simulation,
            csvs=[f"{runs_dir}/output/run_{run}.csv" for run in RUN_IDS],
            tomls=[f"{runs_dir}/config/run_{run}.toml" for run in RUN_IDS],
            temporal=[f"{runs_dir}/config/run_{run}.temporal.json" for run in RUN_IDS],
        output:
            update(f"{engine_dir}/response_inventory.json"),
        run:
            from blueearth_cst.experiment.response_inventory import publish_response_inventory
            from blueearth_cst.experiment.wflow_response_reader import NativeRunArtifacts
            native = {run: NativeRunArtifacts(Path(csv), Path(toml), Path(temporal))
                for run, csv, toml, temporal in zip(RUN_IDS, input.csvs, input.tomls, input.temporal)}
            evidence = read_canonical_json(Path(input.temporal[0]))
            if any(item["descriptor"]["source_calendar"] != evidence["source_calendar"] for item in COLLECTION["forcing"]):
                raise ValueError("response temporal evidence differs from retained source calendar")
            publish_response_inventory(exp_dir, native, evidence)

# 4.07  responses
rule responses:
    message: rule_banner("4.07", "responses")
    input:
        f"{engine_dir}/response_inventory.json",

# 4.11  gather_logs
rule gather_logs:
    message: rule_banner("4.11", "gather_logs")
    input:
        lambda wc: _selected_metric_outputs(wc),
    output:
        f"{project_dir}/logs/{WORKFLOW_LOG_NAME}",
    params:
        rules=LOG_RULES,
        parts_dir=LOG_PARTS_DIR,
    script: "../../shared/merge_logs.py"

# 4.12  gather_benchmarks
rule gather_benchmarks:
    message: rule_banner("4.12", "gather_benchmarks")
    input:
        lambda wc: _selected_metric_outputs(wc),
    output:
        f"{project_dir}/benchmarks/{BENCHMARKS_NAME}",
    params:
        parts_dir=BENCH_PARTS_DIR,
        workflow_num=4,
    script: "../../shared/merge_benchmarks.py"
