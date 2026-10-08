"""WF2 suite artists: plot prepared tables, never recompute climate statistics."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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


def dot_strip(models, summary, *, variable, quantity, statistic="mean", scenarios=None):
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
    fig, axes = _panels(STRIP_PERIODS, f"Change ({unit})")
    scen = _scenarios(selected, scenarios)
    for ax, period in zip(axes, STRIP_PERIODS, strict=True):
        ax.axhline(0, color=MUTED, lw=LW_REF)
        for j, s in enumerate(scen):
            values = (
                selected.loc[
                    (selected.period == period) & (selected.scenario == s), "value"
                ]
                .dropna()
                .to_numpy(float)
            )
            ax.scatter(
                j + np.linspace(-0.13, 0.13, len(values)),
                values,
                color=_color(s),
                s=12,
                alpha=0.65,
            )
            rows = sums.loc[(sums.period == period) & (sums.scenario == s)]
            if not rows.empty:
                row = rows.iloc[0]
                ax.plot(
                    [j + 0.22] * 2,
                    [row["min"], row["max"]],
                    color=_color(s),
                    lw=LW_RANGE,
                )
                if row.iqr_shown:
                    ax.plot(
                        [j + 0.22] * 2, [row.q25, row.q75], color=_color(s), lw=LW_IQR
                    )
                ax.plot([j + 0.16, j + 0.28], [row["median"]] * 2, color=INK)
        ax.set_xticks(
            range(len(scen)), [s.replace("ssp", "") for s in scen], rotation=45
        )
        ax.set_xlim(-0.5, len(scen) - 0.5)
    _legend(fig, scen)
    return fig


def seasonal_figure(climatology, changes, summary, *, variable, scenarios=None):
    """Monthly reference/future cycles and prepared monthly mean changes."""
    data = climatology.loc[climatology.variable == variable]
    fig, axes = new_fig(H_SIDE2, ncols=2, width_mm=W_FULL)
    scen = _scenarios(data, scenarios)
    unit = "°C" if variable == "temp" else "mm d⁻¹"
    for i, ax in enumerate(axes.flat):
        ax.text(
            0.02,
            1.02,
            f"{chr(97 + i)})",
            transform=ax.transAxes,
            va="bottom",
            fontsize=FS_NOTE,
        )
        ax.set_xticks(range(12), MONTHS, rotation=45)
        ygrid(ax)
    for s in scen:
        for side, linestyle in (("reference", "--"), ("future", "-")):
            sub = (
                data.loc[(data.scenario == s) & (data.side == side)]
                .set_index("period")
                .reindex(MONTHS)
            )
            axes[0, 0].plot(range(12), sub["median"], color=_color(s), ls=linestyle)
        sub = (
            summary.loc[
                (summary.variable == variable)
                & (summary.statistic == "mean")
                & (
                    summary.quantity
                    == ("change_pct" if variable == "precip" else "change")
                )
                & (summary.scenario == s)
            ]
            .set_index("period")
            .reindex(MONTHS)
        )
        axes[0, 1].plot(range(12), sub["median"], color=_color(s))
        axes[0, 1].fill_between(
            range(12),
            sub["min"].astype(float),
            sub["max"].astype(float),
            color=_color(s),
            alpha=0.15,
        )
    axes[0, 0].set_ylabel(f"Monthly mean ({unit}); dashed reference")
    axes[0, 1].set_ylabel(f"Change ({'%' if variable == 'precip' else unit})")
    axes[0, 1].axhline(0, color=MUTED, lw=LW_REF)
    _legend(fig, scen)
    return fig


def ipcc_trajectory(envelope, *, variable, scenarios=None):
    """Supplied annual equal-model means and model ranges, unsmoothed."""
    data = envelope.loc[envelope.variable == variable]
    fig, axes = new_fig(H_SINGLE, width_mm=W_MID)
    ax = axes[0, 0]
    scen = _scenarios(data, scenarios)
    for s in scen:
        sub = data.loc[data.scenario == s].sort_values("year")
        years = np.arange(sub.year.min(), sub.year.max() + 1)
        sub = sub.set_index("year").reindex(years)
        ax.plot(years, sub["mean"], color=_color(s))
        ax.fill_between(
            years,
            sub["min"].astype(float),
            sub["max"].astype(float),
            color=_color(s),
            alpha=0.15,
        )
    ax.axhline(0, color=MUTED, lw=LW_REF)
    ax.set(
        xlabel="Water-year label",
        ylabel="Anomaly (%)" if variable == "precip" else "Anomaly (°C)",
    )
    ygrid(ax)
    _legend(fig, scen)
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
    historical_alpha = max(0.06, min(0.3, 0.6 / np.sqrt(max(1, hist.groupby(["model", "member"]).ngroups))))
    labels = (
        "mm yr⁻¹"
        if variable == "precip"
        else "°C",
        "%" if variable == "precip" else "°C",
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
            member_alpha = max(0.05, min(0.25, 0.5 / np.sqrt(max(1, sub.groupby(["model", "member"]).ngroups))))
            for _, member in sub.groupby(["model", "member"]):
                member = member.set_index("year").sort_index()
                years = np.arange(member.index.min(), member.index.max() + 1)
                ax.plot(
                    years,
                    member.reindex(years)[column],
                    color=_color(s),
                    alpha=member_alpha,
                    lw=0.3,
                )
            env = sub.groupby("year")[column].agg(["min", "max", "median"])
            if not env.empty:
                years = np.arange(env.index.min(), env.index.max() + 1)
                env = env.reindex(years)
                ax.fill_between(
                    years, env["min"], env["max"], color=_color(s), alpha=0.15
                )
                ax.plot(years, env["median"], color=_color(s), lw=1.2)
            ax.axvline(2014.5, color=MUTED, lw=LW_REF, ls="--", gid="scenario-handover")
            for window in windows:
                a, b = window["used"]
                ax.axvspan(
                    a - 0.5,
                    b + 0.5,
                    color=".9",
                    zorder=0,
                    gid=f"window:{window['window_id']}",
                )
            ax.text(
                0.0,
                1.02,
                f"{chr(97 + r * len(scen) + j)}) {_label(s)} · {'Anomaly' if r else 'Annual'}",
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
            ax.tick_params(axis="y", length=3)
            ax.tick_params(axis="x", labelbottom=bool(r))
            if j % ncols == 0:
                ax.set_ylabel(labels[r])
            ygrid(ax)
    return fig


def ratio_strip(models, *, variable, statistic, bands=(), summary=None, scenarios=None):
    """Model geometric ratios and supplied exact-mask single-member benchmarks."""
    data = models.loc[(models.variable == variable) & (models.statistic == statistic)]
    fig, axes = _panels(
        STRIP_PERIODS, "Variability ratio (log scale; future/reference)"
    )
    scen = _scenarios(data, scenarios)
    for ax, period in zip(axes, STRIP_PERIODS, strict=True):
        ax.axhline(1, color=MUTED, lw=LW_REF)
        for j, s in enumerate(scen):
            for band in bands:
                if (
                    band.get("scenario") == s
                    and band.get("period") == period
                    and band.get("variable") == variable
                    and band.get("statistic") == statistic
                    and band.get("null_status", band.get("status")) == "ok"
                ):
                    ax.fill_between(
                        [j - 0.35, j + 0.35],
                        band["null_lo"],
                        band["null_hi"],
                        color=_color(s),
                        alpha=0.12,
                    )
            sub = data.loc[
                (data.period == period) & (data.scenario == s) & data.value.gt(0)
            ].sort_values("model")
            for offset, (_, row) in zip(
                np.linspace(-0.13, 0.13, len(sub)), sub.iterrows(), strict=True
            ):
                ax.scatter(
                    j + offset,
                    row.value,
                    edgecolor=_color(s),
                    facecolor=_color(s) if row.outside_null else "white",
                    s=16,
                )
            if summary is not None:
                rows = summary.loc[
                    (summary.period == period)
                    & (summary.scenario == s)
                    & (summary.variable == variable)
                    & (summary.statistic == statistic)
                ]
                if not rows.empty:
                    row = rows.iloc[0]
                    ax.plot(
                        [j + 0.22] * 2,
                        [row["min"], row["max"]],
                        color=_color(s),
                        lw=LW_RANGE,
                    )
                    if row.iqr_shown:
                        ax.plot(
                            [j + 0.22] * 2,
                            [row.q25, row.q75],
                            color=_color(s),
                            lw=LW_IQR,
                        )
                    ax.plot([j + 0.16, j + 0.28], [row["median"]] * 2, color=INK)
        ax.set_xticks(
            range(len(scen)), [s.replace("ssp", "") for s in scen], rotation=45
        )
        ax.set_yscale("log")
        ax.set_xlim(-0.5, len(scen) - 0.5)
    _ratio_limits(
        fig.axes,
        [
            *data.value,
            *(
                b[k]
                for b in bands
                for k in ("null_lo", "null_hi")
                if b.get("variable") == variable
            ),
        ],
    )
    _legend(fig, scen)
    return fig


def pooled_ratio_figure(members, summary, scenarios=None):
    """Eligible annual member ratios and prepared equal-model log quantiles."""
    fig, axes = new_fig(H_SIDE2, ncols=2, width_mm=W_FULL)
    data = members.loc[members.period == "annual"]
    scen = _scenarios(data, scenarios)
    for ax, (variable, statistic) in zip(
        axes.flat, (("temp", "std_detrended"), ("precip", "cv_detrended")), strict=True
    ):
        ax.axhline(1, color=MUTED, lw=LW_REF)
        for j, s in enumerate(scen):
            sub = data.loc[
                (data.variable == variable)
                & (data.statistic == statistic)
                & (data.scenario == s)
                & data.variability_eligible
                & data.ratio.gt(0)
            ]
            for offset, (_, row) in zip(
                np.linspace(-0.16, 0.16, len(sub)), sub.iterrows(), strict=True
            ):
                outside = row.get("null_status") == "ok" and (
                    row.ratio < row.get("null_lo", np.nan)
                    or row.ratio > row.get("null_hi", np.nan)
                )
                if row.get("null_status") == "ok":
                    ax.plot(
                        [j + offset] * 2,
                        [row.null_lo, row.null_hi],
                        color=_color(s),
                        alpha=0.2,
                        lw=LW_RANGE,
                    )
                ax.scatter(
                    j + offset,
                    row.ratio,
                    s=12,
                    edgecolor=_color(s),
                    facecolor=_color(s) if outside else "white",
                    alpha=0.65,
                )
            sums = summary.loc[
                (summary.period == "annual")
                & (summary.variable == variable)
                & (summary.statistic == statistic)
                & (summary.scenario == s)
            ]
            if not sums.empty:
                row = sums.iloc[0]
                ax.plot(
                    [j + 0.24] * 2,
                    [row["min"], row["max"]],
                    color=_color(s),
                    lw=LW_RANGE,
                )
                if row.iqr_shown:
                    ax.plot(
                        [j + 0.24] * 2, [row.q25, row.q75], color=_color(s), lw=LW_IQR
                    )
                ax.plot([j + 0.18, j + 0.30], [row["median"]] * 2, color=INK)
        ax.set(
            xlabel="Temperature SD" if variable == "temp" else "Precipitation CV",
            ylabel="Variability ratio (log scale)",
            yscale="log",
        )
        ax.set_xticks(
            range(len(scen)), [s.replace("ssp", "") for s in scen], rotation=45
        )
        ygrid(ax)
        ax.set_xlim(-0.5, len(scen) - 0.5)
    _ratio_limits(
        fig.axes,
        [
            *data.ratio,
            *(data.null_lo if "null_lo" in data else []),
            *(data.null_hi if "null_hi" in data else []),
        ],
    )
    _legend(fig, scen)
    return fig


def change_cloud(models, *, combined=False, scenarios=None):
    """Paired annual mean changes, no model labels or model style channels."""
    data = models.loc[(models.period == "annual") & (models.statistic == "mean")]
    keys = ["model", "scenario", "window_id"]
    temp = data.loc[
        (data.variable == "temp") & (data.quantity == "change"), [*keys, "value"]
    ]
    precip = data.loc[
        (data.variable == "precip") & (data.quantity == "change_pct"), [*keys, "value"]
    ]
    paired = temp.merge(precip, on=keys, suffixes=("_temp", "_precip")).dropna()
    fig, axes = new_fig(H_SINGLE, width_mm=W_MID)
    ax = axes[0, 0]
    scen = _scenarios(paired, scenarios)
    for s in scen:
        sub = paired.loc[paired.scenario == s]
        ax.scatter(
            sub.value_temp,
            sub.value_precip,
            color=_color(s),
            s=16,
            alpha=0.65,
            marker="o",
        )
        if combined:
            for _, group in sub.groupby("model"):
                group = group.sort_values("window_id")
                ax.plot(
                    group.value_temp,
                    group.value_precip,
                    color=_color(s),
                    alpha=0.25,
                    lw=0.6,
                )
    ax.axhline(0, color=MUTED, lw=LW_REF)
    ax.axvline(0, color=MUTED, lw=LW_REF)
    ax.set(
        xlabel="Temperature change (°C)",
        ylabel="Precipitation change (%)",
        box_aspect=1,
    )
    ygrid(ax)
    _legend(fig, scen)
    return fig


def agreement_matrix(agreement, scenarios=None):
    """Model and code-family counts; neutral small-change cells."""
    data = agreement.loc[agreement.statistic == "mean"].copy()
    scen = _scenarios(data, scenarios)
    quantities = [("temp", "change"), ("precip", "change_pct"), ("precip", "change")]
    periods = [p for p in ("annual", *MONTHS) if p in set(data.period)]
    fig, axes = new_fig(max(H_SINGLE, 30 + 7 * len(periods)), ncols=3, width_mm=W_FULL)
    for b, (ax, (variable, quantity)) in enumerate(
        zip(axes.flat, quantities, strict=True)
    ):
        for i, period in enumerate(periods):
            for j, s in enumerate(scen):
                sub = data.loc[
                    (data.variable == variable)
                    & (data.quantity == quantity)
                    & (data.period == period)
                    & (data.scenario == s)
                ]
                if sub.empty:
                    continue
                row = sub.iloc[0]
                color = (
                    "#eeeeee"
                    if row.small_change
                    else plt.get_cmap("Blues" if row["median"] >= 0 else "Reds")(
                        0.15 + 0.7 * row.fraction
                    )
                )
                ax.add_patch(
                    plt.Rectangle(
                        (j - 0.5, i - 0.5), 1, 1, facecolor=color, edgecolor="white"
                    )
                )
                ax.text(
                    j,
                    i,
                    f"{row.k}/{row.n}\n{row.k_fam}/{row.n_fam}"
                    + (" ·" if row.small_change else ""),
                    ha="center",
                    va="center",
                    fontsize=FS_NOTE,
                    color="white"
                    if not row.small_change and row.fraction > 0.7
                    else INK,
                )
        ax.set(
            xticks=range(len(scen)),
            xticklabels=scen,
            yticks=range(len(periods)),
            yticklabels=["Annual" if p == "annual" else p for p in periods]
            if b == 0
            else [],
            xlim=(-0.5, len(scen) - 0.5),
            ylim=(len(periods) - 0.5, -0.5),
            xlabel=f"{variable} {'%' if quantity == 'change_pct' else '°C' if variable == 'temp' else 'mm d⁻¹'}",
        )
    return fig


def availability_matrix(coverage):
    """Resolved member counts by explicit model identity and scenario."""
    models = sorted(coverage.model.unique())
    scen = _scenarios(coverage)
    fig, axes = new_fig(max(H_SINGLE, 5 * len(models)), width_mm=W_FULL)
    ax = axes[0, 0]
    for i, model in enumerate(models):
        for j, s in enumerate(scen):
            rows = coverage.loc[
                (coverage.model == model)
                & (coverage.scenario == s)
                & coverage.available
            ]
            n = rows.member.nunique()
            ax.add_patch(
                plt.Rectangle(
                    (j - 0.5, i - 0.5),
                    1,
                    1,
                    facecolor="#dce9ed" if n else "#eeeeee",
                    edgecolor="white",
                )
            )
            ax.text(j, i, str(n), ha="center", va="center", fontsize=FS_NOTE)
    ax.set(
        xticks=range(len(scen)),
        xticklabels=scen,
        yticks=range(len(models)),
        yticklabels=models,
        xlim=(-0.5, len(scen) - 0.5),
        ylim=(len(models) - 0.5, -0.5),
    )
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
            return availability_matrix(table("coverage"))
        variable = "temp" if "temperature" in filename else "precip"
        if filename.startswith("trajectory-"):
            return ipcc_trajectory(
                table("trajectory_range"), variable=variable, scenarios=scenarios
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
        if filename.startswith("variability-ratio-"):
            bands = [
                b
                for b in record.get("display_null_bands", [])
                if b["window_id"] == window_id
            ]
            return ratio_strip(
                table("variability_model_ratios"),
                variable=variable,
                statistic="std_detrended" if variable == "temp" else "cv_detrended",
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
                table("variability_summary"),
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
            )
    raise ValueError(f"unknown suite product: {filename}")
