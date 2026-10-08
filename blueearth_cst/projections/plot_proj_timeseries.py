"""Render WF2 suite products from durable analysis tables.

NOTE: Snakemake ``script:`` module; inputs, outputs and settings come from
``snakemake.input/output/params``. No standalone CLI or future-import preamble.
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from blueearth_cst.climate_analysis.diagnostic_figures import STYLE, add_caption
from blueearth_cst.projections.projection_analysis import MONTHS, PERIODS
from blueearth_cst.projections.projection_captions import caption
from blueearth_cst.projections.projection_figures import SUITE_PRODUCTS
from blueearth_cst.projections.projection_suite_figures import render_product
from blueearth_cst.shared.snake_utils import (
    listed,
    log_row,
    plural,
    save_figure,
    tee_to_log,
)


def figure_counts(filename, tables, window_id=""):
    """Count plotted support, rather than claiming the full resolved ensemble."""
    name = "model_changes"
    if filename.startswith(("trajectory-", "annual-")):
        name = "member_anomalies"
    elif filename.startswith("variability-ratio-"):
        name = "variability_model_ratios"
    elif filename == "variability-member-ratios.png":
        name = "variability_member_ratios"
    elif filename == "availability.png":
        name = "coverage"
    elif filename.startswith("seasonal-cycle-"):
        name = "climatology"
    data = tables[name]
    if window_id and "window_id" in data:
        data = data.loc[data.window_id == window_id]
    if "temperature" in filename or "precipitation" in filename:
        data = data.loc[
            data.variable == ("temp" if "temperature" in filename else "precip")
        ]
    if filename.startswith("change-") and "cloud" not in filename:
        data = data.loc[
            (data.statistic == "mean")
            & (data.quantity == ("change_pct" if "-pct" in filename else "change"))
            & data.period.isin(PERIODS[:5])
        ]
    elif filename.startswith("monthly-change-"):
        data = data.loc[(data.statistic == "mean") & data.period.isin(MONTHS)
                        & (data.quantity == ("change_pct" if "precipitation" in filename else "change"))]
    elif "cloud" in filename:
        data = data.loc[(data.statistic == "mean") & (data.period == "annual")]
        keys = ["model", "scenario", "window_id"]
        temp = data.loc[
            (data.variable == "temp")
            & (data.quantity == "change")
            & np.isfinite(data.value),
            keys,
        ]
        precip = data.loc[
            (data.variable == "precip")
            & (data.quantity == "change_pct")
            & np.isfinite(data.value),
            keys,
        ]
        data = temp.merge(precip, on=keys).drop_duplicates()
    elif filename == "sign-agreement.png":
        data = data.loc[
            (data.statistic == "mean")
            & data.period.isin(("annual", *MONTHS))
            & (
                (data.variable.eq("temp") & data.quantity.eq("change"))
                | (
                    data.variable.eq("precip")
                    & data.quantity.isin(("change", "change_pct"))
                )
            )
        ]
    elif filename.startswith("variability-ratio-"):
        data = data.loc[
            (
                data.statistic
                == ("std_detrended" if "temperature" in filename else "cv_detrended")
            )
            & data.period.isin(PERIODS[:5])
        ]
    elif filename == "variability-member-ratios.png":
        data = data.loc[
            data.period.eq("annual")
            & (
                (data.variable.eq("temp") & data.statistic.eq("std_detrended"))
                | (data.variable.eq("precip") & data.statistic.eq("cv_detrended"))
            )
        ]
    column = (
        "anomaly"
        if filename.startswith("trajectory-")
        else "value"
        if filename.startswith("annual-")
        else "ratio"
        if name == "variability_member_ratios"
        else "value"
        if "value" in data
        else None
    )
    used = data.loc[np.isfinite(data[column].astype(float))] if column else data
    if "available" in used:
        used = used.loc[used.available]
    if "variability_eligible" in used:
        used = used.loc[used.variability_eligible & used.ratio.gt(0)]
    if "reference" in used and "future" in used:
        used = used.loc[np.isfinite(used.reference) & np.isfinite(used.future)]
    return {
        "n_models": used.model.nunique(),
        "by_scenario": used.groupby("scenario").model.nunique().to_dict(),
        "n_excluded": int((~data.variability_eligible).sum())
        if "variability_eligible" in data
        else int(data.n_excluded.sum())
        if "n_excluded" in data
        else 0,
        "n_zero_future": int(data.status.eq("zero_future_variability").sum())
        if "status" in data
        else int(data.n_zero_future.sum())
        if "n_zero_future" in data
        else 0,
    }


def render_suite(
    tables, record, plots_root, *, captioned_figures=False, scenarios=None
):
    """Assert ordinary keys and optional captioned_path metadata bijections.

    Manifest keys identify ordinary figures. Optional copies are identified by
    each entry's captioned_path, relative to plots_root, rather than extra keys.
    """
    if not isinstance(captioned_figures, bool):
        raise TypeError("captioned_figures must be bool")
    root = Path(plots_root)
    log_row(
        "Windows used: "
        + listed(
            [
                f"{w['window_id']} (reference {w['reference'][0]}–{w['reference'][1]})"
                for w in record["windows"]
            ]
        ),
        module="plot_proj_timeseries",
    )
    folders = [
        "full-period",
        *dict.fromkeys(f"period-{w['window_id']}" for w in record["windows"]),
    ]
    for folder in folders:
        (root / folder).mkdir(parents=True, exist_ok=True)
    if captioned_figures:
        (root / "captioned").mkdir(parents=True, exist_ok=True)
    available = tables["availability"]
    expected = {
        (folder, filename)
        for product in SUITE_PRODUCTS.values()
        for folder in folders
        if (folder == "full-period") == (product["folder_kind"] == "full-period")
        for filename in product["filenames"]
    }
    actual = set(zip(available.folder, available.filename))
    if actual != expected or available.duplicated(["folder", "filename"]).any():
        raise ValueError(
            f"availability product contract differs: missing={expected - actual}, extra={actual - expected}"
        )
    manifest, skipped = {}, []
    for row in available.to_dict("records"):
        relative = f"{row['folder']}/{row['filename']}"
        if not isinstance(row["available"], bool):
            raise ValueError("availability flags must be booleans")
        if not row["available"]:
            skipped.append({"path": relative, "reason": row["reason"]})
            continue
        window_id = row.get("window_id") or ""
        counts = figure_counts(row["filename"], tables, window_id)
        text = caption(row["filename"], record, window_id, counts)
        with plt.rc_context(STYLE):
            fig = render_product(
                row["filename"],
                tables,
                record,
                window_id=window_id,
                scenarios=scenarios,
            )
            try:
                save_figure(
                    root / relative,
                    module="plot_proj_timeseries",
                    fig=fig,
                    dpi=600,
                    facecolor="white",
                )
                if captioned_figures:
                    add_caption(fig, text)
                    save_figure(
                        root / "captioned" / relative,
                        module="plot_proj_timeseries",
                        fig=fig,
                        dpi=600,
                        facecolor="white",
                    )
            finally:
                plt.close(fig)
        manifest[relative] = {
            "caption": text,
            "window_id": window_id,
            "counts": counts,
            "horizons": [
                h
                for w in record["windows"]
                if w["window_id"] == window_id
                for h in w.get("horizons", [])
            ],
        }
        if captioned_figures:
            manifest[relative]["captioned_path"] = f"captioned/{relative}"
    pngs = {
        str(path.relative_to(root)).replace("\\", "/")
        for folder in folders
        for path in (root / folder).rglob("*.png")
    }
    if pngs != set(manifest):
        raise RuntimeError(
            f"owned PNGs differ from caption manifest: extra={pngs - set(manifest)}, missing={set(manifest) - pngs}"
        )
    if captioned_figures:
        copies = {
            str(path.relative_to(root)).replace("\\", "/")
            for path in (root / "captioned").rglob("*.png")
        }
        declared_copies = {entry["captioned_path"] for entry in manifest.values()}
        if copies != declared_copies:
            raise RuntimeError(
                f"captioned PNGs differ from caption metadata: extra={copies - declared_copies}, missing={declared_copies - copies}"
            )
    engine = root / "_engine"
    engine.mkdir(parents=True, exist_ok=True)
    (engine / "figure_captions.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    markdown = [
        "# Projection figure captions",
        "",
        "Manifest keys identify ordinary figures; captioned_path metadata identifies optional captioned copies.",
        "",
    ]
    for relative, item in manifest.items():
        markdown.extend([f"## {relative}", "", item["caption"], ""])
    markdown.extend(["## Not produced", ""])
    markdown.extend(f"- {item['path']}: {item['reason']}" for item in skipped)
    markdown.extend(
        [
            "",
            "## Retired paths",
            "",
            "Previous overview/ and windows/ figures are retired in this version; safe to delete.",
            "",
        ]
    )
    (root / "figure_captions.md").write_text("\n".join(markdown), encoding="utf-8")
    log_row(
        f"{plural(len(manifest), 'figure')} written; {plural(len(skipped), 'product')} unavailable",
        module="plot_proj_timeseries",
    )
    return manifest, skipped


def run(sm):
    tables = {Path(path).stem: pd.read_csv(path) for path in sm.input.tables}
    record = json.loads(Path(sm.input.record).read_text(encoding="utf-8"))
    root = Path(sm.output.captions_md).parent
    expected_folders = {
        root / "full-period",
        *(root / f"period-{w['window_id']}" for w in record["windows"]),
    }
    if {Path(path) for path in sm.output.folders} != expected_folders:
        raise ValueError("declared suite folders differ from analysis record")
    tables["availability"]["window_id"] = tables["availability"].window_id.fillna("")
    render_suite(
        tables,
        record,
        root,
        captioned_figures=sm.params.captioned_figures,
        scenarios=getattr(sm.params, "scenarios", None),
    )


if "snakemake" in globals():
    sm = globals()["snakemake"]
    with tee_to_log(sm.log[0]):
        run(sm)
