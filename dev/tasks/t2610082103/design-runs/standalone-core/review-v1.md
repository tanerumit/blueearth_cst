# Independent review of design-v1

Reviewer: fresh cst-architect subagent, read-only, local (no external transmission), 2026-10-23.
Reviewed: `design-v1.md` as committed in `c36f234f`. Verdict: **revise**. Findings were spot-checked
against the code before disposition.

| # | Severity | Finding | Disposition in v2 |
|---|---|---|---|
| 1 | Blocking | `map_reference.REFERENCE_FILES` (`map_reference.py:69-79`) hashes `fundamentals.py`, `plot_style.py`, `plot_setup.py`, `plot_colors.py`; any edit makes retained references stale | Accepted: §2.7, §4 |
| 2 | Major | `shared/plot_map.py:283,352` caption through `save_figure(annotation=...)` with no STYLE scope | Accepted: §2.4 inventory and harness |
| 3 | Major | Wrapping non-STYLE paths in `use_preset` would add STYLE rcParams and change cartographic output | Accepted: `rcparams=False` activation |
| 4 | Major | Ten scopes, not nine (`func_plot_signature.py:325`); attribute reads (`artists.FS_LABEL`, `fundamentals.H_SINGLE`) break if only imports move | Accepted: §1, §2.4 |
| 5 | Major | Named `test_case/test_local` inputs do not exist (no WF0 tables) | Accepted: retained all-five root named |
| 6 | Minor | Pandas-free test must also treat `pd.NA` and `np.datetime64("NaT")` as missing | Accepted: §2.2 |
| 7 | Minor | Demo with the full checkout on `sys.path` cannot detect file-relative reads | Accepted: isolated copy, `python -I` |
| 8 | Minor | `map_reference` is not an unscoped caller; STYLE key precedence must survive | Accepted: §2.3 stores STYLE verbatim |
| — | Overengineering | Name availability checks; full artist records for a pure refactor | Accepted: names listed without checks; artist records diagnostic-only |
