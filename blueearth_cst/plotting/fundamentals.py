"""Shared Matplotlib drawing fundamentals and the reviewed CST style preset.

Backend selection belongs to callers; STYLE is a shared mutable dictionary.
"""

from collections.abc import Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.transforms import Affine2D, Bbox

W_COL1, W_PANEL, W_MID, W_FULL = 88.0, 120.0, 140.0, 180.0


MM = 1 / 25.4


H_SINGLE, H_STACK2, H_SIDE2, H_ROW3, H_GRID4 = 80.0, 110.0, 86.0, 80.0, 142.0


OUTER_PAD_X_MM, OUTER_PAD_Y_MM = 4.0, 3.0


FS_LABEL, FS_TICK, FS_NOTE = 7, 6, 6


INK = "#17303c"


MUTED = "#536875"


AXIS = "#82939b"


GRID = "#e6edef"


BOUNDARY = "#c6d2d8"


LW_LINE, LW_MEAN, LW_REF, LW_EDGE, LW_RANGE, LW_IQR, LW_STEM = (
    1.2,
    1.5,
    0.8,
    0.6,
    0.8,
    3.0,
    1.6,
)


LW_BOUNDARY = 0.9


MS_LINE, MS_POINT, S_SCATTER = 3.0, 4.5, 16


BAND_ALPHA = 0.18


LABEL_BOX = {"facecolor": "white", "edgecolor": "none", "alpha": 0.88, "pad": 1.2}


MONTH_ABBR = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)


STYLE = {
    "font.family": "DejaVu Sans",
    "mathtext.fontset": "dejavusans",
    "font.size": FS_LABEL,
    "axes.titlesize": FS_LABEL,
    "axes.titleweight": "normal",
    "axes.titlelocation": "left",
    "axes.titlecolor": INK,
    "axes.labelsize": FS_LABEL,
    "axes.labelcolor": INK,
    "axes.edgecolor": BOUNDARY,
    "axes.linewidth": LW_BOUNDARY,
    "axes.spines.top": True,
    "axes.spines.right": True,
    "axes.axisbelow": True,
    "xtick.color": AXIS,
    "ytick.color": AXIS,
    "xtick.labelcolor": MUTED,
    "ytick.labelcolor": MUTED,
    "xtick.labelsize": FS_TICK,
    "ytick.labelsize": FS_TICK,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "xtick.major.width": LW_EDGE,
    "ytick.major.width": LW_EDGE,
    "grid.color": GRID,
    "grid.linewidth": LW_EDGE,
    "legend.frameon": False,
    "legend.fontsize": FS_TICK,
    "legend.title_fontsize": FS_TICK,
    "legend.labelcolor": INK,
    "legend.handlelength": 2.0,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.dpi": 600,
}


def new_fig(
    height_mm: float, nrows: int = 1, ncols: int = 1, width_mm: float = W_MID, **kw
):
    """Constrained-layout figure at its printed size."""
    fig, axs = plt.subplots(
        nrows,
        ncols,
        figsize=(width_mm * MM, height_mm * MM),
        layout="constrained",
        squeeze=False,
        **kw,
    )
    fig.get_layout_engine().set(w_pad=OUTER_PAD_X_MM * MM, h_pad=OUTER_PAD_Y_MM * MM)
    return fig, axs


def ygrid(ax: plt.Axes) -> None:
    ax.grid(axis="y")


def year_ticks(ax: plt.Axes, years: np.ndarray, continuous: bool = False) -> None:
    """Sparse year labels with finer ticks, thinning ticks for long records."""
    if continuous:
        ax.set_xlim(years[0], years[-1] + 1)
    else:
        ax.set_xlim(years[0] - 0.5, years[-1] + 0.5)
    step = 10 if years.size > 35 else 5 if years.size > 12 else 2
    major = np.arange(years[0] + (-years[0]) % step, years[-1] + 1, step)
    ax.set_xticks(major)
    tick_step = max(1, int(np.ceil((years[-1] - years[0]) / 60)))
    ticks = np.arange(years[0] + (-years[0]) % tick_step, years[-1] + 1, tick_step)
    ax.set_xticks(np.setdiff1d(ticks, major), minor=True)
    ax.tick_params(axis="x", which="major", length=3, width=LW_EDGE, color=AXIS)
    ax.tick_params(axis="x", which="minor", length=2, width=LW_EDGE, color=AXIS)


