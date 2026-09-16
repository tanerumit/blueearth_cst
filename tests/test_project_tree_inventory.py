"""The POST-MIGRATION project-tree inventory (`build_project_tree_rules`).

`[R10-11]`: the R9 path map runs one way — pre-R9 paths to post-R9 ones — so a
tree in the layout R9 delivered matches none of its old-side patterns and
`tree-check` returned exit 1 on every CORRECT tree. The map was never wrong; it
was being asked about an era that has passed.

The inventory answers the question that outlives the migration: **does this tree
hold anything nobody declared?** That is the property that caught
`region.geojson` (R9 phase-1 F1a) and that ADR 0003 §8a's seam intermediate
needed a row for.

Two instruments here, and the second matters more than the first:

1. row-driven coverage — every shape a clean three-workflow run produces
   resolves as IDENTITY;
2. the NON-CATCH-ALL guard — an artifact nobody declared still resolves to
   UNMAPPED. Without it the report is empty by construction and the gate passes
   unconditionally, which is the hazard
   `test_a_catch_all_config_prefix_would_empty_the_report` demonstrates on the
   R9 map.
"""

import os
import re
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dev", "scripts"))
import semantic_tree_diff as std  # noqa: E402

E = "experiment"
KEY = "era5_20000101_20201231"
CP = "cmip6"
#: A WF3 scenario-request key as it appears in a run-record FILENAME: the first
#: 12 characters of the request fingerprint (t2609151643). The
#: `scenarios/requests/` rows below still use the full 64, because the
#: DIRECTORY keeps its full name -- the two lengths in this file are the
#: contract.
PK = "c78c42d77345"
INVENTORY = std.build_project_tree_rules(E, KEY, CP)


def _kind(rel: str) -> str:
    return std.classify_path_map([rel], INVENTORY)[0][2]


# ---------------------------------------------------------------------------
# 1. Coverage — the shapes a clean run produces
# ---------------------------------------------------------------------------

