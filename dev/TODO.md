# TODO

Live task board. Unfinished work only -- move closed tasks to `dev/tasks/` and
delete their working notes. Row order expresses priority.

**Next review:** _not scheduled_ -- set a date or milestone for the first
periodic project-health review.

- **ID** -- date-based, `t<YYMMDD><letter>` (e.g. `t260716a`).
- **Status** -- `backlog`, `active`, or `blocked`.
- **Area** -- free project-specific label.
- **Updated** -- ISO date of the last status change.
- **Working note** -- optional link into `dev/working/`.

| ID | Task | Status | Area | Updated | Working note |
|---|---|---|---|---|---|
| t260716a | R3 workflow-1 followups: `test_cli` xfails, exhaustive M1 warnings triage, `extract_climate_grid` truncation + Snakemake config-staleness | backlog | R3 | 2026-07-16 | [`followups.md`](followups.md) → "R3 — Workflow 1" |
| t260716b | R5 workflow-3 followups: wire `historical:` config into `extract_climate_grid`, weathergenr `spatial_ref`/wavelet fixes | backlog | R5 | 2026-07-16 | [`followups.md`](followups.md) → "R5 — Workflow 3" |
| t260716c | R3+ upgrade followups from M2b: CMIP6 attr loss on merge, outlet naming convention, weathergenr/julia install story | backlog | R3+ | 2026-07-19 | [`followups.md`](followups.md) → "M2b" |
| t260719a | `setup_constant_pars` CSDMS restoration — dedicated scientific-review task (split out of R3, which is behavior-preserving). Requires a parameter-reconciliation table, direct staticmaps.nc/TOML assertions, data-level workflow-1 discharge comparison, and a clean dedicated project-dir re-record. Moves the baseline. | backlog | constant-params | 2026-07-19 | [`followups.md`](followups.md) → "M2b" |
| t260720c | **D-CAL** — `get_change_annual_clim_proj` cftime calendar defect: slices a cftime-indexed dataset with `pd.to_datetime` bounds, raising `TypeError` on 360-day/noleap calendars (CMIP6-native). Latent for the current seed (standard-calendar models) but real for the general model set. Fix = cftime-safe slicing (string bounds or `.to_datetimeindex()`, cf. `plot_proj_timeseries.py`); then remove the strict-xfail on tests rows C1/C2. | backlog | R4-audit | 2026-07-20 | [`chain-audit.md`](r04/chain-audit.md) |
| t260720d | **D-VAR + D-MEM** — fail-loud hardening in `get_change_annual_clim_proj`: asymmetric hist/clim **variables** (silent `intersection()`) and **members** (silent inner-join) must raise `ValueError` naming the dropped element. Scientific decision (error-path change, may surface latent production asymmetries). Then remove the strict-xfail on tests rows V/P and delete their characterization tests. | backlog | R4-audit | 2026-07-20 | [`chain-audit.md`](r04/chain-audit.md) |
| t260720e | **D-ATTRS** — M2b CF-metadata loss on `annual_change_scalar_stats_summary.nc` (`{}` attrs). The R4 probe (`dev/scripts/probe_attrs_chain.py`) localized it to the hydromt catalog read (`get_rasterdataset`), a dependency op — no workflow-2 pure-Python op drops attrs. Fix = upstream hydromt or an explicit attrs re-attach; moves the summary `.nc` fingerprint (a `baseline_diffs.md` entry). | backlog | R4-audit | 2026-07-20 | [`chain-audit.md`](r04/chain-audit.md) |

> **Detail lives in `followups.md`**, kept as the milestone-scoped backlog store
> (it carries reproducible context and is referenced by live tests). Promote an
> individual item to an `active` row here when its milestone starts.
