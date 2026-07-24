"""wf1 wrapper for the raw-climate extraction rule (P3-2a).

Dedicated ``script:`` target for rule 1.10 ``extract_climate_grid_wf1``
(design ext1-4): derives the extraction bbox from the built model's
``staticmaps.nc`` — the declared rule-1.03 producer edge (design arch-1) —
and calls the shared, model-independent ``prep_historical_climate`` with
``bbox=``. The shared module's own wf3 snakemake block stays verbatim and is
exercised only by wf3 rule 3.02. On chirps/chirps_global the shared function's
``{clim_source}_orography.nc`` sidecar is relocated to the rule's declared,
source-independent ``oro_nc`` output (design ext2-1).
"""

import os
import shutil

import hydromt  # noqa: F401 -- registers the xarray .raster accessor
import xarray as xr

from blueearth_cst.climate_analysis.extract_historical_climate import (
    prep_historical_climate,
)

#: Sources supported by the wf1 raw-climate path (design ext2-3). eobs is
#: rejected at DAG-parse time in Snakefile_model_creation; the assert below is
#: the belt-and-braces guard behind that parse-time error.
SUPPORTED_CLIM_SOURCES = ("era5", "chirps", "chirps_global")


def staticmaps_bbox(basin_nc):
    """Return the model-grid bounds (xmin, ymin, xmax, ymax) of ``staticmaps.nc``.

    The same tuple form ``region.geometry.total_bounds`` yields on the wf3
    path; each edge can sit up to ~one model cell outside the region's tight
    bounds (outward snapping to model_resolution — design ext1-5).
    """
    with xr.open_dataset(basin_nc) as ds_sm:
        return tuple(ds_sm.raster.bounds)


if __name__ == "__main__":
    if "snakemake" in globals():
        sm = globals()["snakemake"]
        from blueearth_cst.shared.snake_utils import tee_to_log

        with tee_to_log(sm.log[0]):
            clim_source = sm.params.clim_source
            assert clim_source in SUPPORTED_CLIM_SOURCES, (
                f"clim_historical: {clim_source} is not supported by the "
                "P3-2a wf1 raw-climate path; supported sources: era5, chirps, "
                "chirps_global"
            )
            prep_historical_climate(
                region_fn=None,
                fn_out=sm.output.climate_nc,
                data_libs=sm.params.data_sources,
                clim_source=clim_source,
                starttime=sm.params.starttime,
                endtime=sm.params.endtime,
                bbox=staticmaps_bbox(sm.input.basin_nc),
            )
            if clim_source in ("chirps", "chirps_global"):
                # Relocate the extraction's orography sidecar to the declared
                # rule output so the DAG edge — not a filename convention —
                # carries the DEM/climate co-provenance contract (ext2-1).
                fn_sidecar = os.path.join(
                    os.path.dirname(sm.output.climate_nc),
                    f"{clim_source}_orography.nc",
                )
                shutil.move(fn_sidecar, sm.output.oro_nc)