#: Taken from a clean three-workflow run on the seed config (2026-08-06, 186
#: paths), collapsed to distinct shapes. Grouped by destination root.
COVERED: dict[str, list[str]] = {
    "root": [
        "logs/wf1_build_model.log",
        "logs/wf2_analyze_projections.log",
        # WF3's and WF4's run records joined the project's own logs/ +
        # benchmarks/ on 2026-08-11, KEYED IN THE FILENAME; their scratch parts
        # stay scoped by the same key one level down, so two runs cannot merge
        # each other's. WF4 keys on its experiment name. WF3 has none, so since
        # R12 it keys on its scenario-plan fingerprint -- shortened to the
        # repo's 12-character digest handle (t2609151643), which is why `PK`
        # below is 12 hex and not 64.
        f"logs/wf4_simulate_system_{E}.log",
        f"logs/wf3_generate_scenarios_{PK}.log",
        "logs/_parts/1.01b_delineate_region.log",
        f"logs/_parts/{E}/3.11_generate_weather_realizations.log",
        "logs/dag/test_wf1_dag.png",
        f"logs/dag/test_wf3_{E}_dag.png",
        "benchmarks/wf1_benchmarks.md",
        "benchmarks/wf2_benchmarks.md",
        f"benchmarks/wf4_benchmarks_{E}.md",
        f"benchmarks/wf3_benchmarks_{PK}.md",
        "benchmarks/_parts/1.02_prepare_spatial_maps.tsv",
        f"benchmarks/_parts/{E}/3.16_derive_wflow_indicators.tsv",
        f"logs/_parts/generate_scenarios/{PK}/3.07_generate_weather_realizations.log",
        f"benchmarks/_parts/generate_scenarios/{PK}/3.08_perturb_climate_realization.tsv",
    ],
    "config": [
        "config/runs/project_config_build_model.yml",
        "config/runs/project_config_analyze_projections.yml",
        # The wrapper's per-invocation manifest. Not reachable through the
        # `config/runs/<workflow>/<digest>/` regex below -- it sits DIRECTLY
        # under `invocations/`, with no digest level -- so it carries its own
        # row (2026-08-11).
        "config/runs/invocations/20260811T142556.501Z-83c05db9c855.json",
        # The content-addressed bundles these replaced are GONE (2026-08-13):
        # one record per workflow at an enumerated path, so there is no digest
        # level left for a regex to match. A surviving bundle in an existing
        # project now reports as undeclared -- which is the migration's signal,
        # and dev/scripts/prune_config_snapshots.py is what clears it.
        "config/runs/build_model/run_record.yml",
        "config/runs/analyze_projections/run_record.yml",
        # Written by the workflow's lifecycle handlers rather than by a rule,
        # so the declared tier structurally cannot see it and the inventory
        # whitelists it by hand.
        "config/runs/journal.jsonl",
        "config/runs/README.md",
        "config/catalogs/deltares_data.yml",
        "config/templates/wflow_build_model.yml",
        "config/basin_data/output_locations.csv",
    ],
    "data": [
        "data/spatial/spatial_maps.nc",
        "data/spatial/spatial_catalog.yml",
        "data/spatial/spatial_report.yml",
        "data/spatial/location_registry.csv",
        # ADR 0003 §8a — the seam intermediate this inventory has to cover.
        "data/spatial/hydrography.nc",
        "data/spatial/geoms/region.geojson",
        "data/spatial/geoms/basins.geojson",
        "data/spatial/geoms/subbasins.geojson",
        # ADR 0007: basin_area depicts elevation, so it sits with the data.
        "data/spatial/plots/basin_area.png",
        f"data/climate/historical/{KEY}/extract_historical.nc",
        # The basin-cell mask that ships with every extraction (2026-08-10).
        f"data/climate/historical/{KEY}/basin_cells.csv",
        f"data/climate/historical/{KEY}/.guard_ok",
        # WF0 filename grammar: <dataset>_<var>_<context>_<scope>.png
        f"data/climate/historical/{KEY}/plots/era5_precip_annual_clim_map_basin_ext.png",
        # A SECOND store key is legitimate: the key is a cache key, so a project
        # with an era5 and a chirps store holds both.
        "data/climate/historical/chirps_19900101_20101231/extract_historical.nc",
        f"data/climate/projections/{CP}/raw/cmip6_INM_INM-CM4-8_ssp245_r1i1p1f1.nc",
        f"data/climate/projections/{CP}/scalar/cmip6_INM_INM-CM4-8_ssp245_r1i1p1f1.nc",
        f"data/climate/projections/{CP}/summary/cmip6_change_factors_annual.csv",
        f"data/climate/projections/{CP}/summary/provenance.json",
        f"data/climate/projections/{CP}/plots/overview/change-factor-cloud.png",
        f"data/climate/projections/{CP}/plots/overview/annual-precipitation.png",
        f"data/climate/projections/{CP}/plots/overview/annual-temperature.png",
        f"data/climate/projections/{CP}/plots/windows/far-2070-2090/monthly-change-factors.png",
        f"data/climate/projections/{CP}/report.md",
    ],
    "models": [
        "models/hydrology/wflow/staticmaps.nc",
        "models/hydrology/wflow/wflow_sbm.toml",
        "models/hydrology/wflow/hydromt.log",
        "models/hydrology/wflow/hydromt_data.yml",
        "models/hydrology/wflow/.model_built",
        "models/hydrology/wflow/.outputs_configured",
        # ADR 0004's terminal build sentinel.
        "models/hydrology/wflow/.model_final",
        "models/hydrology/wflow/config/build_historical_forcing.yml",
        # Rule 1.10's second declared config output, beside the build YAML
        # (2026-08-11).
        "models/hydrology/wflow/config/climate_store_catalog.yml",
        "models/hydrology/wflow/forcing/inmaps_historical.nc",
        "models/hydrology/wflow/forcing/plots/forcing_precip_map.png",
        "models/hydrology/wflow/staticgeoms/outlet_index.csv",
        "models/hydrology/wflow/staticgeoms/gauges_locations.geojson",
        # The derived Excel-ready table (rule 1.14b). Since 2026-08-10 it is
        # what `run_default/` holds INSTEAD of the raw csv, not beside it:
        # rule 1.14 declares `output.csv` as temp(), so a successful run leaves
        # none once 1.14b and 1.15 have consumed it. Same reasoning as
        # `log.txt` below -- and the same caveat, that a FAILED run leaves it,
        # so this inventory cannot simply assert its absence either. A run made
        # with `--notemp` (the baseline procedure) keeps it too.
        "models/hydrology/wflow/run_default/output_q.csv",
        # run_default/log.txt is gone: rule 1.14 declares Wflow's own log as a
        # temp() output, so a successful run leaves none. It survives a FAILED
        # run, which is why this inventory cannot simply assert its absence.
        "models/hydrology/wflow/run_default/outstate/outstates.nc",
        "models/hydrology/wflow/evaluation/performance_metrics.csv",
        # Keyed by wflow_id since 2026-08-10; four sheets per station. They sit
        # in a `stations/` bin since 2026-08-18 (t2608071206) because rule 1.15
        # declares that bin as a directory() -- their count is a product of the
        # model build, so the files themselves cannot be declared.
        "models/hydrology/wflow/evaluation/plots/stations/hydrograph_1010.png",
        "models/hydrology/wflow/evaluation/plots/stations/signatures_peaks_1010.png",
        "models/hydrology/wflow/evaluation/plots/stations/signatures_lows_1010.png",
        "models/hydrology/wflow/evaluation/plots/stations/performance_1010.png",
        # The staleness sidecar (rule 1.15b) and the two values-used records
        # (rules 1.07 and 1.08) -- see design §5.6 and §5.8.
        "models/hydrology/wflow/evaluation/run_metadata.json",
        "models/hydrology/wflow/hydromt_build_config.yml",
        "models/hydrology/wflow/hydromt_update_waterbodies.yml",
    ],
    "experiments": [
        f"experiments/{E}/.model_reference_ok",
        f"experiments/{E}/config/simulation.json",
        f"experiments/{E}/config/model_reference.yml",
        f"experiments/{E}/config/response_request.json",
        f"experiments/{E}/config/simulator_settings.json",
        f"experiments/{E}/_engine/response_inventory.json",
        f"experiments/{E}/_engine/metric_requests/{'a' * 12}.json",
        f"experiments/{E}/results/metric_sets/{'b' * 12}/metrics.json",
        f"experiments/{E}/results/metric_sets/{'b' * 12}/unit_index.csv",
        f"experiments/{E}/results/metric_sets/{'b' * 12}/q_indicators.csv",
        f"experiments/{E}/hydrology/wflow/config/run_001.toml",
        f"experiments/{E}/hydrology/wflow/config/run_001.temporal.json",
        f"experiments/{E}/hydrology/wflow/config/run_001.yml",
        f"experiments/{E}/hydrology/wflow/forcing/inmaps_run_001.nc",
        f"experiments/{E}/hydrology/wflow/output/run_001.csv",
        f"experiments/{E}/hydrology/wflow/output/run_001.log",
        # outstates_run_<id>.nc is gone from this list (2026-09-15): the
        # experiment runs no longer emit a warm state at all, so it is not a
        # shape a clean run produces. `downscale_climate_forcing.py` pops
        # `state.path_output` out of every per-run TOML, and the only
        # `measure_member_footprint` call site passes `write_states=False`.
        # Contract HM-6b already says as much -- "an unconsumed named sink;
        # nothing in-repo reads it", "absent on the completed fixture". The row
        # dated from the 2026-08-06 capture, before the suppression.
        #
        # `semantic_tree_diff`'s rule for it deliberately STAYS: if a future
        # config re-enables state output the file maps as declared instead of
        # reporting UNMAPPED. Same reasoning as run_default/log.txt above --
        # coverage rows describe what a run produces, not what is forbidden.
    ],
    "collections": [
        f"scenarios/collections/{'c' * 12}/collection.json",
        f"scenarios/collections/{'c' * 12}/scenario_table.csv",
        f"scenarios/collections/{'c' * 12}/forcing/run_001.nc",
        f"scenarios/collections/{'c' * 12}/stress_test_lookup.csv",
        f"scenarios/collections/{'c' * 12}/preparation_catalog.yml",
        f"scenarios/collections/{'c' * 12}/ancillary/dem/static.nc",
        f"scenarios/requests/{'a' * 12}/request.json",
        f"scenarios/requests/{'a' * 12}/initializations/invocation.json",
        f"scenarios/requests/{'a' * 12}/generation/config/weathergen_config.yml",
        f"scenarios/requests/{'a' * 12}/generation/output/resampled_dates.csv",
    ],
}

