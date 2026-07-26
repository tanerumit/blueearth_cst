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
import matplotlib.lines as mlines
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from cartopy.geodesic import Geodesic
from shapely.geometry import Point as ShapelyPoint
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.mpl.ticker import LatitudeLocator, LongitudeLocator

from blueearth_cst.shared.snake_utils import log_row, save_figure

# Journal double-column width. The figure is authored at final print size, so
# these point sizes are the ones the reader gets — nothing is rescaled later.
_FIG_WIDTH_MM = 180.0
_MM_PER_IN = 25.4

# Figure styling kept local to this module: applied through an rc context so
# nothing leaks into figures drawn later in the same interpreter.
# Three type sizes only: 8 pt body (axis labels, legend), 7 pt secondary
# (ticks, scale bar, locator), 6 pt credit line.
_PT_BODY, _PT_SECONDARY, _PT_CREDIT = 8, 7, 6
_RC = {
    "font.size": _PT_BODY,
    "axes.titlesize": _PT_BODY,
    "axes.labelsize": _PT_BODY,
    "legend.fontsize": _PT_BODY,
    "xtick.labelsize": _PT_SECONDARY,
    "ytick.labelsize": _PT_SECONDARY,
    "figure.facecolor": "white",
}

# Neutral backdrop: the basin is masked, so cells outside it show this colour
# instead of the page white the pale end of the elevation ramp blends into.
_BACKDROP = "#ececec"
_RIVER_COLOR = "#1f6fb4"

# Base map confined to light-to-mid greys: it stays context rather than
# competing ink, and it leaves the dark end of the greyscale free for the DEM
# so the two remain separable in a black-and-white print.
_BASE_CMAP = colors.LinearSegmentedColormap.from_list(
    "basemap_grey", plt.get_cmap("gray")(np.linspace(0.55, 1.0, 256))
)

# Water keeps a colour even though the rest of the base map is monochrome.
# These basins are coastal and tidal — a fully greyscale base map turns an
# estuary into indistinguishable grey and makes the domain look landlocked.
_WATER_RGB = (0.72, 0.83, 0.90)


class _MonochromeOSM(cimgt.OSM):
    """OSM tiles flattened to light greys, with water left in a blue accent."""

    def get_image(self, tile):
        img, extent, origin = super().get_image(tile)
        rgb = np.asarray(img, dtype=float)[..., :3] / 255.0
        red, green, blue = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        # OSM paints water a desaturated blue; nothing else it draws is
        # appreciably bluer than it is red
        is_water = (blue - red > 0.045) & (blue > 0.5)
        luminance = 0.299 * red + 0.587 * green + 0.114 * blue
        # compress land into the light half of the greyscale so the DEM keeps
        # the dark end to itself and the two stay separable in a B&W print
        out = np.repeat((0.55 + 0.45 * luminance)[..., None], 3, axis=2)
        out[is_water] = _WATER_RGB
        # back to uint8: cartopy passes the result straight to imshow, which
        # reads a float RGB array on a 0-1 scale and renders 0-255 data black
        return (out * 255).astype(np.uint8), extent, origin


def _tick_ladder(vmin, vmax):
    """Round colorbar ticks spanning ``vmin``..``vmax``, plus the true ends.

    The elevation ramp is stretched non-linearly, so ticks have to be read off
    the bar rather than interpolated — that only works if they sit on round
    numbers and the real minimum and maximum are both shown.
    """
    candidates = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000]
    # keep clear of the end ticks, which carry the true min/max, so their
    # labels do not collide with a round value sitting just inside them
    ticks = [v for v in candidates if vmin * 1.15 < v < vmax * 0.85]
    return [round(vmin, 1)] + ticks + [round(vmax)]


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


