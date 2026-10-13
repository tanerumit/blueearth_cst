"""Draw prepared geographic rasters without workflow IO or scientific preparation.

The caller supplies common frame, ticks, resolved colors and loaded GeoJSON
features, and owns style context, captions, backend selection and export.
"""

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

from blueearth_cst.plotting.location_labels import location_label


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


def _draw_overlays(
    ax: Axes,
    overlays: Mapping[str, Sequence[Mapping[str, Any]]],
    units: str,
) -> list[tuple[float, float, str]]:
    labels = []
    marker_color = "#007c83" if units == "degC" else "#c51b7d"
    for key in ("subbasins", "rivers", "basins", "locations"):
        for feature in overlays.get(key, []):
            geometry = feature["geometry"]
            if geometry["type"] == "Point":
                x, y = geometry["coordinates"][:2]
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
                properties = feature["properties"]
                label = location_label(properties)
                if label:
                    labels.append((x, y, label))
            for coordinates in _geometry_lines(geometry):
                points = np.asarray(coordinates)
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
                            linewidth=2.1 if key == "basins" else 1.2,
                            foreground="white",
                        ),
                        Normal(),
                    ]
                )
    return labels


def _place_point_labels(
    fig: Figure, ax: Axes, labels: Sequence[tuple[float, float, str]]
) -> None:
    """Preserve existing in-frame offset placement without changing map layout."""
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
            score = 1000 * outside + sum(box.overlaps(other) for other in occupied)
            options.append((score, dx, dy, box))
        _, dx, dy, box = min(options, key=lambda option: option[0])
        text.set_position((dx, dy))
        text.set_ha("left" if dx > 0 else "right" if dx < 0 else "center")
        text.set_va("bottom" if dy > 0 else "top" if dy < 0 else "center")
        occupied.append(box)


def draw_raster_map(
    raster: RasterMap,
    frame: MapFrame,
    scale: MapScale,
    overlays: Mapping[str, Sequence[Mapping[str, Any]]],
) -> Figure:
    """Draw supplied classes or honest unscaled hatching; never change input arrays.

    Available scales always show both rectangular colorbar extensions. Finite
    unscaled cells receive neutral hatching; missing cells stay gray and cells
    outside ``inside`` stay white. Geographic grids use the supplied ticks/aspect.
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
    labels = _draw_overlays(ax, overlays, scale.units)
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
    if scale.status == "available":
        colorbar = fig.colorbar(
            mesh,
            ax=ax,
            shrink=0.48,
            pad=0.03,
            anchor=(0, 0),
            ticks=scale.ticks,
            extend="both",
            extendrect=True,
        )
        colorbar.ax.set_title(
            "(°C)" if scale.units == "degC" else "(mm yr⁻¹)", fontsize=6, pad=10
        )
    _place_point_labels(fig, ax, labels)
    return fig
