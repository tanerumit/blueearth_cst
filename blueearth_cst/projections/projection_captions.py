"""Recoverable captions for table-driven WF2 projection figures."""

from blueearth_cst.climate_analysis.diagnostic_figures import plural
from blueearth_cst.projections.projection_figures import figure_key


def _mask(years):
    """Compact exact coordinates: span, count and any internal missing labels."""
    if not years:
        return "none"
    years = sorted(years)
    missing = sorted(set(range(years[0], years[-1] + 1)) - set(years))
    return (
        f"{years[0]}–{years[-1]} (n={len(years)}"
        + (f", missing={missing}" if missing else "")
        + ")"
    )


def caption(filename, record, window_id="", counts=None):
    """State windows, weighting, benchmark assumptions and exclusions explicitly."""
    filename = figure_key(filename)
    counts = counts or {}
    if filename == "availability.png":
        return (
            "CMIP6 ensemble availability. Numbers give resolved member counts for each model and "
            "scenario; historical counts give unique loaded reference series associated with resolved "
            "scenario members. Zero indicates no resolved or loaded member in this ensemble, not "
            "necessarily absence from the CMIP6 archive. Availability does not guarantee eligibility "
            "for every variable, period, or analysis window. Families describe model code genealogy "
            "using the mapping attributed to Kuma et al. (2023, doi:10.1029/2022MS003588; Zenodo "
            "record 7920408). An asterisk marks a provisional family inferred from institution; "
            "? marks an unknown family. Parentheses identify institution and country where known. "
            "Family labels do not imply statistical independence within or between families."
        )
    if filename == "sign-agreement.png":
        window = next(w for w in record["windows"] if w["window_id"] == window_id)
        return (
            f"CMIP6 sign agreement in annual and monthly mean changes for {window['used'][0]}–"
            f"{window['used'][1]} relative to {window['reference'][0]}–{window['reference'][1]}. "
            "Each model contributes once after averaging its members. Cell signs indicate the sign "
            "of the median model change: + denotes increase and − decrease. Counts k/n give the "
            "number of models sharing that sign out of the eligible models; darker fills indicate "
            "stronger agreement. Blue denotes increase and red decrease. Agreement measures "
            "consistency of direction, not change magnitude, a probability, or statistical "
            "significance. Models sharing code ancestry are not independent, so model counts need "
            "not represent independent lines of evidence."
        )
    if filename.startswith("change-factor-cloud"):
        windows = [
            w for w in record["windows"] if not window_id or w["window_id"] == window_id
        ]
        periods = "; ".join(
            f"{w['used'][0]}–{w['used'][1]} relative to {w['reference'][0]}–{w['reference'][1]}"
            for w in windows
        )
        return (
            f"CMIP6 annual mean changes for {periods}. Each point pairs precipitation and "
            "temperature changes from the same model and scenario, with members averaged within "
            "each model first. Colors identify scenarios. Precipitation changes are percentages "
            "of the reference mean; temperature changes are in °C. Zero reference lines indicate "
            "no change. The cloud shows descriptive model spread, not probabilities or a confidence "
            "region; models from the same code family may be dependent."
            + (
                " Lines connect the same model and scenario across future periods."
                if "combined" in filename
                else ""
            )
        )
    if filename == "variability-member-ratios.png":
        window = next(w for w in record["windows"] if w["window_id"] == window_id)
        return (
            f"Annual interannual variability ratios for {window['used'][0]}–{window['used'][1]} "
            f"relative to {window['reference'][0]}–{window['reference'][1]}: a) temperature SD, "
            "b) precipitation SD, and c) precipitation CV. Members are detrended separately within "
            "each window. Faint points show individual members; capped lines span the model range, "
            "outline boxes show the model interquartile range where at least 10 models contribute, "
            "and thick bars show the model median. Member ratios are averaged geometrically within "
            "each model before summarizing across equally weighted models. Members from one model "
            "are dependent; model spread is descriptive and is not a confidence interval. A ratio "
            "of 1 indicates no change. Precipitation SD uses annual mean daily rates; CV uses "
            "detrended SD of annual totals divided by their original mean. These aggregations can "
            "differ when year lengths vary. Dry reference or future means are excluded from CV. "
            f"Excluded degenerate ratios: {counts.get('n_excluded', 0)}; "
            f"zero-future ratios: {counts.get('n_zero_future', 0)}."
        )
    models = counts.get("n_models", len(record.get("models", [])))
    text = [f"CMIP6 projections: {filename.removesuffix('.png').replace('-', ' ')}."]
    if filename.startswith(("seasonal-cycle-", "monthly-change-")):
        window = next(w for w in record["windows"] if w["window_id"] == window_id)
        text.append(
            f"Reference water years {window['reference'][0]}–{window['reference'][1]}; "
            f"future water years {window['used'][0]}–{window['used'][1]}."
        )
        if filename.startswith("seasonal-cycle-"):
            text.append(
                "Lines show the median monthly climatology across models, with members averaged first. "
                "Black denotes the historical reference and colors denote future scenarios. Gray shading "
                "spans the historical model range; future spread is shown in the companion monthly-change "
                "figure. The historical climatology uses the first displayed scenario's contributing models."
            )
        else:
            text.append(
                "Each panel shows one scenario's monthly changes. Capped lines span the model range, "
                "outline boxes show the interquartile range where at least 10 models contribute, and "
                "thick horizontal bars show the median. Members are averaged within each model first. "
                "Zero indicates no change; precipitation changes are percentages of the reference rate."
            )
        text.append("Model spread is descriptive and is not a confidence interval.")
        return " ".join(text)
    if window_id:
        for window in record.get("windows", []):
            if window["window_id"] != window_id:
                continue
            text.append(
                f"Analysis future WY {window['used'][0]}–{window['used'][1]}; analysis reference WY {window['reference'][0]}–{window['reference'][1]}."
            )
            configured = window.get("configured", {})
            if isinstance(configured, dict):
                for horizon, pair in configured.items():
                    if isinstance(pair, dict):
                        text.append(
                            f"Configured horizon {horizon}: future {pair['future'][0]}–{pair['future'][1]}, reference {pair['reference'][0]}–{pair['reference'][1]}."
                        )
                    else:
                        text.append(
                            f"Configured horizon {horizon}: {pair[0]}–{pair[1]}."
                        )
            else:
                text.append(
                    f"Configured future window: {configured[0]}–{configured[1]}."
                )
            text.append("The change-factor CSV uses the configured windows.")
            for period, bounds in window.get("effective", {}).items():
                text.append(
                    f"Effective {period}: {bounds['start']}–{bounds['end']} "
                    f"({bounds['n_water_years']} complete water years)."
                )
            original = window.get("horizon_windows", {"window": window})
            for horizon, supplied in original.items():
                if supplied.get("shifted"):
                    text.append(
                        f"Far-end shift ({horizon}): requested {supplied['requested']} → used {supplied['used']}."
                    )
                if supplied.get("joined"):
                    text.append(
                        f"Historical + scenario series joined to complete the analysis window ({horizon})."
                    )
        text.append(
            "Seasonal precipitation absolute and percentage changes use rates; the lab's total-based percentages are a documented parity exception. CV uses period integrals."
        )
    if filename.startswith(("change-", "variability-ratio-", "trajectory-")):
        text.append(
            f"Ensemble spread across {plural(models, 'model')} (equal model weight), not a confidence interval; models from one code family count separately."
        )
    if filename.startswith("trajectory-"):
        text.append(
            f"Bold lines show the median across {plural(models, 'model')}, with members averaged first; "
            "ribbons span the model range. Black denotes the historical run and scenario colors the future "
            "runs; faint traces are individual members. Annual values are unsmoothed, so the range includes "
            "year-to-year variability and is not a confidence interval. Each member uses its own "
            f"{record['reference'][0]}–{record['reference'][1]} reference mean. Pale shading marks the future "
            "analysis windows; the dashed line marks the current year."
        )
    if filename.startswith("annual-"):
        text.append(
            f"Absolute annual values are shown above and anomalies relative to each member's "
            f"{record['reference'][0]}–{record['reference'][1]} mean below. "
            + (
                "Precipitation totals are in mm yr⁻¹ and anomalies are percentages. "
                if "precipitation" in filename
                else "Temperature and its anomalies are in °C. "
            )
            + "Thin gray lines show individual historical members and thin scenario-colored lines "
            "show individual future members. Thick black lines show historical member medians; "
            "thick scenario-colored lines show future member medians. Colored envelopes span the "
            "member range, not a confidence "
            "interval or an equal-model reduction. The dashed line marks the historical–scenario "
            "transition at 2014.5; pale shading marks the future analysis windows. Missing years remain gaps."
        )
    if filename.startswith("change-") and "cloud" not in filename:
        text.append(
            "Panels show annual and seasonal changes. Outlined boxes span the model interquartile range "
            "where at least 10 models contribute; horizontal bars mark medians and capped vertical lines "
            "span the full model range. Faint points show individual models, with members averaged first "
            "and horizontal jitter for legibility. Zero indicates no change."
        )
    if filename.startswith("variability-"):
        if filename.startswith("variability-ratio-"):
            window = next(w for w in record["windows"] if w["window_id"] == window_id)
            text = [
                f"CMIP6 interannual variability: {filename.removesuffix('.png').replace('-', ' ')}.",
                f"Future/reference ratios for {window['used'][0]}–{window['used'][1]} relative to "
                f"{window['reference'][0]}–{window['reference'][1]}. Model spread is descriptive, "
                "not a confidence interval.",
            ]
            text.append(
                "Ratios above 1 indicate increased interannual variability and ratios below 1 "
                "indicate decreased variability. Each member is detrended separately within each "
                "window; model ratios are geometric means of member ratios and models have equal weight."
            )
            if "precipitation" in filename:
                text.append(
                    "Precipitation SD is calculated from period mean daily rates; precipitation CV "
                    "uses detrended SD of period totals divided by their original mean. These "
                    "aggregations can differ when period lengths vary. CV excludes periods with dry "
                    "reference or future means."
                )
            text.append(
                "Outlined boxes show the model interquartile range where at least 10 models "
                "contribute, thick bars show the median, capped lines span the model range and "
                "faint points show models. Sampling benchmarks are not displayed in this figure."
            )
            text.append(
                f"Excluded degenerate ratios: {counts.get('n_excluded', 0)}; "
                f"zero-future ratios: {counts.get('n_zero_future', 0)}."
            )
            return " ".join(text)
        null = record.get("methods", {}).get("null_band", {})
        text.append(
            f"90 % range of this ratio expected from sampling alone if variability did not change, assuming year-to-year white noise; autocorrelation widens it. Separate OLS residual SD uses ddof=0 on actual retained years; CV divides integral SD by integral mean. Gaussian draws={null.get('simulations', 20000)}, seed={null.get('seed', 20261007)}; overlapping years share draws. Invalid CV draws with nonpositive means are counted; valid-draw bands are conditional on positive means."
        )
        if filename != "variability-member-ratios.png":
            text.append(
                "Where available, shaded single-member benchmarks are supplied per exact retained-mask pair; precipitation uses the ensemble-median reference CV. Model markers are filled outside their own heterogeneous-member geometric-mean band. Ensemble geometric-marker summaries use log-space quantiles."
            )
        else:
            text.append(
                "Each member interval uses that member's own retained reference/future coordinates and reference SD, or its own reference CV for precipitation. Exact parameters, overlap coordinates, valid and invalid draw counts are retained in variability_member_ratios.csv."
            )
        bands = [
            band
            for band in record.get("display_null_bands", [])
            if band.get("window_id") == window_id
            and (
                filename == "variability-member-ratios.png"
                or band.get("variable")
                == ("temp" if "temperature" in filename else "precip")
            )
            and (
                filename != "variability-member-ratios.png"
                or band.get("period") == "annual"
            )
        ]
        if bands and filename != "variability-member-ratios.png":
            text.append(
                "Benchmark masks and overlap: "
                + "; ".join(
                    f"{b.get('scenario')}/{b.get('period')}/{b.get('variable')}: reference {_mask(b.get('reference_years', []))}, future {_mask(b.get('future_years', []))}, overlap {b.get('overlap')}, referenceCV {b.get('reference_cv')}, valid {b.get('n_valid')}, invalid {b.get('n_invalid')}"
                    for b in bands
                )
                + "."
            )
        elif filename != "variability-member-ratios.png":
            text.append(
                "No prepared display benchmark is available; no shaded band is shown."
            )
        text.append(
            f"Excluded degenerate ratios: {counts.get('n_excluded', 0)}; zero-future ratios: {counts.get('n_zero_future', 0)}."
        )
        if filename == "variability-member-ratios.png":
            text.append(
                "Faint vertical intervals are each member's own exact-mask single-member null band; filled points fall outside it. Each eligible member has weight 1/eligible-members-of-its-model in pooled log quantiles. Pooled quantiles are ensemble spread and carry no band."
            )
    return " ".join(text)
