# WF3: model-independent generation and immutable collection publication.
import os
import sys
import time
import uuid
from pathlib import Path
import yaml
sys.path.insert(0, str(Path(workflow.basedir)))
from blueearth_cst.shared.config_composition import compose_config
from blueearth_cst.shared.snake_utils import catalog_root, declare_path_tokens, declare_project_root, index_width, log_row, member_index_regex, patch_psutil_windows_benchmark
from blueearth_cst.shared.console_style import install_console_style, open_run_header, rule_banner, run_summary, target_banner
from blueearth_cst.shared.provenance import SHORT_DIGEST_CHARS, short_digest
from blueearth_cst.experiment.content_identity import read_canonical_json
from blueearth_cst.experiment.generation_plan import generation_configuration, resolve_generation_plan
from blueearth_cst.experiment.scenario_rows import stochastic_rows
from blueearth_cst.experiment.scenario_provider import legacy_member_name
patch_psutil_windows_benchmark()
config_path = workflow.configfiles[0]
CONFIG_PROJECTION = ("project", "basin", "climate", "workflows.generate_scenarios")
config, WORKFLOW_CONFIG_PATHS = compose_config(config, config_path, entry="generate_scenarios",
    declared_sections=CONFIG_PROJECTION)
WF_CONFIG_PATHS = sorted(WORKFLOW_CONFIG_PATHS.values())
GENERATION = generation_configuration(config, workflow.basedir)
project_dir = GENERATION["project_dir"]
REGION = GENERATION["region"]
CLIMATE_STORE = GENERATION["store"]
store_dir = CLIMATE_STORE.store_dir
_scenario_request_path = GENERATION["request_path"]
wg_dir = (Path(_scenario_request_path).parent / "generation").as_posix()
lookup_path = f"{wg_dir}/config/stress_test_lookup.csv"
# WF3's run records are keyed by the SCENARIO-REQUEST fingerprint, because a
# project can hold several requests at once and WF3 has no user-facing name to
# key on the way WF4 keys on its experiment.
#
# Since t2609152107 the `scenarios/requests/<fingerprint>/` DIRECTORY is itself
# named by the first SHORT_DIGEST_CHARS of that fingerprint, so this is a read
# of the directory name rather than a slice of it. The log, the benchmark table
# and both `_parts/` trees therefore cannot drift from the directory: one
# constant sets all four.
#
# Still not passed through `short_digest`, which RAISES on a value that is not a
# digest. This runs at parse time, so a request directory with an unexpected
# name would fail every WF3 invocation over a cosmetic key.
_plan_key = Path(_scenario_request_path).parent.name
LOG_PARTS_DIR = f"{project_dir}/logs/_parts/generate_scenarios/{_plan_key}"
BENCH_PARTS_DIR = f"{project_dir}/benchmarks/_parts/generate_scenarios/{_plan_key}"
WORKFLOW_LOG_NAME = f"wf3_generate_scenarios_{_plan_key}.log"
BENCHMARKS_NAME = f"wf3_benchmarks_{_plan_key}.md"
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

# The run's key folders, stated ONCE. `run_header` prints them at the top of the
# console and every rule log repeats them in its own header; `log_row` and the
# console tee rewrite every path below to these names. No `model` row -- WF3
# builds none, and that is the point of the R12 split: generation is
# model-independent. `scenarios` is the WF3 output ROOT rather than one request,
# because a project holds several requests at once and the digest-named
# directory under it is the part a reader is telling apart.
#
# Dropped by the R12 split (868c4b7c) along with the rest of the apparatus and
# restored 2026-09-16; `run_stress_test.smk` carried the same block.
declare_path_tokens(
    data=catalog_root(_generation_catalogs),
    climate=store_dir,
    scenarios=f"{project_dir}/scenarios",
)
declare_project_root(project_dir)

_explicit_selection = None
_validated_collections = {}

def _provider_row(wc):
    return _rows_by_member[f"rlz_{wc.rlz_num}_st_{wc.st_num}"]

def _provider_ancestor(wc):
    ancestor = _rows_by_id[_provider_row(wc).derived_from]
    return f"{wg_dir}/output/{legacy_member_name(ancestor, st_width=ST_WIDTH)}.nc"

def _resolved_collection_plan():
    return resolve_generation_plan(GENERATION)

