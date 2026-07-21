Status: proposed
Date: 2026-07-21
Deciders: Ümit Taner
Consulted: Observation 4 investigation (test/pre06 gabon run; plot_results.log);
           commit af38068 (honest-message fix that surfaced the dormant path)
Supersedes: none
Revisions:
  - 2026-07-21: initial draft (scoping only; no code). Genre: decision record.

# ADR 0002 — Revive the subcatchment climate plots by wiring P/T/EP outputs to the plot contract

### Context

`src/plot_results.py` §4 draws yearly and monthly climate figures (temperature,
precipitation, potential ET) at the subcatchment scale. It builds `ds_clim`
(line ~148) only when the wflow results CSV contains **all three** columns named
exactly `P_subcatchment`, `T_subcatchment`, `EP_subcatchment`, and
`src/func_plot_signature.py::plot_clim` reads those exact keys (T averaged; P and
EP summed to monthly/yearly accumulations).

No current configuration produces those columns:

- `src/setup_gauges_and_outputs.py` emits extra outputs as `{var}_basavg`
  (subcatchment **mean**, a basin-average series) — never `*_subcatchment`.
- Its `WFLOW_VARS` map has `precipitation` but **no temperature and no potential
  ET**, so `T`/`EP` cannot even be requested through `wflow_outvars`.
- The default `wflow_outvars: ['river discharge']` yields only `Q_*`.

So `ds_clim` is always empty and §4 always skips. On the gabon run this printed a
misleading "less than 1 year of data" line even though `output.csv` holds 20 years
(7670 daily steps, 2000–2020). Commit `af38068` corrected the **message** to name
the real cause (absent outputs); this ADR decides what to do about the underlying
**dormant capability**. The three variables are wflow's forcing inputs (P, T, PET),
so plotting their historical climatology is legitimate model-build QA — the plots
have value; they are simply unreachable.

A constraint shapes the choice: the durable baseline manifest fingerprints
`hydrology_model/run_default/output.csv` (wf1 discharge). Adding columns to that
file changes the fingerprint and forces a baseline re-record. Any revival must not
silently perturb the sealed discharge-only baseline.

### Decision

We will **revive** the climate plots by producing the three forcing series as
subcatchment-mean CSV timeseries whose headers match the plot contract, **opt-in
and default-off** so the sealed baseline is untouched:

1. Extend `WFLOW_VARS` in `setup_gauges_and_outputs.py` with the two missing
   CSDMS names (verified against the vendored hydromt_wflow catalog):
   - temperature → `atmosphere_air__temperature`
   - potential ET → `land_surface_water__potential_evaporation_volume_flux`
   - (precipitation already maps to `atmosphere_water__precipitation_volume_flux`)
2. Add a dedicated climate-output block (separate from the `_basavg` extras) that,
   **when enabled**, calls `setup_config_output_timeseries(mapname="subcatchment",
   toml_output="csv", header=["P_subcatchment","T_subcatchment","EP_subcatchment"],
   param=[precip, temp, pet CSDMS names], reducer=["mean","mean","mean"])`. The
   `*_subcatchment` header spelling becomes the explicit contract between setup and
   `plot_results`/`plot_clim`.
3. Gate it behind a new opt-in config key (e.g. `plot_climate_outputs: false`
   default) rather than default-on, so `output.csv` and the baseline manifest are
   unchanged unless the user opts in.

`plot_results.py` §4 is left reading the `*_subcatchment` names (now a satisfied
contract) — no change beyond the already-committed honest message.

### Consequences

*Positive*
- The yearly/monthly climate QA figures render when opted in; the dormant §4 path
  becomes reachable and tested.
- `WFLOW_VARS` gains T and PET, enabling other forcing outputs later.
- Default-off keeps the sealed discharge-only baseline stable — no re-record for a
  QA-only feature.

*Negative*
- New opt-in config surface to document and validate; a config typo path to guard
  (the existing `unknown` validation already fails loudly on bad `wflow_outvars`).
- When enabled, `output.csv` gains three columns → a **separate** enabled-mode
  baseline (or an explicit "not fingerprinted in enabled mode") is needed if that
  mode is ever sealed.

*Neutral*
- Requires confirming wflow 1.x accepts these forcing CSDMS names as `[output.csv]`
  params with a subcatchment reducer — a `<VERIFY>` before implementation.
- Units contract: P/EP as per-timestep fluxes (mm/day on daily runs) summed to
  monthly/yearly totals; T in °C averaged. Must be checked for plausibility.

### Alternatives considered

- **Remove the dead §4 code** (and `plot_clim`). One-line-simpler script, no new
  config. Not chosen: discards legitimate forcing-climatology QA the user wants;
  the fix is cheap wiring, not a rewrite. Would be preferred if the plots were
  judged scientifically redundant with the projection workflow.
- **Reconcile `plot_results` to the existing `_basavg` names** instead of adding
  `_subcatchment` outputs. Not chosen: `_basavg` is a single basin-average series,
  but §4 iterates `ds_clim.index` (per-subcatchment) — different semantics; and
  T/EP are still absent from `WFLOW_VARS`, so precipitation alone cannot fill the
  three-panel plot. Would be preferred only if per-subcatchment resolution were
  abandoned.
- **Default-on climate outputs.** Simplest UX (plots always appear). Not chosen:
  changes the sealed discharge-only `output.csv`, forcing a baseline re-record for
  a QA-only feature; opt-in avoids that coupling. Preferred if climate QA were
  deemed mandatory for every build.

### Related

- `src/plot_results.py` §4 and `src/func_plot_signature.py::plot_clim` — the plot
  contract (`P/T/EP_subcatchment`).
- `src/setup_gauges_and_outputs.py` — `WFLOW_VARS`, `setup_config_output_timeseries`.
- Commit `af38068` — the honest-message fix that exposed this dormant path.
- ADR 0001 — same `setup_gauges_and_outputs` / CSDMS-output surface; naming.md §6
  tier-1 (CSDMS names preserved verbatim).
- Baseline manifest (`dev/scripts/check_baseline.py`; memory: baseline-manifest-*)
  — the reason climate outputs are opt-in/default-off.
