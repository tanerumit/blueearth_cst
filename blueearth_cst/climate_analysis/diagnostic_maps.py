"""Native-grid complete reporting-year fields and canonical map artists."""

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap, ListedColormap
from matplotlib.patheffects import Normal, Stroke
from matplotlib.ticker import FuncFormatter
from matplotlib.transforms import Bbox

from blueearth_cst.climate_analysis import diagnostics as dg
from blueearth_cst.climate_analysis.diagnostic_figures import STYLE


def annual_fields(ds, m0, settings):
    """Apply amount/temperature completeness cellwise without interpolating."""
    output = xr.Dataset()
    tol = dg.Completeness(
        settings["max_missing_days_month"], settings["max_missing_days_year"]
    )
    for variable in ("precip", "temp", "pet"):
        if variable not in ds:
            continue
        field = ds[variable].transpose("time", "latitude", "longitude")
        data = field.values
        shape = field.shape[1:]
        means = np.full(shape, np.nan)
        counts = np.zeros(shape, dtype=np.int32)
        index = pd.DatetimeIndex(field.time.values)
        calendar = pd.date_range(index.min(), index.max(), freq="D")
        for i in range(shape[0]):
            for j in range(shape[1]):
                values = pd.Series(data[:, i, j], index=index).reindex(calendar)
                yearly = dg.annual(
                    values, m0, "mean" if variable == "temp" else "sum", tol
                )
                counts[i, j] = yearly.notna().sum()
                means[i, j] = yearly.mean()
        coords = {key: field[key] for key in ("latitude", "longitude")}
        attrs = {"units": "degC" if variable == "temp" else "mm/year"}
        for name in ("latitude", "longitude"):
            if len(field[name]) > 1:
                attrs[f"{name}_resolution"] = abs(
                    float(field[name][1] - field[name][0])
                )
            elif hasattr(ds, "raster"):
                attrs[f"{name}_resolution"] = abs(
                    float(ds.raster.res[0 if name == "longitude" else 1])
                )
        output[variable] = xr.DataArray(
            means, dims=("latitude", "longitude"), coords=coords, attrs=attrs
        )
        output[f"{variable}_valid_years"] = xr.DataArray(
            counts, dims=("latitude", "longitude"), coords=coords
        )
        output[f"{variable}_unavailable"] = xr.DataArray(
            ~np.isfinite(means), dims=("latitude", "longitude"), coords=coords
        )
    return output


def _edges(x, resolution=None):
    x = np.asarray(x)
    if len(x) < 2 and resolution is None:
        raise ValueError("A one-cell map requires retained native grid resolution")
    half = (x[1] - x[0]) / 2 if len(x) > 1 else resolution / 2
    return np.r_[x[0] - half, (x[:-1] + x[1:]) / 2, x[-1] + half]


def visible_values(field, basin_path):
    """Cell values intersecting the displayed basin extent, including padding."""
    import geopandas as gpd

    west, south, east, north = gpd.read_file(basin_path).total_bounds
    px, py = max((east - west) * 0.08, 0.005), max((north - south) * 0.08, 0.005)
    xedges = _edges(field.longitude, field.attrs.get("longitude_resolution"))
    yedges = _edges(field.latitude, field.attrs.get("latitude_resolution"))
    x = (np.minimum(xedges[:-1], xedges[1:]) <= east + px) & (
        np.maximum(xedges[:-1], xedges[1:]) >= west - px
    )
    y = (np.minimum(yedges[:-1], yedges[1:]) <= north + py) & (
        np.maximum(yedges[:-1], yedges[1:]) >= south - py
    )
    return field.values[np.ix_(y, x)].ravel()


