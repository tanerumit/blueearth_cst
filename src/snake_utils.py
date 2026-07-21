"""Shared helpers for the BlueEarth-CST Snakefiles.

Imported by all three ``Snakefile_*`` entry points (and ``tests/conftest.py``)
so the ``get_config`` contract lives in exactly one place. Each Snakefile makes
this module importable regardless of the working directory by prepending its
own directory to ``sys.path`` before importing — see
``dev/r03/model-builder-design.md`` §3.
"""

import contextlib
import os
import re
import subprocess
import sys
from collections.abc import Mapping
from datetime import datetime


# hydromt formats every log record as
# ``<ts> - <name> - <module> - <LEVEL> - <message>`` (its hardcoded
# ``_LOG_FORMAT``; no CLI/env/config override exists). ``<ts>`` is a full
# ``YYYY-MM-DD HH:MM:SS,mmm`` stamp, ``<name>`` the dotted logger path
# (``hydromt.model.model``), ``<module>`` its leaf (``model``) — all verbose or
# redundant per row. We cannot change hydromt's format (vendored, off-limits),
# so both tee paths below rewrite matching lines into *our* logs: drop the
# dotted ``<name>`` (keep ``<module>`` as a short subsystem tag) and shorten the
# stamp to ``HH:MM:SS`` (the date lives once in the log header, not on every
# row). Only lines matching this exact shape are rewritten; everything else
# (Julia/Wflow output, tracebacks, plain prints) passes through verbatim.
_HYDROMT_LOG_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2} (\d{2}:\d{2}:\d{2}),\d{3} - \S+ - (\S+) - (\w+) - (.*)$"
)


def _compact_log_line(text):
    """Compact a hydromt-format log line: ``HH:MM:SS`` stamp, drop dotted name.

    ``<YYYY-MM-DD HH:MM:SS,mmm> - <name> - <module> - <LEVEL> - <msg>`` becomes
    ``<HH:MM:SS> - <module> - <LEVEL> - <msg>``. A trailing newline is preserved.
    Non-matching text is returned unchanged, so the tee stays faithful for all
    output that is not a single hydromt log record.
    """
    had_newline = text.endswith("\n")
    core = text[:-1] if had_newline else text
    match = _HYDROMT_LOG_RE.match(core)
    if not match:
        return text
    hms, module, level, message = match.groups()
    return f"{hms} - {module} - {level} - {message}" + ("\n" if had_newline else "")


def _log_path_parts(log_path):
    """Return ``(project_root, log_id)`` derived from a rule log path.

    The parent of the first ``logs`` / ``benchmarks`` path component is the
    project dir; the path below that anchor is the rule-log id (so wildcard
    sub-logs read e.g. ``3.10_run_wflow/rlz_1_cst_1.log``). Both are ``""`` /
    the bare basename when the anchor is absent (e.g. an ad-hoc test path).
    """
    log_path = os.fspath(log_path)
    parts = os.path.normpath(log_path).split(os.sep)
    for anchor in ("logs", "benchmarks"):
        if anchor in parts:
            i = parts.index(anchor)
            root = os.sep.join(parts[:i]) if i > 0 else ""
            log_id = "/".join(parts[i + 1:]) or os.path.basename(log_path)
            return root, log_id
    return "", os.path.basename(log_path)


def _relativize_paths(text, project_root):
    """Rewrite absolute project paths in ``text`` as project-relative.

    Strips the ``project_root`` prefix (in both native and forward-slash forms,
    since hydromt emits either) so a log line like
    ``Writing geoms to C:\\...\\gabon\\hydrology_model\\...\\basins.geojson``
    reads ``Writing geoms to hydrology_model\\...\\basins.geojson``. Paths
    outside the project (data catalogs, the pixi env) are left absolute.
    """
    if not project_root:
        return text
    text = text.replace(project_root + os.sep, "")
    text = text.replace(project_root.replace(os.sep, "/") + "/", "")
    return text


def _log_header_lines(log_path):
    """Return the header block written at the top of each rule log.

    Carries the project name and run date (the date dropped from each row by
    ``_compact_log_line``), the full project dir, and the rule-log id + start
    time, followed by a blank line separating the header from the log body.
    """
    now = datetime.now()
    root, log_id = _log_path_parts(log_path)
    project = os.path.basename(root) if root else ""
    project_field = f"project: {project} | " if project else ""
    header = [f"# BlueEarth-CST | {project_field}{now:%Y-%m-%d}"]
    if root:
        header.append(f"# project dir: {root.replace(os.sep, '/')}")
    header.append(f"# log: {log_id} | started {now:%H:%M:%S}")
    # trailing "" -> a blank line between the header and the body
    return "".join(line + "\n" for line in header) + "\n"


