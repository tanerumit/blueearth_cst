"""Console summaries from already-validated retained artifacts; no model calculations."""

import csv
import logging
import math
import re
import sys
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

from blueearth_cst.shared.run_log_core import _write_console, log_row, plural


def record_indicator_detail(root, message):
    """Retain technical details even in Snakemake workers without file handlers."""
    # Snakemake's asynchronous file handler can inherit a legacy Windows
    # encoding. Keep that copy ASCII-safe; the dedicated log retains UTF-8.
    native_message = message.encode("ascii", "backslashreplace").decode("ascii")
    logging.getLogger("snakemake.logging").info("Indicator details: " + native_message)
    if root is not None:
        from blueearth_cst.shared.execution_outputs import current_directory

        directory = current_directory()
        path = (
            directory / "wf4-indicators.log"
            if directory
            else Path(root) / "logs/wf4_indicators.log"
        )
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(f"{datetime.now():%H:%M:%S} - {message}\n")
        except OSError:
            # A console-only failure must not stop calculation or lose details.
            _write_console(sys.stdout, "Indicator details: " + message + "\n")


def matching_sets(sets, document):
    """Return every user-facing set sharing this request or manifest.

    ``document`` is a request, plan request or manifest; its calculable and
    unavailable records together are the set's selection.
    """
    from blueearth_cst.experiment.indicator_plan import selected_calculations
    from blueearth_cst.experiment.indicator_sets import calculation_records

    calculations = selected_calculations(document)
    return [
        item for item in sets if calculation_records(item.indicators) == calculations
    ]


def unavailable_summary(document) -> list[str]:
    """One short phrase per unavailable indicator: its locations or response."""
    phrases = [
        f"{item['calculation']['indicator']} ({', '.join(item['reasons'])})"
        for item in document.get("unavailable_calculations", [])
    ]
    by_indicator = {}
    for row in document.get("unavailable_results", []):
        by_indicator.setdefault((row["indicator"], row["reason"]), []).append(
            row["location"]
        )
    phrases += [
        f"{indicator} at {plural(len(locations), 'location')} ({reason})"
        for (indicator, reason), locations in sorted(by_indicator.items())
    ]
    return phrases


class _PlanStream:
    """Route the producer's technical planning row to the full Snakemake log."""

    def __init__(self, stream, root=None):
        self.stream = stream
        self.root = root

    def __getattr__(self, name):
        return getattr(self.stream, name)

    def write(self, text):
        # On a terminal `log_row` paints the row; match and record it plain.
        plain = re.sub(r"\x1b\[[0-9;]*m", "", text)
        if re.fullmatch(
            r"\d{2}:\d{2}:\d{2} - indicators - Indicator set \w+ planned: "
            r"\d+ indicator declarations?; \d+ expected result keys?\n",
            plain,
        ):
            record_indicator_detail(self.root, plain.rstrip())
            return len(text)
        return self.stream.write(text)


def prepare_indicator_plan(root, request, sets, evaluation="strict"):
    """Keep numerical planning unchanged and present its outcome by set name.

    Strict evaluation refuses a request with unavailable entries before planning.
    """
    from blueearth_cst.experiment.indicator_plan import write_indicator_plan
    from blueearth_cst.shared.snake_utils import listed

    unavailable = unavailable_summary(request)
    if unavailable and evaluation == "strict":
        names = ", ".join(item.set_id for item in matching_sets(sets, request))
        raise ValueError(
            f"{names or 'selected set'}: selected indicators lack inputs: "
            f"{listed(unavailable)}. Exclude them with indicator_selection, supply "
            "the missing parameter, or set indicator_evaluation: partial"
        )
    with redirect_stdout(_PlanStream(sys.stdout, root)):
        plan = write_indicator_plan(root, request)
    for item in matching_sets(sets, request):
        log_row(
            f"{item.set_id}: ready to calculate {plural(len(item.indicators), 'indicator')}",
            module="indicators",
        )
    return plan


def result_counts(root: Path, manifest: dict) -> tuple[int, int, int]:
    """Count available, undefined and unavailable results in validated tables.

    Tables before indicator-set/6 have no status; their NaN is undefined.
    """
    counts = {"available": 0, "undefined": 0, "unavailable": 0}
    for table in manifest["tables"]:
        with (root / table["file"]["path"]).open(
            encoding="utf-8", newline=""
        ) as handle:
            for row in csv.DictReader(handle):
                value = row["value"]
                status = row.get("status") or (
                    "available"
                    if value and math.isfinite(float(value))
                    else "undefined"
                )
                counts[status] += 1
    return counts["available"], counts["undefined"], counts["unavailable"]


def report_indicator_set(root: Path, manifest: dict, sets=(), *, reused=False) -> None:
    """Report completed calculation work using selected indicator-set names."""
    record_indicator_detail(
        root,
        f"Indicator set {manifest['indicator_set_id']}; "
        f"manifest → {root / manifest['engine_root'] / 'indicators.json'}",
    )
    from blueearth_cst.shared.snake_utils import listed

    unavailable = unavailable_summary(manifest)
    for item in matching_sets(sets, manifest):
        action = "reusing calculated results" if reused else "calculations complete"
        log_row(f"{item.set_id}: {action}", module="indicators")
        if unavailable:
            # The warning row belongs to publication; keep the detail here.
            record_indicator_detail(
                root, f"{item.set_id}: unavailable indicators: {listed(unavailable)}"
            )
