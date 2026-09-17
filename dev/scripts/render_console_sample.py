"""Render a console transcript per workflow through the REAL handler.

Drives `_ConsoleHandler` with the same synthetic records `tests/test_snake_utils.py`
uses, so what comes out is what a run prints. Every rule row below is the
module's own string literal with only its interpolated values staged; the clock
and the durations are staged too, so a transcript is reproducible.

One spec per workflow in `console_sample_specs.py`; a new workflow costs a
spec rather than a script. Writes `<name>.clean.txt` per workflow plus
`transcripts.json`, into this script's own directory unless `--out` says
otherwise.

Run it to see what a console change actually looks like without executing a
workflow -- which is how the 2026-09-17 styling pass was reviewed:

    pixi run python dev/scripts/render_console_sample.py --out .tmp/console

`dev/scripts/` because it inspects the repo and is never part of a run.
"""

from __future__ import annotations

import datetime as _dt
import io
import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path

from blueearth_cst.shared import console_style as cs
from blueearth_cst.shared import snake_utils as su

HERE = Path(__file__).parent


# --------------------------------------------------------------------------
# harness
# --------------------------------------------------------------------------


class Clock:
    """A fake wall/monotonic clock, so durations and stamps are reproducible."""

    def __init__(self, start_at=_dt.datetime(2026, 9, 17, 9, 12, 3)):
        self.t = 0.0
        self.start_at = start_at

    def advance(self, seconds):
        self.t += seconds

    def monotonic(self):  # `time` shim
        return self.t

    def now(self):  # `datetime` shim
        return self.start_at + _dt.timedelta(seconds=self.t)


def _handler():
    base = logging.StreamHandler(io.StringIO())
    base.name = "DefaultStreamHandler"
    base.setFormatter(logging.Formatter("%(message)s"))
    return cs._ConsoleHandler(base)


def _record(msg="", level=logging.INFO, **extra):
    rec = logging.LogRecord("snakemake", level, __file__, 0, msg, (), None)
    rec.__dict__.update(extra)
    return rec


def _job_info(jobid, name, msg, wildcards=None):
    return _record(
        event="job_info",
        jobid=jobid,
        rule_name=name,
        rule_msg=msg,
        wildcards=dict(wildcards or {}),
    )


@dataclass
class Rule:
    """One `rule_banner(...)` call, as the Snakefile makes it."""

    number: str
    name: str
    context: str | None = None
    summary: str | None = None


@dataclass
class Job:
    """One scheduled job: which rule, its wildcards, how long, what it printed."""

    rule: str
    seconds: float = 2
    wildcards: dict = field(default_factory=dict)
    body: tuple = ()  # ((module, message, gap_before), ...)


@dataclass
class Workflow:
    name: str  # `wf0 analyze_climate`
    project: str
    config: str
    rules: list  # [Rule, ...], `all` included
    stats: str  # Snakemake's `Job stats:` text
    jobs: list  # [Job, ...] in execution order
    targets: list
    elapsed: int
    details: dict = field(default_factory=dict)
    tokens: dict = field(default_factory=dict)


def render(wf: Workflow) -> str:
    cs._RULE_NUMBERS.clear()
    cs._RULE_SUMMARIES.clear()
    # Tokens travel through the environment (`_PATH_TOKENS_ENV`), so clear
    # before declaring or one workflow's tokens leak into the next.
    import os

    os.environ.pop(su._PATH_TOKENS_ENV, None)
    if wf.tokens:
        su.declare_path_tokens(**wf.tokens)
    banners = {
        r.name: cs.rule_banner(r.number, r.name, r.context, r.summary) for r in wf.rules
    }
    cs._RUN_HEADER = (wf.name, wf.project, wf.config, dict(wf.details))

    clock = Clock()
    su.time = clock
    su.datetime = clock

    h = _handler()
    out = h.stream

    def emit(*recs):
        for r in recs:
            h.emit(r)

    def rows(items):
        """Rule stdout, as the tee passes it through: `log_row` lines."""
        saved = sys.stdout
        sys.stdout = out
        try:
            for module, message, gap, *rest in items:
                clock.advance(gap)
                su.log_row(message, module=module, level=(rest[0] if rest else "INFO"))
        finally:
            sys.stdout = saved

    emit(_record(wf.stats, event="run_info"))

    total = len(wf.jobs)
    done = 0
    for jobid, job in enumerate(wf.jobs, start=1):
        # `rule all` prints a target_banner, not a rule_banner: the banner
        # plus one line per declared target.
        msg = (
            cs.target_banner(wf.rules[0].number, "all", wf.targets, wf.project)
            if job.rule == "all"
            else banners[job.rule]
        )
        if job.wildcards:
            msg = msg.format(**job.wildcards)
        emit(_job_info(jobid, job.rule, msg, job.wildcards))
        if job.body:
            rows(job.body)
        clock.advance(job.seconds)
        done += 1
        emit(
            _record(event="job_finished", job_id=jobid),
            _record(event="progress", done=done, total=total),
        )
    h.close()

    text = out.getvalue()
    text += (
        cs.run_summary(
            wf.name,
            wf.project,
            "log",
            "benchmarks",
            elapsed_seconds=wf.elapsed,
        )
        + "\n"
    )
    # Strip the SGR the success verdict adds when stderr looks like a console.
    import re

    return re.sub(r"\x1b\[[0-9;]*m", "", text).replace("\r", "")


def write(name: str, wf: Workflow) -> str:
    text = render(wf)
    (HERE / f"{name}.clean.txt").write_text(text, encoding="utf-8", newline="\n")
    return text


def main(out_dir=None):
    from console_sample_specs import WORKFLOWS

    global HERE
    if out_dir:
        HERE = Path(out_dir)
        HERE.mkdir(parents=True, exist_ok=True)

    payload = {}
    for name, wf in WORKFLOWS.items():
        text = write(name, wf)
        payload[name] = {"label": wf.name, "lines": text.split("\n")}
        sys.stdout.write(f"{name}: {len(payload[name]['lines'])} lines\n")
    (HERE / "transcripts.json").write_text(
        json.dumps(payload, indent=1), encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    _args = sys.argv[1:]
    main(_args[_args.index("--out") + 1] if "--out" in _args else None)
