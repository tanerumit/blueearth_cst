"""Shared generation request and source-time seed resolution for WF3 and WF4."""

from copy import deepcopy
from pathlib import Path

from blueearth_cst.experiment.content_identity import (
    content_sha256,
    identity_segment,
    repository_code_inventory,
    stage_environment,
)
from blueearth_cst.experiment.prepare_weathergen_config import build_weathergen_config
from blueearth_cst.shared.provenance import file_sha256
from blueearth_cst.shared.snake_utils import (
    DEFAULT_BASIN_INDEX,
    DEFAULT_HYDROGRAPHY,
    climate_store_rule,
    region_rule,
    resolve_seed,
    resolve_water_year_start,
    stress_test_grid,
    validate_spell_factor,
    window_year_pair,
)

# Closed classification: every new workflow field needs a seed-dependency ruling.
SEED_FIELDS = {
    "n_realizations": "include: selects stochastic draws",
    "simulation_window": "include: selects generated temporal extent",
    "climate_perturbations": "include: selects perturbations",
    "weathergen_config": "include: classified effective generator settings",
    "seed": "exclude: resolved after this projection",
    "unit_id_capacity": "exclude: identifier spelling only",
    "enabled": "exclude: orchestration only",
}

# Closed nested classification: new upstream arguments require an explicit ruling.
GENERATOR_SEED_FIELDS = {
    "run_weather_generator": (set(), {"eval_max_grids", "log_messages"}),
    "generate_weather": (
        set(
            "vars warm_var warm_signif warm_pool_size warm_filter_bounds relax_order "
            "annual_knn_n wet_q extreme_q start_year n_years n_realizations "
            "year_start_month dry_spell_factor wet_spell_factor".split()
        ),
        set(
            "parallel n_cores verbose save_plots plot_dpi plot_device seed out_dir".split()
        ),
    ),
    "apply_climate_perturbations": (
        set(
            "compute_pet pet_method qm_fit_method scale_var_with_mean enforce_target_mean "
            "precip_intensity_threshold precip_occurrence_transient exaggerate_extremes "
            "extreme_prob_threshold extreme_k precip_cap_mm_day precip_floor_mm_day "
            "precip_cap_quantile diagnostic".split()
        ),
        {"verbose"},
    ),
    "write_netcdf": (
        {"calendar", "spatial_ref", "signif_digits"},
        {"compression", "verbose", "file_prefix", "file_suffix", "out_dir"},
    ),
    "temp": ({"transient_change"}, set()),
    "precip": ({"transient_change"}, set()),
}


def generator_seed_projection(generator):
    """Select effective value dependencies, refusing unclassified arguments."""
    unknown = set(generator) - set(GENERATOR_SEED_FIELDS)
    if unknown:
        raise ValueError(
            f"generator sections lack a seed-dependency declaration: {sorted(unknown)}"
        )
    projection = {}
    for section, values in generator.items():
        included, excluded = GENERATOR_SEED_FIELDS[section]
        unknown = set(values) - included - excluded
        if unknown:
            raise ValueError(
                f"{section} fields lack a seed-dependency declaration: {sorted(unknown)}"
            )
        projection[section] = {
            key: deepcopy(value) for key, value in values.items() if key in included
        }
    if generator.get("apply_climate_perturbations", {}).get("diagnostic") is not False:
        raise ValueError(
            "apply_climate_perturbations.diagnostic must be false for the forcing return-shape contract"
        )
    return projection


def generation_configuration(config, repository):
    """Resolve scheduling settings without reading generation source contents."""
    cfg = config["workflows"]["generate_scenarios"]
    unknown = set(cfg) - set(SEED_FIELDS)
    if unknown:
        raise ValueError(
            f"generation fields lack a seed-dependency declaration: {sorted(unknown)}"
        )
    project = config["project"]
    climate = config["climate"]
    basin = config["basin"]
    sources = basin.get("sources") or {}
    shared = dict(
        project_dir=project["project_dir"],
        model_region=basin["region"],
        data_sources=project["catalog"],
        hydrography=sources.get("hydrography", DEFAULT_HYDROGRAPHY),
        basin_index=sources.get("basin_index", DEFAULT_BASIN_INDEX),
    )
    store = climate_store_rule(
        **shared, clim_source=climate["selected"], historical_window=climate["window"]
    )
    region = region_rule(**shared)
    start, end = window_year_pair(
        cfg["simulation_window"], "generate_scenarios.simulation_window"
    )
    _, _, count = stress_test_grid(cfg["climate_perturbations"])
    realizations = cfg.get("n_realizations", 1)
    template = cfg.get("weathergen_config", "config/defaults/weathergen_config.yml")
    code = repository_code_inventory(
        Path(repository),
        [
            "blueearth_cst/experiment/scenario_provider.py",
            "blueearth_cst/experiment/generation_plan.py",
            "blueearth_cst/experiment/prepare_weathergen_config.py",
            "blueearth_cst/experiment/prepare_cst_parameters.py",
            "blueearth_cst/climate_analysis/prepare_climate_data_catalog.py",
            *[
                f"blueearth_cst/weathergen/{name}"
                for name in (
                    "generate_weather.R",
                    "impose_climate_change.R",
                    "global.R",
                    "read_member_grid.R",
                )
            ],
        ],
    )
    catalogs = project["catalog"]
    catalogs = [catalogs] if isinstance(catalogs, str) else list(catalogs)
    request = {
        "schema_version": "generation-request/1",
        "settings": {key: value for key, value in cfg.items() if key != "enabled"},
        "provider_code": code,
        "source": {
            "catalogs": [Path(p).resolve().as_posix() for p in catalogs],
            "climate": climate["selected"],
            "store": Path(store.store_dir).resolve().as_posix(),
        },
        "water_year_start": resolve_water_year_start(climate.get("water_year_start")),
        "template": Path(template).resolve().as_posix(),
    }
    request_path = (
        Path(project["project_dir"]).resolve()
        / "scenarios"
        / "requests"
        / identity_segment(content_sha256(request), "generation_request_id")
        / "request.json"
    )
    return dict(
        config=cfg,
        project_dir=project["project_dir"],
        store=store,
        region=region,
        start=start,
        end=end,
        n_realizations=realizations,
        n_design_points=count,
        capacity=cfg.get("unit_id_capacity", (realizations + 1) * (count + 1)),
        template=template,
        catalogs=catalogs,
        code=code,
        request=request,
        request_path=request_path.as_posix(),
        source=climate["selected"],
    )


