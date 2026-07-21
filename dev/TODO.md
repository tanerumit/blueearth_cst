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

**Active campaign:** pre-R6 followups (`fix/pre-r6-followups`), tracker at
[`working/2026-07-21_pre-r6-followups.md`](working/2026-07-21_pre-r6-followups.md).
Wave A (no-run tripwire fixes) done 2026-07-21.

| ID | Task | Status | Area | Updated | Working note |
|---|---|---|---|---|---|
| t260720e | **D-ATTRS** — M2b CF-metadata loss on `annual_change_scalar_stats_summary.nc` (`{}` attrs). R4 probe localized it to the hydromt catalog read (`get_rasterdataset`), a dependency op. Needs a real CMIP6 read to confirm, then a wf2 attrs re-attach (or upstream hydromt); moves the summary `.nc` fingerprint. Absorbs the old t260716c "CMIP6 attr loss" item. | backlog | pre-R6 / R4-audit | 2026-07-21 | [`chain-audit.md`](r04/chain-audit.md) |
| t260716a' | wf1 followup remnants (truncation warning DONE `ce56bc3`): (1) exhaustive M1 warnings triage — sweep the now-present per-rule `log:` files; (2) `extract_climate_grid` config-staleness — declare the config (or a key-hash) as a rule input so `historical:` edits invalidate the output. | backlog | pre-R6 / R3 | 2026-07-21 | [`followups.md`](followups.md) → "R3 — Workflow 1" |
| t260719a | `setup_constant_pars` CSDMS restoration — scientific-review task (split out of R3). Design **ACCEPTED** in [ADR 0001](decisions/0001-restore-wflow-constant-parameters.md) (design-review-loop: internal panel + 2 external GPT rounds + arbitration; 26 findings resolved; review record `dev/reviews/2026-07-21_adr-0001-constant-pars.md`). **Implementation remains** — build-heavy (two pinned clean builds + fail-closed two-sided equivalence gate + TOML landing script + a `check_baseline.py` discharge comparator + `record --workflow` + branched wf3 re-record). Moves the baseline. Route to model-builder. | active | pre-R6 / constant-params | 2026-07-21 | [ADR 0001](decisions/0001-restore-wflow-constant-parameters.md) |

**Done this campaign (2026-07-21, `fix/pre-r6-followups`):** t260720a
(`variance.max` endpoint, `d2de843`), t260720c (D-CAL cftime, `c57eda0`),
t260720d (D-VAR/D-MEM fail-loud, `735cc20`), t260716a truncation warning
(`ce56bc3`), t260721a (wf1 tee wrapper, `d13ba37`).

**Closed as already-done (verified 2026-07-21):** t260716a `test_cli` xfails
(R3+R5), t260716b `historical:` wiring (R5), t260716c outlet naming (R3).
Upstream weathergenr (t260716b tail) is a separate `tanerumit/weathergenr`
concern, out of this repo's board.

> **Detail lives in `followups.md`**, kept as the milestone-scoped backlog store
> (it carries reproducible context and is referenced by live tests). Promote an
> individual item to an `active` row here when its milestone starts.