ALL_COVERED = [(section, rel) for section, rows in COVERED.items() for rel in rows]


@pytest.mark.parametrize(
    "section,rel", ALL_COVERED, ids=[f"{s}:{r}" for s, r in ALL_COVERED]
)
def test_every_produced_shape_is_covered(section, rel):
    """A clean run must classify entirely as IDENTITY — zero unmapped."""
    new, matched = std.apply_path_map_matched(rel, INVENTORY)
    assert matched, f"{rel} is UNMAPPED — the inventory does not cover it"
    assert new == rel, f"the inventory must be identity, got {new}"


def test_coverage_is_not_trivially_satisfied():
    """Guard on the guard: every destination root is exercised."""
    assert set(COVERED) == {
        "root",
        "config",
        "data",
        "models",
        "experiments",
        "collections",
    }
    assert len(ALL_COVERED) >= 60


# ---------------------------------------------------------------------------
# 2. The non-catch-all guard — the property the inventory exists for
# ---------------------------------------------------------------------------

#: Artifacts no rule declares. Each must report UNMAPPED: this is the whole
#: point, and each one sits under a root the inventory DOES cover, so a prefix
#: written one level too broad would swallow it silently.
UNDECLARED = [
    "data/spatial/leftover_intermediate.nc",  # a settled dir: enumerated
    "data/spatial/spatial_maps.tmp.nc",  # a crashed write
    "models/hydrology/wflow/stray_output.nc",
    "models/hydrology/wflow/forcing/inmaps_2050.nc",
    "config/runs/something_new.yml",  # not the two contract paths
    "config/whatever_new_thing.yml",
    # Guards on the two rows added 2026-08-11. `invocations/` is a PREFIX
    # because its filenames are open, so this proves it did not widen into a
    # `config/runs/` catch-all that would swallow the contract paths and the
    # stray above. `climate_store_catalog.yml` is an ENUMERATED leaf, so the
    # model's config/ must still report a genuinely new file -- if this row
    # ever starts mapping, someone replaced the leaf list with a prefix.
    "config/runs/invocations.json",  # a FILE named invocations, not the dir
    "models/hydrology/wflow/config/some_new_generated.yml",
    f"experiments/{E}/orphan_table.csv",
    # The retired stress-test parameter artifacts. This pair is the guard on
    # the `climate/weathergenr/` NARROWING: that prefix used to be declared
    # whole, which would have accepted a leftover `_work/` silently -- the
    # migration's own orphan riding the very rule meant to report it.
    f"experiments/{E}/climate/weathergenr/_work/st_4.csv",
    f"experiments/{E}/config/stress_test_design.csv",
    f"experiments/{E}/indicators/Qstats.csv",  # the pre-R9 name, now retired
    # The pre-2026-08-11 WF3 run records. Stale output from an earlier run, and
    # the guard on the new "root" rows: an inventory that kept the old
    # experiment-scoped prefixes "to be safe" would report a clean tree while
    # every WF3 run left a second copy behind.
    f"experiments/{E}/logs/wf3_run_stress_test.log",
    f"experiments/{E}/benchmarks/wf3_benchmarks.md",
    # ...and the new root rows must not be so wide they swallow a stray file.
    "logs/wf3_anything.log",
    "benchmarks/wf3_benchmarks.md",  # unkeyed: no experiment can produce it
    # WF3's rows are HEX-keyed and WF4's are NAME-keyed, and each must refuse
    # the other's shape. A single `wf[34]_..._[a-z0-9_]+` row covered both, and
    # since short hex is a subset of the experiment grammar it silently accepted
    # every pre-R12 experiment-keyed WF3 record -- two stale benchmark tables
    # sat in the rapid tree while it reported clean (t2609151800). These four
    # are the guard on the split.
    f"logs/wf3_generate_scenarios_{E}.log",
    f"benchmarks/wf3_benchmarks_{E}.md",
    "benchmarks/wf3_benchmarks_DEADBEEF1234.md",  # hex, but not lower-case
    f"benchmarks/wf3_benchmarks_{PK[:8]}.md",  # hex, but not the key LENGTH
    f"logs/wf3_generate_scenarios_{PK}extra.log",  # 12 hex then trailing text
    # NOT listed as undeclared, deliberately: a WF4 record whose experiment name
    # happens to be 12 hex characters. That is a legal experiment name, so WF4's
    # row must keep accepting it -- the residual ambiguity the split leaves open
    # and cannot close by grammar.
    "climate_historical/era5_20000101_20201231/extract_historical.nc",  # pre-R9
    "hydrology_model/staticmaps.nc",  # pre-R9
    "spatial/geoms/basins.geojson",  # pre-R9
    "unknown_root/anything.txt",
    f"experiments/{E}/.model_reference_unknown",
    f"scenarios/requests/{'a' * 12}/generation/output/unknown_dates.csv",
]


