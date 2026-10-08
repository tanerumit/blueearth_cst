"""WF2 suite artists: plot prepared tables, never recompute climate statistics."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import date
import zlib
from matplotlib.patches import Rectangle, Patch
from matplotlib.legend_handler import HandlerTuple
from matplotlib.colors import to_rgb
from matplotlib.lines import Line2D

from blueearth_cst.climate_analysis.diagnostic_figures import (
    FS_NOTE,
    H_SIDE2,
    H_SINGLE,
    H_STACK2,
    INK,
    LW_IQR,
    LW_RANGE,
    LW_REF,
    MUTED,
    STYLE,
    W_FULL,
    W_MID,
    inside_legend,
    new_fig,
    year_ticks,
    ygrid,
)
from blueearth_cst.projections.projection_figures import SCENARIO_COLORS

STRIP_PERIODS = ("annual", "DJF", "MAM", "JJA", "SON")
MONTHS = (
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


def _color(scenario):
    return SCENARIO_COLORS.get(scenario, MUTED)


def _label(scenario):
    return (
        f"SSP{scenario[3]}-{int(scenario[4:]) / 10:.1f}"
        if scenario in SCENARIO_COLORS
        else scenario
    )


def _scenarios(table, order=None):
    found = set(table.scenario.dropna())
    return [s for s in (order or SCENARIO_COLORS) if s in found] + sorted(
        found - set(order or SCENARIO_COLORS)
    )


def _panels(periods, ylabel):
    fig, axes = new_fig(H_SINGLE, ncols=len(periods), width_mm=W_FULL, sharey=True)
    for i, (ax, period) in enumerate(zip(axes.flat, periods, strict=True)):
        ax.text(
            0.02,
            1.02,
            f"{chr(97 + i)})",
            transform=ax.transAxes,
            va="bottom",
            color=INK,
            fontsize=FS_NOTE,
        )
        ax.set_xlabel("Annual" if period == "annual" else period)
        ygrid(ax)
    axes.flat[0].set_ylabel(ylabel)
    return fig, axes.flat


def _legend(fig, scenarios):
    fig.legend(
        handles=[
            Line2D([], [], color=_color(s), marker="o", label=_label(s))
            for s in scenarios
        ],
        loc="outside upper center",
        ncols=max(1, len(scenarios)),
    )


def _ratio_limits(axes, values):
    values = np.asarray(values, dtype=float)
    values = np.r_[1.0, values[np.isfinite(values) & (values > 0)]]
    low, high = np.log(values.min()), np.log(values.max())
    pad = max(0.08, 0.15 * (high - low))
    for ax in axes:
        ax.set_ylim(np.exp(low - pad), np.exp(high + pad))


def dot_strip(models, summary, *, variable, quantity, statistic="mean", scenarios=None,
              reference=(1985, 2014), baseline=0.0, ylabel=None):
    """Prepared model points, model range/IQR/median, annual and seasons."""
    selected = models.loc[
        (models.variable == variable)
        & (models.quantity == quantity)
        & (models.statistic == statistic)
    ]
    sums = summary.loc[
        (summary.variable == variable)
        & (summary.quantity == quantity)
        & (summary.statistic == statistic)
    ]
    unit = "%" if quantity == "change_pct" else "°C" if variable == "temp" else "mm d⁻¹"
    fig, grid = new_fig(H_SINGLE, ncols=len(STRIP_PERIODS), width_mm=W_FULL, sharey=True)
    axes = list(grid.flat)
    axes[0].set_ylabel(ylabel or f"Relative to {reference[0]}–{reference[1]} ({unit})")
    scen = _scenarios(selected, scenarios)
    values = selected.loc[selected.period.isin(STRIP_PERIODS), "value"].to_numpy(float)
    values = np.r_[baseline, values[np.isfinite(values)]]
    low, high = values.min(), values.max()
    pad = 0.06 * (high - low or 1)
    for i, (ax, period) in enumerate(zip(axes, STRIP_PERIODS, strict=True)):
        ax.set_title(f"{chr(97 + i)}) {'Annual' if period == 'annual' else period}", loc="left")
        ax.set_ylim(low - pad, high + pad)
        ax.tick_params(axis="both", length=3)
        ygrid(ax)
        ax.axhline(baseline, color=MUTED, lw=LW_REF)
        for j, s in enumerate(scen):
            values = (
                selected.loc[
                    (selected.period == period) & (selected.scenario == s), "value"
                ]
                .dropna()
                .to_numpy(float)
            )
            values = np.sort(values)
            rng = np.random.default_rng(zlib.crc32(f"{period}:{s}".encode()))
            jitter = rng.choice([-1.0, 1.0], len(values)) * rng.uniform(0.09, 0.2, len(values))
            color = _color(s)
            ax.scatter(
                j + jitter,
                values,
                color=tuple(0.65 * c for c in to_rgb(color)),
                edgecolors="white", linewidths=0.4,
                s=10, alpha=0.4, zorder=5,
            )
            rows = sums.loc[(sums.period == period) & (sums.scenario == s)]
            if not rows.empty:
                row = rows.iloc[0]
                ax.plot(
                    [j] * 2,
                    [row["min"], row["max"]],
                    color=_color(s),
                    lw=LW_RANGE,
                )
                for endpoint in (row["min"], row["max"]):
                    ax.plot([j - 0.07, j + 0.07], [endpoint] * 2, color=color, lw=LW_RANGE,
                            solid_capstyle="butt")
                if row.iqr_shown:
                    ax.add_patch(Rectangle((j - 0.25, row.q25), 0.5, row.q75 - row.q25,
                                           facecolor="white", edgecolor=color, lw=0.9, zorder=3))
                ax.plot([j - 0.25, j + 0.25], [row["median"]] * 2, color=color, lw=1.5, zorder=4)
        ax.set_xticks(range(len(scen)), [])
        ax.set_xlim(-0.6, len(scen) - 0.4)
    legend = fig.legend(handles=[Line2D([], [], color=_color(s), lw=1.4, label=_label(s)) for s in scen],
                        loc="upper right", ncols=max(1, len(scen)), frameon=False, borderaxespad=0,
                        bbox_to_anchor=(0.98, 0.99))
    legend.set_in_layout(False)
    fig.get_layout_engine().set(rect=(0, 0, 1, 0.94), w_pad=1.8 / 25.4, h_pad=1.8 / 25.4,
                                wspace=0, hspace=0)
    return fig


def seasonal_figure(climatology, changes, summary, *, variable, scenarios=None):
    """Monthly median climatologies, with only the historical model range shaded."""
    data = climatology.loc[climatology.variable == variable]
    fig, axes = new_fig(H_SINGLE, width_mm=W_MID)
    ax = axes[0, 0]
    scen = _scenarios(data, scenarios)
    unit = "°C" if variable == "temp" else "mm d⁻¹"
    historical = data.loc[(data.scenario == scen[0]) & (data.side == "reference")].set_index("period").reindex(MONTHS)
    ax.fill_between(range(12), historical["min"], historical["max"], color=MUTED, alpha=0.18, lw=0)
    ax.plot(range(12), historical["median"], color=INK, lw=1.5)
    handles = [Line2D([], [], color=INK, lw=1.5, label="Historical")]
    for s in scen:
        future = data.loc[(data.scenario == s) & (data.side == "future")].set_index("period").reindex(MONTHS)
        ax.plot(range(12), future["median"], color=_color(s), lw=1.0)
        handles.append(Line2D([], [], color=_color(s), lw=1.0, label=_label(s)))
    ax.set_xticks(range(12), MONTHS)
    ax.set_xlim(-0.4, 11.4)
    ax.set_ylabel(unit)
    ax.tick_params(axis="both", length=3)
    if variable == "precip":
        ax.set_ylim(bottom=0)
    ygrid(ax)
    inside_legend(fig, ax, handles, bands=ax.collections, lines=ax.lines)
    return fig


def monthly_change_figure(summary, *, variable, scenarios=None, reference=(1985, 2014)):
    """Monthly model-change ranges and outline boxes, with scenarios in column pairs."""
    data = summary.loc[(summary.variable == variable) & (summary.statistic == "mean")
                       & (summary.quantity == ("change_pct" if variable == "precip" else "change"))
                       & summary.period.isin(MONTHS)]
    scen = _scenarios(data, scenarios)
    ncols = min(2, len(scen))
    nrows = (len(scen) + ncols - 1) // ncols
    fig, axes = new_fig(H_SINGLE * nrows, nrows=nrows, ncols=ncols, width_mm=W_FULL, sharey=True)
    unit = "%" if variable == "precip" else "°C"
    for j, s in enumerate(scen):
        ax = axes.flat[j]
        color = _color(s)
        rows = data.loc[data.scenario == s].set_index("period").reindex(MONTHS)
        for x, (_, row) in enumerate(rows.iterrows()):
            if not np.isfinite(row["median"]):
                continue
            ax.plot([x] * 2, [row["min"], row["max"]], color=color, lw=LW_RANGE)
            for endpoint in (row["min"], row["max"]):
                ax.plot([x - 0.08, x + 0.08], [endpoint] * 2, color=color, lw=LW_RANGE)
            if row.iqr_shown:
                ax.add_patch(Rectangle((x - 0.275, row.q25), 0.55, row.q75 - row.q25,
                                       facecolor="white", edgecolor=color, lw=0.8))
            ax.plot([x - 0.275, x + 0.275], [row["median"]] * 2, color=color, lw=1.5)
        ax.set_title(f"{chr(97 + j)}) {_label(s)}", loc="left")
        ax.set_xticks(range(12), MONTHS, rotation=0)
        ax.set_xlim(-0.6, 11.6)
        ax.tick_params(axis="both", length=3)
        ax.axhline(0, color=MUTED, lw=LW_REF)
        if j % ncols == 0:
            ax.set_ylabel(f"Relative to {reference[0]}–{reference[1]} ({unit})")
        ygrid(ax)
    for ax in list(axes.flat)[len(scen):]:
        ax.set_visible(False)
    return fig


def ipcc_trajectory(envelope, *, variable, scenarios=None, members=None, windows=(), current_year=None, reference=(1985, 2014)):
    """Prepared annual model medians and ranges, with distinct historical traces."""
    data = envelope.loc[envelope.variable == variable]
    fig, axes = new_fig(H_SINGLE, width_mm=W_MID)
    ax = axes[0, 0]
    scen = _scenarios(data, scenarios)
    handles = []
    if members is not None:
        traces = members.loc[members.variable == variable]
        historical = traces.loc[traces.year <= 2014].drop_duplicates(["model", "member", "year"])
        historical_models = historical.groupby(["model", "year"]).anomaly.mean()
        historical_range = historical_models.groupby("year").agg(["median", "min", "max"])
        years = np.arange(int(data.year.min()), 2015)
        historical_range = historical_range.reindex(years)
        ax.fill_between(years, historical_range["min"], historical_range["max"], color=MUTED, alpha=0.12, lw=0)
        ax.plot(years, historical_range["median"], color=INK, lw=1.8)
        handles.append(Line2D([], [], color=INK, lw=1.4, label="Historical"))
        for _, member in historical.groupby(["model", "member"]):
            member = member.set_index("year").sort_index()
            years = np.arange(member.index.min(), member.index.max() + 1)
            ax.plot(years, member.reindex(years).anomaly, color=MUTED, lw=0.5, alpha=0.13, zorder=0.5)
        for (scenario, _, _), member in traces.loc[traces.year >= 2014].groupby(["scenario", "model", "member"]):
            member = member.set_index("year").sort_index()
            years = np.arange(member.index.min(), member.index.max() + 1)
            ax.plot(years, member.reindex(years).anomaly, color=_color(scenario), lw=0.5, alpha=0.13, zorder=0.5)
    for s in scen:
        sub = data.loc[data.scenario == s].sort_values("year")
        if members is not None:
            sub = sub.loc[sub.year >= 2014]
        years = np.arange(sub.year.min(), sub.year.max() + 1)
        sub = sub.set_index("year").reindex(years)
        ax.plot(years, sub["median"], color=_color(s), lw=1.5)
        handles.append(Line2D([], [], color=_color(s), lw=1.4, label=_label(s)))
        ax.fill_between(
            years,
            sub["min"].astype(float),
            sub["max"].astype(float),
            color=_color(s),
            alpha=0.12,
            lw=0,
        )
    for window in windows:
        a, b = window["used"]
        ax.axvspan(a - 0.5, b + 0.5, color="#d9d6d4", lw=0, zorder=0)
    if current_year is not None:
        ax.axvline(current_year, color=INK, lw=LW_REF, ls="--")
    ax.axhline(0, color=MUTED, lw=LW_REF)
    ax.set(
        xlabel="Year",
        ylabel=f"Relative to {reference[0]}–{reference[1]} ({'%' if variable == 'precip' else '°C'})",
    )
    year_ticks(ax, np.arange(int(data.year.min()), int(data.year.max()) + 1))
    if data.year.max() - data.year.min() > 100:
        ax.set_xticks(np.arange(int(data.year.min()) // 20 * 20 + 20, int(data.year.max()) + 1, 20))
        ax.set_xticks(np.arange(int(data.year.min()) // 5 * 5, int(data.year.max()) + 1, 5), minor=True)
        ax.set_xlim(data.year.min() - 0.5, data.year.max() + 0.5)
    ax.tick_params(axis="y", length=3)
    ygrid(ax)
    inside_legend(
        fig, ax,
        handles=handles,
        bands=ax.collections, lines=ax.lines,
    )
    return fig


def annual_overview(
    members, *, variable, scenarios=None, reference=(1985, 2014), windows=()
):
    """Unsmoothed absolute values and anomalies; scenarios wrap in column pairs.

    Gray historical traces are deduplicated across scenarios, with their black
    member median. Scenario envelopes are member ranges and medians, never
    claimed to be equal-model reductions. Missing years remain gaps.
    """
    data = members.loc[members.variable == variable]
    scen = _scenarios(data, scenarios)
    ncols = min(2, len(scen))
    blocks = (len(scen) + ncols - 1) // ncols
    fig, axes = new_fig(
        H_STACK2 * blocks, nrows=2 * blocks, ncols=ncols,
        width_mm=W_FULL, sharex=True, sharey="row"
    )
    for block in range(1, blocks):
        for r in range(2):
            axes[2 * block + r, 0].sharey(axes[r, 0])
    for j in range(len(scen), blocks * ncols):
        for r in range(2):
            axes[2 * (j // ncols) + r, j % ncols].set_visible(False)
    hist = data.loc[data.year <= 2014].drop_duplicates(["model", "member", "year"])
    future = data.loc[data.year >= 2014]
    historical_alpha = 0.13
    labels = (
        "mm yr⁻¹"
        if variable == "precip"
        else "°C",
        f"Relative to {reference[0]}–{reference[1]} ({'%' if variable == 'precip' else '°C'})",
    )
    for r, column in enumerate(("value", "anomaly")):
        for j, s in enumerate(scen):
            ax = axes[2 * (j // ncols) + r, j % ncols]
            for _, member in hist.groupby(["model", "member"]):
                member = member.set_index("year").sort_index()
                years = np.arange(member.index.min(), member.index.max() + 1)
                ax.plot(
                    years, member.reindex(years)[column], color=MUTED, lw=0.5, alpha=historical_alpha
                )
            median = hist.groupby("year")[column].median()
            if len(median):
                years = np.arange(median.index.min(), median.index.max() + 1)
                ax.plot(
                    years,
                    median.reindex(years),
                    color="black",
                    lw=1.2,
                    gid="historical-median",
                )
            sub = future.loc[future.scenario == s]
            member_alpha = 0.13
            for _, member in sub.groupby(["model", "member"]):
                member = member.set_index("year").sort_index()
                years = np.arange(member.index.min(), member.index.max() + 1)
                ax.plot(
                    years,
                    member.reindex(years)[column],
                    color=_color(s),
                    alpha=member_alpha,
                    lw=0.25,
                )
            env = sub.groupby("year")[column].agg(["min", "max", "median"])
            if not env.empty:
                years = np.arange(env.index.min(), env.index.max() + 1)
                env = env.reindex(years)
                ax.fill_between(
                    years, env["min"], env["max"], color=_color(s), alpha=0.25, lw=0
                )
                ax.plot(years, env["median"], color=_color(s), lw=1.0)
            ax.axvline(2014.5, color=MUTED, lw=LW_REF, ls="--", gid="scenario-handover")
            for window in windows:
                a, b = window["used"]
                ax.axvspan(
                    a - 0.5,
                    b + 0.5,
                    color="#d9d6d4",
                    zorder=0,
                    gid=f"window:{window['window_id']}",
                )
            ax.text(
                0.0,
                1.02,
                f"{chr(97 + 2 * (j // ncols) * ncols + r * ncols + j % ncols)}) {_label(s)} · {'Anomaly' if r else 'Annual'}",
                transform=ax.transAxes,
                ha="left",
                va="bottom",
                fontsize=FS_NOTE,
            )
            if r:
                ax.axhline(0, color=MUTED, lw=LW_REF)
                ax.set_xlabel("Year")
            year_ticks(ax, np.arange(int(data.year.min()), int(data.year.max()) + 1))
            if data.year.max() - data.year.min() > 100:
                ax.set_xticks(np.arange(int(data.year.min()) // 20 * 20 + 20, int(data.year.max()) + 1, 20))
                ax.set_xticks(np.arange(int(data.year.min()) // 5 * 5, int(data.year.max()) + 1, 5), minor=True)
                ax.set_xlim(data.year.min() - 0.5, data.year.max() + 0.5)
            ax.tick_params(axis="y", length=3)
            ax.tick_params(axis="x", labelbottom=bool(r))
            if j % ncols == 0:
                ax.set_ylabel(labels[r])
            ygrid(ax)
    return fig


def ratio_strip(models, *, variable, statistic, bands=(), summary=None, scenarios=None):
    """Prepared model ratios with the reviewed outline boxes and model points.

    Retained benchmark tables remain available separately; this descriptive
    ensemble figure displays model spread without sampling bands.
    """
    data = models.loc[(models.variable == variable) & (models.statistic == statistic)].copy()
    data["quantity"] = "ratio"
    if summary is None:
        summary = pd.DataFrame(columns=["variable", "statistic", "quantity", "period", "scenario",
                                        "min", "max", "median", "q25", "q75", "iqr_shown"])
    else:
        summary = summary.copy()
        summary["quantity"] = "ratio"
    name = "Temperature" if variable == "temp" else "Precipitation"
    metric = "SD" if statistic == "std_detrended" else "CV"
    return dot_strip(data, summary, variable=variable, quantity="ratio", statistic=statistic,
                     scenarios=scenarios, baseline=1.0, ylabel=f"{name} {metric} ratio")


def pooled_ratio_figure(members, summary, scenarios=None):
    """Member points with prepared geometric-member, equal-model summaries."""
    metrics = (("temp", "std_detrended", "Temp. SD"),
               ("precip", "std_detrended", "Precip. SD"),
               ("precip", "cv_detrended", "Precip. CV"))
    data = members.loc[(members.period == "annual") & np.isfinite(members.ratio)]
    if "variability_eligible" in data:
        data = data.loc[data.variability_eligible]
    scen = _scenarios(data, scenarios)
    fig, axes = new_fig(H_SINGLE, ncols=3, width_mm=W_FULL, sharey=True)
    shown = data.loc[
        ((data.variable == "temp") & (data.statistic == "std_detrended"))
        | ((data.variable == "precip") & data.statistic.isin(["std_detrended", "cv_detrended"]))
    ]
    values = np.r_[1.0, shown.ratio.to_numpy(float)]
    low, high = values.min(), values.max()
    pad = .06 * (high - low or 1)
    for i, (ax, (variable, statistic, title)) in enumerate(zip(axes.flat, metrics, strict=True)):
        ax.set_title(f"{chr(97+i)}) {title}", loc="left")
        ax.set_ylim(low-pad, high+pad)
        ax.axhline(1, color=MUTED, lw=LW_REF)
        ax.tick_params(axis="both", length=3)
        ygrid(ax)
        for j, scenario in enumerate(scen):
            color = _color(scenario)
            vals = np.sort(data.loc[
                (data.variable == variable) & (data.statistic == statistic)
                & (data.scenario == scenario), "ratio"].to_numpy(float))
            rng = np.random.default_rng(zlib.crc32(f"pooled:{variable}:{statistic}:{scenario}".encode()))
            jitter = rng.choice([-1., 1.], len(vals)) * rng.uniform(.09, .2, len(vals))
            ax.scatter(j+jitter, vals, s=10, color=tuple(.65*c for c in to_rgb(color)),
                       edgecolor="white", linewidth=.4, alpha=.4, zorder=5)
            rows = summary.loc[(summary.period == "annual") & (summary.variable == variable)
                               & (summary.statistic == statistic) & (summary.scenario == scenario)]
            if rows.empty:
                continue
            row = rows.iloc[0]
            ax.plot([j, j], [row["min"], row["max"]], color=color, lw=LW_RANGE, zorder=2)
            for end in (row["min"], row["max"]):
                ax.plot([j-.07, j+.07], [end, end], color=color, lw=LW_RANGE,
                        solid_capstyle="butt", zorder=2)
            if row.iqr_shown:
                ax.add_patch(Rectangle((j-.25, row.q25), .5, row.q75-row.q25,
                                       facecolor="white", edgecolor=color, lw=.9, zorder=3))
            ax.plot([j-.25, j+.25], [row["median"]]*2, color=color, lw=1.5, zorder=4)
        ax.set_xticks(range(len(scen)), [""]*len(scen))
        ax.set_xlim(-.6, len(scen)-.4)
    axes.flat[0].set_ylabel("Future / reference")
    legend = fig.legend(handles=[Line2D([], [], color=_color(s), label=_label(s)) for s in scen],
                        loc="upper right", bbox_to_anchor=(.98, .99), ncols=max(1, len(scen)),
                        frameon=False, borderaxespad=0)
    legend.set_in_layout(False)
    fig.get_layout_engine().set(rect=(0, 0, 1, .94))
    return fig


def change_cloud(models, *, combined=False, scenarios=None):
    """Paired model mean changes; scenario colors share a circular marker."""
    data = models.loc[(models.period == "annual") & (models.statistic == "mean")]
    keys = ["model", "scenario", "window_id"]
    temp = data.loc[(data.variable == "temp") & (data.quantity == "change"), [*keys, "value"]]
    precip = data.loc[(data.variable == "precip") & (data.quantity == "change_pct"), [*keys, "value"]]
    paired = temp.merge(precip, on=keys, suffixes=("_temp", "_precip")).dropna()
    fig, axes = new_fig(120, width_mm=120)
    ax = axes[0, 0]
    scen = _scenarios(paired, scenarios)
    handles = []
    for s in scen:
        sub = paired.loc[paired.scenario == s]
        color = _color(s)
        edge = tuple(.6*c for c in to_rgb(color))
        ax.scatter(sub.value_precip, sub.value_temp, color=color, s=28, alpha=.75,
                   marker="o", edgecolor=edge, linewidth=.55, zorder=3)
        handles.append(Line2D([], [], linestyle="", marker="o", markersize=4,
                              markerfacecolor=color, markeredgecolor=edge, alpha=.75, label=_label(s)))
        if combined:
            for _, group in sub.groupby("model"):
                group = group.sort_values("window_id")
                ax.plot(group.value_precip, group.value_temp, color=color, alpha=.25, lw=.6)
    p = paired.value_precip.to_numpy(float)
    t = paired.value_temp.to_numpy(float)
    pad_x = max((p.max()-p.min())*.12, 1.)
    pad_y = max((t.max()-t.min())*.12, .2)
    ax.set(xlim=(min(p.min(), 0)-pad_x, max(p.max(), 0)+pad_x),
           ylim=(min(t.min(), 0)-pad_y, max(t.max(), 0)+pad_y),
           xlabel="Mean precipitation change (%)", ylabel="Mean temperature change (°C)",
           box_aspect=1)
    ax.axhline(0, color=MUTED, lw=LW_REF, zorder=1)
    ax.axvline(0, color=MUTED, lw=LW_REF, zorder=1)
    ax.grid(axis="both")
    ax.tick_params(axis="both", length=3)
    inside_legend(fig, ax, handles)
    return fig


def agreement_matrix(agreement, scenarios=None):
    """Prepared model sign counts, with discrete direction/agreement encoding."""
    data = agreement.loc[agreement.statistic == "mean"]
    scen = _scenarios(data, scenarios)
    quantities = (("temp", "change", "Temperature"), ("precip", "change_pct", "Precipitation"))
    periods = [p for p in ("annual", *MONTHS) if p in set(data.period)]
    positive = ("#eef3f8", "#c6d6e8", "#8fb0d3", "#3d6fa5")
    negative = ("#f8eeee", "#ecc9c9", "#d98f8f", "#a8403f")
    fig, axes = new_fig(34+4.2*len(periods), ncols=2,
                        width_mm=20+2*(13*len(scen)+5))
    ys = [i+(.45 if i and periods[0] == "annual" else 0) for i in range(len(periods))]
    for b, (ax, (variable, quantity, title)) in enumerate(zip(axes.flat, quantities, strict=True)):
        for period, y in zip(periods, ys, strict=True):
            for j, s in enumerate(scen):
                rows = data.loc[(data.variable == variable) & (data.quantity == quantity)
                                & (data.period == period) & (data.scenario == s)]
                if rows.empty:
                    continue
                row = rows.iloc[0]
                median = row["median"]
                sign = "+" if median > 0 else "−" if median < 0 else ""
                k = int(np.clip(np.digitize(row.fraction, [0, .6, .8, .9, 1.0001])-1, 0, 3))
                fill = (positive if sign == "+" else negative)[k] if sign and np.isfinite(row.fraction) else "#eeeeee"
                ax.add_patch(Rectangle((j, y), 1, 1, facecolor=fill, edgecolor="white", lw=1))
                rgb = to_rgb(fill)
                linear = [c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in rgb]
                luminance = sum(c*w for c, w in zip(linear, (.2126, .7152, .0722), strict=True))
                ax.text(j+.5, y+.5, f"{sign} {int(row.k)}/{int(row.n)}".strip(),
                        ha="center", va="center", fontsize=FS_NOTE,
                        color="white" if luminance < .179 else "#173442")
        ax.set(xlim=(0, len(scen)), ylim=(ys[-1]+1, 0))
        ax.set_xticks(np.arange(len(scen))+.5, [_label(s) for s in scen])
        ax.xaxis.tick_top()
        ax.set_yticks(np.array(ys)+.5, ["Annual" if p == "annual" else p for p in periods] if b == 0 else [])
        ax.tick_params(axis="x", length=3, width=.6)
        ax.tick_params(axis="y", length=3 if b == 0 else 0, width=.6)
        ax.set_title(f"{chr(97+b)}) {title}", loc="left")
        ax.grid(False)
        for spine in ax.spines.values():
            spine.set_visible(False)
    handles = [(Patch(facecolor=positive[k], edgecolor=MUTED if k == 0 else "none"),
                Patch(facecolor=negative[k], edgecolor=MUTED if k == 0 else "none")) for k in range(4)]
    fig.legend(handles, ["<60%", "60–80%", "80–90%", "≥90%"],
               handler_map={tuple: HandlerTuple(ndivide=None, pad=.3)},
               loc="outside upper left", ncols=4, frameon=False, alignment="left",
               title="Models sharing median sign · blue: increase; red: decrease")
    return fig


def availability_matrix(coverage, scenarios=None):
    """Resolved scenario member counts and unique loaded historical references."""
    identities = coverage[["model", "source_id", "institution", "family", "family_source", "country"]].drop_duplicates("model")
    identities = identities.sort_values("source_id", key=lambda s: s.str.lower())
    scen = _scenarios(coverage, scenarios)
    runs = ["historical", *scen]
    n = len(identities)
    total = 25+23+14*len(runs)
    fig, axes = new_fig(.9*(10+7*(n+1)), width_mm=total+8)
    ax = axes[0, 0]
    ax.set_axis_off()
    ax.set(xlim=(0, total), ylim=(n+.5, -.5))
    xs = [0, 25, *[48+14*j for j in range(len(runs))]]
    for j, (x, title) in enumerate(zip(xs, ["Model", "Family", "Historical", *[_label(s) for s in scen]], strict=True)):
        ax.text(x+(7 if j >= 2 else 0), 0, title, ha="center" if j >= 2 else "left",
                va="center", fontsize=FS_NOTE, fontweight="bold", color=INK)
    ax.axhline(.5, color=INK, lw=.8)
    for i, row in enumerate(identities.itertuples(index=False), start=1):
        if i % 2 == 0:
            ax.axhspan(i-.5, i+.5, color="#f1f5f6", lw=0, zorder=0)
        ax.text(0, i, row.source_id, ha="left", va="center", fontsize=FS_NOTE, color=INK)
        family = row.family if row.family_source == "listed" else (
            f"{row.family}*" if row.family_source == "provisional" else "?")
        ax.text(25, i-.17, family, ha="left", va="center", fontsize=FS_NOTE, color=INK)
        where = f"({row.institution}, {row.country})" if row.country else f"({row.institution})"
        ax.text(25, i+.2, where, ha="left", va="center", fontsize=FS_NOTE-.5, color=INK)
        available = coverage.loc[(coverage.model == row.model) & coverage.available]
        counts = [available.reference_series_key.replace("", np.nan).nunique()]
        counts.extend(available.loc[available.scenario == s, "member"].nunique() for s in scen)
        for j, count in enumerate(counts):
            ax.text(xs[j+2]+7, i, str(count), ha="center", va="center",
                    fontsize=FS_NOTE, color=INK if count else MUTED)
    ax.axhline(n+.5, color=INK, lw=.8)
    return fig


def render_product(filename, tables, record, *, window_id="", scenarios=None):
    """Dispatch one available product inside the shared WF0 style context."""

    def table(name):
        data = tables[name]
        return (
            data.loc[data.window_id == window_id]
            if window_id and "window_id" in data
            else data
        )

    with plt.rc_context(STYLE):
        if filename == "availability.png":
            return availability_matrix(table("coverage"), scenarios)
        variable = "temp" if "temperature" in filename else "precip"
        if filename.startswith("trajectory-"):
            return ipcc_trajectory(
                table("trajectory_range"), variable=variable, scenarios=scenarios,
                members=table("member_anomalies"), windows=record["windows"], current_year=date.today().year,
                reference=record["reference"],
            )
        if filename.startswith("annual-"):
            return annual_overview(
                table("member_anomalies"),
                variable=variable,
                scenarios=scenarios,
                reference=record["reference"],
                windows=record["windows"],
            )
        if filename.startswith("seasonal-cycle-"):
            return seasonal_figure(
                table("climatology_summary"),
                table("model_changes"),
                table("change_summary"),
                variable=variable,
                scenarios=scenarios,
            )
        if filename.startswith("monthly-change-"):
            return monthly_change_figure(table("change_summary"), variable=variable, scenarios=scenarios,
                                         reference=next(w["reference"] for w in record["windows"] if w["window_id"] == window_id))
        if filename.startswith("variability-ratio-"):
            bands = [
                b
                for b in record.get("display_null_bands", [])
                if b["window_id"] == window_id
            ]
            return ratio_strip(
                table("variability_model_ratios"),
                variable=variable,
                statistic="std_detrended" if filename.endswith("-sd.png") else "cv_detrended",
                bands=bands,
                summary=pd.DataFrame(
                    [
                        r
                        for r in record.get("variability_model_summary", [])
                        if r["window_id"] == window_id
                    ]
                )
                if record.get("variability_model_summary")
                else None,
                scenarios=scenarios,
            )
        if filename == "variability-member-ratios.png":
            return pooled_ratio_figure(
                table("variability_member_ratios"),
                pd.DataFrame([
                    row for row in record["variability_model_summary"]
                    if row["window_id"] == window_id
                ]),
                scenarios,
            )
        if filename == "sign-agreement.png":
            return agreement_matrix(table("sign_agreement"), scenarios)
        if filename.startswith("change-factor-cloud"):
            return change_cloud(
                table("model_changes"),
                combined="combined" in filename,
                scenarios=scenarios,
            )
        if filename.startswith("change-"):
            return dot_strip(
                table("model_changes"),
                table("change_summary"),
                variable=variable,
                quantity="change_pct" if filename.endswith("-pct.png") else "change",
                scenarios=scenarios,
                reference=next((w["reference"] for w in record["windows"] if w["window_id"] == window_id), record["reference"]),
            )
    raise ValueError(f"unknown suite product: {filename}")




