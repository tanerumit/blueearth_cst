"""Update a wflow model with downscaled climate forcing for one realization."""

import os
from pathlib import Path

import hydromt
from hydromt_wflow import WflowSbmModel

from blueearth_cst.climate_analysis.prepare_climate_data_catalog import (
    prepare_clim_data_catalog,
)
from blueearth_cst.experiment.forcing_descriptor import (
    ClimateArtifact,
    UnitInterpretation,
    describe_forcing,
)
from blueearth_cst.experiment.forcing_window import forcing_window
from blueearth_cst.shared.progress import hydromt_progress
from blueearth_cst.shared.provenance import file_sha256


def forcing_chunksize(size):
    """Pick a time-chunk size for a staticmaps grid of ``size`` cells.

    Bigger grids get shorter time chunks so one chunk stays a workable size in
    memory. Thresholds are the ones this workflow has always used.
    """
    if size > 1e6:
        return 1
    if size > 2.5e5:
        return 30
    if size > 1e5:
        return 100
    return 365


def pet_method_for(precip_source):
    """Return the PET method matching ``precip_source``.

    E-OBS carries no radiation, so it takes Makkink; everything else takes
    De Bruin.
    """
    return "makkink" if precip_source == "eobs" else "debruin"


def _as_list(data_libs):
    """The catalogs as a plain list, whether one path or several came in."""
    if isinstance(data_libs, (str, os.PathLike)):
        return [os.fspath(data_libs)]
    return [os.fspath(item) for item in data_libs]


def resolved_unit_interpretation(data_libs, precip_source):
    """Verify the reviewed daily source arithmetic before interpreting labels.

    This checks the consumed adapter, not merely its catalog name. CHIRPS keeps
    its precipitation/time-shift binding and inherits the six ERA5 auxiliaries
    through the existing extraction path. E-OBS remains unsupported by WF1.
    """
    paths = _as_list(data_libs)
    entries = hydromt.DataCatalog(data_libs=paths).to_dict()
    hybrid = precip_source in {"chirps", "chirps_global"}
    selected = entries["era5" if hybrid else precip_source]
    expected = {
        "unit_add": {"temp": -273.15, "temp_min": -273.15, "temp_max": -273.15},
        "unit_mult": {"kin": 0.000277778, "kout": 0.000277778, "press_msl": 0.01},
        "rename": {
            "msl": "press_msl",
            "ssrd": "kin",
            "t2m": "temp",
            "tisr": "kout",
            "tmax": "temp_max",
            "tmin": "temp_min",
            "tp": "precip",
        },
    }
    adapter = selected.get("data_adapter", {})
    if any(adapter.get(key, {}) != value for key, value in expected.items()):
        raise ValueError(
            f"UnverifiedForcingUnits: {precip_source} catalog arithmetic differs from reviewed daily binding"
        )
    if hybrid:
        adapter = entries[precip_source].get("data_adapter", {})
        if (
            adapter.get("rename") != {"precipitation": "precip"}
            or adapter.get("unit_add") != {"time": 86400}
            or adapter.get("unit_mult", {})
        ):
            raise ValueError(
                f"UnverifiedForcingUnits: {precip_source} precipitation/time adapter differs from reviewed binding"
            )
    return UnitInterpretation(
        revision="daily-catalog-hydromt1.3.1-weathergenr2.0.0/1",
        evidence=(
            "dev/milestones/r12/implementation/evidence/p1-forcing-units.md; "
            f"selected={precip_source}; catalogs={[(path, file_sha256(path)) for path in paths]}; "
            f"extraction_sha256={file_sha256(Path(__file__).parents[1] / 'climate_analysis' / 'extract_historical_climate.py')}"
        ),
        variables=(
            ("precip", "mm/day"),
            ("temp", "degC"),
            ("temp_min", "degC"),
            ("temp_max", "degC"),
            ("press_msl", "hPa"),
            ("kin", "W/m2"),
            ("kout", "W/m2"),
        ),
    )


