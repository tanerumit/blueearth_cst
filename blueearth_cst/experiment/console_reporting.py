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


def matching_sets(sets, calculations):
    """Return every user-facing set sharing this calculation request."""
    from blueearth_cst.experiment.indicator_sets import calculation_records

    return [
        item for item in sets if calculation_records(item.indicators) == calculations
    ]


class _PlanStream:
    """Route the producer's technical planning row to the full Snakemake log."""

    def __init__(self, stream, root=None):
        self.stream = stream
        self.root = root

    def __getattr__(self, name):
        return getattr(self.stream, name)

    def write(self, text):
        if re.fullmatch(
            r"\d{2}:\d{2}:\d{2} - indicators - Indicator set \w+ planned: "
            r"\d+ indicator declarations?; \d+ expected result keys?\n",
            text,
        ):
            record_indicator_detail(self.root, text.rstrip())
            return len(text)
        return self.stream.write(text)


def prepare_indicator_plan(root, request, sets):
    """Keep numerical planning unchanged and present its outcome by set name."""
    from blueearth_cst.experiment.indicator_plan import write_indicator_plan

    with redirect_stdout(_PlanStream(sys.stdout, root)):
        plan = write_indicator_plan(root, request)
    for item in matching_sets(sets, request["calculations"]):
        log_row(
            f"{item.set_id}: ready to calculate {plural(len(item.indicators), 'indicator')}",
            module="indicators",
        )
    return plan


def result_counts(root: Path, manifest: dict) -> tuple[int, int]:
    """Count available and missing/invalid results in validated tables."""
    finite = nonfinite = 0
    for table in manifest["tables"]:
        with (root / table["file"]["path"]).open(
            encoding="utf-8", newline=""
        ) as handle:
            for row in csv.DictReader(handle):
                value = row["value"]
                if value and math.isfinite(float(value)):
                    finite += 1
                else:
                    nonfinite += 1
    return finite, nonfinite


def report_indicator_set(root: Path, manifest: dict, sets=(), *, reused=False) -> None:
    """Report completed calculation work using selected indicator-set names."""
    record_indicator_detail(
        root,
        f"Indicator set {manifest['indicator_set_id']}; "
        f"manifest → {root / manifest['engine_root'] / 'indicators.json'}",
    )
    for item in matching_sets(sets, manifest.get("calculations", [])):
        action = "reusing calculated results" if reused else "calculations complete"
        log_row(f"{item.set_id}: {action}", module="indicators")
