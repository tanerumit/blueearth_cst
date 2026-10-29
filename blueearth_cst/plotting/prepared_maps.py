"""Draw prepared geographic rasters without workflow IO or scientific preparation.

The map template (``dev/reference/toolbox-plot-style.md``, Spatial map template).
The caller supplies common frame, ticks, resolved colors and loaded GeoJSON
features (``basins``, ``divides``, ``rivers``, ``locations``), and owns style
context, captions, backend selection and export. Feature styling comes from the
active preset's ``maps`` tokens.
"""

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import BoundaryNorm, ListedColormap, to_rgba
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.patheffects import Normal, Stroke
from matplotlib.ticker import FuncFormatter
from matplotlib.transforms import Bbox
from numpy.typing import NDArray

from blueearth_cst.plotting.fundamentals import style_colourbar
from blueearth_cst.plotting.location_labels import location_label, wrap_label
from blueearth_cst.plotting.preset import active

#: Stream-order attribute names, in lookup order (hydromt spells it ``strord``).
RIVER_ORDER_KEYS = ("order", "strord")
#: Kilometres per degree of latitude; longitude scales by cos(latitude).
KM_PER_DEGREE = 111.32


@dataclass(frozen=True)
class MapFrame:
    """Common west/east/south/north viewport and explicit geographic display."""

    extent: tuple[float, float, float, float]
    longitude_ticks: Sequence[float]
    latitude_ticks: Sequence[float]
    aspect: float


@dataclass(frozen=True)
class MapScale:
    """Resolved reference classes; unavailable scales have no boundaries/ticks."""

    units: str
    boundaries: Sequence[float]
    ticks: Sequence[float]
    colors: Sequence[Any]
    under_color: Any
    over_color: Any
    missing_color: Any
    status: str


@dataclass(frozen=True)
class RasterMap:
    """Native latitude × longitude values and one-more-element cell-edge arrays."""

    values: NDArray[np.number]
    longitude_edges: NDArray[np.number]
    latitude_edges: NDArray[np.number]
    inside: NDArray[np.bool_] | None = None
    cell_edges: bool = True


class _ClosedUpperBoundaryNorm(BoundaryNorm):
    """Keep the final endpoint in the last class; strict excess stays over-range."""

    def __call__(self, value: Any, clip: bool | None = None) -> Any:
        result = super().__call__(value, clip)
        closed = np.ma.where(
            np.ma.asarray(value) == self.boundaries[-1], self.Ncmap - 1, result
        )
        return closed[()] if np.ndim(value) == 0 else closed


def _numeric_vector(value: Any, name: str) -> NDArray[np.number]:
    array = np.asanyarray(value)
    if (
        array.ndim != 1
        or not np.issubdtype(array.dtype, np.number)
        or np.iscomplexobj(array)
        or not np.isfinite(array).all()
        or np.ma.getmaskarray(array).any()
    ):
        raise ValueError(f"{name} must be a finite unmasked numeric vector")
    return array


