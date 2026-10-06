"""Selected reviewed diagnostic artists, fed by retained toolbox tables.

No lab input, page, runner, or output-path machinery is used here.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from textwrap import fill

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap, to_hex, to_rgb
from matplotlib.figure import Figure
from matplotlib.legend_handler import HandlerTuple
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from blueearth_cst.climate_analysis.diagnostics import SPI_SCALES, month_order

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


MISSING = "#a0a0a0"


QA = "#882255"


QA_RAMP = ("#882255", "#d6a5bf", "#e8f2f3")


SOURCE_STYLE = {"era5": ("#236b8e", "o"), "chirps": ("#bf6a3c", "o")}


FREE_SLOTS = (("#009E73", "o"), ("#CC79A7", "o"))


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


TREND_DASH = (0, (5, 2.5))


DODGE = 0.2


DIVERGING_CLASSES = 7


SPI_BOUNDS = [-2, -1.5, -1, 1, 1.5, 2]


LADDER = (1, 1.5, 2, 3, 4, 5, 6, 8)


UNITS = {
    "mm_month": "mm month⁻¹",
    "mm_year": "mm yr⁻¹",
    "mm_decade": "mm decade⁻¹",
    "days_year": "days yr⁻¹",
    "days_decade": "days decade⁻¹",
    "mm_day": "mm d⁻¹",
    "degc": "°C",
}


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


def source_styles(keys: Sequence[str]) -> dict[str, tuple[str, str]]:
    """Colour and marker per source id: registry first, then free slots in config order."""
    free_index = 0
    out = {}
    for k in keys:
        if k.lower() in SOURCE_STYLE:
            out[k] = SOURCE_STYLE[k.lower()]
        else:
            palette = plt.get_cmap("tab10")
            markers = ("s", "^", "D", "v", "P", "X")
            out[k] = (
                to_hex(palette(free_index % 10)),
                markers[(free_index // 10) % len(markers)],
            )
            free_index += 1
    return out


def tint(color: str) -> str:
    """Partial / incomplete: the identity colour 55 % toward white."""
    return to_hex(0.45 * np.array(to_rgb(color)) + 0.55)


def diverging_cmap() -> ListedColormap:
    return ListedColormap(
        plt.get_cmap("RdBu", DIVERGING_CLASSES)(np.arange(DIVERGING_CLASSES))
    )


def anomaly_bounds(values: np.ndarray) -> list[float]:
    """Symmetric class bounds for the anomaly calendar from pooled |anomaly| (figure-rules §3.4)."""
    a = np.abs(values[np.isfinite(values)])
    if not a.size:
        return [-1.0, 1.0]
    breaks: list[float] = []
    for q in np.quantile(a, [0.33, 0.67, 0.90]):
        if q <= 0:
            continue
        exp = 10.0 ** np.floor(np.log10(q))
        cand = np.array(LADDER + (10,)) * exp
        b = float(cand[np.argmin(np.abs(cand - q))])
        if not breaks or b > breaks[-1]:
            breaks.append(b)
    return [-b for b in reversed(breaks)] + breaks


def fmt_signed(x: float, digits: int = 0) -> str:
    return f"{x:+.{digits}f}".replace("-", "−")


def fmt_p(p: float) -> str:
    return "$p$ < 0.01" if p < 0.01 else f"$p$ = {p:.2f}"


def plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


@dataclass
class View:
    sources: list[str]
    labels: dict[str, str]
    styles: dict[str, tuple[str, str]]  # source -> (colour, marker)
    results: dict[str, dict]  # source -> restored plot-ready tables
    years: np.ndarray  # reporting years of the display period
    m0: int
    reference: tuple[int, int]
    wet_mm: float
    agreement: pd.DataFrame
    common_years: np.ndarray
    support: str = "basin mean"
    status: str = "prototype-tested, not scientifically qualified"
    anom_bounds: list[float] | None = None  # fixed per case
    max_missing_month: int = 0
    max_missing_year: int = 0

    def color(self, s: str) -> str:
        return self.styles[s][0]

    def marker(self, s: str) -> str:
        return self.styles[s][1]


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


def dodge(j: int, n: int) -> float:
    return (j - (n - 1) / 2) * DODGE


def ygrid(ax: plt.Axes) -> None:
    ax.grid(axis="y")


def year_ticks(ax: plt.Axes, years: np.ndarray, continuous: bool = False) -> None:
    """Display-period limits (never source availability) and a 2/5/10-year step."""
    if continuous:
        ax.set_xlim(years[0], years[-1] + 1)
    else:
        ax.set_xlim(years[0] - 0.5, years[-1] + 0.5)
    step = 10 if years.size > 35 else 5 if years.size > 12 else 2
    ax.set_xticks(np.arange(years[0] + (-years[0]) % step, years[-1] + 1, step))


def month_axis(ax: plt.Axes, m0: int) -> None:
    ax.set_xticks(np.arange(12), [MONTH_ABBR[m - 1] for m in month_order(m0)])
    ax.set_xlim(-0.5, 11.5)


def heatmap_months(ax: plt.Axes, m0: int) -> None:
    ax.set_ylim(12.5, 0.5)
    ax.set_yticks(range(1, 13), [MONTH_ABBR[m - 1] for m in month_order(m0)])


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


def id_handles(
    v: View, sources: Sequence[str] | None = None, line: bool = True, label=None
) -> list:
    sources = v.sources if sources is None else sources
    return [
        Line2D(
            [],
            [],
            color=v.color(s),
            marker=v.marker(s),
            ms=MS_LINE + 1,
            lw=LW_LINE if line else 0,
            label=label(s) if label else v.labels[s],
        )
        for s in sources
    ]


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


def identity_row(v: View, sources: Sequence[str] | None = None, **kw) -> list:
    """Identity entries, or none for a single source named by the page caption."""
    sources = v.sources if sources is None else sources
    return id_handles(v, sources, **kw) if len(sources) > 1 else []


def colourbar(
    fig: Figure, mesh, axes: list, label: str, ticks: Sequence[float], stack_mm: float
) -> None:
    cb = fig.colorbar(
        mesh,
        ax=axes,
        ticks=ticks,
        spacing="uniform",
        pad=0.02,
        shrink=0.68,
        anchor=(0.0, 0.0),
        aspect=max(stack_mm / 3.0, 8),
    )
    cb.ax.set_title(label, color=INK, fontsize=FS_TICK, pad=4)
    cb.outline.set_edgecolor(AXIS)
    cb.outline.set_linewidth(LW_EDGE)
    cb.ax.tick_params(
        labelsize=FS_TICK, labelcolor=MUTED, color=AXIS, width=LW_EDGE, length=2.5
    )


def add_caption(fig: Figure, text: str) -> None:
    """Reserve a small bottom band for a journal-style caption on a PNG copy."""
    width = max(75, int(fig.get_figwidth() * 21))
    wrapped = fill(text, width=width)
    lines = wrapped.count("\n") + 1
    extra_mm = 6 + 3.5 * lines
    fig.set_size_inches(fig.get_figwidth(), fig.get_figheight() + extra_mm * MM)
    fig.supxlabel(
        wrapped, x=0.04, ha="left", fontsize=FS_NOTE, color=MUTED, linespacing=1.3
    )


MISSING_KEY = Patch(facecolor=MISSING, edgecolor="none", label="Missing or unavailable")


def notice(text: str) -> str:
    """Plain availability notice; the exporter draws and records it."""
    return text


def coverage(v: View) -> Figure:
    n = len(v.sources)
    height = H_SINGLE if n == 1 else H_STACK2 if n == 2 else H_STACK2 + 48 * (n - 2)
    fig, axs = new_fig(height, n, 1, width_mm=W_FULL if n > 1 else W_MID, sharex=True)
    for i, (ax, s) in enumerate(zip(axs[:, 0], v.sources)):
        cls = (
            v.results[s]["coverage"]
            .reindex(columns=v.years)
            .to_numpy(dtype=float, copy=True)
        )
        cls[cls == 0] = np.nan
        ax.set_facecolor(MISSING)
        ax.pcolormesh(
            v.years,
            np.arange(1, 13),
            cls,
            cmap=ListedColormap([tint(v.color(s)), v.color(s)]),
            vmin=0.5,
            vmax=2.5,
            edgecolors="white",
            linewidth=0.25,
            rasterized=True,
        )
        heatmap_months(ax, v.m0)
        ax.tick_params(axis="y", labelsize=FS_NOTE)
        ax.set_title(f"{chr(97 + i)}) {v.labels[s]}" if n > 1 else "Coverage")
        heatmap_frame(ax)
    five_year_ticks(axs[-1, 0], v.years)
    full = tuple(Patch(facecolor=v.color(s), label="") for s in v.sources)
    part = tuple(Patch(facecolor=tint(v.color(s)), label="") for s in v.sources)
    tup = HandlerTuple(ndivide=None, pad=0)
    fig.legend(
        handles=[full, part, MISSING_KEY],
        labels=["Complete month", "Usable, tolerated gaps", "Missing or unusable"],
        loc="outside upper left",
        ncols=3,
        handler_map={tuple: tup},
    )
    return fig


def _climatology(v: View, key: str, ylabel: str, zero: bool) -> Figure:
    have = [s for s in v.sources if v.results[s][key] is not None]
    fig, axs = new_fig(H_SINGLE)
    ax = axs[0, 0]
    x = np.arange(12)
    top = 0.0
    for s in have:
        c = v.results[s][key]
        ax.fill_between(x, c["p10"], c["p90"], color=v.color(s), alpha=BAND_ALPHA, lw=0)
        ax.plot(
            x, c["mean"], color=v.color(s), lw=LW_MEAN, marker=v.marker(s), ms=MS_LINE
        )
        top = max(top, float(np.nanmax(c["p90"])))
    month_axis(ax, v.m0)
    if zero:
        ax.set_ylim(0, max(top * 1.08, 1))
    else:
        ax.margins(y=0.08)
    ax.set_ylabel(ylabel)
    ygrid(ax)
    spread = Patch(facecolor=MUTED, alpha=BAND_ALPHA, edgecolor="none")
    spread.set_label("10–90th percentile")
    mean = Line2D([], [], color=MUTED, lw=LW_MEAN, marker="o", ms=MS_LINE, label="Mean")
    top_legend(fig, identity_row(v, have), [mean, spread] if key == "tclim" else [])
    return fig


def seasonal(v: View) -> Figure:
    return _climatology(v, "clim", f"Precipitation ({UNITS['mm_month']})", zero=True)


def temperature(v: View) -> Figure | str:
    if not any(v.results[s]["tclim"] is not None for s in v.sources):
        return notice("No temperature variable is declared for the selected source(s).")
    return _climatology(v, "tclim", f"Temperature ({UNITS['degc']})", zero=False)


def timing(v: View) -> Figure:
    fig, axs = new_fig(H_SINGLE)
    ax = axs[0, 0]
    fr = (0.25, 0.5, 0.75)
    n = len(v.sources)
    for j, s in enumerate(v.sources):
        t = v.results[s]["timing"]
        for k, f in enumerate(fr):
            d = t[f].dropna()
            if d.empty:
                continue
            y = k + dodge(j, n)
            lo, med, hi = np.percentile(d, [25, 50, 75])
            mean = float(d.mean())
            ax.plot([d.min(), d.max()], [y, y], color=v.color(s), lw=LW_RANGE)
            ax.plot(
                [lo, hi], [y, y], color=v.color(s), lw=LW_IQR, solid_capstyle="butt"
            )
            ax.plot(med, y, marker="|", color="white", ms=LW_IQR, mew=1.0)
            ax.plot(
                mean,
                y,
                marker="o",
                color=v.color(s),
                markeredgecolor="white",
                markeredgewidth=0.5,
                ms=MS_POINT,
                zorder=3,
            )
            label_offset = 5 if j == 0 else -5
            ax.annotate(
                f"{mean:.0f}",
                (mean, y),
                xytext=(0, label_offset),
                textcoords="offset points",
                ha="center",
                va="bottom" if j == 0 else "top",
                fontsize=FS_NOTE,
                color=v.color(s),
            )
    start = date(2001, v.m0, 1)
    starts = [
        (date(2001 + (v.m0 + k - 1) // 12, (v.m0 + k - 1) % 12 + 1, 1) - start).days + 1
        for k in range(12)
    ]
    ax.set_xticks(
        starts, [(start + timedelta(days=d - 1)).strftime("%b") for d in starts]
    )
    ax.set_xlim(1, 366)
    top = ax.secondary_xaxis("top")
    top.set_xticks([1, 91, 182, 274, 366])
    top.tick_params(labelsize=FS_TICK, labelcolor=MUTED, color=AXIS)
    top.spines["top"].set_color(AXIS)
    ax.set_yticks(range(3), ["25 %", "50 %", "75 %"])
    ax.set_ylim(2.6, -0.6)
    ax.set_xlabel("Serial date reached")
    ax.set_ylabel("Annual share")
    ax.grid(axis="x")
    ax.tick_params(axis="y", length=0)
    identities = (
        [
            Line2D(
                [],
                [],
                color=v.color(s),
                marker="o",
                ms=MS_LINE + 1,
                lw=LW_LINE,
                label=v.labels[s],
            )
            for s in v.sources
        ]
        if n > 1
        else []
    )
    top_legend(fig, identities)
    return fig


def _stack(v: View):
    n = len(v.sources)
    height = H_SINGLE if n == 1 else H_STACK2 if n == 2 else H_STACK2 + 48 * (n - 2)
    fig, axs = new_fig(height, n, 1, width_mm=W_FULL if n > 1 else W_MID, sharex=True)
    return fig, axs, height


def anomaly(v: View) -> Figure:
    bounds = v.anom_bounds or [-1.0, 1.0]
    norm = BoundaryNorm(bounds, DIVERGING_CLASSES, extend="both")
    fig, axs, stack = _stack(v)
    mesh = None
    for i, (ax, s) in enumerate(zip(axs[:, 0], v.sources)):
        ax.set_facecolor(MISSING)
        heatmap_frame(ax)
        grid = v.results[s]["anomaly"].reindex(columns=v.years)
        mesh = ax.pcolormesh(
            v.years,
            np.arange(1, 13),
            grid,
            cmap=diverging_cmap(),
            norm=norm,
            edgecolors=GRID,
            linewidth=0.25,
            rasterized=True,
        )
        heatmap_months(ax, v.m0)
        if len(v.sources) > 1:
            ax.set_title(f"{chr(97 + i)}) {v.labels[s]}")
    axs[-1, 0].set_xlim(v.years[0] - 0.5, v.years[-1] + 0.5)
    five_year_ticks(axs[-1, 0], v.years)
    colourbar(fig, mesh, axs[:, 0].tolist(), "Precipitation\n(mm)", bounds, stack)
    fig.get_layout_engine().set(rect=(0, 0, 0.94, 1))
    fig.legend(handles=[MISSING_KEY], loc="outside upper left")
    return fig


def spi(v: View) -> Figure:
    norm = BoundaryNorm(SPI_BOUNDS, DIVERGING_CLASSES, extend="both")
    fig, axs, stack = _stack(v)
    mesh = None
    for i, (ax, s) in enumerate(zip(axs[:, 0], v.sources)):
        ax.set_facecolor(MISSING)
        heatmap_frame(ax)
        for row, k in enumerate(SPI_SCALES):
            ser = v.results[s]["spi"][k]
            x = (
                ser.index.year
                - (ser.index.month < v.m0).astype(int)
                + ((ser.index.month - v.m0) % 12 + 0.5) / 12
            )
            edges = np.append(x - 1 / 24, x[-1] + 1 / 24) if len(x) else x
            mesh = ax.pcolormesh(
                edges,
                [row - 0.5, row + 0.5],
                ser.to_numpy()[None, :],
                cmap=diverging_cmap(),
                norm=norm,
                rasterized=True,
            )
        ax.hlines(
            [0.5, 1.5], v.years[0], v.years[-1] + 1, colors=GRID, linewidth=LW_EDGE
        )
        ax.set_ylim(2.5, -0.5)
        ax.set_yticks(range(3), [f"SPI-{k}" for k in SPI_SCALES])
        if len(v.sources) > 1:
            ax.set_title(f"{chr(97 + i)}) {v.labels[s]}")
    axs[-1, 0].set_xlim(v.years[0], v.years[-1] + 1)
    five_year_ticks(axs[-1, 0], v.years, rotation=0)
    colourbar(fig, mesh, axs[:, 0].tolist(), "SPI", SPI_BOUNDS, stack)
    return fig


def drought_events(v: View) -> Figure:
    """Duration-severity scatter per SPI scale; tinted = censored by a gap or the record edge."""
    scales = (3, 12)
    fig, axs = new_fig(H_SIDE2, 1, 2, width_mm=W_FULL)
    for i, (ax, k) in enumerate(zip(axs[0], scales)):
        drawn = False
        for s in v.sources:
            ev = v.results[s]["drought"][k]
            if ev.empty:
                continue
            drawn = True
            done, cens = (
                ev[~ev["censored"].astype(bool)],
                ev[ev["censored"].astype(bool)],
            )
            ax.scatter(
                done["duration"],
                done["severity"],
                marker=v.marker(s),
                s=S_SCATTER,
                facecolor=v.color(s),
                edgecolor="white",
                linewidth=0.5,
                zorder=3,
            )
            ax.scatter(
                cens["duration"],
                cens["severity"],
                marker=v.marker(s),
                s=S_SCATTER,
                facecolor=tint(v.color(s)),
                edgecolor=v.color(s),
                linewidth=1.0,
                zorder=3,
            )
        if not drawn:
            ax.text(
                0.5,
                0.5,
                "no events",
                transform=ax.transAxes,
                ha="center",
                va="center",
                fontsize=FS_TICK,
                color=MUTED,
            )
        ax.set_title(f"{chr(97 + i)}) SPI-{k}")
        ax.set_xlabel("Duration (months)")
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
        ax.grid()
    axs[0, 0].set_ylabel("Severity (dimensionless)")
    top_legend(fig, identity_row(v, line=False))
    return fig


def spi_checks(v: View) -> Figure:
    """Shapiro-Wilk p-values of reference SPI per calendar month and scale, gamma vs Pearson III."""
    cmap = ListedColormap(list(QA_RAMP))
    norm = BoundaryNorm([0, 0.01, 0.05, 1], cmap.N)
    rows = [(s, d) for s in v.sources for d in ("gamma", "pearson3")]
    fig, axs = new_fig(
        14 + 30 * len(rows),
        len(rows),
        1,
        width_mm=W_MID if len(rows) == 2 else W_FULL,
        sharex=True,
    )
    for ax, (s, d) in zip(axs[:, 0], rows):
        tab = np.array(
            [v.results[s]["spi_checks"][k][f"sw_{d}"].to_numpy() for k in SPI_SCALES],
            dtype=float,
        )
        ax.set_facecolor(MISSING)
        ax.pcolormesh(
            np.arange(13) - 0.5,
            np.arange(4) - 0.5,
            tab,
            cmap=cmap,
            norm=norm,
            edgecolors="white",
            linewidth=0.8,
        )
        for (r, c), val in np.ndenumerate(tab):
            if np.isfinite(val):
                ax.text(
                    c,
                    r,
                    f"{val:.2f}" if val >= 0.01 else "<0.01",
                    ha="center",
                    va="center",
                    fontsize=FS_NOTE,
                    color="white" if val < 0.01 else INK,
                )
        ax.set_ylim(2.5, -0.5)
        ax.set_yticks(range(3), [f"SPI-{k}" for k in SPI_SCALES])
        n_fail = int((tab < 0.05).sum())
        extra = ""
        if d == "pearson3":
            hits = sum(
                int(v.results[s]["spi_checks"][k]["p3_bound_hits"].sum())
                for k in SPI_SCALES
            )
            extra = f" · {plural(hits, 'month')} beyond fit bounds"
        name = "gamma" if d == "gamma" else "Pearson III"
        ax.set_title(f"{v.labels[s]} · {name} · {n_fail}/36 with $p$ < 0.05{extra}")
        heatmap_frame(ax)
    month_axis(axs[-1, 0], v.m0)
    keys = [
        Patch(facecolor=QA_RAMP[0], label="$p$ < 0.01"),
        Patch(facecolor=QA_RAMP[1], label="0.01 ≤ $p$ < 0.05"),
        Patch(facecolor=QA_RAMP[2], label="$p$ ≥ 0.05 (no evidence of misfit)"),
    ]
    top_legend(fig, keys)
    return fig


EXTREME_LABELS = {
    "Rx1day": "Rx1day (mm)",
    "Rx5day": "Rx5day (mm)",
    "SDII": f"SDII ({UNITS['mm_day']})",
    "Wet days": f"Wet days ({UNITS['days_year']})",
}


def extremes(metric: str) -> Callable[[View], Figure]:
    def chart(v: View) -> Figure:
        fig, axs = new_fig(H_SINGLE)
        ax = axs[0, 0]
        for s in v.sources:
            y = v.results[s]["extremes"][metric].reindex(v.years)
            ax.plot(
                v.years, y, color=v.color(s), lw=LW_LINE, marker=v.marker(s), ms=MS_LINE
            )  # NaN breaks the line
        ax.set_ylabel(EXTREME_LABELS[metric])
        ax.margins(y=0.08)
        year_ticks(ax, v.years)
        ygrid(ax)
        top_legend(fig, identity_row(v))
        return fig

    return chart


def spell(v: View) -> Figure:
    fig, axs = new_fig(H_SINGLE)
    ax = axs[0, 0]
    xmax = 2
    for s in v.sources:
        ex = v.results[s]["spells"]
        ex = ex[ex >= 0.002]
        if ex.empty:
            continue
        ax.plot(
            ex.index,
            ex.to_numpy(),
            color=v.color(s),
            lw=LW_LINE,
            marker=v.marker(s),
            ms=MS_LINE,
            markevery=max(1, ex.size // 12),
        )  # shape stays as identity without crowding the curve
        xmax = max(xmax, int(ex.index.max()))
    ax.set_yscale("log")
    ticks = [0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1]
    ax.set_yticks(ticks, [f"{t:g}" for t in ticks])
    ax.minorticks_off()
    ax.set_ylim(0.0015, 1.2)
    ax.set_xlim(0.5, xmax + 0.5)
    ax.set_xlabel("Dry-spell length (days)")
    ax.set_ylabel("Exceedance P (log)")
    ax.grid()
    top_legend(fig, identity_row(v))
    return fig


def acf(v: View) -> Figure:
    fig, axs = new_fig(H_SINGLE)
    ax = axs[0, 0]
    n = len(v.sources)
    rmax = 0.0
    for j, s in enumerate(v.sources):
        a = v.results[s]["acf"]
        lags = a.index.to_numpy() + dodge(j, n)
        ax.vlines(lags, 0, a["r"], color=v.color(s), lw=LW_STEM)
        ax.plot(lags, a["r"], lw=0, marker=v.marker(s), color=v.color(s), ms=MS_LINE)
        finite = a["r"].dropna()
        if not finite.empty:
            rmax = max(rmax, float(np.abs(finite).max()))
    lim = max(0.5, np.ceil(rmax * 10) / 10)
    ax.axhline(0, color=MUTED, lw=LW_REF)
    ax.set_xticks(range(1, 13))
    ax.set_xlim(0.4, 12.6)
    ax.set_ylim(-lim, lim)
    ax.set_xlabel("Lag (months)")
    ax.set_ylabel("Autocorrelation (r)")
    ygrid(ax)

    if n > 1:
        top_legend(fig, identity_row(v, line=False))
    return fig


TREND_METRICS = (
    ("total", "Annual precipitation", UNITS["mm_decade"]),
    ("wet_days", "Wet days", UNITS["days_decade"]),
    ("Rx1day", "Rx1day", UNITS["mm_decade"]),
)


def slopes(v: View) -> Figure:
    n = len(v.sources)
    fig, axs = new_fig(H_ROW3, 1, 3, width_mm=W_FULL)
    for i, (ax, (key, title, unit)) in enumerate(zip(axs[0], TREND_METRICS)):
        span = 0.0
        for k, s in enumerate(v.sources):
            t = v.results[s]["trends"][key]
            if not np.isfinite(t["slope"]):
                continue
            sig = t["p"] < 0.05
            ax.errorbar(
                t["slope"],
                k,
                xerr=[[t["slope"] - t["lo"]], [t["hi"] - t["slope"]]],
                fmt=v.marker(s),
                color=v.color(s),
                mfc=v.color(s) if sig else "white",
                mec=v.color(s),
                mew=1.0,
                ms=MS_POINT,
                lw=LW_LINE,
                capsize=2,
                zorder=3,
            )
            span = max(span, abs(t["lo"]), abs(t["hi"]))
        ax.axvline(0, color=MUTED, lw=LW_REF, zorder=1)
        span = span * 1.15 or 1
        ax.set_xlim(-span, span)
        ax.set_ylim(n - 0.4, -0.75)
        ax.set_yticks([])
        ax.set_title(f"{chr(97 + i)}) {title}")
        ax.set_xlabel(f"Trend ({unit})")
        ax.locator_params(axis="x", nbins=6)
        ax.grid(axis="x", alpha=0.5)
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color(BOUNDARY)
            spine.set_linewidth(LW_BOUNDARY)
        ax.tick_params(axis="y", length=0)
    top_legend(fig, identity_row(v, line=False))
    for ax in axs[0]:
        ax.title.set_fontsize(FS_NOTE)
        ax.xaxis.label.set_fontsize(FS_NOTE)
    return fig


def series(v: View) -> Figure:
    fig, axs = new_fig(H_SINGLE)
    ax = axs[0, 0]
    labels = []
    for s in v.sources:
        y = v.results[s]["annual"]["total"].reindex(v.years)
        ax.plot(
            v.years, y, color=v.color(s), lw=LW_LINE, marker=v.marker(s), ms=MS_LINE
        )
        t = v.results[s]["trends"]["total"]
        ok = y.dropna().index.to_numpy()
        if np.isfinite(t["slope"]) and ok.size:
            span = np.array([ok[0], ok[-1]], dtype=float)
            line = t["intercept"] + t["slope"] / 10 * span
            ax.plot(span, line, color=v.color(s), lw=LW_REF, ls=TREND_DASH, alpha=0.6)
            labels.append(
                [line[-1], f"{fmt_signed(t['slope'])} {UNITS['mm_decade']}", v.color(s)]
            )
    year_ticks(ax, v.years)
    ax.margins(y=0.08)
    lo, hi = ax.get_ylim()
    gap = (hi - lo) * 0.07  # keep end labels from overlapping
    labels.sort(key=lambda r: r[0])
    for i in range(1, len(labels)):
        labels[i][0] = max(labels[i][0], labels[i - 1][0] + gap)
    for y, text, color in labels:
        ax.annotate(
            text,
            (v.years[-1] - 0.4, y),
            xytext=(-3, 0),
            textcoords="offset points",
            ha="right",
            va="center",
            fontsize=FS_TICK,
            color=color,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.88, "pad": 1.2},
        )
    ax.set_ylabel(f"Annual precipitation ({UNITS['mm_year']})")
    top_legend(fig, identity_row(v))
    ygrid(ax)
    return fig


def sensitivity(v: View) -> Figure:
    """Sen slope with dependence-adjusted interval for each start year (end fixed); filled = p < 0.05."""
    fig, axs = new_fig(H_SIDE2, 1, 2, width_mm=W_FULL, sharex=True)
    for i, (ax, (key, title)) in enumerate(
        zip(axs[0], (("total", "Annual precipitation"), ("Rx1day", "Rx1day")))
    ):
        for s in v.sources:
            t = v.results[s]["sensitivity"][key]
            if t.empty:
                continue
            x = t.index.to_numpy()
            c = v.color(s)
            ax.plot(x, t["lo"], color=c, lw=LW_EDGE)
            ax.plot(x, t["hi"], color=c, lw=LW_EDGE)
            ax.plot(x, t["slope"], color=c, lw=LW_LINE)
            sig = (t["p"] < 0.05).to_numpy()
            ax.plot(
                x[sig],
                t["slope"][sig],
                lw=0,
                marker=v.marker(s),
                ms=MS_LINE,
                color=c,
                zorder=3,
            )
            ax.plot(
                x[~sig],
                t["slope"][~sig],
                lw=0,
                marker=v.marker(s),
                ms=MS_LINE,
                mfc="white",
                mec=c,
                mew=1.0,
                zorder=3,
            )
        ax.axhline(0, color=MUTED, lw=LW_REF)
        ax.set_title(f"{chr(97 + i)}) {title}")
        ax.set_ylabel(f"Trend ({UNITS['mm_decade']})")
        ax.set_xlabel(f"Start year (end {v.years[-1]})")
        ygrid(ax)
    sig = [
        Line2D(
            [], [], lw=0, marker="o", ms=MS_LINE + 1, color=MUTED, label="$p$ < 0.05"
        ),
        Line2D(
            [],
            [],
            lw=0,
            marker="o",
            ms=MS_LINE + 1,
            mfc="white",
            mec=MUTED,
            mew=1.0,
            label="$p$ ≥ 0.05",
        ),
    ]
    edge = Line2D([], [], color=MUTED, lw=LW_EDGE, label="95 % interval")
    top_legend(fig, identity_row(v), sig + [edge])
    return fig


def pt_scatter(v: View) -> Figure | str:
    """Seasonal P anomaly (%) against T anomaly; P and T sources are labelled separately."""
    have = [
        s
        for s in v.sources
        if v.results[s]["pt"] is not None and not v.results[s]["pt"].empty
    ]
    if not have:
        return notice(
            "No temperature variable is declared in this case, so the P–T scatter is unavailable."
        )
    # Own y-scale per season: dry-season totals are small, so their % anomalies are much larger.
    fig, axs = new_fig(H_GRID4, 2, 2, width_mm=W_FULL, sharex=True)
    xlim = (
        max(float(np.nanmax(np.abs(v.results[s]["pt"]["t_anom"]))) for s in have) * 1.08
    )
    for i, (ax, season) in enumerate(zip(axs.flat, ("DJF", "MAM", "JJA", "SON"))):
        for s in have:
            d = v.results[s]["pt"]
            d = d[d["season"] == season]
            ax.scatter(
                d["t_anom"],
                d["p_anom_pct"],
                s=S_SCATTER,
                marker=v.marker(s),
                color=v.color(s),
                edgecolor="white",
                linewidth=0.5,
                zorder=3,
            )
        ax.axhline(0, color=MUTED, lw=LW_REF)
        ax.axvline(0, color=MUTED, lw=LW_REF)
        ax.set_xlim(-xlim, xlim)
        ax.set_title(f"{chr(97 + i)}) {season}")
        ax.grid()
    for ax in axs[-1]:
        ax.set_xlabel(f"Temperature anomaly ({UNITS['degc']})")
    fig.supylabel("Precipitation anomaly (%)", fontsize=FS_LABEL, color=INK)
    top_legend(
        fig, identity_row(v, have, line=False, label=lambda s: f"P: {v.labels[s]}")
    )
    return fig


CHARTS: dict[str, Callable[[View], Figure | str]] = {
    "coverage": coverage,
    "seasonal": seasonal,
    "temperature": temperature,
    "timing": timing,
    "anomaly": anomaly,
    "spi": spi,
    "drought-events": drought_events,
    **{f"extreme-{m}": extremes(m) for m in EXTREME_LABELS},
    "spell": spell,
    "acf": acf,
    "slopes": slopes,
    "series": series,
    "pt": pt_scatter,
    "spi-checks": spi_checks,
    "sensitivity": sensitivity,
}
