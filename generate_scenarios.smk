# WF3: model-independent generation and immutable collection publication.
import os
import sys
import uuid
from pathlib import Path
import yaml
sys.path.insert(0, str(Path(workflow.basedir)))
from blueearth_cst.shared.config_composition import compose_config
from blueearth_cst.shared.snake_utils import index_width, member_index_regex, rule_banner, patch_psutil_windows_benchmark
from blueearth_cst.experiment.content_identity import read_canonical_json
from blueearth_cst.experiment.generation_plan import generation_configuration, resolve_generation_plan
from blueearth_cst.experiment.scenario_rows import stochastic_rows
from blueearth_cst.experiment.scenario_provider import legacy_member_name
patch_psutil_windows_benchmark()
config_path = workflow.configfiles[0]
config, WORKFLOW_CONFIG_PATHS = compose_config(config, config_path, entry="generate_scenarios",
    declared_sections=("project", "basin", "climate", "workflows.generate_scenarios"))
WF_CONFIG_PATHS = sorted(WORKFLOW_CONFIG_PATHS.values())
GENERATION = generation_configuration(config, workflow.basedir)
project_dir = GENERATION["project_dir"]
REGION = GENERATION["region"]
CLIMATE_STORE = GENERATION["store"]
store_dir = CLIMATE_STORE.store_dir
_scenario_plan_path = GENERATION["plan_path"]
wg_dir = (Path(_scenario_plan_path).parent / "generation").as_posix()
lookup_path = f"{wg_dir}/config/stress_test_lookup.csv"
LOG_PARTS_DIR = f"{project_dir}/logs/_parts/generate_scenarios/{Path(_scenario_plan_path).parent.name}"
BENCH_PARTS_DIR = f"{project_dir}/benchmarks/_parts/generate_scenarios/{Path(_scenario_plan_path).parent.name}"
WORKFLOW_LOG_NAME = f"wf3_generate_scenarios_{Path(_scenario_plan_path).parent.name}.log"
BENCHMARKS_NAME = f"wf3_benchmarks_{Path(_scenario_plan_path).parent.name}.md"
LOG_RULES = ["3.01_delineate_region", "3.02_extract_historical_climate", "3.03_prepare_stress_test_grid",
             "3.07_generate_weather_realizations", "3.08_perturb_climate_realization"]
INVOCATION_ID = os.environ.setdefault("CST_GENERATION_INVOCATION_ID", uuid.uuid4().hex)
RLZ_NUM = GENERATION["n_realizations"]
ST_NUM = GENERATION["n_design_points"]
ST_WIDTH, RLZ_WIDTH = index_width(ST_NUM), index_width(RLZ_NUM)
_row_capacity = GENERATION["capacity"]
SCENARIO_ROWS = stochastic_rows(RLZ_NUM, ST_NUM, unit_id_capacity=_row_capacity)
_rows_by_id = {row.run_id: row for row in SCENARIO_ROWS}
_rows_by_member = {legacy_member_name(row, st_width=ST_WIDTH): row for row in SCENARIO_ROWS}
_root_rows = tuple(row for row in SCENARIO_ROWS if not row.derived_from)
stress_test_cfg = GENERATION["config"]["climate_perturbations"]
_generation_catalogs = GENERATION["catalogs"]
_generation_request = GENERATION["request"]
clim_source = GENERATION["source"]
_explicit_selection = None
_validated_collections = {}

def _provider_row(wc):
    return _rows_by_member[f"rlz_{wc.rlz_num}_st_{wc.st_num}"]

def _provider_ancestor(wc):
    ancestor = _rows_by_id[_provider_row(wc).derived_from]
    return f"{wg_dir}/output/{legacy_member_name(ancestor, st_width=ST_WIDTH)}.nc"

def _resolved_collection_plan():
    return resolve_generation_plan(GENERATION)

# 3.00  all
rule all:
    input:
        lambda wc: _selected_collection(wc),
        f"{project_dir}/logs/{WORKFLOW_LOG_NAME}",
        f"{project_dir}/benchmarks/{BENCHMARKS_NAME}",

# 3.01  delineate_region
rule delineate_region:
    message: rule_banner("3.01", "delineate_region")
    input:
        **REGION.inputs,
    params:
        **REGION.params,
    output:
        **REGION.outputs,
    log:
        f"{LOG_PARTS_DIR}/3.01_delineate_region.log",
    benchmark:
        f"{BENCH_PARTS_DIR}/3.01_delineate_region.tsv",
    script: REGION.script


# 3.02  extract_historical_climate
rule extract_historical_climate:
    message: rule_banner("3.02", "extract_historical_climate")
    input:
        **CLIMATE_STORE.inputs,
    params:
        **CLIMATE_STORE.params,
    output:
        **CLIMATE_STORE.outputs,
    log:
        f"{LOG_PARTS_DIR}/3.02_extract_historical_climate.log",
    benchmark:
        f"{BENCH_PARTS_DIR}/3.02_extract_historical_climate.tsv",
    script:
        CLIMATE_STORE.script

