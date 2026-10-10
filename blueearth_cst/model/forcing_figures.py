"""Model-grid forcing adapter for the reviewed WF0 calculations and artists."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from blueearth_cst.climate_analysis import diagnostic_figures as artists
from blueearth_cst.climate_analysis import diagnostics as dg
from blueearth_cst.climate_analysis.diagnostic_maps import draw_map
from blueearth_cst.climate_analysis.diagnostic_settings import DEFAULTS
from blueearth_cst.plotting import prepared_charts as pc
from blueearth_cst.plotting.fundamentals import MONTH_ABBR, STYLE
from blueearth_cst.shared.variable_registry import CLIMATE_VARS


def prepare_forcing(
    ds: xr.Dataset, inside: xr.DataArray, m0: int
) -> tuple[xr.Dataset, dict, np.ndarray]:
    """Reduce masked model forcing with WF0's default completeness policy.

    Monthly cell sums and counts implement the same cellwise calculation as
    ``diagnostic_maps.annual_fields`` without loading the daily cube eagerly.
    Basin series use equal-weight available cells, as in WF0. Amount gaps are
    infilled only for summaries; the input forcing is never changed.
    """
    missing = set(CLIMATE_VARS) - set(ds.data_vars)
    if missing:
        raise ValueError(f"Forcing is missing required variables: {sorted(missing)}")
    rename = {
        old: new
        for old, new in (("y", "latitude"), ("x", "longitude"))
        if old in ds.dims
    }
    ds = ds.rename(rename)
    inside = inside.rename(
        {old: new for old, new in rename.items() if old in inside.dims}
    )
    if set(inside.dims) != {"latitude", "longitude"}:
        raise ValueError(
            "The model basin mask must have latitude/longitude or y/x dimensions"
        )
    ds, inside = xr.align(ds, inside, join="exact")
    index = pd.DatetimeIndex(ds.time.values)
    if index.empty or not index.is_unique or not index.is_monotonic_increasing:
        raise ValueError(
            "Forcing requires a nonempty, increasing, unique daily time index"
        )
    if not index.equals(index.normalize()) or not 1 <= m0 <= 12:
        raise ValueError(
            "Forcing requires midnight daily timestamps and a start month from 1 to 12"
        )
    calendar = pd.date_range(index.min(), index.max(), freq="D")
    years = dg.full_years(pd.Series(1.0, index=calendar), m0)
    tol = dg.Completeness(
        DEFAULTS["max_missing_days_month"], DEFAULTS["max_missing_days_year"]
    )
    output = xr.Dataset()
    results = {}
    for variable in CLIMATE_VARS:
        field = ds[variable].where(inside).where(np.isfinite(ds[variable]))
        field = field.reindex(time=calendar).chunk(
            {"time": 365, "latitude": 64, "longitude": 64}
        )
        grouped = field.astype("float64").resample(time="MS")
        # Compute monthly summaries and the daily basin series together so dask
        # can share reads, retaining only small reductions in memory.
        reduced = xr.Dataset(
            {
                "sum": grouped.sum().rename({"time": "month"}),
                "count": grouped.count().rename({"time": "month"}),
                "daily": field.mean(("latitude", "longitude")),
            }
        ).compute()
        month_index = pd.DatetimeIndex(reduced.month.values)
        month_days = xr.DataArray(
            pd.Series(1, index=calendar).resample("MS").size().to_numpy(),
            dims="month",
            coords={"month": reduced.month},
        )
        gaps = month_days - reduced["count"]
        # Infilling with each month's observed mean is algebraically equivalent
        # to WF0's daily infill, including annual mean day weighting for Temp.
        filled_sum = (
            reduced["sum"] / reduced["count"].where(reduced["count"] > 0) * month_days
        )
        year_coord = xr.DataArray(
            np.asarray(dg.reporting_year(month_index, m0)),
            dims="month",
            coords={"month": reduced.month},
            name="reporting_year",
        )
        valid = (gaps <= tol.max_month).groupby(year_coord).all() & (
            gaps.groupby(year_coord).sum() <= tol.max_year
        )
        annual = filled_sum.groupby(year_coord).sum().reindex(reporting_year=years)
        if variable == "temp":
            annual = annual / month_days.groupby(year_coord).sum().reindex(
                reporting_year=years
            )
        annual = annual.where(valid.reindex(reporting_year=years, fill_value=False))
        mean = annual.mean("reporting_year")
        mean.attrs = {"units": "degC" if variable == "temp" else "mm/year"}
        for coordinate in ("latitude", "longitude"):
            if ds.sizes[coordinate] > 1:
                mean.attrs[f"{coordinate}_resolution"] = abs(
                    float(ds[coordinate][1] - ds[coordinate][0])
                )
            elif hasattr(ds, "raster"):
                mean.attrs[f"{coordinate}_resolution"] = abs(
                    float(ds.raster.res[0 if coordinate == "longitude" else 1])
                )
        output[variable] = mean
        output[f"{variable}_valid_years"] = annual.count("reporting_year").astype(
            "int32"
        )
        output[f"{variable}_unavailable"] = ~np.isfinite(mean)
        daily = reduced.daily.to_series()
        yearly = dg.annual(daily, m0, "mean" if variable == "temp" else "sum", tol)
        eligible = dg.valid_years(daily, m0, tol)
        climatology = (
            dg.temperature_climatology(daily, m0, eligible, tol)
            if variable == "temp"
            else dg.monthly_climatology(dg.infill(daily, tol), m0, eligible)
        )
        results[variable] = {
            "annual": yearly.to_frame("total"),
            "clim": climatology,
            "trends": {"total": dg.sen_trend(yearly)},
        }
    # Partial boundary years are unavailable summaries, but retain a useful
    # labelled canvas when the entire input is shorter than one full year.
    display_years = years if years.size else np.unique(dg.reporting_year(calendar, m0))
    return output, results, display_years


def render_forcing_figures(
    ds: xr.Dataset,
    inside: xr.DataArray,
    plot_dir: str | Path,
    overlays: dict[str, str | Path],
    m0: int,
    map_extent: list[float] | None = None,
) -> list[Path]:
    """Write nine canonical figures, optionally framed on historical cell edges."""
    fields, results, years = prepare_forcing(ds, inside, m0)
    map_inside = inside.rename(
        {
            old: new
            for old, new in (("y", "latitude"), ("x", "longitude"))
            if old in inside.dims
        }
    )
    index = pd.DatetimeIndex(ds.time.values)
    input_period = [str(index.min().date()), str(index.max().date())]
    all_years = np.unique(dg.reporting_year(index, m0))
    full_years = dg.full_years(
        pd.Series(1.0, index=pd.date_range(index.min(), index.max())), m0
    )
    partial_years = [int(y) for y in all_years if y not in full_years]
    basin_cells = int(inside.sum().compute())
    max_month = DEFAULTS["max_missing_days_month"]
    max_year = DEFAULTS["max_missing_days_year"]
    root = Path(plot_dir)
    root.mkdir(parents=True, exist_ok=True)
    records = {}
    written = []
    for variable in CLIMATE_VARS:
        is_temperature = variable == "temp"
        unit = artists.UNITS["degc" if is_temperature else "mm_year"]
        label = {"precip": "Precipitation", "temp": "Temperature", "pet": "PET"}[
            variable
        ]
        color, marker = artists.SOURCE_STYLE["era5"]
        yearly = results[variable]["annual"]["total"].reindex(years)
        trend = results[variable]["trends"]["total"]
        eligible = yearly.dropna().index.to_numpy()
        trend_unit = "°C decade⁻¹" if is_temperature else artists.UNITS["mm_decade"]
        segments = []
        if np.isfinite(trend["slope"]) and eligible.size:
            span = np.array([eligible[0], eligible[-1]], dtype=float)
            fitted = trend["intercept"] + trend["slope"] / 10 * span
            digits = 2 if is_temperature else 0
            segments.append(
                pc.TrendSegment(
                    color,
                    tuple(span),
                    tuple(fitted),
                    f"{artists.fmt_signed(trend['slope'], digits)} {trend_unit}",
                )
            )
        for kind in ("map", "annual", "monthly"):
            with plt.rc_context(STYLE):
                if kind == "map":
                    field = fields[variable]
                    finite = field.values[np.isfinite(field.values)]
                    limits = (
                        (float(finite.min()), float(finite.max()))
                        if finite.size
                        else (0.0, 1.0)
                    )
                    fig = draw_map(
                        field,
                        variable,
                        "forcing",
                        overlays,
                        limits,
                        fields[f"{variable}_valid_years"],
                        cell_edges=False,
                        inside=map_inside,
                        extent=map_extent,
                    )
                    encoding = (
                        "Mean of eligible reporting-year means"
                        if is_temperature
                        else "Mean of eligible reporting-year totals"
                    )
                    counts = fields[f"{variable}_valid_years"].values
                    positive = counts[counts > 0]
                    count_text = (
                        str(int(positive.min()))
                        if positive.size and positive.min() == positive.max()
                        else f"{int(positive.min())}–{int(positive.max())}"
                        if positive.size
                        else "0"
                    )
                    details = (
                        f"{encoding} at each model cell ({unit}); {count_text} eligible years per available cell. "
                        "White cells are outside the model basin; gray basin cells have no eligible annual values. "
                        "Basin and subbasin boundaries, rivers and gauges are shown where supplied. No spatial interpolation."
                    )
                    available = bool(finite.size)
                elif kind == "annual":
                    fig = pc.annual_series(
                        years,
                        [
                            pc.AnnualLine(
                                "Wflow forcing", color, marker, yearly.to_numpy()
                            )
                        ],
                        ylabel=unit,
                        trends=segments,
                    )
                    details = (
                        f"Reporting-year {'means' if is_temperature else 'totals'} of the daily equal-weight basin-cell mean ({unit}). "
                        "Invalid years remain gaps. The dashed line and slope annotation show the Theil–Sen trend "
                        "per decade, estimated only when at least five eligible annual values are present."
                    )
                    available = bool(results[variable]["annual"].total.notna().any())
                else:
                    climatology = results[variable]["clim"]
                    fig = pc.monthly_cycle(
                        [
                            pc.MonthlyBand(
                                "Wflow forcing",
                                color,
                                marker,
                                climatology["mean"].to_numpy(),
                                climatology["p10"].to_numpy(),
                                climatology["p90"].to_numpy(),
                            )
                        ],
                        month_labels=[MONTH_ABBR[m - 1] for m in dg.month_order(m0)],
                        ylabel=artists.UNITS["degc" if is_temperature else "mm_month"],
                        band_label="10–90th percentile",
                        zero=not is_temperature,
                    )
                    details = (
                        f"Mean monthly {'temperature' if is_temperature else 'total'} (line) and 10–90th percentile band "
                        "across eligible reporting years, from the daily equal-weight basin-cell mean. "
                        "The band describes interannual spread, not a confidence interval."
                    )
                    available = bool(results[variable]["clim"]["mean"].notna().any())
                name = f"forcing_{variable}_{kind}.png"
                path = root / name
                try:
                    fig.savefig(
                        path,
                        dpi=600,
                        facecolor="white",
                        **(
                            {"bbox_inches": "tight", "pad_inches": 2 / 25.4}
                            if kind == "map"
                            else {}
                        ),
                    )
                finally:
                    plt.close(fig)
            caption = (
                f"{label} in Wflow forcing on the model grid, reporting years {years[0]}–{years[-1]}. {details} "
                f"Input dates: {input_period[0]}–{input_period[1]}; basin support: {basin_cells} model cells. "
                f"Reporting years start in month {m0} and carry the start-year label. "
                + (
                    f"Partial boundary reporting years {', '.join(map(str, partial_years))} are excluded. "
                    if partial_years
                    else ""
                )
                + f"Only full reporting years with at most {max_month} missing days in every month and {max_year} "
                "in total are eligible. Tolerated gaps in "
                "annual summaries and amount climatologies use the month's observed mean; monthly temperature "
                "uses observed-day means. The input forcing is unchanged. Model forcing includes the build's "
                "regridding, configured temperature correction and PET derivation."
            )
            records[name] = {
                "caption": caption,
                "sources": ["forcing"],
                "period": [int(years[0]), int(years[-1])],
                "input_period": input_period,
                "basin_cells": basin_cells,
                "partial_years_excluded": partial_years,
                "support": "model basin cells",
                "encoding": kind,
                "availability": "available"
                if available
                else "unavailable: no eligible values",
                "captioned_path": None,
                "methods": {
                    "water_year_start": m0,
                    "year_labels": "start",
                    "max_missing_days_month": max_month,
                    "max_missing_days_year": max_year,
                    "trend": "Theil–Sen",
                    "monthly_spread": "p10–p90",
                    "map_extent": map_extent if kind == "map" else None,
                },
            }
            written.append(path)
    engine = root / "_engine"
    engine.mkdir(exist_ok=True)
    (engine / "figure_captions.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "figures": records,
                "produced_paths": list(records)
                + ["figure_captions.md", "_engine/figure_captions.json"],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "figure_captions.md").write_text(
        "# Figure captions\n\n"
        + "\n\n".join(
            f"## {name}\n\n{record['caption']}" for name, record in records.items()
        )
        + "\n",
        encoding="utf-8",
    )
    return written
