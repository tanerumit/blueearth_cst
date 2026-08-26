"""The WF3 forcing window — the year span every stress-test member is run over.

Its own module rather than living beside its main consumer in
``downscale_climate_forcing``, because that module imports ``hydromt_wflow`` at
module scope. ``run_stress_test.smk`` needs this window at PARSE time to size
Wflow batches against the disk (:mod:`blueearth_cst.experiment.batch_sizing`),
and a Snakefile cannot pay a hydromt import to learn two integers.

The arithmetic stays in ONE place: :func:`forcing_window` is the string form
rule 3.14 hands to hydromt, :func:`forcing_window_years` is the integer form the
batch estimator counts days between. A second copy of the snapping rule would
be free to drift from the window the run actually uses, which is precisely the
number a disk estimate must not get wrong.

``numpy`` rather than the stdlib because the Snakefile already imports it, so it
is free here, and because ``np.round``'s half-to-even is the rounding the landed
window has always used.
"""

import numpy as np


def forcing_window_years(horizontime_climate, wflow_run_length):
    """Return the inclusive ``(startyear, endyear)`` the forcing window spans.

    The window is ``wflow_run_length`` years wide, split around the horizon year
    and snapped to whole years: ``ceil`` backwards, ``round`` forwards, so an odd
    run length puts the extra year at the end.

    Note the span is ``run_length + 1`` calendar years whenever the halves snap
    outward -- ``run_length`` 8 at horizon 2050 gives 2046..2054, which is NINE
    years of forcing. That surprise is load-bearing for the disk estimate, and is
    why the estimator counts days between these two integers instead of
    multiplying ``run_length`` by 365.
    """
    startyear = int(horizontime_climate - np.ceil(wflow_run_length / 2))
    endyear = int(horizontime_climate + np.round(wflow_run_length / 2))
    return startyear, endyear


def forcing_window_iso(startyear, endyear):
    """Render an INCLUSIVE year pair as the ``(starttime, endtime)`` ISO pair.

    As hydromt and the run TOML want it. Since `C-67` the two years are
    DECLARED, as ``simulation_window: {start, end}``, rather than derived
    from a horizon year and a run length -- so this no longer computes a
    window, it only formats one.

    :func:`forcing_window_years` stays beside it as the record of how the
    pair used to be derived. It is no longer on any run path: the inverse
    is not single-valued for an odd run length, which is why `C-67` moved
    the window into the config instead of keeping the two scalars.
    """
    return f"{startyear}-01-01T00:00:00", f"{endyear}-12-31T00:00:00"