def _add_scale_bar(ax, extent, crs_data, fraction=0.25, divisions=4):
    """Draw a segmented geodesic scale bar, USGS-style.

    The bar length is measured with ``cartopy.geodesic`` between the bar's own
    endpoints, so the km label stays correct at any latitude — a fixed
    degrees-to-km conversion would under-read badly away from the equator.
    """
    lon_min, lon_max, lat_min, lat_max = extent
    lat_bar = lat_min + 0.075 * (lat_max - lat_min)
    lon_start = lon_min + 0.055 * (lon_max - lon_min)
    height = 0.013 * (lat_max - lat_min)

    geod = Geodesic()
    span_m = float(geod.inverse((lon_min, lat_bar), (lon_max, lat_bar))[0, 0])
    length_km = _nice_round(fraction * span_m / 1000.0)
    step_m = length_km * 1000.0 / divisions

    # segment edges, each placed by geodesic offset from the bar's own start
    edges = [lon_start]
    for i in range(1, divisions + 1):
        edges.append(float(geod.direct((lon_start, lat_bar), 90.0, step_m * i)[0, 0]))

    # white halo so the bar reads over any basemap
    ax.add_patch(
        mpatches.Rectangle(
            (edges[0], lat_bar - 0.6 * height),
            edges[-1] - edges[0],
            2.2 * height,
            transform=crs_data,
            facecolor="white",
            edgecolor="none",
            alpha=0.75,
            zorder=7,
        )
    )
    for i in range(divisions):
        ax.add_patch(
            mpatches.Rectangle(
                (edges[i], lat_bar),
                edges[i + 1] - edges[i],
                height,
                transform=crs_data,
                facecolor="black" if i % 2 == 0 else "white",
                edgecolor="black",
                linewidth=0.6,
                zorder=8,
            )
        )
    unit = "km" if length_km >= 1 else "m"
    scale = 1 if length_km >= 1 else 1000
    for i in (0, divisions // 2, divisions):
        value = length_km * scale * i / divisions
        ax.text(
            edges[i],
            lat_bar + 1.35 * height,
            f"{value:g}" + (f" {unit}" if i == divisions else ""),
            transform=crs_data,
            ha="center",
            va="bottom",
            fontsize=_PT_SECONDARY,
            zorder=8,
        )


def _add_north_arrow(ax, x=0.055, y=0.90, size=0.075):
    """Draw a two-tone compass needle.

    Valid because the map is drawn north-up and centred on the basin, so the
    meridian convergence across a basin-scale extent is negligible.
    """
    half = size * 0.22
    # left half filled, right half hollow — the standard cartographic needle
    ax.add_patch(
        mpatches.Polygon(
            [(x, y + size), (x - half, y - size * 0.35), (x, y - size * 0.12)],
            transform=ax.transAxes,
            facecolor="black",
            edgecolor="black",
            linewidth=0.8,
            zorder=8,
        )
    )
    ax.add_patch(
        mpatches.Polygon(
            [(x, y + size), (x + half, y - size * 0.35), (x, y - size * 0.12)],
            transform=ax.transAxes,
            facecolor="white",
            edgecolor="black",
            linewidth=0.8,
            zorder=8,
        )
    )
    ax.text(
        x,
        y + size * 1.12,
        "N",
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=_PT_BODY,
        fontweight="bold",
        zorder=8,
        path_effects=[pe.withStroke(linewidth=2.5, foreground="white")],
    )


def _add_locator_inset(ax, gdf_bas, crs_data, bounds=(0.792, 0.008, 0.20, 0.20)):
    """Corner locator map: the surrounding country with the study area boxed."""
    import cartopy.io.shapereader as shpreader

    minx, miny, maxx, maxy = gdf_bas.total_bounds
    cx, cy = 0.5 * (minx + maxx), 0.5 * (miny + maxy)

    reader = shpreader.Reader(
        shpreader.natural_earth(
            resolution="110m", category="cultural", name="admin_0_countries"
        )
    )
    countries = list(reader.records())
    host = None
    for rec in countries:
        if rec.geometry.contains(ShapelyPoint(cx, cy)):
            host = rec
            break
    if host is None:  # basin on a coastline the 110m outline misses
        host = min(countries, key=lambda r: r.geometry.distance(ShapelyPoint(cx, cy)))

    hminx, hminy, hmaxx, hmaxy = host.geometry.bounds
    pad = 0.35 * max(hmaxx - hminx, hmaxy - hminy)

    inset = ax.inset_axes(bounds, projection=crs_data)
    inset.set_extent(
        [hminx - pad, hmaxx + pad, hminy - pad, hmaxy + pad], crs=crs_data
    )
    inset.set_facecolor("#d9e6f2")  # sea
    for rec in countries:
        inset.add_geometries(
            [rec.geometry],
            crs=crs_data,
            facecolor="#f5f5f5",
            edgecolor="#9a9a9a",
            linewidth=0.35,
            zorder=1,
        )
    inset.add_geometries(
        [host.geometry],
        crs=crs_data,
        facecolor="#dcdcdc",
        edgecolor="#4d4d4d",
        linewidth=0.7,
        zorder=2,
    )
    # study-area marker: a box this small would vanish, so mark it
    inset.plot(
        cx,
        cy,
        transform=crs_data,
        marker="s",
        markersize=5,
        markerfacecolor="#d7191c",
        markeredgecolor="black",
        markeredgewidth=0.6,
        zorder=3,
    )
    name = host.attributes.get("NAME_LONG") or host.attributes.get("NAME") or ""
    # label inside the frame: a title would overhang into the main map
    inset.text(
        0.5,
        0.965,
        name,
        transform=inset.transAxes,
        ha="center",
        va="top",
        fontsize=_PT_SECONDARY,
        fontweight="bold",
        zorder=4,
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=1.2),
    )
    for spine in inset.spines.values():
        spine.set(linewidth=0.8, edgecolor="black")
    return inset