def downscale_climate_forcing(
    config_out_fn,
    fn_out,
    fn_in,
    data_libs,
    model_root,
    precip_source,
    sim_start,
    sim_end,
    catalog_out,
    oro_path=None,
    *,
    run_id,
    unit_interpretation,
    native_output_path,
    native_log_path,
):
    """Resolve current source-specific context outside the neutral simulator.

    P1 retains the current catalogs and ancillary locations. Their fingerprints
    form a transient context, not the portable package introduced in P2.
    Effective units arrive from an independently reviewed catalog binding.
    """
    from blueearth_cst.experiment.simulator_adapter import (
        ArtifactReference,
        ForcingRequirement,
        ModelReference,
        PreparationContext,
        PreparationSettings,
        RunForcing,
        prepare,
        validate_forcing,
    )

    starttime, endtime = forcing_window(sim_start, sim_end)
    oro_source = f"{precip_source}_orography"
    pet_method = pet_method_for(precip_source)
    data_libs = _as_list(data_libs)
    prepare_clim_data_catalog(
        fns=[fn_in],
        data_libs_like=data_libs,
        source_like=precip_source,
        fn_out=catalog_out,
        oro_path=oro_path,
    )
    data_libs = [os.fspath(catalog_out), *data_libs]
    catalog = hydromt.DataCatalog(data_libs=data_libs)
    elevation_path = Path(catalog.get_source(oro_source).full_uri)
    context = PreparationContext(
        catalogs=tuple(
            ArtifactReference(Path(path), file_sha256(path)) for path in data_libs
        ),
        ancillary=(ArtifactReference(elevation_path, file_sha256(elevation_path)),),
        forcing_entry=Path(fn_in).stem,
        elevation_entry=oro_source,
        pet_method=pet_method,
        press_correction=True,
        temp_correction=True,
        conversions=(
            "cftime_to_datetime64",
            "clip_to_configured_window",
            "refresh_toml_endpoints",
        ),
    )
    descriptor = describe_forcing(
        ClimateArtifact(run_id, Path(fn_in)),
        unit_interpretation,
        time_label="interval_end",
    )
    required_variables = (
        ("precip", "mm/day"),
        ("temp", "degC"),
        ("press_msl", "hPa"),
        ("kin", "W/m2"),
    )
    if pet_method == "debruin":
        required_variables += (("kout", "W/m2"),)
    requirement = ForcingRequirement(
        variables=required_variables,
        crs="EPSG:4326",
        dimensions=("longitude", "latitude", "time"),
        calendars=("noleap", "standard", "proleptic_gregorian"),
        timestep_seconds=86400,
        time_label="interval_end",
        first_time=starttime,
        last_time=endtime,
        allow_missing=False,
    )
    forcing = RunForcing(
        run_id,
        Path(fn_in),
        file_sha256(fn_in),
        descriptor,
        context,
        None,
        None,
    )
    return prepare(
        run_id,
        validate_forcing(forcing, requirement),
        ModelReference(Path(model_root), requirement),
        PreparationSettings(
            Path(config_out_fn),
            Path(fn_out),
            Path(native_output_path),
            Path(native_log_path),
            starttime,
            endtime,
        ),
    )