def get_config(config, arg, default=None, optional=True):
    """Read a config key, returning a default for optional missing keys.

    Parameters
    ----------
    config : Mapping
        Config section to read from.
    arg : str
        Key to look up.
    default : Any, optional
        Value returned when ``arg`` is absent and ``optional`` is True.
    optional : bool, optional
        When False, a missing ``arg`` raises ``ValueError`` instead of
        returning ``default``.

    Returns
    -------
    Any
        ``config[arg]`` when present — including ``None`` and other falsey
        values, which are returned as-is rather than replaced by ``default``.
        Otherwise ``default`` for optional keys.

    Raises
    ------
    ValueError
        If ``arg`` is absent and ``optional`` is False.
    """
    if arg in config:
        return config[arg]
    elif optional:
        return default
    else:
        raise ValueError(f"Argument {arg} not found in config")


def _require_step_num(axis_cfg, axis_name):
    """Read and validate a required ``step_num`` from a stress-test axis section.

    Strict by contract: a missing axis section or ``step_num`` raises
    ``KeyError`` (parity with ``prepare_cst_parameters.py``'s direct read); a
    ``step_num`` that is not a non-negative integer raises ``ValueError``.
    ``bool`` is rejected — ``True``/``False`` are not valid grid step counts.
    """
    step_num = axis_cfg[axis_name]["step_num"]  # KeyError on missing axis/key
    if isinstance(step_num, bool) or not isinstance(step_num, int):
        raise ValueError(
            f"stress_test.{axis_name}.step_num must be a non-negative int, "
            f"got {step_num!r}"
        )
    if step_num < 0:
        raise ValueError(
            f"stress_test.{axis_name}.step_num must be non-negative, got {step_num}"
        )
    return step_num


def stress_test_grid(stress_test_cfg: Mapping) -> tuple[int, int, int]:
    """Return ``(temp_step_count, precip_step_count, st_num)`` for a stress_test cfg.

    Single source of truth for the stress-test grid arithmetic, which was
    previously derived twice (inline in ``Snakefile_climate_experiment`` and in
    ``src/prepare_cst_parameters.py``). Both call sites now read this helper.

    STRICT: ``temp.step_num`` and ``precip.step_num`` are REQUIRED — a missing
    axis section or ``step_num`` raises ``KeyError``, and a value that is not a
    non-negative integer raises ``ValueError``. The helper never silently
    invents a grid. Per-axis step count is ``step_num + 1`` (endpoints
    inclusive), and ``st_num = temp_step_count * precip_step_count``.

    Parameters
    ----------
    stress_test_cfg : Mapping
        The ``workflows.climate_experiment.stress_test`` config section, with
        ``temp`` and ``precip`` axis sub-sections each carrying ``step_num``.

    Returns
    -------
    tuple[int, int, int]
        ``(temp_step_count, precip_step_count, st_num)``.

    Raises
    ------
    KeyError
        If the ``temp``/``precip`` axis section or its ``step_num`` is absent.
    ValueError
        If a ``step_num`` is not a non-negative integer.
    """
    temp_step_count = _require_step_num(stress_test_cfg, "temp") + 1
    precip_step_count = _require_step_num(stress_test_cfg, "precip") + 1
    return temp_step_count, precip_step_count, temp_step_count * precip_step_count


class _Tee:
    """Minimal text stream that forwards writes to several sinks.

    Deliberately not an ``io`` subclass: ``script:`` rules only ``print`` /
    log through ``sys.stdout``/``sys.stderr``, so ``write`` + ``flush`` (plus
    ``isatty``) is all that is needed. Note: this operates at the Python
    stream level, so output from *shell* subprocesses (which inherit the real
    file descriptors) is not captured — only in-process Python output is.
    """

    def __init__(self, *sinks, project_root=""):
        self._sinks = sinks
        self._project_root = project_root

    def write(self, text):
        out = _relativize_paths(_compact_log_line(text), self._project_root)
        for sink in self._sinks:
            sink.write(out)
        return len(text)

    def flush(self):
        for sink in self._sinks:
            sink.flush()

    def isatty(self):
        return False