def _validate(raster: RasterMap, frame: MapFrame, scale: MapScale) -> None:
    values = np.asanyarray(raster.values)
    if (
        values.ndim != 2
        or 0 in values.shape
        or not np.issubdtype(values.dtype, np.number)
        or np.iscomplexobj(values)
    ):
        raise ValueError("Raster values must be a nonempty numeric 2D array")
    for edges, name, length in (
        (raster.longitude_edges, "longitude edges", values.shape[1] + 1),
        (raster.latitude_edges, "latitude edges", values.shape[0] + 1),
    ):
        array = _numeric_vector(edges, name)
        if len(array) != length:
            raise ValueError(f"{name} must contain {length} values")
        steps = np.diff(array.astype(np.float64))
        precision = (
            2 * float(np.max(np.abs(np.spacing(array))))
            if np.issubdtype(array.dtype, np.floating)
            else 0
        )
        if not (np.all(steps > 0) or np.all(steps < 0)) or not np.allclose(
            steps, steps[0], rtol=0, atol=precision
        ):
            raise ValueError(f"{name} must describe a regular monotonic grid")
    if raster.inside is not None:
        inside = np.asanyarray(raster.inside)
        if (
            inside.shape != values.shape
            or inside.dtype != np.dtype(bool)
            or np.ma.getmaskarray(inside).any()
        ):
            raise ValueError("inside must be an unmasked boolean array matching values")
    if not isinstance(raster.cell_edges, bool):
        raise ValueError("cell_edges must be boolean")
    extent = _numeric_vector(frame.extent, "frame extent")
    if len(extent) != 4:
        raise ValueError("Frame extent must contain west/east/south/north")
    west, east, south, north = extent
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise ValueError("Frame must be geographic and not cross the antimeridian")
    if not np.isfinite(frame.aspect) or frame.aspect <= 0:
        raise ValueError("Frame aspect must be finite and positive")
    for ticks, name, low, high in (
        (frame.longitude_ticks, "longitude ticks", west, east),
        (frame.latitude_ticks, "latitude ticks", south, north),
    ):
        array = _numeric_vector(ticks, name)
        if not np.all(np.diff(array) > 0) or np.any((array < low) | (array > high)):
            raise ValueError(f"{name} must increase within the closed frame")
    if scale.units not in {"degC", "mm/year"}:
        raise ValueError("Map scale units must be degC or mm/year")
    if scale.status not in {"available", "unavailable"}:
        raise ValueError("Map scale status must be available or unavailable")
    boundaries = _numeric_vector(scale.boundaries, "scale boundaries")
    ticks = _numeric_vector(scale.ticks, "scale ticks")
    for color in (
        *scale.colors,
        scale.under_color,
        scale.over_color,
        scale.missing_color,
    ):
        to_rgba(color)
    if scale.status == "unavailable":
        if len(boundaries) or len(ticks) or len(scale.colors):
            raise ValueError("Unavailable scales must have no classes or ticks")
    elif (
        len(boundaries) < 2
        or not np.all(np.diff(boundaries) > 0)
        or len(scale.colors) != len(boundaries) - 1
        or not np.array_equal(ticks, boundaries)
    ):
        raise ValueError(
            "Available scale needs increasing boundaries, colors and ticks"
        )


def _geometry_lines(geometry: Mapping[str, Any]) -> Sequence[Any]:
    kind, coordinates = geometry["type"], geometry["coordinates"]
    if kind == "Polygon":
        return coordinates
    if kind == "MultiPolygon":
        return [ring for polygon in coordinates for ring in polygon]
    if kind == "LineString":
        return [coordinates]
    return coordinates if kind == "MultiLineString" else []


def _river_order(properties: Mapping[str, Any]) -> float | None:
    for key in RIVER_ORDER_KEYS:
        value = properties.get(key)
        if isinstance(value, (int, float)) and math.isfinite(value):
            return float(value)
    return None


def _draw_rivers(ax: Axes, rivers: Sequence[Mapping[str, Any]]) -> None:
    """Blue reaches stepped by stream order; thin reaches first, round joins.

    The layer's lowest order takes the first step and orders past the last
    step reuse it. A layer without an order attribute draws one uniform weight.
    """
    maps = active().maps
    orders = [_river_order(f.get("properties") or {}) for f in rivers]
    known = [order for order in orders if order is not None]
    lowest = min(known) if known else 0.0
    steps = maps["river_order"]
    styled = []
    for feature, order in zip(rivers, orders):
        if order is None:
            width, color = maps["river_width"], maps["river"]
        else:
            width, color = steps[min(max(int(order - lowest), 0), len(steps) - 1)]
        styled.append((width, color, feature))
    # A thin white halo keeps reaches legible over any ramp, blue ones included.
    halo = maps["halo"]
    for width, color, feature in sorted(styled, key=lambda item: item[0]):
        for coordinates in _geometry_lines(feature["geometry"]):
            points = np.asarray(coordinates)
            ax.plot(
                points[:, 0],
                points[:, 1],
                color=color,
                lw=width,
                solid_capstyle="round",
                solid_joinstyle="round",
                zorder=3,
                path_effects=[
                    Stroke(
                        linewidth=width + maps["river_halo_width"],
                        foreground=halo,
                        capstyle="round",
                        joinstyle="round",
                    ),
                    Normal(),
                ],
            )


