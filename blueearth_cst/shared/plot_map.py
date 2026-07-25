# -*- coding: utf-8 -*-
"""Plot the wflow basin, rivers, gauges/outlets and DEM on a map.

Created 2022-01-13 (@author: bouaziz); refactored in R3 into a guarded
function so the rule's output can be tee'd to its log and the module stays
importable. Redesigned 2026-07-25: offline basemap-free rendering, sequential
CVD-safe elevation ramp, geodesic scale bar, formatted graticule.
"""

import os
from os.path import basename

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.patheffects as pe
import matplotlib.patches as mpatches
import cartopy.crs as ccrs
from cartopy.geodesic import Geodesic
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.mpl.ticker import LatitudeLocator, LongitudeLocator

from blueearth_cst.shared.snake_utils import save_figure

# Figure styling kept local to this module: applied through an rc context so
# nothing leaks into figures drawn later in the same interpreter.
_RC = {
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.labelsize": 9,
    "legend.fontsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "figure.facecolor": "white",
}

# Neutral backdrop: the basin is masked, so cells outside it show this colour
# instead of the page white the pale end of the elevation ramp blends into.
_BACKDROP = "#ececec"
_RIVER_COLOR = "#1f6fb4"


def _nice_round(value):
    """Snap ``value`` down to the nearest 1/2/5 x 10^n, for scale-bar lengths."""
    if value <= 0:
        return 1.0
    exponent = np.floor(np.log10(value))
    fraction = value / 10**exponent
    for step in (5.0, 2.0, 1.0):
        if fraction >= step:
            return step * 10**exponent
    return 10**exponent


def _add_scale_bar(ax, extent, proj, fraction=0.25):
    """Draw a geodesic scale bar sized at the latitude where it is drawn.

    The bar length is measured with ``cartopy.geodesic`` between the bar's own
    endpoints, so the km label stays correct at any latitude — a fixed
    degrees-to-km conversion would under-read badly away from the equator.
    """
    lon_min, lon_max, lat_min, lat_max = extent
    lat_bar = lat_min + 0.07 * (lat_max - lat_min)
    lon_start = lon_min + 0.06 * (lon_max - lon_min)

    geod = Geodesic()
    span_m = float(geod.inverse((lon_min, lat_bar), (lon_max, lat_bar))[0, 0])
    length_km = _nice_round(fraction * span_m / 1000.0)
    lon_end = float(geod.direct((lon_start, lat_bar), 90.0, length_km * 1000.0)[0, 0])

    ax.plot(
        [lon_start, lon_end],
        [lat_bar, lat_bar],
        transform=proj,
        color="black",
        linewidth=3.0,
        solid_capstyle="butt",
        zorder=7,
        path_effects=[pe.withStroke(linewidth=5, foreground="white")],
    )
    label = f"{length_km:g} km" if length_km >= 1 else f"{length_km * 1000:g} m"
    ax.text(
        0.5 * (lon_start + lon_end),
        lat_bar + 0.015 * (lat_max - lat_min),
        label,
        transform=proj,
        ha="center",
        va="bottom",
        fontsize=8,
        zorder=7,
        path_effects=[pe.withStroke(linewidth=2.5, foreground="white")],
    )


def _add_north_arrow(ax):
    """Draw a north arrow. Valid because the map is plotted north-up in PlateCarree."""
    ax.annotate(
        "N",
        xy=(0.055, 0.94),
        xytext=(0.055, 0.855),
        xycoords="axes fraction",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
        zorder=7,
        arrowprops=dict(arrowstyle="-|>", facecolor="black", edgecolor="black", lw=1.3),
        path_effects=[pe.withStroke(linewidth=2.5, foreground="white")],
    )