def five_year_ticks(ax: plt.Axes, years: np.ndarray, rotation: int = 0) -> None:
    """Label five-year marks and show intervening years as short minor ticks."""
    major = np.arange(years[0] + (-years[0]) % 5, years[-1] + 1, 5)
    ax.set_xticks(major)
    ax.set_xticks(np.setdiff1d(years, major), minor=True)
    ax.tick_params(
        axis="x",
        which="major",
        length=3,
        width=LW_EDGE,
        color=AXIS,
        labelrotation=rotation,
        labelsize=FS_TICK,
    )
    ax.tick_params(axis="x", which="minor", length=2, width=LW_EDGE, color=AXIS)


def heatmap_frame(ax: plt.Axes) -> None:
    """Keep the shared soft plot boundary while suppressing heatmap tick marks."""
    ax.tick_params(length=0)


def blank() -> Line2D:
    return Line2D([], [], lw=0, alpha=0, label=" ")


def top_legend(fig: Figure, *rows: list, handler_map: dict | None = None) -> None:
    """Outside upper-left figure legend; each row stays a row (no column-major interleave)."""
    rows = [r for r in rows if r]
    if not rows:
        return
    ncols = max(len(r) for r in rows)
    grid = [r + [blank()] * (ncols - len(r)) for r in rows]
    handles = [grid[i][j] for j in range(ncols) for i in range(len(grid))]
    fig.legend(
        handles=handles,
        loc="outside upper left",
        ncols=ncols,
        handler_map=handler_map,
        columnspacing=1.2,
        handletextpad=0.5,
    )


def colourbar(
    fig: Figure,
    mesh,
    axes: list,
    label: str,
    ticks: Sequence[float],
    stack_mm: float,
    shrink: float = 0.68,
) -> None:
    cb = fig.colorbar(
        mesh,
        ax=axes,
        ticks=ticks,
        spacing="uniform",
        extendrect=True,
        pad=0.02,
        shrink=shrink,
        anchor=(0.0, 0.0),
        aspect=max(stack_mm / 3.0, 8),
    )
    cb.ax.set_title(label, color=INK, fontsize=FS_TICK, pad=10)
    cb.outline.set_edgecolor(AXIS)
    cb.outline.set_linewidth(LW_EDGE)
    cb.ax.tick_params(
        labelsize=FS_TICK, labelcolor=MUTED, color=AXIS, width=LW_EDGE, length=2.5
    )