# Benign CPython interpreter-shutdown noise. A subprocess -- notably the verbose
# ``hydromt build wflow_sbm ... -vv`` step -- can emit a repeating
# ``Error in sys.excepthook:`` / ``Original exception was:`` cascade with EMPTY
# bodies *after* it has finished successfully (rc=0), when a stderr write fails
# during interpreter finalization (many GDAL/rasterio datasets torn down at once
# on Windows). It floods the tail of an otherwise-clean log. Triaged as cosmetic
# in dev/phase-1/m01/warnings.md; ``run_and_tee`` collapses a *pure* trailing run
# of these into one summary line. A real traceback puts non-empty content
# between the markers, so it is never collapsed (see ``_is_shutdown_noise``).
_EXCEPTHOOK_MARKERS = ("Error in sys.excepthook:", "Original exception was:")


def _is_shutdown_noise(line):
    """True if ``line`` is a shutdown-excepthook marker or a blank line.

    Only pure marker/blank lines are collapsible. A genuine excepthook failure
    interleaves the markers with an actual traceback (``Traceback (most recent
    call last):`` ...); those body lines return False here, which breaks the
    candidate block and forces it to be emitted verbatim -- so no real error is
    ever hidden by the collapse.
    """
    stripped = line.strip()
    return stripped == "" or stripped in _EXCEPTHOOK_MARKERS


def run_and_tee(command, log_path):
    """Run ``command`` (an argv list), streaming combined stdout+stderr to the
    console AND ``log_path``, and return the child's exit code.

    Replaces the ``<cmd> 2>&1 | tee {log}`` idiom in ``shell:`` rules. A bare
    ``| tee`` pipeline returns *tee*'s exit status, not the command's, unless
    bash ``pipefail`` is active -- and Snakemake injects no ``pipefail`` prefix
    on Windows/cmd.exe, so a failed ``hydromt``/``julia`` step is misread as
    success (t260721a; dev/followups.md). Teeing in-process restores exit-code
    fidelity while keeping live console output. The child runs with
    ``shell=False`` so argument quoting is preserved identically across cmd.exe
    and bash (e.g. Julia's ``-e "using Wflow; Wflow.run()"`` stays one argv).

    A *pure* trailing run of benign interpreter-shutdown excepthook noise (see
    ``_EXCEPTHOOK_MARKERS``) is collapsed into a single summary line so it does
    not bury the real end of the log. The collapse is conservative: candidate
    lines are buffered, and any real content flushes them verbatim, so the
    filter only ever fires on a genuinely empty-bodied shutdown cascade.

    Parameters
    ----------
    command : list[str]
        Program and arguments, already tokenized (as a ``shell:`` rule's words
        arrive after ``--``).
    log_path : str | os.PathLike
        Destination log file; parent directories are created.

    Returns
    -------
    int
        The child process's return code.
    """
    log_path = os.fspath(log_path)
    parent = os.path.dirname(log_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    project_root, _ = _log_path_parts(log_path)
    with open(log_path, "w", encoding="utf-8", errors="replace") as log:
        log.write(_log_header_lines(log_path))  # header to file only, not console
        log.flush()

        def emit(text):
            # Compact hydromt's redundant log format (see _compact_log_line) and
            # show project files relative to the project dir; non-hydromt lines
            # and out-of-project paths pass through unchanged.
            text = _relativize_paths(_compact_log_line(text), project_root)
            # The log file is UTF-8. The live console mirror may be a legacy
            # code page (cp1252 on Windows) that cannot encode glyphs the child
            # emits (e.g. Julia/Wflow progress-bar blocks); fall back to a lossy
            # encode for the console only — the log always gets the real text.
            try:
                sys.stdout.write(text)
            except UnicodeEncodeError:
                enc = getattr(sys.stdout, "encoding", None) or "utf-8"
                sys.stdout.write(text.encode(enc, "replace").decode(enc))
            sys.stdout.flush()
            log.write(text)
            log.flush()

        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True,
            # Decode the child's pipe as UTF-8. Julia/Wflow (and Python under
            # UTF-8 mode) emit UTF-8; without this, text mode uses the Windows
            # locale code page (cp1252) and mangles non-ASCII — a `█` (UTF-8
            # E2 96 88) decoded as cp1252 becomes "â–ˆ". ASCII-only children
            # (hydromt logs) are unaffected; `errors="replace"` guards any
            # genuinely non-UTF-8 byte instead of crashing the tee.
            encoding="utf-8",
            errors="replace",
        )
        # ``pending`` holds a trailing run of candidate shutdown-noise lines that
        # are withheld until we know whether real content follows (flush
        # verbatim) or the stream ends (collapse if it is a true cascade).
        pending = []
        for line in proc.stdout:
            if _is_shutdown_noise(line):
                pending.append(line)
                continue
            for buffered in pending:
                emit(buffered)
            pending = []
            emit(line)
        rc = proc.wait()
        _flush_pending(pending, emit, rc)
        return rc