def resolve_generation_plan(settings):
    """Hash actual sources, resolve the seed, then construct immutable intent."""
    from blueearth_cst.climate_analysis.prepare_climate_data_catalog import (
        resolve_preparation_payloads,
        resolved_unit_interpretation,
    )
    from blueearth_cst.experiment.legacy_scenario_provider import plan_collection
    from blueearth_cst.shared.climate_window import require_min_years, store_time_bounds

    cfg = settings["config"]
    store = settings["store"].store_dir
    historical = f"{store}/extract_historical.nc"
    require_min_years(
        store_time_bounds(historical),
        settings["source"],
        historical,
        where="This is the historical store the scenario generator resamples",
    )
    units = resolved_unit_interpretation(settings["catalogs"], settings["source"])
    context, catalog, ancillary = resolve_preparation_payloads(
        settings["catalogs"],
        settings["source"],
        units,
        oro_path=f"{store}/orography.nc",
    )
    sources = {
        "historical_climate": f"{store}/extract_historical.nc",
        "basin_cells": f"{store}/basin_cells.csv",
        "generator_template": settings["template"],
        **{f"catalog_{i}": p for i, p in enumerate(settings["catalogs"])},
        **{f"ancillary_{name}": p for name, p in ancillary.items()},
    }
    # R consumes the extracted values. Raw catalog/template text remains in the
    # collection identity, but locators, comments and console options select no draw.
    source_projection = [
        {
            "role": "forcing_elevation" if role.startswith("ancillary_") else role,
            "sha256": file_sha256(Path(p)),
            "size_bytes": Path(p).stat().st_size,
        }
        for role, p in sorted(sources.items())
        if role != "generator_template" and not role.startswith("catalog_")
    ]
    perturbations = cfg["climate_perturbations"]
    spells = perturbations.get("spell_factors") or {}
    generator = build_weathergen_config(
        settings["n_realizations"],
        perturbations,
        "",
        "rlz",
        settings["template"],
        settings["end"],
        0,
        settings["request"]["water_year_start"],
        validate_spell_factor(spells.get("dry"), "spell_factors.dry"),
        validate_spell_factor(spells.get("wet"), "spell_factors.wet"),
        # Legacy collections were generated from a fixed 2010 anchor; keep it so
        # their recorded generator config still reproduces.
        2010,
    )
    material = {
        "schema_version": "generation-seed-material/1",
        "scenario_type": "stochastic",
        "n_realizations": settings["n_realizations"],
        "simulation_window": {"start": settings["start"], "end": settings["end"]},
        "climate_perturbations": cfg["climate_perturbations"],
        "water_year_start": settings["request"]["water_year_start"],
        "provider_revision": content_sha256(settings["code"]),
        "source_inventory_sha256": content_sha256(source_projection),
        "generator_settings": generator_seed_projection(generator),
    }
    digest = content_sha256(material)
    requested = cfg.get("seed")
    resolved = (
        (int(digest, 16) % (2**31 - 1))
        if requested == "auto"
        else resolve_seed(requested, "")
    )
    resolution = {
        "seed_request": requested,
        "resolved_seed": resolved,
        "projection": material,
        "projection_sha256": digest,
    }
    resolution["seed_resolution_id"] = content_sha256(resolution)
    generator["generate_weather"]["seed"] = resolved
    generator["generate_weather"].pop("out_dir")
    generation = {
        "seed": {"requested": requested, "resolved": resolved},
        "seed_resolution": resolution,
        "unit_id_capacity": settings["capacity"],
        "weathergen": generator,
        "climate_perturbations": perturbations,
    }
    spec = {
        "scenario_type": "stochastic",
        "n_realizations": settings["n_realizations"],
        "n_design_points": settings["n_design_points"],
        "unperturbed_per_realization": 1,
        "expected_run_count": settings["n_realizations"]
        * (settings["n_design_points"] + 1),
        "simulation_window": material["simulation_window"],
        "pairing": "paired_across_design_points",
        "row_order": "rlz-major/unperturbed-first/st-id-ascending",
    }
    plan = plan_collection(
        settings["project_dir"],
        settings["request"],
        generation_config=generation,
        scenario_spec=spec,
        source_inputs=sources,
        provider_code=settings["code"],
        environment=stage_environment(
            ["hydromt", "xarray", "netCDF4", "PyYAML"], include_weathergen=True
        ),
        preparation_context=context,
    )
    return plan, catalog, ancillary