# 3.03  prepare_stress_test_grid
rule prepare_stress_test_grid:
    message: rule_banner("3.03", "prepare_stress_test_grid")
    input:
        config = ancient(config_path),
        config_workflows = ancient(WF_CONFIG_PATHS),
    params:
        stress_test_cfg = stress_test_cfg,
    output:
        lookup_csv = lookup_path,
    log:
        f"{LOG_PARTS_DIR}/3.03_prepare_stress_test_grid.log",
    benchmark:
        f"{BENCH_PARTS_DIR}/3.03_prepare_stress_test_grid.tsv",
    script:
        "blueearth_cst/experiment/prepare_cst_parameters.py"

# 3.06  prepare_weathergen_config
rule prepare_weathergen_config:
    input:
        plan=lambda wc: checkpoints.prepare_collection_sources.get().output[0],
    output:
        weathergen_config=f"{wg_dir}/config/weathergen_config.yml",
    run:
        import copy
        plan = read_canonical_json(Path(input.plan))
        settings = copy.deepcopy(plan["documents"]["generation_config"]["weathergen"])
        settings["generate_weather"]["out_dir"] = f"{wg_dir}/"
        Path(output[0]).parent.mkdir(parents=True, exist_ok=True)
        Path(output[0]).write_text(yaml.safe_dump(settings, sort_keys=False), encoding="utf-8")

def _collection_plan(wildcards=None):
    path = checkpoints.prepare_collection_sources.get().output[0]
    plan = read_canonical_json(Path(path))
    if wildcards is not None and hasattr(wildcards, "collection_id") and wildcards.collection_id != plan["collection_id"]:
        raise ValueError("requested collection differs from the exact source plan")
    return plan


def _ready_collection(plan):
    from blueearth_cst.experiment.forcing_descriptor import collection_forcing_descriptor, describe_ancillary
    from blueearth_cst.experiment.scenario_collection import read_collection

    marker = Path(plan["manifest_path"])
    if not marker.exists():
        return None
    if plan["collection_id"] not in _validated_collections:
        _validated_collections[plan["collection_id"]] = read_collection(
            marker, describe_forcing=collection_forcing_descriptor, describe_ancillary=describe_ancillary)
    return _validated_collections[plan["collection_id"]]



_source_reuse_ready = False
_live_plan = None
if Path(_scenario_plan_path).exists():
    _retained_plan = read_canonical_json(Path(_scenario_plan_path))
    if all(Path(entry["path"]).is_file() for entry in _retained_plan["source_inventory"]):
        _live_plan, _, _ = _resolved_collection_plan()
        if _live_plan == _retained_plan:
            _source_reuse_ready = _ready_collection(_retained_plan) is not None

# 3.04  prepare_collection_sources
checkpoint prepare_collection_sources:
    input:
        lambda wc: [] if _source_reuse_ready else [
            f"{store_dir}/extract_historical.nc", f"{store_dir}/basin_cells.csv",
            *_generation_catalogs, GENERATION["template"],
            lookup_path,
            *([f"{store_dir}/orography.nc"] if clim_source in {"chirps", "chirps_global"} else []),
        ],
    output:
        _scenario_plan_path,
    params:
        request=_generation_request,
        live_plan_sha256=_live_plan["plan_sha256"] if _live_plan is not None else None,
    run:
        from blueearth_cst.experiment.collection_resolution import write_scenario_plan
        plan, _, _ = _resolved_collection_plan()
        write_scenario_plan(project_dir, plan)


# 3.05  initialize_scenario_collection
rule initialize_scenario_collection:
    input:
        plan=lambda wc: checkpoints.prepare_collection_sources.get().output[0],
        lookup=lookup_path,
    output:
        update((Path(_scenario_plan_path).parent / "initializations" / f"{INVOCATION_ID}.json").as_posix()),
    run:
        from blueearth_cst.experiment.scenario_provider import initialize_planned_collection
        plan, catalog, ancillary = _resolved_collection_plan()
        if plan != read_canonical_json(Path(input.plan)):
            raise ValueError("GeneratedCollectionStale: inputs changed before initialization")
        initialize_planned_collection(project_dir, plan, INVOCATION_ID,
            lookup_path=input.lookup, catalog_bytes=catalog, ancillary_sources=ancillary)


def _collection_row_inputs(wc):
    plan = _collection_plan(wc)
    if _ready_collection(plan) is not None:
        return [_scenario_plan_path]
    row = _rows_by_id[wc.run_id]
    return [(Path(_scenario_plan_path).parent / "initializations" / f"{INVOCATION_ID}.json").as_posix(),
            f"{wg_dir}/output/{legacy_member_name(row, st_width=ST_WIDTH)}.nc"]


# 3.09  retain_scenario_forcing
rule retain_scenario_forcing:
    input:
        _collection_row_inputs,
    output:
        update((Path(project_dir).resolve() / "scenario_collections" / "{collection_id}" / "forcing" / "run_{run_id}.nc").as_posix()),
    wildcard_constraints:
        collection_id="[a-f0-9]{64}",
        run_id=rf"[0-9]{{{len(str(_row_capacity))}}}",
    run:
        from blueearth_cst.experiment.scenario_collection import _job_collection_claim, write_collection_payload
        plan = _collection_plan(wildcards)
        if _ready_collection(plan) is None:
            claim = _job_collection_claim(project_dir, plan, INVOCATION_ID)
            write_collection_payload(claim, f"forcing/run_{wildcards.run_id}.nc", Path(input[1]))