def _draw_overlays(
    ax: Axes, overlays: Mapping[str, Sequence[Mapping[str, Any]]]
) -> list[tuple[float, float, str]]:
    """Draw rivers, divides, the basin outline and locations; return labels."""
    maps = active().maps
    halo = maps["halo"]
    _draw_rivers(ax, overlays.get("rivers", []))
    for key, color, width, dashes, zorder in (
        ("divides", maps["divide"], maps["divide_width"], maps["divide_dash"], 4),
        ("basins", maps["basin_outline"], maps["basin_outline_width"], None, 4.5),
    ):
        for feature in overlays.get(key, []):
            for coordinates in _geometry_lines(feature["geometry"]):
                points = np.asarray(coordinates)
                (artist,) = ax.plot(
                    points[:, 0], points[:, 1], color=color, lw=width, zorder=zorder
                )
                if dashes is not None:
                    artist.set_dashes(dashes)
                artist.set_path_effects(
                    [Stroke(linewidth=width + 1.0, foreground=halo), Normal()]
                )
    labels = []
    for feature in overlays.get("locations", []):
        geometry = feature["geometry"]
        if geometry["type"] != "Point":
            continue
        x, y = geometry["coordinates"][:2]
        ax.plot(
            x,
            y,
            maps["location_marker"],
            color=maps["location"],
            mec=maps["marker_edge"],
            mew=0.6,
            ms=maps["location_size"],
            zorder=5,
        )
        label = location_label(feature.get("properties") or {})
        if label:
            labels.append((x, y, label))
    return labels


def _nice_length(target_km: float) -> float:
    """The largest 1/2/2.5/5 x 10^k kilometres not above ``target_km``."""
    exponent = math.floor(math.log10(target_km))
    for step in (5, 2.5, 2, 1):
        if step * 10**exponent <= target_km:
            return step * 10**exponent
    return 10 ** (exponent - 1) * 5


def _draw_scale_bar(ax: Axes, frame: MapFrame) -> None:
    """Alternating kilometre segments in the lower left, latitude-corrected."""
    maps = active().maps
    preset = active()
    west, east, south, north = frame.extent
    km_per_degree = KM_PER_DEGREE * math.cos(math.radians((south + north) / 2))
    length_km = _nice_length(0.25 * (east - west) * km_per_degree)
    segments = maps["scale_bar_segments"]
    length = length_km / km_per_degree
    x0 = west + 0.04 * (east - west)
    y0 = south + 0.05 * (north - south)
    height = 0.012 * (north - south)
    ink = preset.colors["ink"]
    for index in range(segments):
        ax.add_patch(
            Rectangle(
                (x0 + index * length / segments, y0),
                length / segments,
                height,
                facecolor=ink if index % 2 == 0 else "white",
                edgecolor=ink,
                linewidth=0.5,
                zorder=6,
            )
        )
    halo = [Stroke(linewidth=2.0, foreground=maps["halo"]), Normal()]
    for step in (0, segments // 2, segments):
        value = length_km * step / segments
        ax.text(
            x0 + length * step / segments,
            y0 + height + 0.01 * (north - south),
            f"{value:g} km" if step == segments else f"{value:g}",
            ha="center",
            va="bottom",
            fontsize=preset.fonts["tick"],
            color=ink,
            zorder=6,
            path_effects=halo,
        )


def _place_point_labels(
    fig: Figure, ax: Axes, labels: Sequence[tuple[float, float, str]]
) -> None:
    """Haloed, optionally two-line labels at the clearest in-frame offset."""
    maps = active().maps
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
            wrap_label(label, maps["location_label_wrap"]),
            (x, y),
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=maps["location_label_size"],
            fontweight="bold",
            color=active().colors["ink"],
            zorder=6,
            path_effects=[Stroke(linewidth=2.2, foreground=maps["halo"]), Normal()],
            arrowprops={
                "arrowstyle": "-",
                "color": active().colors["muted"],
                "lw": 0.5,
                "shrinkA": 1.5,
                "shrinkB": 4,
                "path_effects": [
                    Stroke(linewidth=1.5, foreground=maps["halo"]),
                    Normal(),
                ],
            },
        )
        text.set_in_layout(False)
        options = []
        for dx, dy in candidates:
            text.set_position((dx, dy))
            align = "left" if dx > 0 else "right" if dx < 0 else "center"
            text.set_ha(align)
            text.set_multialignment(align)
            text.set_va("bottom" if dy > 0 else "top" if dy < 0 else "center")
            text.update_positions(renderer)
            box = text.get_window_extent(renderer).expanded(1.08, 1.15)
            outside = not (
                ax.bbox.contains(box.x0, box.y0) and ax.bbox.contains(box.x1, box.y1)
            )
            score = 1000 * outside + sum(box.overlaps(other) for other in occupied)
            options.append((score, dx, dy, box))
        _, dx, dy, box = min(options, key=lambda option: option[0])
        text.set_position((dx, dy))
        align = "left" if dx > 0 else "right" if dx < 0 else "center"
        text.set_ha(align)
        text.set_multialignment(align)
        text.set_va("bottom" if dy > 0 else "top" if dy < 0 else "center")
        occupied.append(box)