def prepare_model_forcing(run_forcing, model_reference, settings):
    """Apply the predecessor HydroMT preparation with explicit physical context."""
    context = run_forcing.preparation_context
    fn_out = settings.forcing_path
    starttime, endtime = settings.first_time, settings.last_time
    model_root = model_reference.root
    data_libs = [str(item.path) for item in context.catalogs]
    climate_name = context.forcing_entry
    oro_source = context.elevation_entry
    pet_method = context.pet_method
    config_out_fn = settings.toml_path
    config_out_root = os.path.dirname(config_out_fn)
    config_out_name = os.path.basename(config_out_fn)
    run_name = run_forcing.run_id

    # Read metadata through the same public catalog adapters as preparation;
    # no coordinate/unit repair is introduced by this compatibility check.
    from blueearth_cst.experiment.simulator_adapter import validate_ancillary_grid

    physical_catalog = hydromt.DataCatalog(data_libs=data_libs)
    forcing_grid = physical_catalog.get_rasterdataset(climate_name, variables=["temp"])
    elevation_grid = physical_catalog.get_rasterdataset(
        oro_source, variables=["elevtn"]
    )
    try:
        validate_ancillary_grid(
            run_name, forcing_grid, elevation_grid, context.ancillary[0].path
        )
    finally:
        forcing_grid.close()
        elevation_grid.close()

    # Instantiate model in r+ on the source root, then redirect writes to the
    # per-realization run directory by rebinding root.
    mod = WflowSbmModel(root=model_root, mode="r+", data_libs=data_libs)

    chunksize = forcing_chunksize(mod.staticmaps.data.raster.size)

    mod.setup_config(
        data={
            # The R weathergen writes netcdfs with calendar=noleap. Keeping
            # noleap here would cause hydromt_wflow 1.x's forcing validation
            # to fail comparing cftime.DatetimeNoLeap against datetime.datetime.
            # Convert forcing time axis to standard calendar below and keep
            # the TOML in sync.
            "time.calendar": "standard",
            "time.starttime": starttime,
            "time.endtime": endtime,
            "time.timestepsecs": 86400,
            # Wflow.jl resolves output pointers against dirname(toml) +
            # dir_output; keep dir_output at the toml's own dir and carry the
            # config/ -> output/ hop in the explicit native pointers below.
            "dir_output": ".",
            # Absolute paths into the wf1 model dir (staticmaps + instates).
            # The run dir is experiments/<name>/hydrology/wflow/config/, and it
            # has moved twice -- R07 B5 gave each realization its own rlz_<r>/
            # level, R9 P2 dissolved that level again -- which is exactly why
            # the "../" depth is not a literal anyone should maintain by hand.
            # Pass ABSOLUTE paths: hydromt_wflow's config.write re-relativizes any
            # absolute same-mount value against the new toml's own directory on
            # write, emitting the correct relative pointer (verified against the
            # vendored make_config_paths_relative; design §5/§5a).
            # state.path_input is inert under reinit=true but set for future
            # warm-state safety.
            "state.path_input": str(
                Path(model_root, "instate", "instates.nc").resolve()
            ),
            "input.path_static": str(Path(model_root, "staticmaps.nc").resolve()),
            "input.path_forcing": str(fn_out.resolve()),
            "output.csv.path": os.path.relpath(
                settings.native_output_path, config_out_root
            ).replace("\\", "/"),
            # R9 P2 commit 3 -- ships WITH the rlz_<r>/ flattening, never after.
            # Wflow's `[logging] path_log` defaults to `log.txt` beside the TOML.
            # While each realization owned a run directory that was already one
            # shared log per realization; removing the level puts EVERY member's
            # log at one path, and rule 3.10 batches members concurrently, so it
            # becomes a race rather than an overwrite. Measured on the
            # pre-flattening tree (R9 P1 observed tier): exactly two log.txt for
            # twelve members -- one per realization, six writers each. Keyed per
            # member here through the explicit native log path; the rule owns
            # the layout and the adapter only relativizes its declared pointer.
            "logging.path_log": os.path.relpath(
                settings.native_log_path, config_out_root
            ).replace("\\", "/"),
        }
    )

    # WF3 consumes only the CSV. Remove the inherited output pointer while
    # retaining state.path_input and state.variables for warm initialization.
    mod.config.data.get("state", {}).pop("path_output", None)

    mod.setup_precip_forcing(
        precip_fn=climate_name,
        precip_clim_fn=None,
        chunksize=chunksize,
    )
    mod.setup_temp_pet_forcing(
        temp_pet_fn=climate_name,
        press_correction=context.press_correction,
        temp_correction=context.temp_correction,
        dem_forcing_fn=oro_source,
        pet_method=pet_method,
        chunksize=chunksize,
    )

    # Convert forcing time axis from cftime.DatetimeNoLeap (R weathergen
    # default) to numpy datetime64 so hydromt_wflow 1.x's timespan
    # validation can compare it against datetime.datetime config values.
    # noleap doesn't have Feb 29, so the conversion is lossless.
    forcing = mod.forcing.data
    if hasattr(forcing.indexes["time"], "to_datetimeindex"):
        forcing["time"] = forcing.indexes["time"].to_datetimeindex(time_unit="ns")

    # weathergen has off-by-one timestamps at the year boundaries; clip the forcing
    # in place via the component's data.
    for var in list(forcing.data_vars):
        forcing[var] = forcing[var].sel(time=slice(starttime, endtime))

    # Refresh starttime/endtime from the actual forcing axis (weathergen quirk).
    last_var = next(iter(forcing.data_vars))
    times = forcing[last_var].time.values
    mod.config.set("time.starttime", str(times[0])[:19])
    mod.config.set("time.endtime", str(times[-1])[:19])

    # Write forcing + per-realization toml to absolute paths so the model root
    # (which is the source hydrology_model dir) doesn't have to be moved.
    with hydromt_progress(f"{run_name} forcing"):
        mod.forcing.write(filename=str(fn_out.resolve()))
    mod.config.write(
        filename=config_out_name,
        config_root=Path(config_out_root).resolve(),
    )
    mod.close()  # commit any deferred writes


if __name__ == "__main__":
    if "snakemake" in globals():
        sm = globals()["snakemake"]
        from blueearth_cst.shared.snake_utils import tee_to_log

        with tee_to_log(sm.log[0]):
            downscale_climate_forcing(
                config_out_fn=sm.output.toml,
                fn_out=sm.output.nc,
                fn_in=sm.input.nc,
                data_libs=sm.input.data_sources,
                model_root=sm.params.model_dir,
                precip_source=sm.params.clim_source,
                sim_start=sm.params.sim_window_start,
                sim_end=sm.params.sim_window_end,
                catalog_out=sm.output.catalog,
                oro_path=sm.params.oro_path,
                run_id=sm.params.run_id,
                unit_interpretation=resolved_unit_interpretation(
                    sm.input.data_sources, sm.params.clim_source
                ),
                native_output_path=sm.params.native_output_path,
                native_log_path=sm.params.native_log_path,
            )
    else:
        raise ValueError("This script should be run from a snakemake environment")