def plot_basin_map(project_dir, gauges_fn, plot_dir=None):
    """Render basin_area.png (DEM + rivers + basin + outlets/gauges/waterbodies)."""
    from hydromt_wflow import WflowSbmModel

    if gauges_fn is not None:
        gauges_name = f'gauges_{basename(gauges_fn).split(".")[0]}'
    else:
        gauges_name = None

    if plot_dir is None:
        plot_dir = f"{project_dir}/plots/wflow_model_performance"
    root = f"{project_dir}/hydrology_model"

    mod = WflowSbmModel(root, mode="r")

    # read and mask the model elevation
    da = mod.staticmaps.data["land_elevation"].raster.mask_nodata()
    da.attrs.update(long_name="elevation", units="m")
    # read/derive river geometries
    gdf_riv = mod.rivers
    # read/derive model basin boundary
    gdf_bas = mod.basins
    # modelled domain area, on an equal-area local UTM zone (basins may be multipart)
    area_km2 = float(gdf_bas.to_crs(gdf_bas.estimate_utm_crs()).area.sum()) / 1e6

    # we assume the model maps are in the geographic CRS EPSG:4326
    proj = ccrs.PlateCarree()
    extent = np.array(da.raster.box.buffer(0.02).total_bounds)[[0, 2, 1, 3]]
    lon_span = extent[1] - extent[0]
    lat_span = extent[3] - extent[2]

    with plt.rc_context(_RC):
        # size the canvas from the basin's own aspect ratio rather than a fixed
        # figsize, so wide and tall basins both fill the frame
        map_width = 7.5
        map_height = float(np.clip(map_width * lat_span / lon_span, 3.0, 9.0))
        fig = plt.figure(figsize=(map_width + 1.8, map_height + 1.6))
        ax = fig.add_subplot(projection=proj)
        ax.set_extent(extent, crs=proj)
        ax.set_facecolor(_BACKDROP)

        ## plot elevation
        # sequential ColorBrewer YlOrBr: monotonic in lightness, CVD-safe and
        # greyscale-degradable, and it leaves blue free for the river network.
        cmap = plt.get_cmap("YlOrBr").copy()
        cmap.set_bad(color=_BACKDROP)
        # full data range: percentile clipping used to render the top cells
        # white, indistinguishable from masked no-data
        vmin = float(da.min())
        vmax = float(da.max())
        if vmax <= vmin:
            vmax = vmin + 1.0
        norm = colors.Normalize(vmin=vmin, vmax=vmax)
        mesh = da.plot(
            transform=proj, ax=ax, zorder=1, cmap=cmap, norm=norm, add_colorbar=False
        )

        # colorbar pinned to the map's own height, immediately beside it
        cax = ax.inset_axes([1.015, 0.0, 0.025, 1.0])
        cbar = fig.colorbar(mesh, cax=cax)
        cbar.set_label("Elevation (m a.s.l.)")
        cbar.outline.set_linewidth(0.6)

        # plot rivers with increasing width with stream order
        gdf_riv.plot(
            ax=ax,
            linewidth=gdf_riv["strord"] / 2,
            color=_RIVER_COLOR,
            zorder=3,
            label="river",
        )
        # plot the basin boundary
        gdf_bas.boundary.plot(ax=ax, color="black", linewidth=1.0, zorder=4)
        # plot various vector layers if present
        geoms = mod.geoms.data
        if "outlets" in geoms:
            geoms["outlets"].plot(
                ax=ax,
                marker="d",
                markersize=45,
                facecolor="black",
                edgecolor="white",
                linewidth=0.8,
                zorder=6,
                label="outlets",
            )
        if gauges_name is not None and gauges_name in geoms:
            geoms[gauges_name].plot(
                ax=ax,
                marker="o",
                markersize=45,
                facecolor=_RIVER_COLOR,
                edgecolor="white",
                linewidth=0.8,
                zorder=6,
                label="output locs",
            )
            if "station_name" in geoms[gauges_name].columns:
                geoms[gauges_name].apply(
                    lambda x: ax.annotate(
                        text=x["station_name"],
                        xy=x.geometry.coords[0],
                        xytext=(3.0, 3.0),
                        textcoords="offset points",
                        fontsize=7,
                        fontweight="bold",
                        color="black",
                        zorder=7,
                        path_effects=[pe.withStroke(linewidth=2, foreground="white")],
                    ),
                    axis=1,
                )

        # manual patches for legend (geopandas/geopandas#660)
        patches = []
        if "lakes" in geoms:
            kwargs = dict(
                facecolor="#9ecae1", edgecolor="black", linewidth=0.8, label="lakes"
            )
            geoms["lakes"].plot(ax=ax, zorder=5, **kwargs)
            patches.append(mpatches.Patch(**kwargs))
        if "reservoirs" in geoms:
            kwargs = dict(
                facecolor="#08519c", edgecolor="black", linewidth=0.8, label="reservoirs"
            )
            geoms["reservoirs"].plot(ax=ax, zorder=5, **kwargs)
            patches.append(mpatches.Patch(**kwargs))
        if "glaciers" in geoms:
            kwargs = dict(
                facecolor="#f0f0f0", edgecolor="#525252", linewidth=0.8, label="glaciers"
            )
            geoms["glaciers"].plot(ax=ax, zorder=5, **kwargs)
            patches.append(mpatches.Patch(**kwargs))

        # graticule with proper degree labels, replacing raw decimal axis labels
        gl = ax.gridlines(
            draw_labels=True, linewidth=0.4, color="0.55", alpha=0.7, linestyle=":"
        )
        gl.top_labels = False
        gl.right_labels = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        # degree-aware locators: a bare MaxNLocator can emit ticks outside
        # [-180, 180] for a basin near the antimeridian or the poles
        gl.xlocator = LongitudeLocator(nbins=5, steps=[1, 2, 2.5, 5, 10])
        gl.ylocator = LatitudeLocator(nbins=5, steps=[1, 2, 2.5, 5, 10])
        ax.spines["geo"].set(linewidth=0.8, edgecolor="0.3")

        _add_scale_bar(ax, extent, proj)
        _add_north_arrow(ax)

        # xarray's plot() leaves a "spatial_ref = 0" centre title behind
        ax.set_title("")
        # an explicit ``y`` is required: title auto-positioning resolves to NaN
        # on a GeoAxes carrying a gridliner, and the title silently disappears
        ax.set_title(f"Model domain — {area_km2:,.0f} km²", loc="left", y=1.01)
        # legend below the map: no in-map position is safe for an arbitrary
        # basin shape, and the map is already carrying scale bar + north arrow
        # de-duplicate by label: current geopandas registers polygon handles
        # itself, so the manual patches above would otherwise double every
        # waterbody entry (only visible on basins that actually have them)
        handles = []
        seen = set()
        for handle in [*ax.get_legend_handles_labels()[0], *patches]:
            label = handle.get_label()
            if label and not label.startswith("_") and label not in seen:
                seen.add(label)
                handles.append(handle)
        if handles:
            ax.legend(
                handles=handles,
                loc="upper center",
                bbox_to_anchor=(0.5, -0.07),
                ncol=min(len(handles), 6),
                frameon=False,
                handlelength=1.6,
                columnspacing=1.6,
            )

        # save figure
        save_figure(
            os.path.join(plot_dir, "basin_area.png"), dpi=300, bbox_inches="tight"
        )
        plt.close(fig)


if __name__ == "__main__":
    if "snakemake" in globals():
        sm = globals()["snakemake"]
        from blueearth_cst.shared.snake_utils import tee_to_log

        with tee_to_log(sm.log[0]):
            plot_basin_map(
                project_dir=sm.params.project_dir,
                gauges_fn=sm.params.output_locations,
            )