def draw_raster_map(
    raster: RasterMap,
    frame: MapFrame,
    scale: MapScale,
    overlays: Mapping[str, Sequence[Mapping[str, Any]]],
    colorbar_title: str | None = None,
) -> Figure:
    """Draw supplied classes or honest unscaled hatching; never change input arrays.

    Available scales always show both rectangular colorbar extensions. Finite
    unscaled cells receive neutral hatching; missing cells stay gray and cells
    outside ``inside`` stay white. Geographic grids use the supplied ticks/aspect.
    ``colorbar_title`` defaults to the scale's units.
    """
    _validate(raster, frame, scale)
    fig, ax = plt.subplots(figsize=(180 / 25.4, 113 / 25.4), layout="constrained")
    values = np.ma.masked_invalid(raster.values)
    inside = (
        np.ones(values.shape, dtype=bool)
        if raster.inside is None
        else np.asarray(raster.inside)
    )
    if scale.status == "available":
        cmap = ListedColormap(scale.colors)
        cmap.set_under(scale.under_color)
        cmap.set_over(scale.over_color)
        cmap.set_bad(scale.missing_color)
        norm = _ClosedUpperBoundaryNorm(scale.boundaries, cmap.N, clip=False)
        displayed = values
    else:
        cmap = ListedColormap(["#eeeeee"])
        cmap.set_bad(scale.missing_color)
        norm = None
        displayed = np.ma.array(np.zeros(values.shape), mask=np.ma.getmaskarray(values))
    mesh = ax.pcolormesh(
        raster.longitude_edges,
        raster.latitude_edges,
        displayed,
        cmap=cmap,
        norm=norm,
        shading="flat",
        edgecolors=(0.25, 0.25, 0.25, 0.12) if raster.cell_edges else "none",
        linewidth=0.25 if raster.cell_edges else 0,
    )
    if scale.status == "unavailable":
        xedges, yedges = raster.longitude_edges, raster.latitude_edges
        for i, j in np.argwhere(inside & ~np.ma.getmaskarray(values)):
            ax.add_patch(
                Rectangle(
                    (min(xedges[j : j + 2]), min(yedges[i : i + 2])),
                    abs(xedges[j + 1] - xedges[j]),
                    abs(yedges[i + 1] - yedges[i]),
                    facecolor="none",
                    edgecolor="#b0b0b0",
                    linewidth=0,
                    hatch="///",
                )
            )
    if raster.inside is not None:
        ax.pcolormesh(
            raster.longitude_edges,
            raster.latitude_edges,
            np.ma.masked_where(inside, np.zeros(values.shape)),
            cmap=ListedColormap(["white"]),
            shading="flat",
            edgecolors="none",
            linewidth=0,
        )
    labels = _draw_overlays(ax, overlays)
    west, east, south, north = frame.extent
    ax.set_xlim(west, east)
    ax.set_ylim(south, north)
    ax.set_aspect(frame.aspect)
    ax.set_xticks(frame.longitude_ticks)
    ax.set_yticks(frame.latitude_ticks)
    ax.set_xlabel("Longitude (°)")
    ax.set_ylabel("Latitude (°)")
    formatter = FuncFormatter(lambda value, _: f"{value:g}".replace("-", "−"))
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    ax.grid(color="#777777", alpha=0.15, linewidth=0.4)
    _draw_scale_bar(ax, frame)
    if scale.status == "available":
        # Placed in the map axes' own fractions rather than through
        # ``fig.colorbar(ax=ax)``: the locked aspect leaves the axes shorter than
        # its layout cell, so a cell-anchored bar overhangs the frame bottom.
        # Width keeps matplotlib's default 20:1 bar in physical units.
        height = 0.7
        axes_ratio = frame.aspect * (north - south) / (east - west)
        cax = ax.inset_axes((1.03, 0.0, height / 20 * axes_ratio, height))
        colorbar = fig.colorbar(
            mesh,
            cax=cax,
            ticks=scale.ticks,
            extend="both",
            extendrect=True,
        )
        if colorbar_title is None:
            colorbar_title = "(°C)" if scale.units == "degC" else "(mm yr⁻¹)"
        style_colourbar(colorbar, colorbar_title)
    _place_point_labels(fig, ax, labels)
    return fig
