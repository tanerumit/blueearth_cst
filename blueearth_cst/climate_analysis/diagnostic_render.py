"""Render retained CSV/NetCDF products and one recoverable caption inventory."""

import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from blueearth_cst.climate_analysis import diagnostic_figures as artists
from blueearth_cst.climate_analysis.diagnostic_captions import caption
from blueearth_cst.climate_analysis.diagnostic_maps import draw_map, visible_values
from blueearth_cst.climate_analysis.diagnostic_tables import write_json


def load_result(root, source):
    """Restore artist inputs from explicit plot-ready tables, never raw climate."""
    folder = Path(root) / "tables"

    def read(name):
        frame = pd.read_csv(folder / f"{name}.csv")
        return frame[frame.source == source].drop(
            columns=["source", "period_start", "period_end"]
        )

    coverage = read("coverage").pivot(
        index="calendar_month", columns="reporting_year", values="class"
    )
    monthly = read("monthly_values")
    anomaly = monthly.pivot(
        index="calendar_month", columns="reporting_year", values="anomaly"
    )
    indices = read("annual_indices").set_index("reporting_year")
    spi = read("spi")
    spi.date = pd.to_datetime(spi.date)
    checks = read("spi_fit_checks")
    events = read("drought_events")
    events.start = pd.to_datetime(events.start)
    events.end = pd.to_datetime(events.end)
    trends = read("trends").set_index("metric")
    sensitivity = read("trend_sensitivity")
    temp = read("temp_climatology").set_index("calendar_month")
    pt = read("pt_anomalies")
    spells = read("dry_spell_exceedance")
    valid = read("valid_years")
    metadata = json.loads(
        (Path(root) / "_engine" / "diagnostics.json").read_text(encoding="utf-8")
    )
    return {
        "coverage": coverage,
        "valid": valid.loc[valid.valid_precip, "reporting_year"].to_numpy(),
        "clim": read("precip_climatology").set_index("calendar_month"),
        "tclim": temp if not temp.empty else None,
        "timing": read("rainfall_timing")
        .pivot(index="reporting_year", columns="fraction", values="day")
        .reindex(columns=[0.25, 0.5, 0.75]),
        "anomaly": anomaly,
        "spi": {k: spi[spi.scale == k].set_index("date").value for k in (3, 6, 12)},
        "spi_dist": metadata["settings"]["spi_distribution"],
        "spi_checks": {
            k: checks[checks.scale == k].set_index("calendar_month") for k in (3, 6, 12)
        },
        "drought": {k: events[events.scale == k] for k in (3, 12)},
        "extremes": indices.rename(columns={"sdii": "SDII", "wet_days": "Wet days"}),
        "spells": spells.set_index("length_days").probability,
        "n_spells": len(read("dry_spells")),
        "acf": read("anomaly_acf").set_index("lag_months"),
        "annual": indices,
        "trends": trends.to_dict(orient="index"),
        "sensitivity": {
            k: sensitivity[sensitivity.metric == k]
            .set_index("start_year")
            .drop(columns="metric")
            for k in ("total", "Rx1day")
        },
        "pt": pt if not pt.empty else None,
        "t_source": pt.temperature_source.iloc[0] if not pt.empty else None,
    }