# The targets `rule all` lists, built HERE rather than inline in its `message:`.
# Snakemake's own f-string preprocessor cannot parse an f-string inside a
# multi-line directive expression -- it raises `UnboundLocalError: t1` out of
# `parser.parse_fstring` before the Snakefile is ever executed. `run_stress_test.smk`
# had the same constraint and answered it the same way, with a pre-built dict.
#
# The selected collection is a CHECKPOINT-dependent lambda with no parse-time
# path, so it is named in prose; the other two are plain strings.
WF3_TARGETS = ["selected scenario collection",
               f"{project_dir}/logs/{WORKFLOW_LOG_NAME}",
               f"{project_dir}/benchmarks/{BENCHMARKS_NAME}"]

# 3.00  all
rule all:
    message: target_banner("3.00", "all", WF3_TARGETS, project_dir)
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
    message: rule_banner("3.06", "prepare_weathergen_config")
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
    # The wildcard is the DIRECTORY name, which is the identity's first
    # SHORT_DIGEST_CHARS since t2609152107 -- so this compares segment against
    # segment. The full identity is not weakened by that: `_ready_collection`
    # reads the manifest below and `read_collection` recomputes it from content.
    if wildcards is not None and hasattr(wildcards, "collection_id") and wildcards.collection_id != short_digest(plan["collection_id"]):
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
if Path(_scenario_request_path).exists():
    _retained_plan = read_canonical_json(Path(_scenario_request_path))
    if all(Path(entry["path"]).is_file() for entry in _retained_plan["source_inventory"]):
        _live_plan, _, _ = _resolved_collection_plan()
        if _live_plan == _retained_plan:
            _source_reuse_ready = _ready_collection(_retained_plan) is not None

# 3.04  prepare_collection_sources
checkpoint prepare_collection_sources:
    message: rule_banner("3.04", "prepare_collection_sources", summary="fingerprint the generation inputs into a scenario request")
    input:
        lambda wc: [] if _source_reuse_ready else [
            f"{store_dir}/extract_historical.nc", f"{store_dir}/basin_cells.csv",
            *_generation_catalogs, GENERATION["template"],
            lookup_path,
            *([f"{store_dir}/orography.nc"] if clim_source in {"chirps", "chirps_global"} else []),
        ],
    output:
        _scenario_request_path,
    params:
        request=_generation_request,
        live_request_sha256=_live_plan["request_sha256"] if _live_plan is not None else None,
    run:
        from blueearth_cst.experiment.collection_resolution import write_scenario_request
        plan, _, _ = _resolved_collection_plan()
        write_scenario_request(project_dir, plan)


# 3.05  initialize_scenario_collection
rule initialize_scenario_collection:
    message: rule_banner("3.05", "initialize_scenario_collection")
    input:
        plan=lambda wc: checkpoints.prepare_collection_sources.get().output[0],
        lookup=lookup_path,
    output:
        update((Path(_scenario_request_path).parent / "initializations" / f"{INVOCATION_ID}.json").as_posix()),
    run:
        from blueearth_cst.experiment.scenario_provider import initialize_planned_collection
        from blueearth_cst.shared.workflow_config_snapshot import snapshot_bytes
        plan, catalog, ancillary = _resolved_collection_plan()
        if plan != read_canonical_json(Path(input.plan)):
            raise ValueError("GeneratedCollectionStale: inputs changed before initialization")
        # Written inside the seal (rule 3.10 makes the collection immutable), so
        # the snapshot cannot be added to -- or diverge from -- a retained
        # collection later. Unreferenced by `collection_intent.json`, so it
        # leaves `collection_id` where it was.
        initialize_planned_collection(project_dir, plan, INVOCATION_ID,
            lookup_path=input.lookup, catalog_bytes=catalog, ancillary_sources=ancillary,
            config_snapshot=snapshot_bytes(
                "generate_scenarios", config_path,
                WORKFLOW_CONFIG_PATHS.get("generate_scenarios"), config))


def _collection_row_inputs(wc):
    plan = _collection_plan(wc)
    if _ready_collection(plan) is not None:
        return [_scenario_request_path]
    row = _rows_by_id[wc.run_id]
    return [(Path(_scenario_request_path).parent / "initializations" / f"{INVOCATION_ID}.json").as_posix(),
            f"{wg_dir}/output/{legacy_member_name(row, st_width=ST_WIDTH)}.nc"]


