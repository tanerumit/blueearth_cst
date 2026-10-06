"""Native-grid complete reporting-year fields and canonical map artists."""

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap
from matplotlib.patheffects import Normal, Stroke

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
        cmap = LinearSegmentedColormap.from_list(f"wf0-{variable}", ramp).resampled(
            len(levels) - 1
        )
        cmap.set_bad("#a0a0a0")
        mesh = ax.pcolormesh(
            _edges(field.longitude, field.attrs.get("longitude_resolution")),
            _edges(field.latitude, field.attrs.get("latitude_resolution")),
            np.ma.masked_invalid(field.values),
            cmap=cmap,
            norm=BoundaryNorm(levels, cmap.N),
            shading="flat",
        )
        layers = {
            key: json.loads(Path(path).read_text(encoding="utf-8"))["features"]
            for key, path in overlays.items()
            if Path(path).is_file()
        }
        extent = []

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
                    ax.plot(x, y, "o", color="#17303c", mec="white", ms=5)
                    props = feature["properties"]
                    label = props.get(
                        "wflow_id",
                        props.get("station_name", props.get("location_code", "")),
                    )
                    text = ax.annotate(
                        str(label),
                        (x, y),
                        xytext=(5, 5),
                        textcoords="offset points",
                        fontsize=7,
                        fontweight="bold",
                        color="black",
                    )
                    text.set_path_effects(
                        [Stroke(linewidth=2.4, foreground="white"), Normal()]
                    )
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
                    if key == "basins":
                        extent.extend(points[:, :2].tolist())
        if extent:
            points = np.asarray(extent)
            lo, hi = points.min(axis=0), points.max(axis=0)
            pad = np.maximum((hi - lo) * 0.08, 0.005)
            ax.set_xlim(lo[0] - pad[0], hi[0] + pad[0])
            ax.set_ylim(lo[1] - pad[1], hi[1] + pad[1])
        lat = float(field.latitude.mean())
        ax.set_aspect(1 / math.cos(math.radians(lat)))
        ax.set_xlabel("Longitude (°E/°W)")
        ax.set_ylabel("Latitude (°N/°S)")
        cb = fig.colorbar(
            mesh, ax=ax, shrink=0.48, pad=0.03, anchor=(0, 0), ticks=levels
        )
        cb.ax.set_title(
            f"{variable.capitalize()}\n({'°C' if variable == 'temp' else 'mm yr⁻¹'})",
            fontsize=6,
        )
        supported = counts.values[counts.values > 0]
        years = (
            f"{int(supported.min())}–{int(supported.max())}" if supported.size else "0"
        )
        if supported.size and supported.min() == supported.max():
            years = str(int(supported.max()))
        ax.text(
            0,
            -0.11,
            f"{source.upper()} · {field.attrs.get('period_start', '?')}–{field.attrs.get('period_end', '?')} · {years} complete years per cell",
            transform=ax.transAxes,
            fontsize=6,
            va="top",
        )
        return fig
