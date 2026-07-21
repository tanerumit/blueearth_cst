"""Shared helpers for the BlueEarth-CST Snakefiles.

Imported by all three ``Snakefile_*`` entry points (and ``tests/conftest.py``)
so the ``get_config`` contract lives in exactly one place. Each Snakefile makes
this module importable regardless of the working directory by prepending its
own directory to ``sys.path`` before importing — see
``dev/r03/model-builder-design.md`` §3.
"""

import contextlib
import os
import subprocess
import sys
from collections.abc import Mapping


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

    def __init__(self, *sinks):
        self._sinks = sinks

    def write(self, text):
        for sink in self._sinks:
            sink.write(text)
        return len(text)

    def flush(self):
        for sink in self._sinks:
            sink.flush()

    def isatty(self):
        return False


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
    with open(log_path, "w", encoding="utf-8", errors="replace") as log:
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True,
            errors="replace",
        )
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            log.write(line)
            log.flush()
        return proc.wait()


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
    with open(log_path, "w", encoding="utf-8") as handle:
        sys.stdout = _Tee(orig_out, handle)
        sys.stderr = _Tee(orig_err, handle)
        try:
            yield
        finally:
            sys.stdout, sys.stderr = orig_out, orig_err