# 3.09  retain_scenario_forcing
rule retain_scenario_forcing:
    # Fanned out over RLZ_NUM x ST_NUM, so the context is what separates one
    # member's line from the next 399. `collection_id` is in the banner too --
    # the same run can hold more than one collection over its lifetime.
    # `quiet_start`: this is BOOKKEEPING -- one payload copied into the
    # collection, about a second, interleaved with 3.08 so the console
    # alternated identities and spent two lines per member. On a 10 x 20 grid
    # that is 800 lines to report file copies. The finish line still carries
    # the duration and the counter.
    #
    # The collection id is no longer in the context: it does not change across
    # the fan-out, and rule 3.04 announces it before any member line prints
    # (`Collection <id>: claiming N scenario rows`), with 3.10 naming it again
    # when the collection is sealed. It was 25 constant characters on every
    # member line. If one invocation ever claims two collections whose members
    # interleave, two lines can both read `[run 01]` -- the claim rows still
    # distinguish them, at the cost of reading in order.
    message: rule_banner("3.09", "retain_scenario_forcing", "run {wildcards.run_id}", quiet_start=True)
    input:
        _collection_row_inputs,
    output:
        update((Path(project_dir).resolve() / "scenarios" / "collections" / "{collection_id}" / "forcing" / "run_{run_id}.nc").as_posix()),
    wildcard_constraints:
        collection_id=rf"[a-f0-9]{{{SHORT_DIGEST_CHARS}}}",
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
        return [_scenario_request_path]
    root = Path(plan["manifest_path"]).parent
    return [(root / "forcing" / f"run_{row.run_id}.nc").as_posix() for row in SCENARIO_ROWS]


# 3.10  publish_scenario_collection
checkpoint publish_scenario_collection:
    message: rule_banner("3.10", "publish_scenario_collection", "collection {wildcards.collection_id}", summary="seal the collection and make it immutable")
    input:
        _collection_publication_inputs,
    output:
        update((Path(project_dir).resolve() / "scenarios" / "collections" / "{collection_id}" / "collection.json").as_posix()),
    wildcard_constraints:
        collection_id=rf"[a-f0-9]{{{SHORT_DIGEST_CHARS}}}",
    run:
        from blueearth_cst.experiment.scenario_provider import publish_planned_collection
        plan = _collection_plan(wildcards)
        if _ready_collection(plan) is None:
            publish_planned_collection(project_dir, plan, INVOCATION_ID)
        else:
            # The REUSE row, and the only place it can be said out loud. The
            # decision itself is made at PARSE time (`_source_reuse_ready`
            # above), where no console style is installed yet and a row would
            # print unstyled and out of order. Rules 3.05, 3.09 and 3.10 all
            # take the same branch on a reuse, but 3.09 is one job per member --
            # so the statement is made once, here, rather than 400 times.
            log_row(f"Reusing the retained collection {wildcards.collection_id}; nothing to generate",
                    module="collection")


def _selected_collection(wc):
    plan = _collection_plan()
    return checkpoints.publish_scenario_collection.get(collection_id=short_digest(plan["collection_id"])).output[0]



# 3.07  generate_weather_realizations
rule generate_weather_realizations:
    message: rule_banner("3.07", "generate_weather_realizations", summary="generate stochastic weather with weathergenr")
    input:
        initialization=(Path(_scenario_request_path).parent / "initializations" / f"{INVOCATION_ID}.json").as_posix(),
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
    message: rule_banner("3.11", "gather_logs")
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
    message: rule_banner("3.12", "gather_benchmarks")
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
        initialization=(Path(_scenario_request_path).parent / "initializations" / f"{INVOCATION_ID}.json").as_posix(),
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


# --------------------------------------------------------------------------
# Console: the run's own opening and closing block, and the Snakemake restyle.
#
# Restored 2026-09-16. The R12 split (868c4b7c) carried the rule bodies out of
# `run_stress_test.smk` but not the file scaffolding, so WF3 ran with no
# `_ConsoleHandler` at all: the banners it did keep printed unstyled among
# Snakemake's un-suppressed scheduler chatter, which is what the owner saw.
# --------------------------------------------------------------------------

# Wall clock for the end-of-run summary. Taken at PARSE, not in `onstart`:
# Snakemake exposes no run duration to these handlers, and parse-to-finish is
# the interval a person actually waited. It therefore includes DAG construction
# -- and on WF3 that is not free, since the parse-time collection validation
# above reads the retained plan.
_RUN_STARTED = time.monotonic()


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
                "wf3 generate_scenarios",
                project_dir,
                WORKFLOW_LOG_NAME,
                BENCHMARKS_NAME,
                elapsed_seconds=time.monotonic() - _RUN_STARTED,
                failed=failed,
                log_parts_dir=LOG_PARTS_DIR,
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
    costs a line of console rather than the run.
    """
    try:
        # One write, carrying its own blank line on both sides: the block is the
        # first thing this toolbox puts on the console and it must not open
        # flush against Snakemake's preamble nor close flush against its
        # `Job stats:`. `open_run_header` owns that; the spacing is its business.
        open_run_header("wf3 generate_scenarios", project_dir, config_path)
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
