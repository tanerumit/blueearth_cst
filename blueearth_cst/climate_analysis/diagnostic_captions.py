"""Unnumbered scientific captions reused by Markdown, JSON and optional PNG bands."""

from blueearth_cst.climate_analysis.diagnostic_figures import View

DESCRIPTIONS = {
    "coverage": (
        "Monthly data coverage. Each cell is a reporting-year month: source colour is complete, "
        "a lighter tint has tolerated gaps, and gray is missing or unusable. Annual diagnostics use "
        "only years meeting the completeness rule."
    ),
    "seasonal": (
        "Monthly precipitation climatology. Lines show the mean monthly total; bands span the "
        "10th–90th percentiles across available years. Months follow the reporting-year order."
    ),
    "temperature": (
        "Monthly temperature climatology. The line shows mean monthly temperature and the "
        "band spans the 10th–90th percentiles across available years."
    ),
    "timing": (
        "Timing of cumulative annual precipitation reaching 25%, 50% and 75% of each year's total. "
        "Thick bars span the interquartile range, thin lines the observed range, white ticks the median, "
        "and labelled dots the mean day of the reporting year."
    ),
    "anomaly": (
        "Monthly precipitation departures from the calendar-month mean in the reference period. "
        "Red indicates drier and blue wetter months; gray marks missing or incomplete monthly totals. "
        "The colour scale is shared across sources and years."
    ),
    "spi": (
        "Standardized Precipitation Index at 3-, 6- and 12-month accumulation scales. "
        "Red indicates dryness, blue wetness and gray unavailable values; the distribution is fitted "
        "by calendar month using the reference period."
    ),
    "drought-events": (
        "Drought-event duration and accumulated SPI deficit for SPI-3 and SPI-12. "
        "Events are consecutive months below zero that reach SPI ≤ −1; lighter points touch "
        "a data gap or record edge, so their full duration is unknown."
    ),
    "extreme-Rx1day": (
        "Annual maximum one-day precipitation (Rx1day). Each point represents a reporting "
        "year meeting the completeness rule; gaps indicate years without a valid estimate."
    ),
    "extreme-Rx5day": (
        "Annual maximum five-day precipitation (Rx5day), calculated from complete five-day "
        "windows within each reporting year. Gaps indicate years without a valid estimate."
    ),
    "extreme-SDII": (
        "Simple daily intensity index (SDII): mean precipitation on observed wet days in "
        "each valid reporting year. Gaps indicate years without a valid estimate."
    ),
    "extreme-Wet days": (
        "Annual wet-day count, scaled from observed days to the full reporting year. "
        "Gaps indicate years without a valid estimate."
    ),
    "spell": (
        "Exceedance probability of dry-spell length on a logarithmic probability axis. "
        "A dry day falls below the wet-day threshold; spells touching gaps or record edges "
        "are excluded."
    ),
    "acf": (
        "Autocorrelation of monthly precipitation anomalies at lags of 1–12 months. "
        "Pearson correlations use only pairs with usable monthly totals; no significance "
        "threshold is shown."
    ),
    "slopes": (
        "Theil–Sen trends in annual precipitation, wet days and Rx1day. Points are slope estimates "
        "and whiskers are 95% intervals adjusted for lag-1 serial dependence; filled points "
        "have a two-sided Mann–Kendall p < 0.05."
    ),
    "series": (
        "Annual precipitation totals and descriptive Theil–Sen trend lines. End labels give "
        "the slope per decade; totals are shown only for valid reporting years."
    ),
    "pt": (
        "Seasonal precipitation anomalies against temperature anomalies. Precipitation is relative "
        "to its reference-season mean and temperature is an absolute departure; each point is a "
        "reporting year. The precipitation axis varies by season."
    ),
}


def caption(name: str, view: View) -> str:
    """Return a brief journal-style caption without a figure-number prefix."""
    plotted = (
        [s for s in view.sources if view.results[s]["tclim"] is not None]
        if name == "temperature"
        else view.sources
    )
    sources = ", ".join(view.labels[s] for s in plotted)
    identity = f"{sources}; " if len(view.sources) == 1 or name == "temperature" else ""
    period = f"{view.years[0]}–{view.years[-1]}"
    context = f"{identity}{period}; {view.support}."
    detail = DESCRIPTIONS[name]
    if name == "anomaly" or name == "spi":
        if view.reference[0] == view.years[0] and view.reference[1] == view.years[-1]:
            context = f"{identity}{period} (reference period); {view.support}."
        else:
            detail += f" Reference: {view.reference[0]}–{view.reference[1]}."
    if name == "spi":
        distribution = view.results[view.sources[0]]["spi_dist"]
        detail += (
            f" Fit: {'Pearson III' if distribution == 'pearson3' else distribution}."
        )
    if name in {"extreme-SDII", "extreme-Wet days", "spell"}:
        detail += f" Wet day: ≥{view.wet_mm:g} mm."
    if name == "coverage":
        detail += (
            f" Usable months permit ≤{view.max_missing_month} missing days; valid years "
            f"permit ≤{view.max_missing_year} in total."
        )
    if name == "spell":
        counts = ", ".join(
            f"{view.labels[s]} {view.results[s]['n_spells']}" for s in view.sources
        )
        detail += f" Complete spells: {counts}."
    if name == "acf":
        pairs = []
        for s in view.sources:
            values = view.results[s]["acf"]["pairs"]
            pairs.append(f"{view.labels[s]} {values.min()}–{values.max()}")
        detail += f" Pairs per lag: {', '.join(pairs)}."
    if name == "pt":
        t_source = next(
            (
                view.results[s]["t_source"]
                for s in view.sources
                if view.results[s]["pt"] is not None
            ),
            None,
        )
        if t_source:
            detail += f" Temperature source: {t_source}."
    return f"{detail} {context}"
