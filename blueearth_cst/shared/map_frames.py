"""Adapter helpers that turn workflow geometry into ``prepared_maps`` inputs.

One home for what every map adapter (WF0/WF1 climate maps, the spatial set)
prepares the same way: the basin-zoom frame, regular-grid cell edges and the
overlay features, including the merged divide linework.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from blueearth_cst.plotting.prepared_maps import MapFrame

#: Coordinate names tried for the horizontal and vertical raster axes.
_X_NAMES, _Y_NAMES = ("longitude", "lon", "x"), ("latitude", "lat", "y")


def frame_from_extent(extent: Sequence[float]) -> MapFrame:
    """A geographic frame with rounded ticks and midpoint-latitude aspect."""
    from blueearth_cst.shared.map_reference import geographic_ticks

    west, east, south, north = (float(value) for value in extent)
    return MapFrame(
        (west, east, south, north),
        geographic_ticks(west, east),
        geographic_ticks(south, north),
        1 / math.cos(math.radians((south + north) / 2)),
    )


def basin_frame(basins, within: Sequence[float] | None = None) -> MapFrame:
    """The basin bounds with spatial-map padding, as every map zooms to them.

    ``within`` (west, east, south, north) clips the padded view to a raster's
    outer cell edges, so a grid stored close to the basin fills the frame
    instead of leaving blank padding.
    """
    from blueearth_cst.shared.map_classes import extent_from_layer

    west, east, south, north = extent_from_layer(basins)
    if within is not None:
        w, e, s, n = (float(value) for value in within)
        clipped = (max(west, w), min(east, e), max(south, s), min(north, n))
        if clipped[0] < clipped[1] and clipped[2] < clipped[3]:
            west, east, south, north = clipped
    return frame_from_extent((west, east, south, north))


def grid_edges(field) -> tuple[np.ndarray, np.ndarray]:
    """Cell-edge arrays (one longer than the centres) of a regular 2-D grid."""

    def edges(name_options):
        name = next(name for name in name_options if name in field.coords)
        centres = np.asarray(field[name].values, dtype=float)
        step = centres[1] - centres[0] if centres.size > 1 else 1.0
        return np.concatenate([centres - step / 2, [centres[-1] + step / 2]])

    return edges(_X_NAMES), edges(_Y_NAMES)


def as_lat_lon(field):
    """``field`` with its axes ordered (vertical, horizontal)."""
    y = next(name for name in _Y_NAMES if name in field.dims)
    x = next(name for name in _X_NAMES if name in field.dims)
    return field.transpose(y, x)


def features(layer) -> list[dict[str, Any]]:
    """A GeoDataFrame's features as GeoJSON mappings in EPSG:4326."""
    if layer is None or len(layer) == 0:
        return []
    if layer.crs is not None and layer.crs.to_epsg() != 4326:
        layer = layer.to_crs(4326)
    return json.loads(layer.to_json())["features"]


def overlay_features(
    layers: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, list]:
    """The template's overlay keys from loaded features.

    Subbasin polygons become one merged ``divides`` linework: drawing each ring
    dashed lays every shared edge down twice, and the interleaved dashes render
    those edges solid.
    """
    out = {key: list(value) for key, value in layers.items() if key != "subbasins"}
    subbasins = layers.get("subbasins") or []
    if subbasins:
        from shapely import line_merge, union_all
        from shapely.geometry import mapping, shape

        rings = union_all([shape(f["geometry"]).boundary for f in subbasins])
        out["divides"] = [
            {
                "type": "Feature",
                "geometry": mapping(line_merge(rings)),
                "properties": {},
            }
        ]
    return out