def _tile_zoom(extent, tiles_across=4, lo=4, hi=16):
    """Pick a web-mercator zoom level so the extent spans ~``tiles_across`` tiles."""
    width_deg = max(extent[1] - extent[0], 1e-6)
    zoom = int(round(np.log2(360.0 * tiles_across / width_deg)))
    return int(np.clip(zoom, lo, hi))


def plot_basin_map(
    project_dir,
    gauges_fn,
    plot_dir=None,
    basemap=True,
    locator=True,
    width_mm=_FIG_WIDTH_MM,
    title=None,
    panel_label=None,
    dpi=600,
    context=0.25,
):
    """Render basin_area.png (DEM + rivers + basin + outlets/gauges/waterbodies).

    ``width_mm`` is the final print width the figure is authored at (default
    180 mm, a journal double column) — type sizes are set for that width and
    the figure is not meant to be rescaled afterwards. ``title`` defaults to
    none: journals carry the title in the caption, and a suggested caption is
    written to the log instead. ``context`` is the margin drawn around the model domain, as a
    fraction of its own extent. ``panel_label`` stamps a bold tag ("a", "b")
    for use as one panel of a composite figure. ``basemap`` draws OSM tiles as
    context around the basin and ``locator`` adds a corner overview map; both
    need network access on first use (the locator outline is then cached
    locally, tiles are re-fetched per run).
    """
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
    crs_data = ccrs.PlateCarree()
    # Margin scaled to the basin rather than a flat 0.02°. The outlet sits on
    # the domain edge by construction, so a tight crop cuts off exactly the
    # water body the basin drains into — here the outlet was 0.004° from the
    # frame and the Komo estuary fell outside it.
    bounds = da.raster.box.total_bounds
    margin = context * max(bounds[2] - bounds[0], bounds[3] - bounds[1])
    extent = np.array(da.raster.box.buffer(margin).total_bounds)[[0, 2, 1, 3]]
    lon_mid = 0.5 * (extent[0] + extent[1])
    lat_mid = 0.5 * (extent[2] + extent[3])
    # Plotting straight into PlateCarree stretches the map badly away from the
    # equator (a 60°N basin comes out ~2x too wide). An equal-area projection
    # centred on the basin holds shape and area at any latitude, and this
    # figure reports an area, so equal-area is the honest choice.
    crs_map = ccrs.LambertAzimuthalEqualArea(
        central_longitude=lon_mid, central_latitude=lat_mid
    )
    corners = crs_map.transform_points(
        crs_data,
        np.array([extent[0], extent[1], extent[1], extent[0]]),
        np.array([extent[2], extent[2], extent[3], extent[3]]),
    )
    proj_aspect = float(
        (corners[:, 1].max() - corners[:, 1].min())
        / (corners[:, 0].max() - corners[:, 0].min())
    )

    cell_km = (
        float(Geodesic().inverse((lon_mid, lat_mid), (lon_mid + abs(da.raster.res[0]), lat_mid))[0, 0])
        / 1000.0
    )

    with plt.rc_context(_RC):
        # size the canvas from the basin's own aspect ratio rather than a fixed
        # figsize, so wide and tall basins both fill the frame
        # Explicit margins rather than a tight bbox. The figure is authored at
        # an exact print width, and deriving that width by trimming after the
        # fact proved unreliable — a GeoAxes reports a tight bbox clipped to
        # the figure, so trimming silently dropped artists and, once, collapsed
        # the whole canvas. Fixed margins make the width exact by construction.
        left, right_pad, top_pad = 0.075, 0.135, 0.03
        # the legend sits under the axes and wraps, so the bottom margin has to
        # know how many rows it will take before the axes is placed — count the
        # entries from the layers actually present rather than guessing
        n_entries = 3  # river + basin boundary + model cell
        n_entries += "outlets" in mod.geoms.data
        n_entries += bool(gauges_name) and gauges_name in mod.geoms.data
        n_entries += sum(
            layer in mod.geoms.data for layer in ("lakes", "reservoirs", "glaciers")
        )
        legend_rows = int(np.ceil(n_entries / 3))
        bottom = 0.115 + 0.042 * legend_rows  # lon labels + legend + credits
        fig_width = width_mm / _MM_PER_IN
        axes_width_in = fig_width * (1.0 - left - right_pad)
        axes_height_in = float(np.clip(axes_width_in * proj_aspect, 1.6, 7.0))
        fig_height = axes_height_in / (1.0 - bottom - top_pad)

        fig = plt.figure(figsize=(fig_width, fig_height))
        ax = fig.add_axes(
            [left, bottom, 1.0 - left - right_pad, 1.0 - bottom - top_pad],
            projection=crs_map,
        )
        # geopandas .plot() draws in raw axes coordinates and honours no
        # cartopy transform, so every vector layer is reprojected to the
        # map CRS first — otherwise degrees get read as metres
        to_map = lambda gdf: gdf.to_crs(crs_map.proj4_init)  # noqa: E731
        ax.set_extent(extent, crs=crs_data)
        ax.set_facecolor(_BACKDROP)

        # context around the basin: zoom derived from the extent, not hardcoded
        if basemap:
            try:
                # desired_tile_form="L" fetches single-band tiles, so the
                # basemap renders greyscale and never competes with the DEM
                ax.add_image(_MonochromeOSM(), _tile_zoom(extent), zorder=0)
            except Exception as err:  # offline / tile server unreachable
                log_row(f"basemap skipped ({type(err).__name__}: {err})", module="plot")

        ## plot elevation
        # sequential ColorBrewer YlOrBr: monotonic in lightness, CVD-safe and
        # greyscale-degradable, and it leaves blue free for the river network.
        cmap = plt.get_cmap("YlOrBr").copy()
        # masked cells must be see-through when a basemap is drawn, otherwise
        # the DEM's bounding box blanks the context around the basin
        cmap.set_bad(alpha=0.0) if basemap else cmap.set_bad(color=_BACKDROP)
        # power-law stretch, not linear and not quantile classes. Linear
        # collapses a lowland basin into one tone; quantile classes fix that
        # but imply far more relief than exists (a 0.3 m class rendered the
        # same width as a 170 m one). gamma < 1 expands the low end while the
        # mapping stays continuous and monotonic, so magnitudes stay honest.
        vmin = float(np.nanmin(da.values))
        vmax = float(np.nanmax(da.values))
        if vmax <= vmin:
            vmax = vmin + 1.0
        norm = colors.PowerNorm(gamma=0.45, vmin=vmin, vmax=vmax)
        levels = _tick_ladder(vmin, vmax)
        mesh = da.plot(
            transform=crs_data,
            ax=ax,
            zorder=1,
            cmap=cmap,
            norm=norm,
            add_colorbar=False,
            # hairline cell edges: makes the model resolution legible without
            # competing with the elevation ramp
            edgecolors="0.75",
            linewidths=0.15,
        )

        # colorbar pinned to the map's own height, immediately beside it
        cax = ax.inset_axes([1.015, 0.22, 0.022, 0.55])
        cbar = fig.colorbar(mesh, cax=cax, ticks=levels, spacing="uniform")
        cbar.set_label("Elevation (m a.s.l.)")
        cbar.ax.set_yticklabels([f"{v:g}" for v in levels])
        cbar.ax.tick_params(length=2, pad=1.5)
        cbar.outline.set_linewidth(0.6)

        # plot rivers with increasing width with stream order
        to_map(gdf_riv).plot(
            ax=ax,
            linewidth=gdf_riv["strord"] / 2,
            color=_RIVER_COLOR,
            zorder=3,
            label="river (width ∝ Strahler order)",
        )
        # plot the basin boundary
        to_map(gdf_bas).boundary.plot(ax=ax, color="black", linewidth=1.0, zorder=4)
        # plot various vector layers if present
        geoms = mod.geoms.data
        if "outlets" in geoms:
            to_map(geoms["outlets"]).plot(
                ax=ax,
                marker="d",
                markersize=45,
                facecolor="black",
                edgecolor="white",
                linewidth=0.8,
                zorder=6,
                label="basin outlet (discharge reported)",
            )
        if gauges_name is not None and gauges_name in geoms:
            to_map(geoms[gauges_name]).plot(
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
                to_map(geoms[gauges_name]).apply(
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
            to_map(geoms["lakes"]).plot(ax=ax, zorder=5, **kwargs)
            patches.append(mpatches.Patch(**kwargs))
        if "reservoirs" in geoms:
            kwargs = dict(
                facecolor="#08519c", edgecolor="black", linewidth=0.8, label="reservoirs"
            )
            to_map(geoms["reservoirs"]).plot(ax=ax, zorder=5, **kwargs)
            patches.append(mpatches.Patch(**kwargs))
        if "glaciers" in geoms:
            kwargs = dict(
                facecolor="#f0f0f0", edgecolor="#525252", linewidth=0.8, label="glaciers"
            )
            to_map(geoms["glaciers"]).plot(ax=ax, zorder=5, **kwargs)
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

        _add_scale_bar(ax, extent, crs_data)
        _add_north_arrow(ax)
        if locator:
            try:
                _add_locator_inset(ax, gdf_bas, crs_data)
            except Exception as err:  # outline not cached and no network
                log_row(f"locator skipped ({type(err).__name__}: {err})", module="plot")

        # xarray's plot() leaves a "spatial_ref = 0" centre title behind
        ax.set_title("")
        if title:
            # an explicit ``y`` is required: title auto-positioning resolves to
            # NaN on a GeoAxes carrying a gridliner, and the title silently
            # disappears
            ax.set_title(title, loc="left", y=1.01)
        if panel_label:
            ax.text(
                0.0,
                1.015,
                panel_label,
                transform=ax.transAxes,
                ha="left",
                va="bottom",
                fontsize=_PT_BODY,
                fontweight="bold",
            )
        # legend below the map: no in-map position is safe for an arbitrary
        # basin shape, and the map is already carrying scale bar + north arrow
        # de-duplicate by label: current geopandas registers polygon handles
        # itself, so the manual patches above would otherwise double every
        # waterbody entry (only visible on basins that actually have them)
        # proxies for the two things drawn but never registered: the domain
        # outline and the model grid the reader is looking at
        patches.append(
            mlines.Line2D([], [], color="black", linewidth=1.0, label="basin boundary")
        )
        patches.append(
            mpatches.Patch(
                facecolor="none",
                edgecolor="0.75",
                linewidth=0.6,
                label=f"model cell (~{cell_km:.1f} km)",
            )
        )

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
                bbox_to_anchor=(0.5, -0.075),
                ncol=min(len(handles), 3),
                frameon=False,
                handlelength=1.6,
                columnspacing=1.6,
            )

        # source, licence and datum: a map figure without these gets queried in
        # review, and the OSM tiles are ODbL — attribution is a licence term
        sources = ["Elevation: Wflow model staticmaps (land_elevation)"]
        if basemap:
            sources.insert(0, "Base map © OpenStreetMap contributors (ODbL)")
        credits = [
            " · ".join(sources),
            "Lambert azimuthal equal-area projection centred on "
            f"{lat_mid:.2f}°N, {lon_mid:.2f}°E · WGS 84 datum",
        ]
        # Anchored in FIGURE coordinates, not axes coordinates. Placed below
        # the axes it landed off-canvas, and a GeoAxes tight bbox clips to the
        # figure instead of growing, so the line was silently dropped.
        fig.text(
            0.012,
            0.012,
            "\n".join(credits),
            ha="left",
            va="bottom",
            fontsize=_PT_CREDIT,
            color="0.35",
            linespacing=1.5,
        )

        # the area used to sit in the title; with the title gone it has to
        # reach the reader through the caption, so hand one over ready to use
        log_row(
            "Suggested caption: Wflow model domain "
            f"({area_km2:,.0f} km²), showing land-surface elevation, the river "
            "network (line width proportional to Strahler order) and the basin "
            "outlet at which discharge is reported. Lambert azimuthal "
            f"equal-area projection centred on {lat_mid:.2f}°N, {lon_mid:.2f}°E.",
            module="plot",
        )

        # save figure
        save_figure(
            os.path.join(plot_dir, "basin_area.png"),
            dpi=dpi,
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