def _flush_pending(pending, emit, rc):
    """Emit the trailing candidate block: collapse a real cascade, else verbatim.

    Collapse only when the block holds at least two markers (one full
    ``excepthook``/``original`` unit); a smaller or marker-free tail is emitted
    unchanged so nothing real is dropped.
    """
    marker_count = sum(1 for ln in pending if ln.strip() in _EXCEPTHOOK_MARKERS)
    if marker_count >= 2:
        emit(
            f"[run_logged] collapsed {len(pending)} benign interpreter-shutdown "
            f"lines (repeated 'Error in sys.excepthook:' / 'Original exception "
            f"was:'; child rc={rc})\n"
        )
    else:
        for buffered in pending:
            emit(buffered)


@contextlib.contextmanager
def tee_to_log(log_path):
    """Tee ``sys.stdout``/``sys.stderr`` to ``log_path`` for a ``script:`` rule.

    Snakemake does not auto-redirect ``script:`` output to the rule's ``log:``
    (unlike ``shell:`` rules), so a script wraps its body in this manager and
    passes ``snakemake.log[0]``.

    Contract (R3 design §6):
    - creates ``log_path`` and any missing parent directories;
    - both streams are restored in a ``finally`` — the redirection cannot leak
      past the ``with`` block even if the body raises;
    - the exception is **re-raised** (not swallowed), so the traceback still
      reaches Snakemake and the rule fails loudly rather than leaving an empty
      log that Snakemake would read as a finished product.

    Parameters
    ----------
    log_path : str | os.PathLike
        Destination log file. Callers pass the rule's unique
        ``snakemake.log[0]`` so concurrent jobs never share a path.
    """
    log_path = os.fspath(log_path)
    parent = os.path.dirname(log_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    orig_out, orig_err = sys.stdout, sys.stderr
    project_root, _ = _log_path_parts(log_path)
    with open(log_path, "w", encoding="utf-8") as handle:
        handle.write(_log_header_lines(log_path))  # header to file only
        handle.flush()
        sys.stdout = _Tee(orig_out, handle, project_root=project_root)
        sys.stderr = _Tee(orig_err, handle, project_root=project_root)
        try:
            yield
        finally:
            sys.stdout, sys.stderr = orig_out, orig_err


def log_row(message, module="cst", level="INFO"):
    """Print one log row in the standard compact format used across rule logs.

    ``HH:MM:SS - <module> - <LEVEL> - <message>`` — the same shape
    ``_compact_log_line`` produces for hydromt records, so a ``script:`` rule's
    own messages sit uniformly among the hydromt/library lines rather than as
    bare, timestamp-less text. Use this instead of a plain ``print`` for anything
    meant to appear in a rule log. The row is already compact, so the tee passes
    it through (only any project paths in it are relativized).
    """
    print(f"{datetime.now():%H:%M:%S} - {module} - {level} - {message}")


def save_figure(path, module="plot", **kwargs):
    """Save the current matplotlib figure to ``path`` and announce it cleanly.

    Centralizes the "write a figure + log one line" pattern for the plotting
    ``script:`` rules: every produced map/plot appears in the rule's log as a
    standard row ``HH:MM:SS - <module> - INFO - Saved figure: <path>`` (via
    ``log_row``) instead of the log being empty or showing only upstream
    library chatter. Parent directories are created. ``kwargs`` pass through to
    ``matplotlib.pyplot.savefig`` (e.g. ``dpi``, ``bbox_inches``). matplotlib is
    imported lazily so this module stays light for the Snakefiles that import it
    only for ``get_config`` / ``stress_test_grid``.
    """
    import matplotlib.pyplot as plt

    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    plt.savefig(path, **kwargs)
    log_row(f"Saved figure: {path}", module=module)