@pytest.mark.parametrize("rel", UNDECLARED)
def test_undeclared_artifacts_are_reported(rel):
    """An artifact nobody declared must not be absorbed by a broad prefix.

    Includes PRE-R9 paths deliberately: on a migrated tree those are leftovers
    from before the move, and reporting them is how a stale copy gets noticed.
    """
    assert _kind(rel) == "UNMAPPED", f"{rel} was silently absorbed"


def test_a_broad_data_prefix_would_empty_the_report():
    """Demonstrates the hazard rather than asserting its absence.

    Same argument as `test_a_catch_all_config_prefix_would_empty_the_report` on
    the R9 map: with `data/` -> `data/` an unknown artifact reads as a
    deliberate identity, so the unmapped report goes empty by construction.
    """
    unknown = "data/spatial/leftover_intermediate.nc"
    assert _kind(unknown) == "UNMAPPED"
    catch_all = [("data/", "data/")] + INVENTORY
    assert std.classify_path_map([unknown], catch_all)[0][2] == "IDENTITY"


# ---------------------------------------------------------------------------
# 3. The inventory describes ONE era — today's
# ---------------------------------------------------------------------------


def test_a_pre_migration_path_is_unmapped_rather_than_quietly_accepted():
    """`[R10-11]`'s finding, from the surviving side.

    This used to be a two-map test: a post-R9 path was covered here and
    UNMAPPED under `build_r09_path_map`, a pre-R9 path the exact inverse.
    Neither map was wrong — they answered about different eras, and
    `tree-check` was asking the wrong one. The migration map was retired
    2026-08-11 (`dev/reviews/2026-08-11_test-suite-bloat-assessment.md` §6a),
    so what remains testable is the half that can still regress: the inventory
    must NOT silently absorb an old-layout path. A tree still holding one has
    not been migrated, and saying so is the report's job.
    """
    assert std.apply_path_map_matched("data/spatial/spatial_maps.nc", INVENTORY)[1]
    assert not std.apply_path_map_matched("spatial/spatial_maps.nc", INVENTORY)[1]
    assert _kind("spatial/spatial_maps.nc") == "UNMAPPED"


def test_other_experiments_are_covered_but_not_the_project_root():
    """A tree may hold several experiments; all are legitimate.

    The catch-all is scoped INSIDE `experiments/`, so it cannot reach anything
    else — checked by the undeclared cases above, which include a project-root
    stray.
    """
    assert _kind("experiments/another_run/results/q_indicators.csv") == "IDENTITY"
    assert _kind(f"experiments/{E}/results/q_indicators.csv") == "UNMAPPED"


def test_the_inventory_is_identity_everywhere():
    """No rule may MOVE a path — this map describes, it does not migrate."""
    moved = [
        (rel, std.apply_path_map(rel, INVENTORY))
        for _, rel in ALL_COVERED
        if std.apply_path_map(rel, INVENTORY) != rel
    ]
    assert not moved, moved


def test_rules_are_well_formed():
    """Every rule is a (pattern, template) pair the applier can use."""
    for old, new in INVENTORY:
        assert isinstance(old, (str, re.Pattern))
        assert isinstance(new, str) and new
