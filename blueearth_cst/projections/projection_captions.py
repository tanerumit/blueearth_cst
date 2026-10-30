"""Recoverable captions for table-driven WF2 projection figures.

Captions follow the geographic-map skeleton: one sentence naming quantity,
units, period, support and any encoding the figure has no key for, plus a
sentence only for a material, figure-specific fact. Caveats shared by every
WF2 figure (spread is not a confidence interval, model dependence,
availability is not eligibility) are stated once in ``SUITE_NOTE``.
"""

from blueearth_cst.climate_analysis.diagnostic_figures import plural
from blueearth_cst.projections.projection_figures import figure_key

TITLES = {
    "availability.png": "CMIP6 ensemble availability",
    "trajectory-temperature.png": "Annual temperature anomalies",
    "trajectory-precipitation.png": "Annual precipitation anomalies",
    "annual-temperature.png": "Annual temperature projections",
    "annual-precipitation.png": "Annual precipitation projections",
    "change-temperature.png": "Annual and seasonal temperature changes",
    "change-precipitation-pct.png": "Annual and seasonal precipitation changes (%)",
    "change-precipitation-abs.png": "Annual and seasonal precipitation changes (absolute)",
    "seasonal-cycle-temperature.png": "Monthly temperature climatology",
    "seasonal-cycle-precipitation.png": "Monthly precipitation climatology",
    "monthly-change-temperature.png": "Monthly temperature changes",
    "monthly-change-precipitation.png": "Monthly precipitation changes (%)",
    "variability-ratio-temperature-sd.png": "Annual and seasonal temperature variability ratios (SD)",
    "variability-ratio-precipitation-sd.png": "Annual and seasonal precipitation variability ratios (SD)",
    "variability-ratio-precipitation-cv.png": "Annual and seasonal precipitation variability ratios (CV)",
    "variability-member-ratios.png": "Annual interannual variability ratios by ensemble member",
    "change-factor-cloud.png": "Annual precipitation and temperature changes",
    "sign-agreement.png": "Model sign agreement in annual and monthly climate changes",
    "change-factor-cloud-combined.png": "Annual precipitation and temperature changes across future periods",
}

#: Stated once for the whole suite, at the head of ``figure_captions.md``.
SUITE_NOTE = (
    "Model spread in these figures is descriptive, not a confidence interval, and models that share "
    "code ancestry are not independent. Each model counts once, with its members averaged first unless "
    "a caption says otherwise. Availability does not imply eligibility for every variable, period or "
    "window. Window definitions, eligibility thresholds and per-figure support and exclusion counts are "
    "recorded in _engine/analysis_record.json and _engine/figure_captions.json."
)

#: The box-and-whisker encoding shared by the change and ratio strips.
_BOXES = (
    "bars mark the median, boxes the interquartile range (where at least 10 models contribute) "
    "and capped lines the full range"
)


def title(filename, record, window_id=""):
    """Name a projection product using its resolved period, not a horizon alias."""
    name = TITLES[figure_key(filename)]
    if window_id:
        window = next(w for w in record["windows"] if w["window_id"] == window_id)
        name += f" — {window['used'][0]}–{window['used'][1]} relative to {window['reference'][0]}–{window['reference'][1]}"
    return f"{name}; CMIP6 basin average"


def _period(window):
    return (
        f"{window['used'][0]}–{window['used'][1]} relative to "
        f"{window['reference'][0]}–{window['reference'][1]}"
    )


def _window_notes(window):
    """Only the window facts a reader could not infer: shifted or joined series."""
    notes = []
    for horizon, supplied in window.get("horizon_windows", {"window": window}).items():
        label = "" if horizon == "window" else f" ({horizon})"
        if supplied.get("shifted"):
            notes.append(
                f"The analysis window{label} was shifted from {supplied['requested']} to "
                f"{supplied['used']} to stay within the scenario runs."
            )
        if supplied.get("joined"):
            notes.append(
                f"Historical and scenario series are joined to complete the window{label}."
            )
    return notes


def _exclusions(counts):
    """Exclusion counts, only when nonzero; the manifest always records them."""
    excluded, zero = counts.get("n_excluded", 0), counts.get("n_zero_future", 0)
    parts = [
        f"{plural(excluded, 'degenerate ratio')} {'is' if excluded == 1 else 'are'} excluded"
        if excluded
        else "",
        f"{plural(zero, 'ratio')} with zero future variability {'is' if zero == 1 else 'are'} excluded"
        if zero
        else "",
    ]
    text = " and ".join(part for part in parts if part)
    return [text[0].upper() + text[1:] + "."] if text else []


