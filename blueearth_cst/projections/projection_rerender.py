"""Re-render WF2 projection figures (rule 2.06) from a finished run.

Calls ``plot_proj_timeseries.render_suite`` on the run's retained analysis
tables and record, writing to a separate directory: a few minutes at 600 dpi,
not a WF2 rerun.
Scenario order falls back to the IPCC colour order rather than the run config.
Front end: ``scripts/render_figures.py``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

#: Where WF2 writes each ensemble's products, relative to ``project_dir``.
PROJECTIONS_DIR = Path("data") / "climate" / "projections"


def rerender_projections(
    project_dir: str | Path, out_dir: str | Path, annotation: str = "none"
) -> dict[str, Path]:
    """Write each ensemble's suite into ``out_dir/projections/<ensemble>/plots``."""
    from blueearth_cst.projections.plot_proj_timeseries import render_suite
    from blueearth_cst.projections.projection_figures import FIGURE_KEYS

    records = sorted(
        (Path(project_dir) / PROJECTIONS_DIR).glob("*/_engine/analysis_record.json")
    )
    if not records:
        raise FileNotFoundError(f"{project_dir}: no retained WF2 analysis record")
    written = {}
    for record_path in records:
        ensemble_dir = record_path.parents[1]
        tables = {
            path.stem: pd.read_csv(path)
            for path in (ensemble_dir / "analysis").glob("*.csv")
        }
        availability = tables["availability"]
        availability["window_id"] = availability.window_id.fillna("")
        # A run made before a product was retired still lists it; render the
        # current contract rather than failing on the extra row.
        tables["availability"] = availability.loc[
            availability.filename.isin(FIGURE_KEYS)
        ]
        plot_dir = Path(out_dir) / "projections" / ensemble_dir.name / "plots"
        render_suite(
            tables,
            json.loads(record_path.read_text(encoding="utf-8")),
            plot_dir,
            annotation=annotation,
            captions_json=plot_dir.parent / "_engine" / "figure_captions.json",
        )
        written[ensemble_dir.name] = plot_dir
    return written