def _collection_publication_inputs(wc):
    plan = _collection_plan(wc)
    if _ready_collection(plan) is not None:
        return [_scenario_plan_path]
    root = Path(plan["manifest_path"]).parent
    return [(root / "forcing" / f"run_{row.run_id}.nc").as_posix() for row in SCENARIO_ROWS]


# 3.10  publish_scenario_collection
checkpoint publish_scenario_collection:
    input:
        _collection_publication_inputs,
    output:
        update((Path(project_dir).resolve() / "scenario_collections" / "{collection_id}" / "collection.json").as_posix()),
    wildcard_constraints:
        collection_id="[a-f0-9]{64}",
    run:
        from blueearth_cst.experiment.scenario_provider import publish_planned_collection
        plan = _collection_plan(wildcards)
        if _ready_collection(plan) is None:
            publish_planned_collection(project_dir, plan, INVOCATION_ID)


def _selected_collection(wc):
    plan = _collection_plan()
    return checkpoints.publish_scenario_collection.get(collection_id=plan["collection_id"]).output[0]



# 3.07  generate_weather_realizations
rule generate_weather_realizations:
    message: rule_banner("3.07", "generate_weather_realizations", summary="generate stochastic weather with weathergenr")
    input:
        initialization=(Path(_scenario_plan_path).parent / "initializations" / f"{INVOCATION_ID}.json").as_posix(),
        source_plan=lambda wc: checkpoints.prepare_collection_sources.get().output[0],
        climate_nc = ancient(f"{store_dir}/extract_historical.nc"),
        basin_cells = ancient(f"{store_dir}/basin_cells.csv"),
        weathergen_config = f"{wg_dir}/config/weathergen_config.yml",
    output:
        temp([f"{wg_dir}/output/{legacy_member_name(row, st_width=ST_WIDTH)}.nc" for row in _root_rows])
    params:
        operation = "generate_roots",
        collection_plan = lambda wc: _collection_plan(),
        project_dir = project_dir,
        invocation_id = INVOCATION_ID,
        rows = [row.as_record() for row in _root_rows],
        output_dir = f"{wg_dir}/output",
        rlz_width = RLZ_WIDTH,
        st_width = ST_WIDTH,
    threads: 1
    resources:
        mem_mb = 2048,
    log:
        f"{LOG_PARTS_DIR}/3.07_generate_weather_realizations.log",
    benchmark:
        f"{BENCH_PARTS_DIR}/3.07_generate_weather_realizations.tsv",
    script:
        "blueearth_cst/experiment/scenario_provider.py"

# 3.11  gather_logs
rule gather_logs:
    input:
        _selected_collection,
    output:
        f"{project_dir}/logs/{WORKFLOW_LOG_NAME}",
    params:
        rules=LOG_RULES,
        parts_dir=LOG_PARTS_DIR,
    script: "blueearth_cst/shared/merge_logs.py"

# 3.12  gather_benchmarks
rule gather_benchmarks:
    input:
        _selected_collection,
    output:
        f"{project_dir}/benchmarks/{BENCHMARKS_NAME}",
    params:
        parts_dir=BENCH_PARTS_DIR,
        workflow_num=3,
    script: "blueearth_cst/shared/merge_benchmarks.py"

# 3.08  perturb_climate_realization
rule perturb_climate_realization:
    message: rule_banner("3.08", "perturb_climate_realization", "rlz {wildcards.rlz_num} | st {wildcards.st_num}", summary="apply one stress-test member to one realization")
    wildcard_constraints:
        st_num=member_index_regex(ST_WIDTH),
    input:
        initialization=(Path(_scenario_plan_path).parent / "initializations" / f"{INVOCATION_ID}.json").as_posix(),
        source_plan=lambda wc: checkpoints.prepare_collection_sources.get().output[0],
        rlz_nc = _provider_ancestor,
        lookup_csv = lookup_path,
        weathergen_config = f"{wg_dir}/config/weathergen_config.yml",
    output:
        rlz_st_nc = temp(f"{wg_dir}/output/rlz_"+"{rlz_num}"+"_st_"+"{st_num}"+".nc")
    params:
        operation = "transform",
        collection_plan = lambda wc: _collection_plan(),
        project_dir = project_dir,
        invocation_id = INVOCATION_ID,
        row = lambda wildcards: _provider_row(wildcards).as_record(),
    threads: 1
    resources:
        mem_mb = 2048,
    log:
        f"{LOG_PARTS_DIR}/3.08_perturb_climate_realization/rlz_{{rlz_num}}_st_{{st_num}}.log",
    benchmark:
        f"{BENCH_PARTS_DIR}/3.08_perturb_climate_realization/rlz_{{rlz_num}}_st_{{st_num}}.tsv",
    script:
        "blueearth_cst/experiment/scenario_provider.py"