def caption(filename, record, window_id="", counts=None):
    """One sentence per figure, plus figure-specific notes only where material."""
    filename = figure_key(filename)
    counts = counts or {}
    window = next(
        (w for w in record.get("windows", []) if w["window_id"] == window_id), None
    )
    models = plural(
        counts.get("n_models", len(record.get("models", []))), "CMIP6 model"
    )
    reference = f"{record['reference'][0]}–{record['reference'][1]}"
    temperature = "temperature" in filename
    variable = "temperature" if temperature else "precipitation"
    notes = _window_notes(window) if window else []

    if filename == "availability.png":
        lead = (
            "Resolved CMIP6 members per model and scenario, with unique historical reference series; "
            "families follow Kuma et al. (2023), with * marking a provisional family and – an unknown one"
        )
    elif filename.startswith("trajectory-"):
        unit = "°C" if temperature else "%"
        lead = (
            f"Annual {variable} anomaly ({unit}) relative to each member's {reference} mean, as the "
            f"median and range of {models} with members faint; the dashed line marks the 2014.5 "
            "historical–scenario handover and shading the analysis window"
        )
    elif filename.startswith("annual-"):
        units = "°C, top" if temperature else "mm yr⁻¹, top"
        anomaly = "°C" if temperature else "%"
        lead = (
            f"Annual {variable} ({units}) and its anomaly ({anomaly}, bottom) relative to each member's "
            f"{reference} mean, per scenario, as individual members, their median and their range; the "
            "dashed line marks the 2014.5 historical–scenario handover and shading the analysis window"
        )
    elif filename.startswith("change-factor-cloud"):
        windows = [
            w for w in record["windows"] if not window_id or w["window_id"] == window_id
        ]
        lead = (
            "Annual mean precipitation (%) and temperature (°C) change, "
            f"{'; '.join(_period(w) for w in windows)}, one point per CMIP6 model and scenario"
        )
        if "combined" in filename:
            notes.append(
                "Lines connect the same model and scenario across future periods."
            )
    elif filename == "sign-agreement.png":
        lead = (
            f"Share of CMIP6 models sharing the sign (+ or −) of the median annual and monthly change, "
            f"{_period(window)}; this measures agreement in direction, not probability or significance"
        )
    elif filename.startswith("seasonal-cycle-"):
        unit = "°C" if temperature else "mm d⁻¹"
        lead = (
            f"Median monthly {variable} ({unit}) across CMIP6 models for {reference} (black, with the "
            f"historical model range shaded) and {window['used'][0]}–{window['used'][1]} by scenario"
        )
    elif filename.startswith("monthly-change-"):
        unit = "°C" if temperature else "%"
        lead = f"Monthly {variable} change ({unit}), {_period(window)}, across {models} by scenario: {_BOXES}"
    elif filename.startswith("change-"):
        unit = (
            "°C" if temperature else "%" if filename.endswith("-pct.png") else "mm d⁻¹"
        )
        lead = (
            f"Annual and seasonal {variable} change ({unit}), {_period(window)}, across {models}: "
            f"{_BOXES}; points are individual models"
        )
    elif filename.startswith("variability-ratio-"):
        statistic = "CV" if filename.endswith("-cv.png") else "SD"
        lead = (
            f"Future-to-reference ratio of detrended interannual {variable} {statistic}, annual and "
            f"seasonal, {_period(window)}, across {models} (geometric mean of members): {_BOXES}; "
            "1 means no change"
        )
        if statistic == "CV":
            notes.append("CV excludes periods with a dry reference or future mean.")
        notes += _exclusions(counts)
    else:  # variability-member-ratios.png
        lead = (
            f"Future-to-reference ratio of detrended annual a) temperature SD, b) precipitation SD and "
            f"c) precipitation CV, {_period(window)}, with members as faint points and {_BOXES} across "
            "models; 1 means no change"
        )
        notes += _exclusions(counts)
    if counts.get("mostly_dry"):
        if filename == "sign-agreement.png":
            notes.append(
                "Hatched cells are excluded: half or more of the models fall below the dry-reference "
                "threshold, leaving too few to judge agreement."
            )
        else:
            shaded = "Gray months" if filename.startswith("monthly-") else "Gray panels"
            notes.append(
                f"{shaded} mark periods where half or more of the models fall below the dry-reference "
                "threshold and are excluded; the models left are too few to be representative."
            )
    return " ".join([f"{lead}.", *notes])