def add_caption(
    fig: Figure,
    text: str,
    *,
    above: bool = False,
    crop: bool = False,
    pad_inches: float = 0,
) -> None:
    """Add a caption below, or title above, without changing artists' physical size.

    Call after drawing the ordinary product and before its final captioned export.
    Layout and axes locators are frozen at the configured save DPI: the caption
    extends the canvas rather than asking constrained layout to resize the panels.
    Export at that same DPI; further figure resizing or artist edits need a new
    ordinary figure rather than rerunning layout on this finalized copy.
    ``above=True`` uses the label font and a band above the original canvas.
    ``crop=True`` freezes the tight artist bounds plus ``pad_inches`` before
    adding the band; export that finalized canvas without another tight crop.
    """
    original_dpi = fig.dpi
    try:
        export_dpi = mpl.rcParams["savefig.dpi"]
        if export_dpi != "figure":
            fig.set_dpi(export_dpi)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        old_width, old_height = fig.get_size_inches()
        bounds = (
            fig.get_tightbbox(renderer).padded(pad_inches)
            if crop
            else Bbox.from_bounds(0, 0, old_width, old_height)
        )
        width, height = bounds.width, bounds.height
        axes = [(ax, ax.get_position().frozen()) for ax in fig.axes]
        legends = [*fig.legends]
        legends.extend(ax.get_legend() for ax in fig.axes if ax.get_legend())
        anchors = [
            (
                legend,
                legend.get_bbox_to_anchor()
                .transformed(fig.dpi_scale_trans.inverted())
                .frozen(),
            )
            for legend in legends
        ]
        left = (
            min((box.x0 for _, box in axes), default=0.04) * old_width - bounds.x0
        ) / width
        right = (
            max((box.x1 for _, box in axes), default=0.96) * old_width - bounds.x0
        ) / width
        caption = fig.text(
            left,
            0,
            "",
            ha="left",
            va="bottom",
            fontsize=FS_LABEL if above else FS_NOTE,
            color=INK if above else MUTED,
            linespacing=1.3,
        )
        available = (right - left) * width * fig.dpi
        lines, line = [], ""
        for word in text.split():
            trial = f"{line} {word}".strip()
            caption.set_text(trial)
            if caption.get_window_extent(renderer).width <= available:
                line = trial
                continue
            if line:
                lines.append(line)
                line = ""
            # Like textwrap.fill, break a token that cannot fit on its own line.
            for character in word:
                trial = line + character
                caption.set_text(trial)
                if line and caption.get_window_extent(renderer).width > available:
                    lines.append(line.rstrip())
                    line = character
                else:
                    line = trial
        lines.append(line)
        caption.set_text("\n".join(lines))
        extra = caption.get_window_extent(renderer).height / fig.dpi + 6 * MM
        fig.set_layout_engine("none")
        fig.set_size_inches(width, height + extra)
        mapping = (
            Affine2D()
            .scale(old_width / width, old_height / (height + extra))
            .translate(
                -bounds.x0 / width,
                (-bounds.y0 + (0 if above else extra)) / (height + extra),
            )
        )
        for ax, box in axes:
            ax.set_axes_locator(None)
            ax.set_position(mapping.transform_bbox(box))
        for legend, box in anchors:
            legend.set_bbox_to_anchor(
                Bbox.from_bounds(
                    box.x0 - bounds.x0,
                    box.y0 - bounds.y0 + (0 if above else extra),
                    box.width,
                    box.height,
                ),
                fig.dpi_scale_trans,
            )
        for artist in fig.get_children():
            if (
                artist is caption
                or artist in fig.axes
                or artist in fig.legends
                or artist is fig.patch
            ):
                continue
            transform = artist.get_transform()
            if transform.contains_branch(fig.transFigure):
                artist.set_transform(
                    transform - fig.transFigure + mapping + fig.transFigure
                )
        caption.set_position(
            (left, (height + 3 * MM if above else 3 * MM) / (height + extra))
        )
    finally:
        fig.set_dpi(original_dpi)


def inside_legend(
    fig: Figure,
    ax: plt.Axes,
    handles: list,
    bands: Sequence = (),
    lines: Sequence = (),
) -> None:
    """Stack legend entries on translucent white in the less occupied top corner."""
    if not handles:
        return
    legend = ax.legend(
        handles=handles,
        loc="upper right",
        ncols=1,
        frameon=True,
        facecolor="white",
        edgecolor="none",
        framealpha=0.88,
        borderpad=0.6,
        labelspacing=0.5,
        handletextpad=0.5,
    )
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    scores = []
    for location in ("upper right", "upper left"):
        legend.set_loc(location)
        box = legend.get_window_extent(renderer)
        xx, yy = np.meshgrid(
            np.linspace(box.x0, box.x1, 30), np.linspace(box.y0, box.y1, 20)
        )
        points = np.column_stack((xx.ravel(), yy.ravel()))
        overlap = 0
        for band in bands:
            for path in band.get_paths():
                overlap += path.contains_points(points, band.get_transform()).sum()
        for line in lines:
            path = line.get_transform().transform_path(line.get_path())
            if path.intersects_bbox(box, filled=False):
                overlap += points.shape[0]
        for collection in ax.collections:
            offsets = collection.get_offsets()
            if offsets.size:
                positions = collection.get_offset_transform().transform(offsets)
                overlap += (
                    sum(box.contains(x, y) for x, y in positions) * points.shape[0]
                )
        scores.append((overlap, location))
    legend.set_loc(min(scores, key=lambda item: item[0])[1])
