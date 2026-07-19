"""Shared helpers for the BlueEarth-CST Snakefiles.

Imported by all three ``Snakefile_*`` entry points (and ``tests/conftest.py``)
so the ``get_config`` contract lives in exactly one place. Each Snakefile makes
this module importable regardless of the working directory by prepending its
own directory to ``sys.path`` before importing — see
``dev/r03/model-builder-design.md`` §3.
"""


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