def render(
    paths, settings, m0, sources, pooled_roots, overlays=None, scope="basin_avg"
):
    """Export standard PNGs, optional captioned copies, JSON and Markdown."""
    root = Path(paths["root"])
    metadata = json.loads(
        Path(paths["compute"]["metadata"]).read_text(encoding="utf-8")
    )
    period = metadata["period"]
    results = {s: load_result(root, s) for s in sources}
    months = artists.month_order(m0)
    calendar = pd.date_range(
        pd.Timestamp(year=period[0], month=m0, day=1),
        pd.Timestamp(year=period[1] + 1, month=m0, day=1),
        freq="MS",
        inclusive="left",
    )
    for result in results.values():
        for key in ("coverage", "anomaly"):
            result[key] = result[key].reindex(
                index=months, columns=range(period[0], period[1] + 1)
            )
        for scale in (3, 6, 12):
            result["spi"][scale] = result["spi"][scale].reindex(calendar)
    pooled = [
        pd.read_csv(Path(p) / "tables" / "monthly_values.csv").anomaly.to_numpy()
        for p in pooled_roots
    ]
    bounds = artists.anomaly_bounds(np.concatenate(pooled))
    view = artists.View(
        sources=sources,
        labels={
            s: "CHIRPS v2.0" if s in {"chirps", "chirps_global"} else s.upper()
            for s in sources
        },
        styles=artists.source_styles(sources),
        results=results,
        years=np.arange(period[0], period[1] + 1),
        m0=m0,
        reference=tuple(settings["reference_period"][k] for k in ("start", "end")),
        wet_mm=settings["wet_day_threshold_mm"],
        agreement=pd.DataFrame(),
        common_years=np.array([]),
        support=f"{scope.replace('_', ' ')}, equal-weight cells",
        status="real-data exercised, not scientifically qualified",
        anom_bounds=bounds,
        max_missing_month=settings["max_missing_days_month"],
        max_missing_year=settings["max_missing_days_year"],
    )
    records = {}
    for form, filename in paths["figures"].items():
        availability = "available"
        support = (
            "native source grid, basin extent"
            if form.startswith("map-")
            else view.support
        )
        with plt.rc_context(artists.STYLE):
            if form.startswith("map-"):
                variable = form.removeprefix("map-")
                with xr.open_dataset(paths["compute"]["maps"]) as fields:
                    field = fields[variable].load()
                    counts = fields[f"{variable}_valid_years"].load()
                    field.attrs.update(period_start=period[0], period_end=period[1])
                all_values = []
                for p in pooled_roots:
                    with xr.open_dataset(
                        Path(p) / "tables" / "annual_climatology.nc"
                    ) as ds:
                        if variable in ds:
                            all_values.extend(
                                visible_values(ds[variable], overlays["basins"])
                                if overlays and "basins" in overlays
                                else ds[variable].values.ravel()
                            )
                values = np.asarray(all_values)
                values = values[np.isfinite(values)]
                limits = (
                    (float(values.min()), float(values.max()))
                    if values.size
                    else (0, 1)
                )
                fig = draw_map(
                    field, variable, sources[0], overlays or {}, limits, counts
                )
                text = f"{sources[0].upper()} native-grid annual {variable} climatology, {period[0]}–{period[1]}. Complete reporting-year {'means' if variable == 'temp' else 'totals'}; gray cells are unavailable. Basin boundary, dashed subbasin boundaries, rivers and gauges are shown where supplied. No interpolation."
                if variable == "pet":
                    text += " PET is derived on the source grid with the existing de Bruin machinery and can differ from model PET."
                if not np.isfinite(field.values).any():
                    availability = "unavailable: no complete annual map values"
            else:
                available = form in {"coverage", "anomaly"} or any(
                    result["annual"].total.notna().any() for result in results.values()
                )
                if form in {"spi", "drought-events"}:
                    available = any(
                        series.notna().any()
                        for result in results.values()
                        for series in result["spi"].values()
                    )
                if form == "pt":
                    available = any(
                        result["pt"] is not None
                        and result["pt"].t_anom.notna().any()
                        and result["pt"].p_anom_pct.notna().any()
                        for result in results.values()
                    )
                if form == "timing":
                    available = any(
                        result["timing"].notna().any().any()
                        for result in results.values()
                    )
                fig = (
                    artists.CHARTS[form](view)
                    if available
                    else "Unavailable: no usable data or reference fit for this diagnostic."
                )
                if isinstance(fig, str):
                    availability = re.sub("<[^>]*>", "", fig)
                    fig, axs = artists.new_fig(80)
                    axs[0, 0].text(
                        0.5, 0.5, availability, ha="center", va="center", wrap=True
                    )
                    axs[0, 0].set_axis_off()
                text = (
                    caption(form, view)
                    if form not in {"spi-checks", "sensitivity"}
                    else (
                        "Calendar-month reference SPI gamma/Pearson III fit checks; Shapiro–Wilk p-values are exploratory, not a qualification gate."
                        if form == "spi-checks"
                        else "Start-year Theil–Sen slope sensitivity with dependence-adjusted 95% intervals; at least 15 valid years per fit."
                    )
                )
            text += f" Sources: {', '.join(view.labels.values())}. Support: {support}. Method implementation was exercised on Ntoum real data; this run is not scientifically qualified. Source agreement is not accuracy; input homogeneity is unverified."
            if availability != "available":
                text += f" Availability: {availability}."
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(filename, dpi=600, facecolor="white")
            captioned = paths["render"].get(f"captioned_{form}")
            if captioned:
                Path(captioned).parent.mkdir(parents=True, exist_ok=True)
                artists.add_caption(fig, text)
                fig.savefig(captioned, dpi=600, facecolor="white")
            plt.close(fig)
            relative = str(Path(filename).relative_to(root)).replace("\\", "/")
            contributing = (
                [s for s in sources if results[s]["tclim"] is not None]
                if form == "temperature"
                else sources
            )
            records[relative] = {
                "caption": text,
                "sources": contributing,
                "period": period,
                "reference": settings["reference_period"],
                "support": support,
                "encoding": form,
                "methods": metadata["methods"],
                "availability": availability,
                "captioned_path": str(Path(captioned).relative_to(root)).replace(
                    "\\", "/"
                )
                if captioned
                else None,
                "caveats": [
                    "Not scientifically qualified",
                    "Source agreement is not accuracy",
                    "Input homogeneity unverified",
                ],
            }
    write_json(
        paths["render"]["captions_json"],
        {
            "schema_version": 1,
            "figures": records,
            "anomaly_bounds": bounds,
            "produced_paths": list(records)
            + [r["captioned_path"] for r in records.values() if r["captioned_path"]]
            + ["_engine/figure_captions.json", "figure_captions.md"],
        },
    )
    Path(paths["render"]["captions_md"]).write_text(
        "# Figure captions\n\n"
        + "\n\n".join(
            f"## {key}\n\n{value['caption']}" for key, value in records.items()
        )
        + "\n",
        encoding="utf-8",
    )
    return records
