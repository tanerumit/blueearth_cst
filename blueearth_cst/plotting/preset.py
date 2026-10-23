"""Style presets for the shared plotting core.

The core draws with whichever preset is active. ``use_preset`` scopes one around
rendering; outside any scope the neutral built-in default applies. Workflow
presets live with their workflows and are passed in, never loaded here.
"""

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

import matplotlib.pyplot as plt


@dataclass(frozen=True)
class Preset:
    """Physical sizes (mm), fonts and line weights (pt), colours and rcParams.

    Keys: widths ``col1/panel/mid/full``; heights ``single/stack2/side2/row3/grid4``;
    padding ``x/y``; fonts ``label/tick/note``; colors ``ink/muted/axis/grid/boundary``;
    lines ``line/mean/ref/edge/range/iqr/stem/boundary``; markers ``line/point/scatter``.
    """

    widths: Mapping[str, float]
    heights: Mapping[str, float]
    padding: Mapping[str, float]
    fonts: Mapping[str, float]
    colors: Mapping[str, str]
    lines: Mapping[str, float]
    markers: Mapping[str, float]
    band_alpha: float
    label_box: Mapping[str, Any]
    rcparams: Mapping[str, Any]


def chart_rcparams(
    colors: Mapping[str, str], fonts: Mapping[str, float], lines: Mapping[str, float]
) -> dict[str, Any]:
    """rcParams that make Matplotlib's own artists agree with a preset's tokens."""
    return {
        "font.size": fonts["label"],
        "axes.titlesize": fonts["label"],
        "axes.titlecolor": colors["ink"],
        "axes.labelsize": fonts["label"],
        "axes.labelcolor": colors["ink"],
        "axes.edgecolor": colors["boundary"],
        "axes.linewidth": lines["boundary"],
        "xtick.color": colors["axis"],
        "ytick.color": colors["axis"],
        "xtick.labelcolor": colors["muted"],
        "ytick.labelcolor": colors["muted"],
        "xtick.labelsize": fonts["tick"],
        "ytick.labelsize": fonts["tick"],
        "xtick.major.width": lines["edge"],
        "ytick.major.width": lines["edge"],
        "grid.color": colors["grid"],
        "grid.linewidth": lines["edge"],
        "legend.fontsize": fonts["tick"],
        "legend.title_fontsize": fonts["tick"],
        "legend.labelcolor": colors["ink"],
    }


_NEUTRAL_COLORS = {
    "ink": "#222222",
    "muted": "#555555",
    "axis": "#808080",
    "grid": "#e5e5e5",
    "boundary": "#bfbfbf",
}
_NEUTRAL_FONTS = {"label": 7, "tick": 6, "note": 6}
_NEUTRAL_LINES = {
    "line": 1.2,
    "mean": 1.5,
    "ref": 0.8,
    "edge": 0.6,
    "range": 0.8,
    "iqr": 3.0,
    "stem": 1.6,
    "boundary": 0.9,
}

NEUTRAL = Preset(
    widths={"col1": 88.0, "panel": 120.0, "mid": 140.0, "full": 180.0},
    heights={
        "single": 80.0,
        "stack2": 110.0,
        "side2": 86.0,
        "row3": 80.0,
        "grid4": 142.0,
    },
    padding={"x": 4.0, "y": 3.0},
    fonts=_NEUTRAL_FONTS,
    colors=_NEUTRAL_COLORS,
    lines=_NEUTRAL_LINES,
    markers={"line": 3.0, "point": 4.5, "scatter": 16},
    band_alpha=0.18,
    label_box={"facecolor": "white", "edgecolor": "none", "alpha": 0.88, "pad": 1.2},
    rcparams={
        "axes.axisbelow": True,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "legend.frameon": False,
        **chart_rcparams(_NEUTRAL_COLORS, _NEUTRAL_FONTS, _NEUTRAL_LINES),
        "savefig.dpi": 300,
    },
)

_ACTIVE: ContextVar[Preset | None] = ContextVar("plotting_preset", default=None)


def active() -> Preset:
    """The preset of the innermost ``use_preset`` scope, else ``NEUTRAL``."""
    return _ACTIVE.get() or NEUTRAL


@contextmanager
def use_preset(preset: Preset, *, rcparams: bool = True) -> Iterator[Preset]:
    """Draw with ``preset`` inside the block; with ``rcparams`` also apply its rcParams.

    ``rcparams=False`` suits callers that own their Matplotlib settings and need
    only the preset's tokens, for example a caption added to a cartographic map.
    """
    token = _ACTIVE.set(preset)
    try:
        if rcparams:
            with plt.rc_context(dict(preset.rcparams)):
                yield preset
        else:
            yield preset
    finally:
        _ACTIVE.reset(token)