def draw_map(field, variable, source, overlays, limits, counts):
    """Native cells, basin/subbasin/river/gauge overlays and discrete colourbar."""
    with plt.rc_context(STYLE):
        fig, ax = plt.subplots(figsize=(180 / 25.4, 113 / 25.4), layout="constrained")
        low, high = limits
        if not np.isfinite(low + high):
            low, high = (0, 1)
        if high <= low:
            high = low + (1 if variable != "temp" else 0.2)
        step = (
            100
            if variable != "temp"
            else 0.2
            if high - low <= 1.6
            else 0.5
            if high - low <= 4
            else 1
        )
        levels = np.arange(
            math.floor(low / step) * step,
            math.ceil(high / step) * step + step / 2,
            step,
        )
        ramp = (
            ("#ffffcc", "#ffe895", "#fec45f", "#fd953f", "#fa4a29")
            if variable == "temp"
            else (
                "#deebf7",
                "#c6dbef",
                "#9ecae1",
                "#6baed6",
                "#4292c6",
                "#2171b5",
                "#08519c",
            )
        )
        classes = len(levels) - 1
        # A one-class resampling otherwise selects the pale start of the ramp.
        cmap = (
            ListedColormap([ramp[-1]], name=f"wf0-{variable}")
            if classes == 1
            else LinearSegmentedColormap.from_list(f"wf0-{variable}", ramp).resampled(
                classes
            )
        )
        cmap.set_bad("#a0a0a0")
        xedges = _edges(field.longitude, field.attrs.get("longitude_resolution"))
        yedges = _edges(field.latitude, field.attrs.get("latitude_resolution"))
        mesh = ax.pcolormesh(
            xedges,
            yedges,
            np.ma.masked_invalid(field.values),
            cmap=cmap,
            norm=BoundaryNorm(levels, cmap.N),
            shading="flat",
            edgecolors=(0.25, 0.25, 0.25, 0.18),
            linewidth=0.25,
        )
        layers = {
            key: json.loads(Path(path).read_text(encoding="utf-8"))["features"]
            for key, path in overlays.items()
            if Path(path).is_file()
        }
        labels = []
        marker_color = "#007c83" if variable == "temp" else "#c51b7d"

        def lines(geom):
            kind, coordinates = geom["type"], geom["coordinates"]
            if kind == "Polygon":
                return coordinates
            if kind == "MultiPolygon":
                return [ring for polygon in coordinates for ring in polygon]
            if kind == "LineString":
                return [coordinates]
            if kind == "MultiLineString":
                return coordinates
            return []

        for key in ("subbasins", "rivers", "basins", "locations"):
            for feature in layers.get(key, []):
                geom = feature["geometry"]
                if geom["type"] == "Point":
                    x, y = geom["coordinates"][:2]
                    ax.plot(
                        x,
                        y,
                        "o",
                        color=marker_color,
                        mec="white",
                        mew=0.9,
                        ms=5.5,
                        zorder=5,
                    )
                    props = feature["properties"]
                    label = props.get(
                        "wflow_id",
                        props.get("station_name", props.get("location_code", "")),
                    )
                    if str(label):
                        labels.append((x, y, str(label)))
                for coords in lines(geom):
                    points = np.asarray(coords)
                    (artist,) = ax.plot(
                        points[:, 0],
                        points[:, 1],
                        color="black",
                        lw=1.3 if key == "basins" else 0.65,
                        ls="--" if key == "subbasins" else "-",
                    )
                    artist.set_path_effects(
                        [
                            Stroke(
                                linewidth=(2.1 if key == "basins" else 1.2),
                                foreground="white",
                            ),
                            Normal(),
                        ]
                    )
        # Cell edges, rather than padded basin bounds, fill the entire map frame.
        ax.set_xlim(float(xedges.min()), float(xedges.max()))
        ax.set_ylim(float(yedges.min()), float(yedges.max()))
        lat = float(field.latitude.mean())
        ax.set_aspect(1 / math.cos(math.radians(lat)))
        ax.set_xlabel("Longitude (°)")
        ax.set_ylabel("Latitude (°)")
        formatter = FuncFormatter(lambda value, _: f"{value:g}".replace("-", "−"))
        ax.xaxis.set_major_formatter(formatter)
        ax.yaxis.set_major_formatter(formatter)
        cb = fig.colorbar(
            mesh, ax=ax, shrink=0.48, pad=0.03, anchor=(0, 0), ticks=levels
        )
        cb.ax.set_title(
            f"{variable.capitalize()}\n({'°C' if variable == 'temp' else 'mm yr⁻¹'})",
            fontsize=6,
            pad=10,
        )
        _place_point_labels(fig, ax, labels)
        return fig


def _place_point_labels(fig, ax, labels):
    """Choose readable offsets inside the map, avoiding labels and markers."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    radius = 4 * fig.dpi / 72
    occupied = []
    for x, y, _ in labels:
        px, py = ax.transData.transform((x, y))
        occupied.append(
            Bbox.from_extents(px - radius, py - radius, px + radius, py + radius)
        )
    candidates = (
        (8, 8),
        (-8, 8),
        (8, -8),
        (-8, -8),
        (16, 0),
        (-16, 0),
        (0, 16),
        (0, -16),
        (24, 16),
        (-24, 16),
        (24, -16),
        (-24, -16),
    )
    for x, y, label in labels:
        if not ax.get_xlim()[0] <= x <= ax.get_xlim()[1] or not (
            ax.get_ylim()[0] <= y <= ax.get_ylim()[1]
        ):
            continue
        text = ax.annotate(
            label,
            (x, y),
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=7,
            fontweight="bold",
            color="#222222",
            zorder=6,
            bbox={
                "boxstyle": "round,pad=0.18",
                "fc": "white",
                "ec": "#777777",
                "lw": 0.35,
                "alpha": 0.95,
            },
            arrowprops={
                "arrowstyle": "-",
                "color": "#444444",
                "lw": 0.55,
                "shrinkB": 4,
            },
        )
        # Offsets fit inside the existing map; they must not move its layout.
        text.set_in_layout(False)
        options = []
        for dx, dy in candidates:
            text.set_position((dx, dy))
            text.set_ha("left" if dx > 0 else "right" if dx < 0 else "center")
            text.set_va("bottom" if dy > 0 else "top" if dy < 0 else "center")
            text.update_positions(renderer)
            text.update_bbox_position_size(renderer)
            box = text.get_bbox_patch().get_window_extent(renderer).expanded(1.08, 1.15)
            outside = not (
                ax.bbox.contains(box.x0, box.y0) and ax.bbox.contains(box.x1, box.y1)
            )
            score = 1000 * outside + sum(box.overlaps(b) for b in occupied)
            options.append((score, dx, dy, box))
        _, dx, dy, box = min(options, key=lambda option: option[0])
        text.set_position((dx, dy))
        text.set_ha("left" if dx > 0 else "right" if dx < 0 else "center")
        text.set_va("bottom" if dy > 0 else "top" if dy < 0 else "center")
        occupied.append(box)
