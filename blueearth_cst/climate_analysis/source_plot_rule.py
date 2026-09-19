"""One canonical source-plot producer, shared by WF0 and WF1.

Workflow labels, logs and benchmarks belong to the caller. Everything that
determines the figures belongs here; cross-source comparison has separate outputs.
"""

from dataclasses import dataclass

from blueearth_cst.climate_analysis.climate_figures import (
    source_climate_vars,
    source_figure_names,
)
from blueearth_cst.shared.snake_utils import ClimateStoreRule, SpatialUnitsRule


@dataclass(frozen=True)
class SourcePlotRule:
    """Plot paths and the content-determining fields of a Snakemake rule."""

    inputs: dict[str, str]
    figures: tuple[str, ...]
    subbasin_dir: str
    params: dict[str, object]
    script: str = "blueearth_cst/climate_analysis/plot_climate_source.py"


def source_plot_rule(
    store: ClimateStoreRule,
    spatial: SpatialUnitsRule,
    source: str,
    data_sources: str | list[str],
    water_year_start: str,
) -> SourcePlotRule:
    """Build the source-local figure contract independently of its workflow.

    Keep input order stable as well as names. The subbasin directory is wrapped
    in Snakemake's ``directory()`` by each caller because its members are only
    known after delineation. Catalog freshness is owned by the climate store.
    """
    variables = source_climate_vars(source)
    inputs = {"climate_nc": store.outputs["climate_nc"]}
    if "oro_nc" in store.outputs and variables != ("precip",):
        inputs["oro_nc"] = store.outputs["oro_nc"]
    inputs.update(
        {
            name: spatial.outputs[name]
            for name in ("basins", "subbasins", "rivers", "locations")
        }
    )
    inputs["basin_cells"] = store.outputs["basin_cells"]
    plot_dir = f"{store.store_dir}/plots"
    subbasin_dir = f"{plot_dir}/subbasins"
    return SourcePlotRule(
        inputs=inputs,
        figures=tuple(
            f"{plot_dir}/{name}"
            for name in source_figure_names(
                source, variables=variables, spatial_scopes=("basin_avg",)
            )
        ),
        subbasin_dir=subbasin_dir,
        params={
            "plot_dir": plot_dir,
            "subbasin_plot_dir": subbasin_dir,
            "data_sources": data_sources,
            "clim_source": source,
            "geoms_dir": f"{spatial.spatial_dir}/geoms",
            "water_year_start": water_year_start,
        },
    )
